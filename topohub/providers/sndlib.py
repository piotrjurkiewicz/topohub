import http.client as http

import topohub.generate

class SNDlibGenerator(topohub.generate.TopoGenerator):
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
