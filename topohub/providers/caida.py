#!/usr/bin/python3
import subprocess

import networkx as nx

import topohub.generate

NODES_AS_FILE  = "external/caida/2024-08/midar-iff.nodes.as"
NODES_GEO_FILE = "external/caida/2024-08/midar-iff.nodes.geo"
LINKS_FILE     = "external/caida/2024-08/midar-iff.links"

ASN_TO_NODES = None
NODE_TO_GEO = None
ADJACENCY = None

def parse_nodes_as(path, asn=None, grep=True):
    if asn and grep:
        output = subprocess.run(["grep", f"\t{asn}\t", path], stdout=subprocess.PIPE)
        f = output.stdout.decode("utf-8").splitlines()
    else:
        f = open(path, "r", encoding="utf-8", errors="replace")
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
            asn_to_nodes[parsed_asn] = []
        asn_to_nodes[parsed_asn].append(node)
    if not isinstance(f, list):
        f.close()
    return asn_to_nodes


def parse_nodes_geo(path, nodes=None, grep=True):
    if nodes and grep:
        regexp = "\n".join(f"N{node}:" for node in nodes).encode("utf-8")
        output = subprocess.run(["grep", "-Ff", "-", path], input=regexp, stdout=subprocess.PIPE)
        f = output.stdout.decode("utf-8").splitlines()
    else:
        f = open(path, "r", encoding="utf-8", errors="replace")
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
    if nodes and grep:
        regexp = "\n".join(f"N{node}" for node in nodes).encode("utf-8")
        output = subprocess.run(["grep", "-Ff", "-", path], input=regexp, stdout=subprocess.PIPE)
        f = output.stdout.decode("utf-8").splitlines()
    else:
        f = open(path, "r", encoding="utf-8", errors="replace")
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
        if src not in adj:
            adj[src] = set()
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
            adj[src].add(dst)
            if dst not in adj:
                adj[dst] = set()
            adj[dst].add(src)
    if not isinstance(f, list):
        f.close()
    return adj


def graph(asn):
    asn = int(asn)
    if ASN_TO_NODES is None:
        asn_to_nodes = parse_nodes_as(NODES_AS_FILE, asn)
    else:
        asn_to_nodes = ASN_TO_NODES

    selected = set(asn_to_nodes[asn])

    if NODE_TO_GEO is None:
        node_to_geo = parse_nodes_geo(NODES_GEO_FILE, selected)
    else:
        node_to_geo = NODE_TO_GEO

    selected_with_geo = {n for n in selected if n in node_to_geo}
    dropped_for_no_geo = selected - selected_with_geo

    print("=== Summary (pre-graph) ===")
    print("ASN requested:", asn)
    print("Nodes in ASN (raw):", len(selected))
    print("Selected nodes with geo:", len(selected_with_geo))
    print("Dropped (no geo):", len(dropped_for_no_geo))

    if ADJACENCY is None:
        adjacency = parse_links(LINKS_FILE, selected_with_geo)
    else:
        adjacency = ADJACENCY

    edge_pairs = []
    for src in selected_with_geo:
        if src in adjacency:
            for dst in adjacency[src]:
                if dst in selected_with_geo and src < dst:
                    edge_pairs.append((src, dst))

    print("Edges touching selected nodes:", len(edge_pairs))

    nodes = {}
    edges = []
    for n in selected_with_geo:
        *_, name, lat, lon = node_to_geo[n]
        nodes[n] = {'id': n, 'pos': (float(lon), float(lat))}
        if name:
            nodes[n]['name'] = name

    # add neighbors and edges
    for u, v in edge_pairs:
        edges.append({'source': u, 'target': v, 'dist': 10})

    return nodes, edges


class CaidaGenerator(topohub.generate.TopoGenerator):
    """
    Generator of CAIDA topologies.

    https://publicdata.caida.org/datasets/topology/ark/
    """

    @classmethod
    def generate_topo(cls, name):
        """
        Generate CAIDA topology.

        Parameters
        ----------
        name : str
            name

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        nodes, edges = graph(name)

        g = nx.node_link_graph({'directed': False, 'multigraph': False, 'graph': {'name': str(name), 'demands': {}}, 'nodes': list(nodes.values()), 'edges': edges}, edges='edges')
        # g = topohub.backbone.remove_dead_ends(g)
        # g = g.subgraph(max(nx.connected_components(g), key=len))

        return nx.node_link_data(g, edges='edges')
