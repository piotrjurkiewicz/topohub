import collections
import itertools
import math
import statistics
import time

def haversine(src, dst):
    """
    Calculate the great-circle distance between two points on a sphere given their longitudes and latitudes.

    Parameters
    ----------
    src : (float, float)
        coordinates (lon0, lat0)
    dst : (float, float)
        coordinates (lon1, lat1)

    Returns
    -------
    float
        distance in kilometers
    """

    (lon0, lat0) = src
    (lon1, lat1) = dst
    R = 6372.8
    d_lat = math.radians(lat1 - lat0)
    d_lon = math.radians(lon1 - lon0)
    lat0 = math.radians(lat0)
    lat1 = math.radians(lat1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat0) * math.cos(lat1) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))

def gini(list_of_values):
    """
    Calculate the Gini coefficient of a given list of values.

    Parameters
    ----------
    list_of_values : list[float]
        given list of values

    Returns
    -------
    float
        calculated Gini coefficient
    """

    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2
    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area

def all_shortest_paths_all_targets(g, source, weight=None, limit=None):
    """
    Find all shortest paths from a source node to all other nodes.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    source : object
        source node
    weight : str | function, default None
        name of edge attribute or a function returning edge weight
    limit : int, default None
        limit the number of shortest paths to find

    Returns
    -------
    dict[object, list], dict[object, int]
        paths and distances from the source node to all other nodes
    """

    import networkx as nx

    paths = {}

    if weight is not None:
        pred, dist = nx.dijkstra_predecessor_and_distance(g, source,
                                                          weight=weight)
    else:
        pred = nx.predecessor(g, source)
        dist = None

    if source not in g:
        raise nx.NodeNotFound('Source {} is not in G'.format(source))

    for target in g:

        if target not in pred:
            raise nx.NetworkXNoPath()

        paths_to_target = []

        stack = [[target, 0]]
        top = 0
        while top >= 0:
            node, i = stack[top]
            if node == source:
                paths_to_target.append([p for p, n in reversed(stack[:top + 1])])
                if limit and len(paths_to_target) == limit:
                    break
            if len(pred[node]) > i:
                top += 1
                if top == len(stack):
                    stack.append([pred[node][i], 0])
                else:
                    stack[top] = [pred[node][i], 0]
            else:
                stack[top - 1][1] += 1
                top -= 1

        paths[target] = paths_to_target

    return paths, dist

def all_shortest_nhops_all_targets(g, source, weight=None, limit=None):
    """
    Find all next hops from a source node to all other nodes.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    source : object
        source node
    weight : str | function, default None
        name of edge attribute or a function returning edge weight
    limit : int, default None
        limit the number of shortest paths to find

    Returns
    -------
    dict[object, set], dict[object, int]
        next hops and distances from the source node to all other nodes
    """

    import networkx as nx

    nhops = {}

    if weight is not None:
        pred, dist = nx.dijkstra_predecessor_and_distance(g, source,
                                                          weight=weight)
    else:
        pred = nx.predecessor(g, source)
        dist = None

    if source not in g:
        raise nx.NodeNotFound('Source {} is not in G'.format(source))

    for target in g:

        if target not in pred:
            raise nx.NetworkXNoPath()

        nhops_to_target = set()

        stack = [[target, 0]]
        top = 0
        while top >= 0:
            node, i = stack[top]
            if node == source:
                nhops_to_target.add(stack[top - 1][0])
                if limit and len(nhops_to_target) == limit:
                    break
            if len(pred[node]) > i:
                top += 1
                if top == len(stack):
                    stack.append([pred[node][i], 0])
                else:
                    stack[top] = [pred[node][i], 0]
            else:
                stack[top - 1][1] += 1
                top -= 1

        nhops[target] = nhops_to_target

    return nhops, dist

def all_disjoint_paths(g, ff, node_filter=None):
    """
    Find all disjoint paths between all node pairs in a graph.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    ff : function
        function for computing the maximum flow among a pair of nodes

    Returns
    -------
    dict[(object, object), list]
        dictionary of lists of disjoint paths between (src, dst) node pairs
    """

    import networkx as nx
    h = nx.algorithms.connectivity.build_auxiliary_edge_connectivity(g)
    r = nx.algorithms.flow.build_residual_network(h, 'capacity')
    result = {}
    for src, dst in itertools.permutations(g, 2):
        if node_filter is None or node_filter(g.nodes[src]) and node_filter(g.nodes[dst]):
            result[src, dst] = list(nx.edge_disjoint_paths(g, src, dst, auxiliary=h, residual=r, flow_func=ff))
    return result

def all_disjoint_paths_scipy(g, ff):
    """
    Find all disjoint paths between all node pairs in a graph using scipy.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    ff : function
        function for computing the maximum flow among a pair of nodes

    Returns
    -------
    dict[(object, object), list]
        dictionary of lists of disjoint paths between (src, dst) node pairs
    """

    import networkx as nx
    import scipy.sparse
    mat = nx.convert_matrix.to_scipy_sparse_matrix(g)
    result = {}
    i_to_node = {}
    node_to_i = {}
    for n, node in enumerate(g):
        i_to_node[n] = node
        node_to_i[node] = n
    for s, t in itertools.permutations(g, 2):
        r = scipy.sparse.csgraph.maximum_flow(mat, node_to_i[s], node_to_i[t])
        R = nx.convert_matrix.from_scipy_sparse_matrix(r.residual, edge_attribute='flow', create_using=nx.DiGraph)
        # print(json.dumps(nx.node_link_data(R), indent=4, default=str))
        # Saturated edges in the residual network form the edge disjoint paths
        # between source and target
        cutset = [(i_to_node[int(u)], i_to_node[int(v)]) for u, v, d in R.edges(data=True)
                  if d['flow'] == 1]
        # This is equivalent of what flow.utils.build_flow_dict returns, but
        # only for the nodes with saturated edges and without reporting 0 flows.
        flow_dict = {n: {} for edge in cutset for n in edge}
        for u, v in cutset:
            flow_dict[u][v] = 1
        paths = []
        # Rebuild the edge disjoint paths from the flow dictionary.
        paths_found = 0
        for v in list(flow_dict[s]):
            path = [s]
            if v == t:
                path.append(v)
                paths.append(path)
                continue
            u = v
            while u != t:
                path.append(u)
                try:
                    u, _ = flow_dict[u].popitem()
                except KeyError:
                    break
            else:
                path.append(t)
                paths.append(path)
                paths_found += 1

        result[s, t] = paths

    return result

def shortest_disjoint_paths_slow(g):
    """
    Find all shortest disjoint paths between all node pairs in a graph.

    Parameters
    ----------
    g : networkx.Graph
        network graph

    Returns
    -------
    dict[(object, object), list]
        dictionary of lists of disjoint paths between (src, dst) node pairs
    """

    import networkx as nx
    result = {}
    for src, dst in itertools.permutations(g, 2):
        longest_paths = []
        for pp in itertools.permutations(nx.all_shortest_paths(g, src, dst, weight='cost')):
            paths = []
            used_edges = set()
            for path in pp:
                this_used_edges = set()
                for f, t in zip(path, path[1:]):
                    edge = (f, t)
                    if edge in used_edges:
                        break
                    else:
                        this_used_edges.add(edge)
                else:
                    paths.append(path)
                    used_edges |= this_used_edges
            if len(paths) > len(longest_paths):
                longest_paths = paths
        result[src, dst] = longest_paths
    return result

def shortest_disjoint_paths(g, ff, node_filter=None):
    """
    Find all shortest disjoint paths between all node pairs in a graph.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    ff : function
        function for computing the maximum flow among a pair of nodes

    Returns
    -------
    dict[(object, object), list]
        dictionary of lists of disjoint paths between (src, dst) node pairs
    """

    import networkx as nx
    nhops = {}
    for n in g:
        nhops[n] = all_shortest_nhops_all_targets(g, n)[0]

    def dfs(src, dst, sg, ae):
        for nhop in nhops[src][dst]:
            edge = src, nhop
            if edge not in ae:
                sg.add_edge(src, nhop)
                ae.add(edge)
            if nhop != dst:
                dfs(nhop, dst, sg, ae)

    result = {}
    for src in g:
        for dst in g:
            if src != dst:
                if node_filter is None or node_filter(g.nodes[src]) and node_filter(g.nodes[dst]):
                    subgraph = nx.Graph()
                    added_edges = set()
                    dfs(src, dst, subgraph, added_edges)
                    result[src, dst] = list(nx.edge_disjoint_paths(subgraph, src, dst, flow_func=ff))
    return result

def save_topo_graph_pdf(g, filename=None, plot_aspect=1.0):
    """
    Generate and save topology graph as PDF file using matplotlib.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    filename : str, default None
        filename
    plot_aspect : float, default 1.0
        plot aspect ratio
    """

    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    g = nx.relabel_nodes(g, lambda n: str(n))

    matplotlib.rcParams['pdf.use14corefonts'] = True
    matplotlib.rcParams['font.family'] = 'sans'

    pos = {}

    for node in g.nodes(data=True):
        pos[node[0]] = node[1]['pos']

    min0 = min(v[0] for v in pos.values())
    max0 = max(v[0] for v in pos.values())
    min1 = min(v[1] for v in pos.values())
    max1 = max(v[1] for v in pos.values())

    aspect = plot_aspect * (max0 - min0) / (max1 - min1)

    plt.figure(figsize=(2 * 3.4, 2 * 3.4 / aspect))
    nx.draw(g, pos=pos, node_size=100, alpha=0.25, node_color='k', edgelist=[])
    nx.draw_networkx_edges(g, pos=pos, node_size=100, alpha=0.25)
    nx.draw_networkx_labels(g, pos=pos)
    if not filename:
        filename = 'mininet/topo_lib/' + g.graph['name']
    plt.savefig(filename + '.pdf', metadata={'Creator': None, 'Producer': None, 'CreationDate': None})
    plt.close('all')

def minmax(pos):
    """
    Find min and max in node positions dictionary.

    Parameters
    ----------
    pos : dict
        node positions dictionary

    Returns
    -------
    (float, float, float, float)
        max_x, max_y, min_x, min_y
    """

    min0 = min(v[0] for v in pos.values())
    max0 = max(v[0] for v in pos.values())
    min1 = min(v[1] for v in pos.values())
    max1 = max(v[1] for v in pos.values())
    return max0, max1, min0, min1

def save_topo_graph_svg(g, filename=None, scale=None, background=None):
    """
    Generate and save topology graph as SVG file.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    filename : str, default None
        filename
    scaling : bool, default True
        scale width and height of SVG to topology diameter
    """

    pos = {}
    names = {}
    for node in g.nodes(data=True):
        pos[node[0]] = node[1]['pos'][0], node[1]['pos'][1]
        names[node[0]] = node[1].get('name')

    max0, max1, min0, min1 = minmax(pos)

    if not scale:
        scale_factor = 1
    elif scale is True:
        scale_factor = max(abs(max0 - min0), abs(max1 - min1)) / 250
    else:
        scale_factor = scale

    stroke_width = scale_factor * 1
    circle_radius = scale_factor * 2
    font_size = scale_factor * 3

    with open(filename + '.svg', 'w') as f:
        f.write(f'<svg id="topo" viewBox="{(min0 - 0.05 * abs(max0 - min0)):.2f} {(-max1 - 0.05 * abs(max1 - min1)):.2f} {(1.10 * abs(max0 - min0)):.2f} {(1.10 * abs(max1 - min1)):.2f}" xmlns="http://www.w3.org/2000/svg">\n')
        f.write(f'<style>#topo path {{fill: none; stroke: grey; stroke-width: {stroke_width:.4f}px;}} #topo circle {{fill: lightblue; stroke: none; stroke-width: 0.3px; vector-effect: non-scaling-stroke; r: {circle_radius:.4f}px;}} #topo text {{fill: black; stroke: none; font-size: {font_size:.4f}px; font-family: sans-serif; text-anchor:middle; transform: translateY(0.3em);}} #topo path.country {{fill: lightgrey; stroke: black; stroke-width: 1px; vector-effect: non-scaling-stroke; visibility: visible;}} #topo path.selection {{fill: none; stroke: red; stroke-width: 1px; vector-effect: non-scaling-stroke; visibility: visible;}} #topo path.utilization {{visibility: hidden;}}</style>\n')

        if background:
            for item in background:
                f.write(item)

        for e in g.edges:
            x0, y0 = pos[e[0]]
            x1, y1 = pos[e[1]]
            f.write(f'<path data-id="{e[0]}-{e[1]}" d="M{x0:.2f},{-y0:.2f},{x1:.2f},{-y1:.2f}"/>\n')

        for n, (x, y) in pos.items():
            f.write(f'<circle data-id="{n}" cx="{x:.2f}" cy="{-y:.2f}" r="{circle_radius:.2f}px"/>\n')
            f.write(f'<text data-id="{n}" x="{x:.2f}" y="{-y:.2f}">{names[n] or n}</text>\n')

        f.write('</svg>\n')

def path_stats(g, node_filter=None):
    """
    Calculate statistics for paths between all node pairs.

    Parameters
    ----------
    g : networkx.Graph
        network graph

    Returns
    -------
    dict[(object, object), (int, int, float, int, float, float, float, object, object)]
        dictionary of paths statistics between (src, dst) node pairs in a format (adp_number, sdp_number, avg_adp_hops, avg_sdp_hops, avg_adp_length, avg_sdp_length, demand, src, dst)
    """

    import networkx as nx
    for ff in [
        nx.algorithms.flow.edmonds_karp,
        # nx.algorithms.flow.shortest_augmenting_path,
        # nx.algorithms.flow.preflow_push,
        # nx.algorithms.flow.dinitz,
        # nx.algorithms.flow.boykov_kolmogorov
    ]:
        ts = time.time()
        ap = all_disjoint_paths(g, ff, node_filter=node_filter)
        sp = shortest_disjoint_paths(g, ff, node_filter=node_filter)
        print(time.time() - ts)
    # sp_slow = shortest_disjoint_paths_slow(g)
    stats = {}
    for src, dst in ap:
        # assert len(sp[src, dst]) == len(sp_slow[src, dst])
        avg_ap_hops = sum(len(path) - 1 for path in ap[src, dst]) / float(len(ap[src, dst]))
        avg_sp_hops = sum(len(path) - 1 for path in sp[src, dst]) // len(sp[src, dst])
        avg_ap_length = 0
        for path in ap[src, dst]:
            for u, v in zip(path, path[1:]):
                avg_ap_length += g.edges[u, v]['dist']
        avg_ap_length /= float(len(ap[src, dst]))
        avg_sp_length = 0
        for path in sp[src, dst]:
            for u, v in zip(path, path[1:]):
                avg_sp_length += g.edges[u, v]['dist']
        avg_sp_length /= float(len(ap[src, dst]))
        if 'demands' in g.graph:
            try:
                demand = g.graph['demands'][src][dst]
            except KeyError:
                try:
                    demand = g.graph['demands'][dst][src]
                except KeyError:
                    demand = 0
        else:
            demand = 1
        stats[src, dst] = (len(ap[src, dst]), len(sp[src, dst]),
                           avg_ap_hops, avg_sp_hops,
                           avg_ap_length, avg_sp_length,
                           demand,
                           str(src), str(dst))
    for src, dst in stats:
        assert stats[src, dst][0:2] == stats[dst, src][0:2]
        # TODO: avg_ap_hops and avg_sp_hops are not symmetric (due to edmonds_karp not taking salts into account?)
    return stats

def path_stats_print(stats, filename=None):
    """
    Print statistics for paths between all node pairs in the CSV format.

    Parameters
    ----------
    stats : dict
        dictionary of paths statistics between (src, dst) node pairs
    filename : str, default None
        filename
    """

    table = sorted(stats.values(), reverse=True, key=lambda r: (r[0:2], sorted(r[-2:]), r[-1]))
    text = 'adp_number,sdp_number,avg_adp_hops,avg_sdp_hops,avg_adp_length,avg_sdp_length,demand,src,dst\n'
    text += '\n'.join(','.join(f'{v:.2f}' if isinstance(v, float) else str(v) for v in row) for row in table)
    if not filename:
        print(text)
    else:
        open(filename + '.csv', 'w').write(text)

def calculate_utilization(g, node_filter=None):
    """
    Calculate link utilizations for ECMP shortest path routing and save them as edges properties.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    """

    nhops = {}
    for n in g:
        nhops[n] = all_shortest_nhops_all_targets(g, n)[0]

    modes = {
        'org': (((src, dst, g.graph['demands'][src][dst]) for src in g.graph['demands'] for dst in g.graph['demands'][src]) if 'demands' in g.graph else None),
        'uni': ((src, dst, 1) for src, dst in itertools.combinations(g, 2) if node_filter is None or node_filter(g.nodes[src]) and node_filter(g.nodes[dst])),
        'deg': ((src, dst, g.degree[src] * g.degree[dst]) for src, dst in itertools.combinations(g, 2) if node_filter is None or node_filter(g.nodes[src]) and node_filter(g.nodes[dst]))
    }

    def dfs(src, dst, dem, ut):
        dem /= len(nhops[src][dst])
        for nhop in nhops[src][dst]:
            ut[src, nhop] += dem
            if nhop != dst:
                dfs(nhop, dst, dem, ut)

    for mode, gen in modes.items():
        if gen:
            util = collections.defaultdict(float)
            for src, dst, dem in gen:
                dfs(src, dst, dem, util)
                dfs(dst, src, dem, util)
            if util:
                max_util = max(util.values())
                for src, dst in g.edges:
                    g.edges[src, dst].setdefault('ecmp_fwd', {})[mode] = util.get((src, dst), 0.0) / max_util * 100
                    g.edges[src, dst].setdefault('ecmp_bwd', {})[mode] = util.get((dst, src), 0.0) / max_util * 100

def topo_stats(g, ps=None):
    """
    Calculate topology properties statistics.

    Parameters
    ----------
    g : networkx.Graph
        network graph
    ps : dict, default None
        dictionary of paths statistics between (src, dst) node pairs

    Returns
    -------
    dict[str, int | float]
        dictionary topology properties
    """

    import networkx as nx

    min_link_length = min(e['dist'] for u, v, e in g.edges(data=True))
    avg_link_length = sum(e['dist'] for u, v, e in g.edges(data=True)) / float(len(g.edges))
    max_link_length = max(e['dist'] for u, v, e in g.edges(data=True))

    if isinstance(g, nx.MultiDiGraph):
        number_links = g.size() / 2
        degree = g.out_degree
    else:
        number_links = g.size()
        degree = g.degree
    degrees = [d for (_, d) in degree()]

    stats = {
        'nodes': len(g),
        'links': number_links,
        'demands': 0,
        'min_degree': min(degrees),
        'avg_degree': sum(degrees) / float(len(g)),
        'std_degree': statistics.pstdev(degrees),
        'max_degree': max(degrees),
        'gini': gini(degrees),
        'min_link_len': min_link_length,
        'avg_link_len': avg_link_length,
        'max_link_len': max_link_length,
        'diameter_len': nx.diameter(g, weight='dist'),
        'diameter_hops': nx.diameter(g)
    }

    if ps is None:
        dem_num = 0
        if 'demands' in g.graph:
            dem_num = sum(len(demands) for demands in g.graph['demands'].values())
        if dem_num == 0:
            dem_num = len(g) ** 2 - len(g)
    else:
        adp_sum, sdp_sum = 0, 0
        avg_adp_hops_sum, avg_sdp_hops_sum = 0.0, 0.0
        avg_adp_length_sum, avg_sdp_length_sum = 0.0, 0.0
        dem_num = 0
        dem_sum = 0.0
        max_adp_num = 0
        max_sdp_num = 0

        for pair, (adp_number, sdp_number, avg_adp_hops, avg_sdp_hops, avg_adp_length, avg_sdp_length, demand, src, dst) in ps.items():
            max_adp_num = max(max_adp_num, adp_number)
            max_sdp_num = max(max_sdp_num, sdp_number)
            dem_sum += demand

        for pair, (adp_number, sdp_number, avg_adp_hops, avg_sdp_hops, avg_adp_length, avg_sdp_length, demand, src, dst) in ps.items():
            if demand > 0 or dem_sum == 0:
                if dem_sum == 0:
                    demand = 1
                adp_sum += adp_number * demand
                sdp_sum += sdp_number * demand
                avg_adp_hops_sum += avg_adp_hops * demand
                avg_sdp_hops_sum += avg_sdp_hops * demand
                avg_adp_length_sum += avg_adp_length * demand
                avg_sdp_length_sum += avg_sdp_length * demand
                dem_num += 1

        if dem_sum == 0:
            dem_sum = dem_num

        stats['avg_sdp_num'] = sdp_sum / float(dem_sum)
        stats['max_sdp_num'] = max_sdp_num
        stats['avg_sdp_hops'] = avg_sdp_hops_sum / float(dem_sum)
        stats['avg_sdp_len'] = avg_sdp_length_sum / float(dem_sum)
        stats['avg_adp_num'] = adp_sum / float(dem_sum)
        stats['max_adp_num'] = max_adp_num
        stats['avg_adp_hops'] = avg_adp_hops_sum / float(dem_sum)
        stats['avg_adp_len'] = avg_adp_length_sum / float(dem_sum)

    stats['demands'] = dem_num
    return stats

def topo_stats_print(stats, name, filename=None):
    """
    Print topology statistics in a LaTeX format.

    Parameters
    ----------
    stats : dict
        dictionary topology properties
    name : str
        topology name
    filename : str, default None
        filename
    """

    just = 38
    text = \
        'Topology name'.ljust(just) + ' & %s' % name.replace('_', '\\_') + '\n\n' + \
        'Number of nodes'.ljust(just) + ' & %s' % stats['nodes'] + '\n' + \
        'Number of links'.ljust(just) + ' & %s' % stats['links'] + '\n' + \
        'Number of demands'.ljust(just) + ' & %s' % stats['demands'] + '\n' + \
        'Min. vertex degree'.ljust(just) + ' & %.2f' % stats['min_degree'] + '\n' + \
        'Avg. vertex degree'.ljust(just) + ' & %.2f' % stats['avg_degree'] + '\n' + \
        'Max. vertex degree'.ljust(just) + ' & %.2f' % stats['max_degree'] + '\n' + \
        'Min. link length'.ljust(just) + ' & %.2f' % stats['min_link_len'] + '\n' + \
        'Avg. link length'.ljust(just) + ' & %.2f' % stats['avg_link_len'] + '\n' + \
        'Max. link length'.ljust(just) + ' & %.2f' % stats['max_link_len'] + '\n'

    if 'avg_sdp_num' in stats:
        text += \
            'Avg. number of disjoint shortest paths'.ljust(just) + ' & %.2f' % stats['avg_sdp_num'] + '\n' + \
            'Max. number of disjoint shortest paths'.ljust(just) + ' & %.2f' % stats['max_sdp_num'] + '\n' + \
            'Avg. hops of disjoint shortest paths'.ljust(just) + ' & %.2f' % stats['avg_sdp_hops'] + '\n' + \
            'Avg. length of disjoint shortest paths'.ljust(just) + ' & %.2f' % stats['avg_sdp_len'] + '\n' + \
            'Avg. number of all disjoint paths'.ljust(just) + ' & %.2f' % stats['avg_adp_num'] + '\n' + \
            'Max. number of all disjoint paths'.ljust(just) + ' & %.2f' % stats['max_adp_num'] + '\n' + \
            'Avg. hops of all disjoint paths'.ljust(just) + ' & %.2f' % stats['avg_adp_hops'] + '\n' + \
            'Avg. length of all disjoint paths'.ljust(just) + ' & %.2f' % stats['avg_adp_len'] + '\n'

    if not filename:
        print(text)
    else:
        open(filename + '.tex', 'w').write(text)

def write_gml(g, path):
    """
    Writes a NetworkX graph to a GML format file.

    Parameters
    ----------
    g : networkx.Graph
        the input NetworkX graph
    path : str, default None
        the file path to write the GML file to

    """
    with open(path, 'w') as f:
        f.write('graph [\n')

        # Write graph attributes
        f.write(f'  name "{g.graph.get("name", "G")}"\n')
        f.write(f'  directed {int(g.is_directed())}\n')

        # Write stats
        stats = g.graph.get('stats')
        if stats:
            f.write('  stats [\n')
            for key, value in stats.items():
                f.write(f'    {key} {round(value, 2) if isinstance(value, float) else value}\n')
            f.write('  ]\n')

        # Write nodes
        for node, attr in g.nodes(data=True):
            f.write('  node [\n')
            f.write(f'    id {node}\n')
            f.write(f'    label "{attr["name"] if "name" in attr else node}"\n')
            if 'type' in attr:
                f.write(f'    type "{attr["type"]}"\n')
            if 'pos' in attr:
                f.write(f'    lon {round(attr["pos"][0], 2)}\n')
                f.write(f'    lat {round(attr["pos"][1], 2)}\n')
            f.write('  ]\n')

        # Write edges
        for source, target, attr in g.edges(data=True):
            f.write('  edge [\n')
            f.write(f'    source {source}\n')
            f.write(f'    target {target}\n')
            if 'type' in attr:
                f.write(f'    type "{attr["type"]}"\n')
            if 'dist' in attr:
                f.write(f'    dist {round(attr["dist"], 2)}\n')
            f.write('  ]\n')

        f.write(']')
