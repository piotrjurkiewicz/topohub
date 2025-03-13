__version__ = '1.4.1'

def get(key, use_names=False):
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

        # By default, nodes are referred by their integer IDs
        # You can obtain node names through the `name` attribute
        print(g.nodes[0]['name'])
        print(g.nodes[10]['name'])

        # Obtain link length in kilometers between node 0 and 10
        print(g.edges[0, 10]['dist'])
        # Obtain percentage utilization of the link between node 0 and 10 under ECMP routing in forward direction
        print(g.edges[0, 10]['ecmp_fwd']['uni'])

        # You can also load a topology using node names instead integer IDs as node identifiers
        # (this will not work for 'backbone' category topologies which have unnamed or duplicated name nodes)
        topo = topohub.get('sndlib/polska', use_names=True)
        g = nx.node_link_graph(topo)

        print(g.graph['demands'])
        print(g.edges['Gdansk', 'Warsaw']['dist'])
        print(g.edges['Gdansk', 'Warsaw']['ecmp_fwd']['uni'])

    """
    import importlib.resources
    import json

    import topohub.data

    try:
        topo = json.load((importlib.resources.files(topohub) / f'data/{key}.json').open())
        if use_names:
            id_to_name = {}
            name_to_id = {}
            for n in topo['nodes']:
                id_to_name[n['id']] = n['name']
                if n['name'] in name_to_id:
                    raise RuntimeError(f"Duplicate node name '{n['name']}'")
                else:
                    name_to_id[n['name']] = n['id']
            for n in topo['nodes']:
                n['id'] = id_to_name[n['id']]
            for l in topo['links']:
                l['source'] = id_to_name[l['source']]
                l['target'] = id_to_name[l['target']]
            topo['graph']['demands'] = {id_to_name[int(n)]: {id_to_name[int(k)]: v for k, v in dems.items()} for n, dems in topo['graph']['demands'].items()}
        else:
            topo['graph']['demands'] = {int(n): {int(k): v for k, v in dems.items()} for n, dems in topo['graph']['demands'].items()}
        return topo
    except IOError:
        raise KeyError
