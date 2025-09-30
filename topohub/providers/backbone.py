"""
Backbone synthetic topology provider.

Generates synthetic backbone-style topologies from TopoGen JSON definitions.
Node positions are stored as (longitude, latitude) tuples.
"""

import json
import networkx as nx

import topohub.generate

class BackboneGenerator(topohub.generate.TopoGenerator):
    """
    Generator of backbone synthetic topologies.

    https://doi.org/10.1109/ICC.2015.7249292
    https://www.sciencedirect.com/science/article/pii/S2352711023002364
    """

    @classmethod
    def generate_topo(cls, name, **kwargs) -> dict:
        """
        Generate the specified backbone topology.

        Parameters
        ----------
        name : str
            Topology key identifying the region, e.g., 'africa' or 'africa_nosc'.
        **kwargs : dict
            Additional options reserved for future use (currently unused).

        Returns
        -------
        dict
            Topology graph in NetworkX node-link format. Node positions are
            stored as (lon, lat) tuples.
        """
        import topohub.geo
        _ = kwargs

        j = json.load(open('external/backbone/graph.json'))

        nodes = {}
        names_set = set()
        edges = []

        node_types = ['City', 'Seacable Landing Point']
        region = topohub.geo.regions.get(name)
        if name.endswith('_nosc'):
            region = topohub.geo.regions.get(name[:-5])
        else:
            node_types.append('Seacable Waypoint')

        for n in j['nodes']:
            if n['type'] in node_types and (not region or topohub.geo.point_in_polygon(n['longitude'], n['latitude'], region)) and -180 < n['longitude'] < 180:
                if n['type'] in ['City', 'Seacable Landing Point']:
                    names_set.add(n['name'])
                else:
                    n['name'] = None
                nodes[n['id']] = {'id': n['id'], 'pos': (n['longitude'], n['latitude']), 'type': n['type']}
                if n['name']:
                    nodes[n['id']]['name'] = n['name']

        for e in j['edges']:
            if e['u'] in nodes and e['v'] in nodes and (not name.endswith('_nosc') or e['type'] != 'seacable') and abs(nodes[e['u']]['pos'][0] - nodes[e['v']]['pos'][0]) < 180:
                edges.append({'source': e['u'], 'target': e['v'], 'dist': e['distance'], 'type': e['type']})

        g = nx.node_link_graph({'directed': False, 'multigraph': False, 'graph': {'name': str(name), 'demands': {}}, 'nodes': list(nodes.values()), 'edges': edges}, edges='edges')
        g = topohub.geo.remove_dead_ends(g)
        g = g.subgraph(max(nx.connected_components(g), key=len))

        return nx.node_link_data(g, edges='edges')
