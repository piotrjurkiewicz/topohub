import collections
import itertools
import math
import statistics
import time

def haversine(src, dst):
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
    sorted_list = sorted(list_of_values)
    height, area = 0, 0
    for value in sorted_list:
        height += value
        area += height - value / 2
    fair_area = height * len(list_of_values) / 2
    return (fair_area - area) / fair_area

def all_shortest_paths_all_targets(g, source, weight=None, limit=None):
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

def all_disjoint_paths(g, ff):
    import networkx as nx
    h = nx.algorithms.connectivity.build_auxiliary_edge_connectivity(g)
    r = nx.algorithms.flow.build_residual_network(h, 'capacity')
    result = {}
    for src, dst in itertools.permutations(g, 2):
        result[src, dst] = list(nx.edge_disjoint_paths(g, src, dst, auxiliary=h, residual=r, flow_func=ff))
    return result

def all_disjoint_paths_scipy(g, ff):
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

def shortest_disjoint_paths(g, ff):
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
                subgraph = nx.Graph()
                added_edges = set()
                dfs(src, dst, subgraph, added_edges)
                result[src, dst] = list(nx.edge_disjoint_paths(subgraph, src, dst, flow_func=ff))
    return result

def save_topo_graph_pdf(g, filename=None, plot_aspect=1.0):
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
    min0 = min(v[0] for v in pos.values())
    max0 = max(v[0] for v in pos.values())
    min1 = min(v[1] for v in pos.values())
    max1 = max(v[1] for v in pos.values())
    return max0, max1, min0, min1

def save_topo_graph_svg(g, filename=None, scaling=True):
    pos = {}
    for node in g.nodes(data=True):
        pos[node[0]] = node[1]['pos'][0], node[1]['pos'][1]

    max0, max1, min0, min1 = minmax(pos)

    if scaling:
        scale = 1000 / max(max0 - min0, max1 - min1)
        for n in pos:
            pos[n] = pos[n][0] * scale, (max1 - pos[n][1]) * scale
        max0, max1, min0, min1 = minmax(pos)

    with open(filename + '.svg', 'w') as f:
        f.write(f'<svg width="{max0 - min0 + 90:.2f}" height="{max1 - min1 + 90:.2f}" viewBox="{min0 - 45:.2f} {min1 - 45:.2f} {max0 - min0 + 90:.2f} {max1 - min1 + 90:.2f}" xmlns="http://www.w3.org/2000/svg">\n')
        f.write('<style>path {fill: none; stroke: grey; stroke-width: 6;} circle {fill: lightblue; stroke: none;} text {fill: black; stroke: none; font-size: 16; font-family: sans-serif; text-anchor:middle;}</style>\n')

        for e in g.edges:
            x0, y0 = pos[e[0]]
            x1, y1 = pos[e[1]]
            f.write(f'<path d="M{x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f}"/>\n')

        for n, (x, y) in pos.items():
            f.write(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="10"/>\n')
            f.write(f'<text x="{x:.2f}" y="{y + 5:.2f}">{n}</text>\n')

        f.write('</svg>\n')

def path_stats(g):
    import networkx as nx
    for ff in [
        nx.algorithms.flow.edmonds_karp,
        # nx.algorithms.flow.shortest_augmenting_path,
        # nx.algorithms.flow.preflow_push,
        # nx.algorithms.flow.dinitz,
        # nx.algorithms.flow.boykov_kolmogorov
    ]:
        ts = time.time()
        ap = all_disjoint_paths(g, ff)
        sp = shortest_disjoint_paths(g, ff)
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
                avg_ap_length += g.edges[u, v]['distance']
        avg_ap_length /= float(len(ap[src, dst]))
        avg_sp_length = 0
        for path in sp[src, dst]:
            for u, v in zip(path, path[1:]):
                avg_sp_length += g.edges[u, v]['distance']
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
    table = sorted(stats.values(), reverse=True, key=lambda r: (r[0:2], sorted(r[-2:]), r[-1]))
    text = 'adp_number,sdp_number,avg_adp_hops,avg_sdp_hops,avg_adp_length,avg_sdp_length,demand,src,dst\n'
    text += '\n'.join(','.join(f'{v:.2f}' if isinstance(v, float) else str(v) for v in row) for row in table)
    if not filename:
        print(text)
    else:
        open(filename + '.csv', 'w').write(text)

def calculate_utilization(g):
    nhops = {}
    for n in g:
        nhops[n] = all_shortest_nhops_all_targets(g, n)[0]

    modes = {
        'demands': (((src, dst, g.graph['demands'][src][dst]) for src in g.graph['demands'] for dst in g.graph['demands'][src]) if 'demands' in g.graph else None),
        'unit': ((src, dst, 1) for src, dst in itertools.combinations(g, 2)),
        'degree': ((src, dst, g.degree[src] * g.degree[dst]) for src, dst in itertools.combinations(g, 2))
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

    return g

def topo_stats(g, ps=None):
    import networkx as nx

    min_edge_length = min(e['distance'] for u, v, e in g.edges(data=True))
    avg_edge_length = sum(e['distance'] for u, v, e in g.edges(data=True)) / float(len(g.edges))
    max_edge_length = max(e['distance'] for u, v, e in g.edges(data=True))

    if isinstance(g, nx.MultiDiGraph):
        number_edges = g.size() / 2
        degree = g.out_degree
    else:
        number_edges = g.size()
        degree = g.degree
    degrees = [d for (_, d) in degree()]

    stats = {
        'nodes': len(g),
        'edges': number_edges,
        'demands': 0,
        'min_degree': min(degrees),
        'avg_degree': sum(degrees) / float(len(g)),
        'std_degree': statistics.pstdev(degrees),
        'max_degree': max(degrees),
        'gini': gini(degrees),
        'min_edge_len': min_edge_length,
        'avg_edge_len': avg_edge_length,
        'max_edge_len': max_edge_length,
        'diameter_len': nx.diameter(g, weight='distance')
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
        diameter_hops = 0
        max_adp_num = 0
        max_sdp_num = 0

        for pair, (adp_number, sdp_number, avg_adp_hops, avg_sdp_hops, avg_adp_length, avg_sdp_length, demand, src, dst) in ps.items():
            diameter_hops = max(diameter_hops, avg_sdp_hops)
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

        stats['diameter_hops'] = diameter_hops
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
    # with importlib.resources.open_text("MyPackage", "data.json") as file:
    #     data = json.load(file)

    JUST = 38
    text = \
        'Topology name'.ljust(JUST) + ' & %s' % name.replace('_', '\\_') + '\n\n' + \
        'Number of nodes'.ljust(JUST) + ' & %s' % stats['nodes'] + '\n' + \
        'Number of edges'.ljust(JUST) + ' & %s' % stats['edges'] + '\n' + \
        'Number of demands'.ljust(JUST) + ' & %s' % stats['demands'] + '\n' + \
        'Min. vertex degree'.ljust(JUST) + ' & %.2f' % stats['min_degree'] + '\n' + \
        'Avg. vertex degree'.ljust(JUST) + ' & %.2f' % stats['avg_degree'] + '\n' + \
        'Max. vertex degree'.ljust(JUST) + ' & %.2f' % stats['max_degree'] + '\n' + \
        'Min. edge length'.ljust(JUST) + ' & %.2f' % stats['min_edge_len'] + '\n' + \
        'Avg. edge length'.ljust(JUST) + ' & %.2f' % stats['avg_edge_len'] + '\n' + \
        'Max. edge length'.ljust(JUST) + ' & %.2f' % stats['max_edge_len'] + '\n'

    if 'avg_sdp_num' in stats:
        text += \
            'Avg. number of disjoint shortest paths'.ljust(JUST) + ' & %.2f' % stats['avg_sdp_num'] + '\n' + \
            'Max. number of disjoint shortest paths'.ljust(JUST) + ' & %.2f' % stats['max_sdp_num'] + '\n' + \
            'Avg. hops of disjoint shortest paths'.ljust(JUST) + ' & %.2f' % stats['avg_sdp_hops'] + '\n' + \
            'Avg. length of disjoint shortest paths'.ljust(JUST) + ' & %.2f' % stats['avg_sdp_len'] + '\n' + \
            'Avg. number of all disjoint paths'.ljust(JUST) + ' & %.2f' % stats['avg_adp_num'] + '\n' + \
            'Max. number of all disjoint paths'.ljust(JUST) + ' & %.2f' % stats['max_adp_num'] + '\n' + \
            'Avg. hops of all disjoint paths'.ljust(JUST) + ' & %.2f' % stats['avg_adp_hops'] + '\n' + \
            'Avg. length of all disjoint paths'.ljust(JUST) + ' & %.2f' % stats['avg_adp_len'] + '\n'

    if not filename:
        print(text)
    else:
        open(filename + '.tex', 'w').write(text)
