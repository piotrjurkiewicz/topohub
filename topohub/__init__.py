__version__ = '1.3'

import importlib.resources
import json

import topohub.data

def get(key):
    """
    Use this method to obtain topologies from the repository as dicts in node-link format.

    Example:

    .. code-block:: python

        import networkx as nx
        import topohub

        # Obtain topology dicts from JSON files stored in the repository
        topo = topohub.get('gabriel/25/0')
        topo = topohub.get('backbone/africa')
        topo = topohub.get('topozoo/Abilene')
        topo = topohub.get('sndlib/polska')

        # Create NetworkX graph from node-link dict
        g = nx.node_link_graph(topo)

        # Access graph parameters
        print(g.graph['name'])
        print(g.graph['demands'])
        print(g.graph['stats']['avg_degree'])

        # Obtain link length or ECMP routing utilization
        print(g.edges['Bydgoszcz', 'Warsaw']['dist'])
        print(g.edges['Bydgoszcz', 'Warsaw']['ecmp_fwd']['uni'])

    """
    try:
        topo = json.load((importlib.resources.files(topohub) / f'data/{key}.json').open())
        return topo
    except IOError:
        raise KeyError
