#!/usr/bin/python3
"""
CAIDA topology provider.

Parses CAIDA Ark datasets to build ASN-specific undirected graphs. Node
positions are stored as (longitude, latitude) tuples. Includes optional
geo-filtering and node merging by identical or close positions.
"""
import subprocess

import networkx as nx

import topohub.generate
import topohub.geo
import topohub.graph

NODES_AS_FILE = "external/caida/2024-08/midar-iff.nodes.as"
NODES_GEO_FILE = "external/caida/2024-08/midar-iff.nodes.geo"
LINKS_FILE = "external/caida/2024-08/midar-iff.links"

ASN_TO_NODES = None
NODE_TO_GEO = None
ADJACENCY = None

def parse_nodes_as(path, asn=None, grep=True):
    """
    Parse CAIDA node-to-ASN mappings.

    Parameters
    ----------
    path : str
        Path to the midar-iff.nodes.as file.
    asn : int | None, default None
        If provided, filter to a specific ASN.
    grep : bool, default True
        Use external grep to speed up filtering for large files.

    Returns
    -------
    dict[int, set[int]]
        Mapping ASN -> set of node IDs.
    """
    if asn and grep:
        output = subprocess.run(["grep", f"\t{asn}\t", path], check=False, stdout=subprocess.PIPE)
        f = output.stdout.decode("utf-8").splitlines()
    else:
        f = open(path, encoding="utf-8", errors="replace")
    asn_to_nodes = {}
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 3:
            continue
        if cols[0] != "node.AS":
            continue
        node = int(cols[1][1:])
        parsed_asn = int(cols[2])
        if asn is not None and parsed_asn != asn:
            continue
        if parsed_asn == -1:
            continue
        if parsed_asn not in asn_to_nodes:
            asn_to_nodes[parsed_asn] = set()
        asn_to_nodes[parsed_asn].add(node)
    if not isinstance(f, list):
        f.close()
    return asn_to_nodes

def parse_nodes_geo(path, nodes=None, grep=True):
    """
    Parse CAIDA node geolocation data.

    Parameters
    ----------
    path : str
        Path to the midar-iff.nodes.geo file.
    nodes : Iterable[int] | None, default None
        If provided, limit parsing to these node IDs.
    grep : bool, default True
        Use external grep to speed up filtering for large files.

    Returns
    -------
    dict[int, tuple[str, ...]]
        Mapping node ID -> tuple of fields (as provided by CAIDA). Consumers
        should extract city, latitude, longitude and convert to floats as needed.
    """
    if nodes is not None and grep:
        regexp = "\n".join(f"N{node}:" for node in nodes).encode("utf-8")
        output = subprocess.run(["grep", "-Ff", "-", path], check=False, input=regexp, stdout=subprocess.PIPE)
        f = output.stdout.decode("utf-8").splitlines()
    else:
        f = open(path, encoding="utf-8", errors="replace")
    node_to_geo = {}
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 7:
            continue
        if cols[0][:8] != "node.geo":
            continue
        node = int(cols[0][10:-1])
        if nodes is not None and node not in nodes:
            continue
        node_to_geo[node] = tuple(cols[1:7])
    if not isinstance(f, list):
        f.close()
    return node_to_geo

def parse_links(path, nodes=None, grep=True):
    """
    Parse undirected adjacency from the CAIDA links file.

    Parameters
    ----------
    path : str
        Path to midar-iff.links file.
    nodes : Iterable[int] | None, default None
        If provided, include links only among this node subset.
    grep : bool, default True
        Use external grep to speed up filtering for large files.

    Returns
    -------
    dict[int, set[int]]
        Undirected adjacency list (both directions present).
    """
    if nodes is not None and grep:
        regexp = "\n".join(f"N{node}" for node in nodes).encode("utf-8")
        output = subprocess.run(["grep", "-Ff", "-", path], check=False, input=regexp, stdout=subprocess.PIPE)
        f = output.stdout.decode("utf-8").splitlines()
    else:
        f = open(path, encoding="utf-8", errors="replace")
    adj = {}
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split()
        if len(cols) < 3:
            continue
        if cols[0] != "link":
            continue
        src = cols[2][1:]
        i = src.find(":")
        if i != -1:
            src = int(src[:i])
        else:
            src = int(src)
        if nodes is not None and src not in nodes:
            continue
        for dst in cols[3:]:
            dst = dst[1:]
            i = dst.find(":")
            if i != -1:
                dst = int(dst[:i])
            else:
                dst = int(dst)
            if src == dst:
                continue
            if nodes is not None and dst not in nodes:
                continue
            if src not in adj:
                adj[src] = set()
            adj[src].add(dst)
            if dst not in adj:
                adj[dst] = set()
            adj[dst].add(src)
    if not isinstance(f, list):
        f.close()
    return adj

def merge_nodes_by_pos(selected_with_pos, adjacency, distance_km=None):
    """
    Merge nodes that share the same coordinates or are within a threshold distance.

    Representative selection rules within each group:
    1) Among nodes which have a city name, select a node whose city name is most common;
    2) If all city names occur equally often, select the lowest node id among named nodes;
    3) If there are no nodes with names, select the lowest node id.

    If ``distance_km`` is provided, a second pass merges groups whose representatives are within
    the given distance (in kilometers), using the same selection rules on the combined group.

    Parameters
    ----------
    selected_with_pos : dict[int, (float, float, str)]
        Mapping from node id to (lon, lat, city) for nodes selected for the graph.
    adjacency : dict[int, set[int]]
        Undirected adjacency list of nodes.
    distance_km : float | None, default None
        If None, merge nodes only with the exact same (lon, lat). If provided, also merge nodes whose
        haversine distance is <= ``distance_km``.

    Returns
    -------
    tuple[dict[int, (float, float, str)], dict[int, set[int]]]
        positions remain as (lon, lat) tuples.
    """

    if not selected_with_pos:
        return {}, {}

    # Helper: choose representative according to rules
    # 1) Among nodes with a city name, prefer the most common city name;
    # 2) If tie among names, pick the lowest id among named nodes;
    # 3) If no nodes have names, pick the lowest id.
    def choose_representative(nodes):
        named_nodes = [n for n in nodes if selected_with_pos[n][2]]
        if named_nodes:
            name_to_nodes = {}
            for n in named_nodes:
                name = selected_with_pos[n][2]
                name_to_nodes.setdefault(name, []).append(n)
            max_count = max(len(v) for v in name_to_nodes.values())
            top_names = {name for name, arr in name_to_nodes.items() if len(arr) == max_count}
            candidates = [n for n in named_nodes if selected_with_pos[n][2] in top_names]
            return min(candidates)
        return min(nodes)

    # Exact (lon, lat) merge first
    rep_map = {}
    pos_to_nodes = {}
    for n, (lon, lat, _) in selected_with_pos.items():
        pos_to_nodes.setdefault((lon, lat), []).append(n)
    for nodes in pos_to_nodes.values():
        rep = choose_representative(nodes)
        for n in nodes:
            rep_map[n] = rep

    # Optional distance-based merge on the reduced set of representatives
    if distance_km is not None:
        thr = float(distance_km)
        reps = list(set(rep_map.values()))

        # Union-Find over representatives
        parent = {r: r for r in reps}
        rank = dict.fromkeys(reps, 0)

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1

        # Pairwise check (O(m^2)) across representatives only
        for i in range(len(reps)):
            ri = reps[i]
            lon0, lat0, _ = selected_with_pos[ri]
            for j in range(i + 1, len(reps)):
                rj = reps[j]
                lon1, lat1, _ = selected_with_pos[rj]
                if topohub.graph.haversine((lon0, lat0), (lon1, lat1)) <= thr:
                    union(ri, rj)

        # Normalize roots to minimal-id representative per cluster
        groups = {}
        for r in reps:
            root = find(r)
            groups.setdefault(root, []).append(r)
        rep_map_second = {}
        for group_nodes in groups.values():
            # Consider all original nodes that collapsed to these first-pass reps
            original_nodes = [n for n, r in rep_map.items() if r in group_nodes]
            final_rep = choose_representative(original_nodes)
            for r in group_nodes:
                rep_map_second[r] = final_rep

        # Update mapping from original nodes to final representatives
        for n in rep_map:
            rep_map[n] = rep_map_second[rep_map[n]]

    # Build merged_selected using the chosen representative's attributes
    merged_selected = {rep: selected_with_pos[rep] for rep in set(rep_map.values())}

    # Rebuild adjacency on representatives (merge parallel edges, drop self-loops)
    merged_adjacency = {rep: set() for rep in merged_selected}
    for src, dsts in adjacency.items():
        if src not in rep_map:
            continue
        rsrc = rep_map[src]
        for dst in dsts:
            if dst not in rep_map:
                continue
            rdst = rep_map[dst]
            if rsrc == rdst:
                continue
            merged_adjacency[rsrc].add(rdst)
            merged_adjacency.setdefault(rdst, set()).add(rsrc)

    return merged_selected, merged_adjacency

def graph(asn, distance_km=None, include_countries=None, include_continents=None, exclude_countries=None,
          mainland_only=False):
    """
    Build an ASN-specific undirected graph from CAIDA data.

    Nodes are assigned positions as (lon, lat) tuples and optional city names.
    Optionally, nodes at the same or nearby coordinates can be merged to reduce
    clutter, and nodes can be filtered by geographic regions.

    Parameters
    ----------
    asn : int | str
        Target ASN to extract.
    distance_km : float | None, default None
        Merge nodes within this geographic distance after exact-position grouping.
    include_countries : list[str] | None
        Country names to include.
    include_continents : list[str] | None
        Continent names to include (supports 'EU' expansion in geo module).
    exclude_countries : list[str] | None
        Country names to exclude.
    mainland_only : bool, default False
        If True, reduce countries to their mainland polygons during filtering.

    Returns
    -------
    tuple[dict[int, dict], list[dict]]
        (nodes, edges) for building a NetworkX node-link graph. Each node has
        'pos': (lon, lat) and optional 'name' attributes. Each edge has 'source', 'target',
        and 'dist' (km).
    """
    asn = int(asn)
    print("ASN requested:", asn)

    if ASN_TO_NODES is None:
        asn_to_nodes = parse_nodes_as(NODES_AS_FILE, asn)
    else:
        asn_to_nodes = ASN_TO_NODES

    # Filter to ASN nodes
    selected = asn_to_nodes[asn]
    print("Nodes in ASN:", len(selected))

    # Filter nodes geographically

    if NODE_TO_GEO is None:
        node_to_geo = parse_nodes_geo(NODES_GEO_FILE, selected)
    else:
        node_to_geo = NODE_TO_GEO

    # Filter to nodes with geo data and materialize float lon/lat for later use
    selected_with_pos = {}
    for n in selected:
        if n in node_to_geo:
            *_, city, lat, lon = node_to_geo[n]
            selected_with_pos[n] = (float(lon), float(lat), city)
    print("Nodes selected (with lon/lat):", len(selected_with_pos))
    print("Nodes dropped (no lon/lat):", len(selected) - len(selected_with_pos))

    # Optional geographic filter by countries/continents
    if include_countries or include_continents:
        previous_len = len(selected_with_pos)
        selected_with_pos = topohub.geo.filter_nodes_by_geo(selected_with_pos, include_countries, include_continents,
                                                            exclude_countries, mainland_only)
        print("Nodes selected (geography filter):", len(selected_with_pos))
        print("Nodes dropped (geography filter):", previous_len - len(selected_with_pos))

    if ADJACENCY is None:
        adjacency = parse_links(LINKS_FILE, selected_with_pos.keys())
    else:
        adjacency = {}
        for src, dsts in ADJACENCY.items():
            if src in selected_with_pos:
                adjacency[src] = {dst for dst in dsts if dst in selected_with_pos}

    print("Adjacency entries (undirected):", sum(len(v) for v in adjacency.values()))

    # Drop nodes with no links
    previous_len = len(selected_with_pos)
    selected_with_pos = {n: pos for n, pos in selected_with_pos.items() if n in adjacency}
    print("Nodes selected (with links):", len(selected_with_pos))
    print("Nodes dropped (no links):", previous_len - len(selected_with_pos))

    # Merge nodes with same or close position
    previous_len = len(selected_with_pos)
    selected_with_pos, adjacency = merge_nodes_by_pos(selected_with_pos, adjacency, distance_km=distance_km)
    print("Nodes selected (after geo merge):", len(selected_with_pos))
    print("Nodes dropped (merged geo):", previous_len - len(selected_with_pos))
    print("Adjacency entries (undirected) after geo merge:", sum(len(v) for v in adjacency.values()))

    edge_pairs = []
    for src, dsts in adjacency.items():
        assert src in selected_with_pos
        for dst in dsts:
            assert dst in selected_with_pos
            if src < dst:
                edge_pairs.append((src, dst))

    print("Edge pairs (undirected):", len(edge_pairs))

    nodes = {}
    edges = []
    for n in selected_with_pos:
        lon, lat, city = selected_with_pos[n]
        nodes[n] = {'id': n, 'pos': (lon, lat)}
        if city:
            nodes[n]['name'] = city

    for u, v in edge_pairs:
        lon0, lat0, _ = selected_with_pos[u]
        lon1, lat1, _ = selected_with_pos[v]
        edges.append({'source': u, 'target': v, 'dist': topohub.graph.haversine((lon0, lat0), (lon1, lat1))})

    return nodes, edges


class CaidaGenerator(topohub.generate.TopoGenerator):
    """
    Generator of CAIDA topologies.

    https://publicdata.caida.org/datasets/topology/ark/
    """

    @classmethod
    def generate_topo(cls, name, distance_km=None, include_countries=None, include_continents=None,
                      exclude_countries=None, mainland_only=False, **kwargs) -> dict:
        """
        Generate a CAIDA ASN topology in NetworkX node-link format.

        Parameters
        ----------
        name : str
            ASN identifier (as string or number).
        distance_km : float | None, default None
            Merge nodes within this distance (kilometers) after grouping by identical coordinates.
        include_countries : list[str] | None
            Country names to include.
        include_continents : list[str] | None
            Continent names to include (supports 'EU' expansion).
        exclude_countries : list[str] | None
            Country names to exclude.
        mainland_only : bool, default False
            If True, reduce countries to their mainland polygons during filtering.
        **kwargs : dict
            Additional options reserved for future use (currently unused).

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        _ = kwargs

        nodes, edges = graph(name, distance_km, include_countries, include_continents, exclude_countries, mainland_only)

        g = nx.node_link_graph({'directed': False, 'multigraph': False, 'graph': {'name': str(name), 'demands': {}},
                                'nodes': list(nodes.values()), 'edges': edges}, edges='edges')
        # g = topohub.backbone.remove_dead_ends(g)
        g = g.subgraph(max(nx.connected_components(g), key=len))

        return nx.node_link_data(g, edges='edges')
