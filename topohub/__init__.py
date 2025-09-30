"""
TopoHub Python package.

This package provides access to a repository of real-world and synthetic
network topologies in NetworkX node-link format. Unless otherwise noted,
node positions are stored as (longitude, latitude) tuples.
"""

__version__ = '1.5'

def get(key, use_names=False):
    """
    Load a topology from the embedded repository as a node-link dictionary.

    Parameters
    ----------
    key : str
        Repository key in the form "group/name" (e.g., "gabriel/25/0",
        "backbone/africa", "topozoo/Abilene", "sndlib/polska").
    use_names : bool, default False
        If True, replace integer node IDs with their ``name`` attributes in
        the returned structure. Not supported for topologies that contain
        unnamed or duplicate node names (e.g., some "backbone" or "caida").

    Returns
    -------
    dict
        NetworkX node-link dictionary with keys: ``graph``, ``nodes``, ``edges``.

    Raises
    ------
    KeyError
        If the specified topology key cannot be found/read.

    Examples
    --------
    .. code-block:: python

        import networkx as nx
        import topohub

        # Obtain topology dicts from JSON files stored in the repository
        topo = topohub.get('gabriel/25/0')
        topo = topohub.get('backbone/africa')
        topo = topohub.get('topozoo/Abilene')
        topo = topohub.get('sndlib/polska')

        # Create NetworkX graph from node-link dict
        g = nx.node_link_graph(topo, edges='edges')

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
        # Obtain percentage utilization of the link between node 0 and 10 under ECMP routing in the forward direction
        print(g.edges[0, 10]['ecmp_fwd']['uni'])

        # You can also load a topology using node names instead of integer IDs as node identifiers
        # (this will not work for 'backbone' and 'caida' topologies which have unnamed or duplicated name nodes)
        topo = topohub.get('sndlib/polska', use_names=True)
        g = nx.node_link_graph(topo, edges='edges')

        print(g.graph['demands'])
        print(g.edges['Gdansk', 'Warsaw']['dist'])
        print(g.edges['Gdansk', 'Warsaw']['ecmp_fwd']['uni'])

    """
    import importlib.resources
    import json

    import topohub.data

    try:
        topo = json.load((importlib.resources.files(topohub) / f'data/{key}.json').open())
    except OSError as err:
        raise KeyError from err
    else:
        if use_names:
            id_to_name = {}
            name_to_id = {}
            for node in topo['nodes']:
                id_to_name[node['id']] = node['name']
                if node['name'] in name_to_id:
                    raise RuntimeError(f"Duplicate node name '{node['name']}'")
                else:
                    name_to_id[node['name']] = node['id']
            for node in topo['nodes']:
                node['id'] = id_to_name[node['id']]
            for edge in topo['edges']:
                edge['source'] = id_to_name[edge['source']]
                edge['target'] = id_to_name[edge['target']]
            topo['graph']['demands'] = {id_to_name[int(n)]: {id_to_name[int(k)]: v for k, v in dems.items()} for n, dems in topo['graph']['demands'].items()}
        else:
            topo['graph']['demands'] = {int(n): {int(k): v for k, v in dems.items()} for n, dems in topo['graph']['demands'].items()}
        return topo
