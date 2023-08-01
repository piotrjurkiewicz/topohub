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
    scaling = True

    @classmethod
    def generate_topo(cls, *args):
        return {}

    @classmethod
    def save_topo(cls, *args, **kwargs):
        g = nx.node_link_graph(cls.generate_topo(*args))
        topohub.graph.calculate_utilization(g)
        if 'filename' in kwargs:
            filename = kwargs['filename']
        else:
            filename = f'mininet/topo_lib/{g.name}'
        os.makedirs(filename.rpartition('/')[0], exist_ok=True)
        json.dump(nx.node_link_data(g), open(f'{filename}.json', 'w'), indent=kwargs.get('indent', 0))
        ps = None
        if kwargs.get('with_plot'):
            topohub.graph.save_topo_graph_svg(g, filename, cls.scaling)
        if kwargs.get('with_path_stats'):
            ps = topohub.graph.path_stats(g)
            topohub.graph.path_stats_print(ps, filename)
        if kwargs.get('with_topo_stats'):
            ts = topohub.graph.topo_stats(g, ps)
            # graph.topo_stats_print(ts, g.graph['name'], filename)
            g.graph['stats'] = ts
        json.encoder.float = RoundingFloat
        json.dump(nx.node_link_data(g), open(f'{filename}.json', 'w'), indent=kwargs.get('indent', 0), default=lambda x: format(x, '.2f'))
        json.encoder.float = float

class SNDLibGenerator(TopoGenerator):

    @classmethod
    def download_topo(cls, name):

        con = http.HTTPConnection("sndlib.zib.de", timeout=5)
        con.request('GET', "/coredata.download.action?objectName=%s&format=native&objectType=network" % name)
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name):

        mode = None
        nodes = []
        links = []
        pos = {}
        demands = {}

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
                pos[node] = (float(lon), float(lat))
                nodes.append({'id': node, 'pos': (float(lon), float(lat))})

            if mode == 'links':
                if line.startswith(")"):
                    mode = None
                    continue
                node0, node1 = line.split()[2:4]
                distance = topohub.graph.haversine(pos[node0], pos[node1])
                links.append({'source': node0, 'target': node1, 'distance': distance})

            if mode == 'demands':
                if line.startswith(")"):
                    mode = None
                    continue
                node0, node1 = line.split()[2:4]
                value = float(line.split()[6])
                if node0 not in demands:
                    demands[node0] = {}
                demands[node0][node1] = value

        name = ''.join([c if c.isalnum() else '_' for c in name.title()])
        name = name.lower()

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'links': links}

class TopoZooGenerator(TopoGenerator):

    @classmethod
    def download_topo(cls, name):

        con = http.HTTPConnection("www.topology-zoo.org", timeout=5)
        con.request('GET', f"/files/{name}.gml")
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name):

        mode = None
        node_id, node, lon, lat, node0, node1 = None, None, None, None, None, None
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
                    node0, node1 = None, None
                continue

            if mode == 'node':
                if line.startswith("  ]"):
                    if lon is not None and lat is not None:
                        node_id_to_name[node_id] = node
                        pos[node_id] = (float(lon), float(lat))
                        nodes.append({'id': node, 'pos': (float(lon), float(lat))})
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
                        distance = topohub.graph.haversine(pos[node0], pos[node1])
                        links.append({'source': node_id_to_name[node0], 'target': node_id_to_name[node1], 'distance': distance})
                    except KeyError:
                        pass
                    mode = None
                elif line.startswith("    source "):
                    node0 = line.split()[-1]
                elif line.startswith("    target "):
                    node1 = line.split()[-1]

        name = ''.join([c if c.isalnum() else '_' for c in name.title()])
        name = name.lower()

        if not nodes or not links:
            raise ValueError("Empty graph")

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'links': links}


class GabrielGenerator(TopoGenerator):
    scaling = False

    @classmethod
    def generate_topo(cls, nnodes, seed):

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
            node = 'R' + str(len(nodes))
            pos[node] = p
            nodes.append({'id': node, 'pos': p})

        def neighbors(p, q):
            c = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            dd = dist2(p, c)
            for r in pos.values():
                if r != p and r != q and dist2(r, c) < dd:
                    return False
            return True

        for p, (p_name, p_pos) in enumerate(pos.items()):
            for q, (q_name, q_pos) in enumerate(pos.items()):
                if p < q and neighbors(p_pos, q_pos):
                    distance = dist2(p_pos, q_pos) ** 0.5
                    links.append({'source': p_name, 'target': q_name, 'distance': distance})

        # nps = []
        # nss = []
        # nns = []
        # for pn, (p_name, p) in enumerate(pos.items()):
        #     for qn, (q_name, q) in enumerate(pos.items()):
        #         if p < q:
        #             nps.append(tuple(sorted((p_name, q_name))))
        #         if p_name < q_name:
        #             nss.append(tuple(sorted((p_name, q_name))))
        #         if pn < qn:
        #             nns.append(tuple(sorted((p_name, q_name))))
        #
        # assert(set(nps) == set(nss) == set(nns))

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'links': links}


class NumpyGabrielGenerator(TopoGenerator):

    @classmethod
    def generate_topo(cls, nnodes, seed):
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
            node = f'R{n}'
            pos[n] = p
            nodes.append({'id': node, 'pos': p})
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
                    distance = (pos[p] - pos[q]) ** 2
                    distance = (distance[0] + distance[1]) ** 0.5
                    links.append({'source': nodes[p]['id'], 'target': nodes[q]['id'], 'distance': distance})

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'links': links}


if __name__ == '__main__':

    topo_names = sys.argv[1:]

    if topo_names[0] == 'gabriel':

        for n in range(25, 525, 25):
            start_time = time.time()
            for i in range(10):
                GabrielGenerator.save_topo(n, (i * MAX_GABRIEL_NODES) + n, filename=f'data/gabriel/{n}/{i}', with_plot=True, with_topo_stats=True, with_path_stats=True)
            print(time.time() - start_time)

    elif topo_names[0] == 'sndlib':

        topo_names = ['abilene', 'atlanta', 'brain', 'cost266', 'dfn-bwin', 'dfn-gwin', 'di-yuan', 'france', 'geant',
                      'germany50', 'giul39', 'india35', 'janos-us', 'janos-us-ca', 'newyork', 'nobel-eu',
                      'nobel-germany', 'nobel-us', 'norway', 'pdh', 'pioro40', 'polska', 'sun', 'ta1', 'ta2', 'zib54']

        for topo_name in topo_names:
            SNDLibGenerator.save_topo(topo_name, filename=f'data/sndlib/{topo_name}', with_plot=True, with_path_stats=True, with_topo_stats=True)

    elif topo_names[0] == 'topozoo':

        topo_names = ['Aarnet', 'Abilene', 'Abvt', 'Aconet', 'Agis', 'Airtel', 'Ai3', 'Amres', 'Ans', 'Arn', 'Arnes',
                      'Arpanet196912', 'Arpanet19706', 'Arpanet19719', 'Arpanet19723', 'Arpanet19728', 'AsnetAm', 'Atmnet',
                      'AttMpls', 'Azrena', 'Bandcon', 'Basnet', 'Bbnplanet', 'Bellcanada', 'Bellsouth', 'Belnet2003',
                      'Belnet2004', 'Belnet2005', 'Belnet2006', 'Belnet2007', 'Belnet2008', 'Belnet2009', 'Belnet2010',
                      'BeyondTheNetwork', 'Bics', 'Biznet', 'Bren', 'BsonetEurope', 'BtAsiaPac', 'BtEurope',
                      'BtLatinAmerica', 'BtNorthAmerica', 'Canerie', 'Carnet', 'Cernet', 'Cesnet1993', 'Cesnet1997',
                      'Cesnet1999', 'Cesnet2001', 'Cesnet200304', 'Cesnet200511', 'Cesnet200603', 'Cesnet200706',
                      'Cesnet201006', 'Chinanet', 'Claranet', 'Cogentco', 'Colt', 'Columbus', 'Compuserve',
                      'CrlNetworkServices', 'Cudi', 'Cwix', 'Cynet', 'Darkstrand', 'Dataxchange', 'Deltacom',
                      'DeutscheTelekom', 'Dfn', 'DialtelecomCz', 'Digex', 'Easynet', 'Eenet', 'EliBackbone', 'Epoch',
                      'Ernet', 'Esnet', 'Eunetworks', 'Evolink', 'Fatman', 'Fccn', 'Forthnet', 'Funet', 'Gambia',
                      'Garr199901', 'Garr199904', 'Garr199905', 'Garr200109', 'Garr200112', 'Garr200212', 'Garr200404',
                      'Garr200902', 'Garr200908', 'Garr200909', 'Garr200912', 'Garr201001', 'Garr201003', 'Garr201004',
                      'Garr201005', 'Garr201007', 'Garr201008', 'Garr201010', 'Garr201012', 'Garr201101', 'Garr201102',
                      'Garr201103', 'Garr201104', 'Garr201105', 'Garr201107', 'Garr201108', 'Garr201109', 'Garr201110',
                      'Garr201111', 'Garr201112', 'Garr201201', 'Gblnet', 'Geant2001', 'Geant2009', 'Geant2010',
                      'Geant2012', 'Getnet', 'Globalcenter', 'Globenet', 'Goodnet', 'Grena', 'Gridnet', 'Grnet', 'GtsCe',
                      'GtsCzechRepublic', 'GtsHungary', 'GtsPoland', 'GtsRomania', 'GtsSlovakia', 'Harnet', 'Heanet',
                      'HiberniaCanada', 'HiberniaGlobal', 'HiberniaIreland', 'HiberniaNireland', 'HiberniaUk', 'HiberniaUs',
                      'Highwinds', 'HostwayInternational', 'HurricaneElectric', 'Ibm', 'Iij', 'Iinet', 'Ilan', 'Integra',
                      'Intellifiber', 'Internetmci', 'Internode', 'Interoute', 'Intranetwork', 'Ion',
                      'IowaStatewideFiberMap', 'Iris', 'Istar', 'Itnet', 'Janetbackbone', 'JanetExternal', 'Janetlense',
                      'Jgn2Plus', 'Karen', 'Kdl', 'KentmanApr2007', 'KentmanAug2005', 'KentmanFeb2008', 'KentmanJan2011',
                      'KentmanJul2005', 'Kreonet', 'LambdaNet', 'Latnet', 'Layer42', 'Litnet', 'Marnet', 'Marwan',
                      'Missouri', 'Mren', 'Myren', 'Napnet', 'Navigata', 'Netrail', 'NetworkUsa', 'Nextgen', 'Niif', 'Noel',
                      'Nordu1989', 'Nordu1997', 'Nordu2005', 'Nordu2010', 'Nsfcnet', 'Nsfnet', 'Ntelos', 'Ntt', 'Oteglobe',
                      'Oxford', 'Pacificwave', 'Packetexchange', 'Padi', 'Palmetto', 'Peer1', 'Pern', 'PionierL1',
                      'PionierL3', 'Psinet', 'Quest', 'RedBestel', 'Rediris', 'Renam', 'Renater1999', 'Renater2001',
                      'Renater2004', 'Renater2006', 'Renater2008', 'Renater2010', 'Restena', 'Reuna', 'Rhnet', 'Rnp',
                      'Roedunet', 'RoedunetFibre', 'Sago', 'Sanet', 'Sanren', 'Savvis', 'Shentel', 'Sinet', 'Singaren',
                      'Spiralight', 'Sprint', 'Sunet', 'Surfnet', 'Switch', 'SwitchL3', 'Syringa', 'TataNld', 'Telcove',
                      'Telecomserbia', 'Tinet', 'TLex', 'Tw', 'Twaren', 'Ulaknet', 'UniC', 'Uninet', 'Uninett2010',
                      'Uninett2011', 'Uran', 'UsCarrier', 'UsSignal', 'Uunet', 'Vinaren', 'VisionNet', 'VtlWavenet2008',
                      'VtlWavenet2011', 'WideJpn', 'Xeex', 'Xspedius', 'York', 'Zamren']

        for topo_name in topo_names:
            print(topo_name)
            try:
                TopoZooGenerator.save_topo(topo_name, filename=f'data/topozoo/{topo_name}', with_plot=True, with_path_stats=True, with_topo_stats=True)
            except nx.exception.NetworkXNoPath:
                pass
            except ValueError as exc:
                if exc.args[0] == 'Empty graph':
                    pass
                else:
                    raise
