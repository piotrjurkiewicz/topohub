#!/usr/bin/python3
import http.client as http
import json
import os
import random
import sys
import time

import networkx as nx

import topohub.graph

json.encoder.c_make_encoder = None
MAX_GABRIEL_NODES = 4096


class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.2f'))


class TopoGenerator:

    @classmethod
    def generate_topo(cls, *args):
        return {}

    @classmethod
    def save_topo(cls, *args, **kwargs):
        g = nx.node_link_graph(cls.generate_topo(*args))
        if 'filename' in kwargs:
            filename = kwargs['filename']
        else:
            filename = f'mininet/topo_lib/{g.name}'
        os.makedirs(filename.rpartition('/')[0], exist_ok=True)
        ps = None
        if kwargs.get('with_plot'):
            topohub.graph.save_topo_graph_svg(g, filename, kwargs.get('scale'), kwargs.get('background'))
        if kwargs.get('with_utilization'):
            topohub.graph.calculate_utilization(g, node_filter=kwargs.get('node_filter'))
        if kwargs.get('with_path_stats'):
            ps = topohub.graph.path_stats(g, node_filter=kwargs.get('node_filter'))
            topohub.graph.path_stats_print(ps, filename)
        if kwargs.get('with_topo_stats'):
            ts = topohub.graph.topo_stats(g, ps)
            # graph.topo_stats_print(ts, g.graph['name'], filename)
            g.graph['stats'] = ts
        json.encoder.float = RoundingFloat
        json.dump(nx.node_link_data(g), open(f'{filename}.json', 'w'), indent=kwargs.get('indent', 0), default=lambda x: format(x, '.2f'))
        json.encoder.float = float
        topohub.graph.write_gml(g, f'{filename}.gml')

class SNDlibGenerator(TopoGenerator):
    """
    Generator of topologies from the SNDlib.

    Source of data: https://sndlib.put.poznan.pl

    Orlowski, S., Wessäly, R., Pióro, M. and Tomaszewski, A. (2010),
    SNDlib 1.0—Survivable Network Design Library. Networks, 55: 276-286.
    https://doi.org/10.1002/net.20371
    """

    @classmethod
    def download_topo(cls, name):

        con = http.HTTPSConnection("sndlib.put.poznan.pl", timeout=5)
        con.request('GET', "/download/sndlib-networks-native/%s.txt" % name)
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name):
        """
        Download topology specified by name from SNDlib and generate its JSON.

        Parameters
        ----------
        name : str
            topology name

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        mode = None
        nodes = []
        links = []
        name_to_id = {}
        pos = {}
        demands = {}
        next_id = 0

        for line in cls.download_topo(name).splitlines():

            line = line.decode()

            if not mode:
                if line.startswith("NODES ("):
                    mode = 'nodes'
                elif line.startswith("LINKS ("):
                    mode = 'links'
                elif line.startswith("DEMANDS ("):
                    mode = 'demands'
                continue

            if mode == 'nodes':
                if line.startswith(")"):
                    mode = None
                    continue
                node = line.split()[0]
                lon, lat = line.split()[2:4]
                node_id = next_id
                next_id += 1
                name_to_id[node] = node_id
                pos[node] = (float(lon), float(lat))
                nodes.append({'id': node_id, 'name': node, 'pos': (float(lon), float(lat))})

            if mode == 'links':
                if line.startswith(")"):
                    mode = None
                    continue
                node0, node1 = line.split()[2:4]
                dist = topohub.graph.haversine(pos[node0], pos[node1])
                links.append({'source': name_to_id[node0], 'target': name_to_id[node1], 'dist': dist})

            if mode == 'demands':
                if line.startswith(")"):
                    mode = None
                    continue
                node0, node1 = line.split()[2:4]
                node0_id, node1_id = name_to_id[node0], name_to_id[node1]
                value = float(line.split()[6])
                if node0_id not in demands:
                    demands[node0_id] = {}
                demands[node0_id][node1_id] = value

        name = ''.join([c if c.isalnum() else '_' for c in name.title()])
        name = name.lower()

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'links': links}


class TopoZooGenerator(TopoGenerator):
    """
    Generator of topologies from the Internet Topology Zoo.

    Source of data: https://topology-zoo.org/

    S. Knight, H. X. Nguyen, N. Falkner, R. Bowden and M. Roughan,
    The Internet Topology Zoo. IEEE Journal on Selected Areas in Communications, vol. 29, no. 9, pp. 1765-1775.
    https://doi.org/10.1109/JSAC.2011.111002
    """

    @classmethod
    def download_topo(cls, name):

        con = http.HTTPSConnection("topology-zoo.org", timeout=5)
        con.request('GET', f"/files/{name}.gml")
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name):
        """
        Download topology specified by name from Topology Zoo and generate its JSON.

        Parameters
        ----------
        name : str
            topology name

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        mode = None
        node_id, node, lon, lat, node0_id, node1_id = None, None, None, None, None, None
        nodes = []
        links = []
        pos = {}
        node_id_to_name = {}
        demands = {}

        for line in cls.download_topo(name).splitlines():

            line = line.decode()

            if not mode:
                if line.startswith("  node ["):
                    mode = 'node'
                    node_id, node, lon, lat = None, None, None, None
                elif line.startswith("  edge ["):
                    mode = 'edge'
                    node0_id, node1_id = None, None
                continue

            if mode == 'node':
                if line.startswith("  ]"):
                    if lon is not None and lat is not None:
                        node_id_to_name[node_id] = node
                        pos[node_id] = (float(lon), float(lat))
                        nodes.append({'id': node_id, 'name': node, 'pos': (float(lon), float(lat))})
                    mode = None
                elif line.startswith("    id "):
                    node_id = line.split()[-1]
                elif line.startswith("    label "):
                    node = line.split(maxsplit=1)[-1].strip('"')
                elif line.startswith("    Longitude "):
                    lon = line.split()[-1]
                elif line.startswith("    Latitude "):
                    lat = line.split()[-1]

            if mode == 'edge':
                if line.startswith("  ]"):
                    try:
                        dist = topohub.graph.haversine(pos[node0_id], pos[node1_id])
                        links.append({'source': node0_id, 'target': node1_id, 'dist': dist})
                    except KeyError:
                        pass
                    mode = None
                elif line.startswith("    source "):
                    node0_id = line.split()[-1]
                elif line.startswith("    target "):
                    node1_id = line.split()[-1]

        name = ''.join([c if c.isalnum() else '_' for c in name.title()])
        name = name.lower()

        if not nodes or not links:
            raise ValueError("Empty graph")

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'links': links}


class GabrielGenerator(TopoGenerator):
    """
    Generator of Gabriel graph synthetic topologies.

    E. K. Çetinkaya, M. J. F. Alenazi, Y. Cheng, A. M. Peck and J. P. G. Sterbenz,
    On the fitness of geographic graph generators for modelling physical level topologies.
    2013 5th International Congress on Ultra Modern Telecommunications and Control Systems and Workshops (ICUMT), Almaty, Kazakhstan, 2013, pp. 38-45.
    https://doi.org/10.1109/ICUMT.2013.6798402.

    K. Ruben Gabriel , Robert R. Sokal,
    A New Statistical Approach to Geographic Variation Analysis. Systematic Biology, Volume 18, Issue 3, September 1969, Pages 259–278.
    https://doi.org/10.2307/2412323
    """

    @classmethod
    def generate_topo(cls, nnodes, seed):
        """
        Generate Gabriel graph topology with given number of nodes.

        Parameters
        ----------
        nnodes : int
            number of nodes
        seed : int
            random seed

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        assert nnodes <= MAX_GABRIEL_NODES

        nodes = []
        links = []
        pos = {}
        demands = {}

        random.seed(seed)

        scale = (nnodes * 10000) ** 0.5
        exclusion = 25.0  # prevent points from being too close
        print(nnodes, seed, scale, exclusion)

        def dist2(p, q):
            return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

        while len(pos) < nnodes:
            p = (random.random() * scale, random.random() * scale)
            if pos:
                nn = min(dist2(p, q) ** 0.5 for q in pos.values())
                if nn < exclusion:
                    continue
            node_id = len(nodes)
            node = 'R' + str(node_id)
            pos[node_id] = p
            nodes.append({'id': node_id, 'name': node, 'pos': p})

        def neighbors(p, q):
            c = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            dd = dist2(p, c)
            for r in pos.values():
                if r != p and r != q and dist2(r, c) < dd:
                    return False
            return True

        for p, (p_id, p_pos) in enumerate(pos.items()):
            for q, (q_id, q_pos) in enumerate(pos.items()):
                if p < q and neighbors(p_pos, q_pos):
                    dist = dist2(p_pos, q_pos) ** 0.5
                    links.append({'source': p_id, 'target': q_id, 'dist': dist})

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'links': links}


class NumpyGabrielGenerator(TopoGenerator):
    """
    Generator of Gabriel graph synthetic topologies basen on NumPy.

    E. K. Çetinkaya, M. J. F. Alenazi, Y. Cheng, A. M. Peck and J. P. G. Sterbenz,
    On the fitness of geographic graph generators for modelling physical level topologies.
    2013 5th International Congress on Ultra Modern Telecommunications and Control Systems and Workshops (ICUMT), Almaty, Kazakhstan, 2013, pp. 38-45.
    https://doi.org/10.1109/ICUMT.2013.6798402.

    K. Ruben Gabriel , Robert R. Sokal,
    A New Statistical Approach to Geographic Variation Analysis. Systematic Biology, Volume 18, Issue 3, September 1969, Pages 259–278.
    https://doi.org/10.2307/2412323
    """

    @classmethod
    def generate_topo(cls, nnodes, seed):
        """
        Generate Gabriel graph topology with given number of nodes.

        Parameters
        ----------
        nnodes : int
            number of nodes
        seed : int
            random seed

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        import numpy as np

        assert nnodes <= MAX_GABRIEL_NODES

        nodes = []
        links = []
        pos = {}
        demands = {}

        random.seed(seed)

        scale = (nnodes * 10000) ** 0.5
        exclusion = 25.0  # prevent points from being too close
        print(nnodes, seed, scale, exclusion)

        pos = np.empty((nnodes, 2))
        pos.fill(np.nan)

        def dist2(p, q):
            x = (p - q) ** 2
            return x[:, 0] + x[:, 1]

        n = 0
        exclusion_2 = exclusion ** 2
        while n < nnodes:
            p = (random.random() * scale, random.random() * scale)
            if nodes:
                if np.nanmin(dist2(p, pos)) < exclusion_2:
                    continue
            node_id = n
            node = f'R{node_id}'
            pos[node_id] = p
            nodes.append({'id': node_id, 'name': node, 'pos': p})
            n += 1

        def neighbors(p, q):
            c = (pos[p] + pos[q]) / 2
            dd = (pos[p] - c) ** 2
            dd = dd[0] + dd[1]
            # print(np.nanmin(dist2(c, pos)), dd)
            if dist2(pos, c).min() < dd:
                return False
            return True

        for p in range(nnodes):
            for q in range(nnodes):
                if p < q and neighbors(p, q):
                    dist = (pos[p] - pos[q]) ** 2
                    dist = (dist[0] + dist[1]) ** 0.5
                    links.append({'source': p, 'target': q, 'dist': dist})

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'links': links}


class BackboneGenerator(TopoGenerator):
    """
    Generator of Gabriel graph synthetic topologies.

    E. K. Çetinkaya, M. J. F. Alenazi, Y. Cheng, A. M. Peck and J. P. G. Sterbenz,
    On the fitness of geographic graph generators for modelling physical level topologies.
    2013 5th International Congress on Ultra Modern Telecommunications and Control Systems and Workshops (ICUMT), Almaty, Kazakhstan, 2013, pp. 38-45.
    https://doi.org/10.1109/ICUMT.2013.6798402.

    K. Ruben Gabriel , Robert R. Sokal,
    A New Statistical Approach to Geographic Variation Analysis. Systematic Biology, Volume 18, Issue 3, September 1969, Pages 259–278.
    https://doi.org/10.2307/2412323
    """

    @classmethod
    def generate_topo(cls, name):
        """
        Generate Gabriel graph topology with given number of nodes.

        Parameters
        ----------
        nnodes : int
            number of nodes
        seed : int
            random seed

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """
        import topohub.backbone

        j = json.load(open('external/backbone/graph.json'))

        nodes = {}
        names_set = set()
        links = []

        node_types = ['City', 'Seacable Landing Point']
        region = topohub.backbone.regions.get(name)
        if name.endswith('_nosc'):
            region = topohub.backbone.regions.get(name[:-5])
        else:
            node_types.append('Seacable Waypoint')

        for n in j['nodes']:
            if n['type'] in node_types:
                if not region or topohub.backbone.point_in_polygon(n['longitude'], n['latitude'], region):
                    if -180 < n['longitude'] < 180:
                        if n['type'] in ['City', 'Seacable Landing Point']:
                            names_set.add(n['name'])
                        else:
                            n['name'] = None
                        nodes[n['id']] = {'id': n['id'], 'pos': (n['longitude'], n['latitude']), 'type': n['type']}
                        if n['name']:
                            nodes[n['id']]['name'] = n['name']

        for e in j['edges']:
            if e['u'] in nodes and e['v'] in nodes:
                if not name.endswith('_nosc') or e['type'] != 'seacable':
                    if abs(nodes[e['u']]['pos'][0] - nodes[e['v']]['pos'][0]) < 180:
                        links.append({'source': e['u'], 'target': e['v'], 'dist': e['distance'], 'type': e['type']})

        g = nx.node_link_graph({'directed': False, 'multigraph': False, 'graph': {'name': str(name), 'demands': {}}, 'nodes': list(nodes.values()), 'links': links})
        g = topohub.backbone.remove_dead_ends(g)
        g = g.subgraph(max(nx.connected_components(g), key=len))

        return nx.node_link_data(g)


def main(topo_names):
    if topo_names[0] == 'gabriel':

        for nodes_number in range(25, 525, 25):
            start_time = time.time()
            for i in range(10):
                GabrielGenerator.save_topo(nodes_number, (i * MAX_GABRIEL_NODES) + nodes_number, filename=f'data/gabriel/{nodes_number}/{i}', with_plot=True, with_utilization=True, with_topo_stats=True, with_path_stats=True, scale=5)
            print(time.time() - start_time)

    elif topo_names[0] == 'sndlib':

        import topohub.backbone

        topo_names = {
            'abilene': {'include_countries': ['US']},
            'atlanta': None,
            'brain': {'include_countries': ['Germany']},
            'cost266': {'include_continents': ['EU']},
            'dfn-bwin': {'include_countries': ['Germany']},
            'dfn-gwin': {'include_countries': ['Germany']},
            'di-yuan': None,
            'france': None,
            'geant': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'germany50': {'include_countries': ['Germany']},
            'giul39': None,
            'india35': None,
            'janos-us': {'include_countries': ['US']},
            'janos-us-ca': {'include_countries': ['US', 'Canada']},
            'newyork': None,
            'nobel-eu': {'include_continents': ['EU']},
            'nobel-germany': {'include_countries': ['Germany']},
            'nobel-us': {'include_countries': ['US']},
            'norway': None,
            'pdh': {'include_countries': ['Germany']},
            'pioro40': None,
            'polska': {'include_countries': ['Poland']},
            'sun': None,
            'ta1': None,
            'ta2': None,
            'zib54': None
        }

        for topo_name in topo_names:
            if topo_names[topo_name]:
                background = topohub.backbone.generate_map(**topo_names[topo_name])
            else:
                background = None
            SNDlibGenerator.save_topo(topo_name, filename=f'data/sndlib/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=True)

    elif topo_names[0] == 'topozoo':

        import topohub.backbone

        topo_names = {
            'Aarnet': {'include_countries': ['Australia']},
            'Abilene': {'include_countries': ['US']},
            'Abvt': {'include_continents': ['EU'], 'include_countries': ['US', 'Japan']},
            'Aconet': {'include_countries': ['Austria']},
            'Agis': {'include_countries': ['US']},
            'Airtel': {'include_continents': ['EU', 'Asia'], 'include_countries': ['US']},
            # 'Ai3': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Amres': {'include_countries': ['Serbia']},
            'Ans': {'include_countries': ['United States of America']},
            'Arn': {'include_countries': ['Algeria']},
            'Arnes': {'include_countries': ['Slovenia']},
            'Arpanet196912': {'include_countries': ['US']},
            'Arpanet19706': {'include_countries': ['US']},
            'Arpanet19719': {'include_countries': ['US']},
            'Arpanet19723': {'include_countries': ['US']},
            'Arpanet19728': {'include_countries': ['US']},
            'AsnetAm': {'include_countries': ['US']},
            'Atmnet': {'include_countries': ['US']},
            'AttMpls': {'include_countries': ['US']},
            # 'Azrena': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Bandcon': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Basnet': {'include_countries': ['Belarus']},
            'Bbnplanet': {'include_countries': ['US']},
            'Bellcanada': {'include_countries': ['US', 'Canada']},
            'Bellsouth': {'include_countries': ['US']},
            'Belnet2003': {'include_countries': ['Belgium']},
            'Belnet2004': {'include_countries': ['Belgium']},
            'Belnet2005': {'include_countries': ['Belgium']},
            'Belnet2006': {'include_countries': ['Belgium']},
            'Belnet2007': {'include_countries': ['Belgium']},
            'Belnet2008': {'include_countries': ['Belgium']},
            'Belnet2009': {'include_countries': ['Belgium']},
            'Belnet2010': {'include_countries': ['Belgium']},
            'BeyondTheNetwork': {'include_countries': ['US']},
            'Bics': {'include_continents': ['EU']},
            'Biznet': {'include_countries': ['Indonesia']},
            # 'Bren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'BsonetEurope': {'include_continents': ['EU']},
            'BtAsiaPac': {'include_continents': ['Asia', 'Oceania']},
            'BtEurope': {'include_continents': ['EU']},
            # 'BtLatinAmerica': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'BtNorthAmerica': {'include_countries': ['US']},
            'Canerie': {'include_countries': ['US', 'Canada']},
            'Carnet': {'include_countries': ['Croatia']},
            'Cernet': {'include_countries': ['China']},
            'Cesnet1993': {'include_countries': ['Czechia']},
            'Cesnet1997': {'include_countries': ['Czechia']},
            'Cesnet1999': {'include_countries': ['Czechia']},
            'Cesnet2001': {'include_countries': ['Czechia']},
            'Cesnet200304': {'include_countries': ['Czechia']},
            'Cesnet200511': {'include_countries': ['Czechia']},
            'Cesnet200603': {'include_countries': ['Czechia']},
            'Cesnet200706': {'include_countries': ['Czechia']},
            'Cesnet201006': {'include_countries': ['Czechia']},
            'Chinanet': {'include_countries': ['China']},
            'Claranet': {'include_continents': ['EU']},
            # 'Cogentco': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Colt': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Columbus': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Compuserve': {'include_countries': ['US']},
            'CrlNetworkServices': {'include_countries': ['US']},
            # 'Cudi': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Cwix': {'include_countries': ['US']},
            'Cynet': {'include_countries': ['Cyprus']},
            'Darkstrand': {'include_countries': ['US']},
            'Dataxchange': {'include_countries': ['US']},
            # 'Deltacom': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'DeutscheTelekom': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Dfn': {'include_countries': ['Germany']},
            # 'DialtelecomCz': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Digex': {'include_countries': ['US']},
            # 'Easynet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Eenet': {'include_countries': ['Estonia']},
            'EliBackbone': {'include_countries': ['US']},
            'Epoch': {'include_countries': ['US']},
            'Ernet': {'include_countries': ['India']},
            # 'Esnet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Eunetworks': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Evolink': {'include_countries': ['Bulgaria']},
            # 'Fatman': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Fccn': {'include_countries': ['Portugal']},
            'Forthnet': {'include_countries': ['Greece']},
            'Funet': {'include_countries': ['Finland']},
            'Gambia': {'include_countries': ['Gambia']},
            'Garr199901': {'include_countries': ['Italy']},
            'Garr199904': {'include_countries': ['Italy']},
            'Garr199905': {'include_countries': ['Italy']},
            'Garr200109': {'include_countries': ['Italy']},
            'Garr200112': {'include_countries': ['Italy']},
            'Garr200212': {'include_countries': ['Italy']},
            'Garr200404': {'include_countries': ['Italy']},
            'Garr200902': {'include_countries': ['Italy']},
            'Garr200908': {'include_countries': ['Italy']},
            'Garr200909': {'include_countries': ['Italy']},
            'Garr200912': {'include_countries': ['Italy']},
            'Garr201001': {'include_countries': ['Italy']},
            'Garr201003': {'include_countries': ['Italy']},
            'Garr201004': {'include_countries': ['Italy']},
            'Garr201005': {'include_countries': ['Italy']},
            'Garr201007': {'include_countries': ['Italy']},
            'Garr201008': {'include_countries': ['Italy']},
            'Garr201010': {'include_countries': ['Italy']},
            'Garr201012': {'include_countries': ['Italy']},
            'Garr201101': {'include_countries': ['Italy']},
            'Garr201102': {'include_countries': ['Italy']},
            'Garr201103': {'include_countries': ['Italy']},
            'Garr201104': {'include_countries': ['Italy']},
            'Garr201105': {'include_countries': ['Italy']},
            'Garr201107': {'include_countries': ['Italy']},
            'Garr201108': {'include_countries': ['Italy']},
            'Garr201109': {'include_countries': ['Italy']},
            'Garr201110': {'include_countries': ['Italy']},
            'Garr201111': {'include_countries': ['Italy']},
            'Garr201112': {'include_countries': ['Italy']},
            'Garr201201': {'include_countries': ['Italy']},
            'Gblnet': {'include_continents': ['EU']},
            'Geant2001': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Cyprus']},
            'Geant2009': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Turkey', 'Cyprus']},
            'Geant2010': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Turkey', 'Cyprus']},
            'Geant2012': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Turkey', 'Cyprus']},
            'Getnet': {'include_countries': ['US']},
            'Globalcenter': {'include_countries': ['US']},
            # 'Globenet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Goodnet': {'include_countries': ['US']},
            'Grena': {'include_countries': ['Georgia']},
            'Gridnet': {'include_countries': ['US']},
            'Grnet': {'include_countries': ['Greece']},
            # 'GtsCe': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'GtsCzechRepublic': {'include_countries': ['Czechia']},
            'GtsHungary': {'include_countries': ['Hungary']},
            'GtsPoland': {'include_countries': ['Poland']},
            'GtsRomania': {'include_countries': ['Romania']},
            'GtsSlovakia': {'include_countries': ['Slovakia']},
            # 'Harnet': {'include_countries': ['Ireland']},
            'Heanet': {'include_countries': ['Ireland']},
            'HiberniaCanada': {'include_countries': ['Canada']},
            'HiberniaGlobal': {'include_continents': ['EU'], 'include_countries': ['US']},
            'HiberniaIreland': {'include_countries': ['Ireland']},
            'HiberniaNireland': {'include_countries': ['Ireland', 'United Kingdom']},
            'HiberniaUk': {'include_countries': ['United Kingdom']},
            'HiberniaUs': {'include_countries': ['US', 'Canada']},
            'Highwinds': {'include_continents': ['North America', 'South America', 'Europe'], 'exclude_countries': ['Russia']},
            'HostwayInternational': {'include_continents': ['all']},
            'HurricaneElectric': {'include_continents': ['all']},
            'Ibm': {'include_countries': ['US']},
            'Iij': {'include_countries': ['US', 'Japan']},
            'Iinet': {'include_countries': ['Australia']},
            'Ilan': {'include_countries': ['Israel']},
            'Integra': {'include_countries': ['US']},
            # 'Intellifiber': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Internetmci': {'include_countries': ['US']},
            'Internode': {'include_continents': ['all']},
            # 'Interoute': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Intranetwork': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Ion': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'IowaStatewideFiberMap': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Iris': {'include_countries': ['US']},
            'Istar': {'include_countries': ['Canada']},
            'Itnet': {'include_countries': ['Ireland']},
            'Janetbackbone': {'include_countries': ['United Kingdom']},
            # 'JanetExternal': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Janetlense': {'include_countries': ['United Kingdom']},
            'Jgn2Plus': {'include_countries': ['Japan']},
            'Karen': {'include_countries': ['New Zealand']},
            # 'Kdl': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'KentmanApr2007': {'include_countries': ['United Kingdom']},
            # 'KentmanAug2005': {'include_countries': ['United Kingdom']},
            'KentmanFeb2008': {'include_countries': ['United Kingdom']},
            # 'KentmanJan2011': {'include_countries': ['United Kingdom']},
            'KentmanJul2005': {'include_countries': ['United Kingdom']},
            'Kreonet': {'include_countries': ['South Korea']},
            # 'LambdaNet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Latnet': {'include_countries': ['Latvia']},
            'Layer42': {'include_countries': ['US']},
            'Litnet': {'include_countries': ['Lithuania']},
            'Marnet': {'include_countries': ['North Macedonia']},
            'Marwan': {'include_countries': ['Morocco']},
            # 'Missouri': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Mren': {'include_countries': ['Montenegro']},
            'Myren': {'include_countries': ['Malaysia']},
            'Napnet': {'include_countries': ['US']},
            'Navigata': {'include_countries': ['Canada']},
            'Netrail': {'include_countries': ['US']},
            'NetworkUsa': {'include_countries': ['US']},
            'Nextgen': {'include_countries': ['Australia']},
            'Niif': {'include_countries': ['Hungary']},
            'Noel': {'include_countries': ['US', 'Canada']},
            'Nordu1989': {'include_continents': ['EU']},
            'Nordu1997': {'include_continents': ['EU']},
            'Nordu2005': {'include_continents': ['EU']},
            # 'Nordu2010': {'include_continents': ['EU']},
            # 'Nsfcnet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Nsfnet': {'include_countries': ['US']},
            # 'Ntelos': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Ntt': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Oteglobe': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Oxford': {'include_countries': ['US']},
            'Pacificwave': {'include_countries': ['US']},
            'Packetexchange': {'include_continents': ['all']},
            # 'Padi': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Palmetto': {'include_countries': ['US']},
            'Peer1': {'include_continents': ['North America', 'Europe'], 'exclude_countries': ['Russia']},
            # 'Pern': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'PionierL1': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'PionierL3': {'include_countries': ['Poland']},
            'Psinet': {'include_countries': ['US']},
            'Quest': {'include_continents': ['all']},
            # 'RedBestel': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Rediris': {'include_countries': ['Spain']},
            'Renam': {'include_countries': ['Moldova']},
            'Renater1999': {'include_countries': ['France']},
            'Renater2001': {'include_countries': ['France']},
            'Renater2004': {'include_countries': ['France']},
            'Renater2006': {'include_countries': ['France']},
            'Renater2008': {'include_countries': ['France']},
            'Renater2010': {'include_countries': ['France']},
            'Restena': {'include_countries': ['Luxembourg']},
            # 'Reuna': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Rhnet': {'include_countries': ['Iceland']},
            'Rnp': {'include_countries': ['Brazil']},
            'Roedunet': {'include_countries': ['Romania']},
            # 'RoedunetFibre': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Sago': {'include_countries': ['US']},
            # 'Sanet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Sanren': {'include_countries': ['South Africa']},
            'Savvis': {'include_countries': ['US']},
            # 'Shentel': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Sinet': {'include_countries': ['Japan']},
            # 'Singaren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Spiralight': {'include_countries': ['US']},
            'Sprint': {'include_countries': ['US']},
            'Sunet': {'include_countries': ['Sweden']},
            'Surfnet': {'include_countries': ['Kingdom of the Netherlands']},
            # 'Switch': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'SwitchL3': {'include_countries': ['Switzerland']},
            # 'Syringa': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'TataNld': {'include_countries': ['India']},
            # 'Telcove': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Telecomserbia': {'include_countries': ['Serbia', 'Montenegro']},
            # 'Tinet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'TLex': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Tw': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Twaren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Ulaknet': {'include_countries': ['Turkey']},
            'UniC': {'include_countries': ['Denmark']},
            # 'Uninet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Uninett2010': {'include_countries': ['Norway']},
            'Uninett2011': {'include_countries': ['Norway', 'Sweden']},
            'Uran': {'include_countries': ['Ukraine']},
            # 'UsCarrier': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'UsSignal': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Uunet': {'include_countries': ['US', 'Canada']},
            'Vinaren': {'include_continents': ['Asia', 'Oceania']},
            'VisionNet': {'include_countries': ['US']},
            'VtlWavenet2008': {'include_continents': ['EU']},
            'VtlWavenet2011': {'include_continents': ['EU']},
            'WideJpn': {'include_continents': ['all']},
            'Xeex': {'include_continents': ['all']},
            'Xspedius': {'include_countries': ['US']},
            'York': {'include_countries': ['United Kingdom']},
            # 'Zamren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']}
        }

        for topo_name in topo_names:
            print(topo_name)
            if topo_names[topo_name]:
                background = topohub.backbone.generate_map(**topo_names[topo_name])
            else:
                background = None
            try:
                TopoZooGenerator.save_topo(topo_name, filename=f'data/topozoo/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=True)
            except nx.exception.NetworkXNoPath:
                pass
            except nx.NetworkXError:
                pass
            except ValueError as exc:
                if exc.args[0] == 'Empty graph':
                    pass
                else:
                    raise

    elif topo_names[0] == 'backbone':

        import topohub.backbone

        topo_names = {
            'africa': {'include_continents': ['Africa']},
            'africa_nosc': {'include_continents': ['Africa']},
            'americas': {'include_continents': ['North America', 'South America']},
            'americas_nosc': {'include_continents': ['North America', 'South America']},
            'atlantica': {'include_continents': ['North America', 'Europe'], 'include_countries': ['Turkey', 'Georgia', 'Cyprus'], 'exclude_countries': ['Russia']},
            'eastern': {'include_continents': ['Europe', 'Africa', 'Asia', 'Oceania']},
            'eastern_nosc': {'include_continents': ['Europe', 'Africa', 'Asia', 'Oceania']},
            'emea': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'emea_nosc': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'eurafrasia': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'eurafrasia_nosc': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'eurasia': {'include_continents': ['Europe', 'Asia']},
            'eurasia_nosc': {'include_continents': ['Europe', 'Asia']},
            'europe': {'include_continents': ['Europe'], 'include_countries': ['Turkey', 'Georgia', 'Cyprus'], 'exclude_countries': ['Russia']},
            'europe_nosc': {'include_continents': ['Europe'], 'include_countries': ['Turkey', 'Georgia', 'Cyprus'], 'exclude_countries': ['Russia']},
            'north_america': {'include_continents': ['North America']},
            'north_america_nosc': {'include_continents': ['North America']},
            'south_america': {'include_continents': ['South America']},
            'south_america_nosc': {'include_continents': ['South America']},
            'world': {'include_continents': ['all']}
        }

        for topo_name in topo_names:
            background = []
            if topo_names[topo_name]:
                background = topohub.backbone.generate_map(**topo_names[topo_name])
            # region = topohub.backbone.regions.get(topo_name)
            # if topo_name.endswith('_nosc'):
            #     region = topohub.backbone.regions.get(topo_name[:-5])
            # if region:
            #     path_data = topohub.backbone.polygon_to_path(region)
            #     background.append(f'<path class="selection" vector-effect="non-scaling-stroke" d="{path_data}"/>\n')
            BackboneGenerator.save_topo(topo_name, filename=f'data/backbone/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=0.1, node_filter=lambda n: n['type'] == 'City')


if __name__ == '__main__':
    main(sys.argv[1:])
