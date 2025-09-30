"""
Internet Topology Zoo provider.

Downloads GML topologies from the Internet Topology Zoo and converts them to
NetworkX node-link format. Node positions are stored as (longitude, latitude)
tuples when available in the GML.
"""

import http.client as http

import topohub.generate
import topohub.graph

class TopoZooGenerator(topohub.generate.TopoGenerator):
    """
    Generator of topologies from the Internet Topology Zoo.

    Source of data: https://topology-zoo.org/

    S. Knight, H. X. Nguyen, N. Falkner, R. Bowden and M. Roughan,
    The Internet Topology Zoo. IEEE Journal on Selected Areas in Communications, vol. 29, no. 9, pp. 1765-1775.
    https://doi.org/10.1109/JSAC.2011.111002
    """

    @classmethod
    def download_topo(cls, name) -> bytes:
        """
        Download a GML topology file by name from the Internet Topology Zoo.

        Parameters
        ----------
        name : str
            Topology name (as used by Topology Zoo filenames).

        Returns
        -------
        bytes
            Raw GML file contents.
        """

        con = http.HTTPSConnection("topology-zoo.org", timeout=5)
        con.request('GET', f"/files/{name}.gml")
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name, **kwargs) -> dict:
        """
        Download topology specified by name from Topology Zoo and generate its JSON.

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
        node_id, node, lon, lat, node0_id, node1_id = None, None, None, None, None, None
        nodes = []
        edges = []
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
                        edges.append({'source': node0_id, 'target': node1_id, 'dist': dist})
                    except KeyError:
                        pass
                    mode = None
                elif line.startswith("    source "):
                    node0_id = line.split()[-1]
                elif line.startswith("    target "):
                    node1_id = line.split()[-1]

        name = ''.join([c if c.isalnum() else '_' for c in name.title()])
        name = name.lower()

        if not nodes or not edges:
            raise ValueError("Empty graph")

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'edges': edges}
