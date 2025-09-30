"""
SNDlib topology provider.

Downloads native SNDlib topologies and converts them to NetworkX node-link
format. Node positions are stored as (longitude, latitude) tuples.
"""

import http.client as http

import topohub.generate
import topohub.graph

class SNDlibGenerator(topohub.generate.TopoGenerator):
    """
    Generator of topologies from the SNDlib.

    Source of data: https://sndlib.put.poznan.pl

    Orlowski, S., Wessäly, R., Pióro, M. and Tomaszewski, A. (2010),
    SNDlib 1.0—Survivable Network Design Library. Networks, 55: 276-286.
    https://doi.org/10.1002/net.20371
    """

    @classmethod
    def download_topo(cls, name) -> bytes:
        """
        Download a native SNDlib topology text file by name.

        Parameters
        ----------
        name : str
            Topology identifier as used in SNDlib native filenames.

        Returns
        -------
        bytes
            Raw file contents.
        """

        con = http.HTTPSConnection("sndlib.put.poznan.pl", timeout=5)
        con.request('GET', f"/download/sndlib-networks-native/{name}.txt")
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name, **kwargs) -> dict:
        """
        Download topology specified by name from SNDlib and generate its JSON.

        Parameters
        ----------
        name : str
            topology name
        **kwargs : dict
            Additional options reserved for future use (currently unused).

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        _ = kwargs

        mode = None
        nodes = []
        edges = []
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
                edges.append({'source': name_to_id[node0], 'target': name_to_id[node1], 'dist': dist})

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

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'edges': edges}
