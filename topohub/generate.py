#!/usr/bin/python3

import os
import http.client as http
import json
import random
import sys
import time

import networkx as nx

# from . import graph
import graph

json.encoder.c_make_encoder = None
MAX_GABRIEL_NODES = 4096

class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.2f'))

class TopoGenerator:

    @classmethod
    def generate_topo(cls, *args):
        return {}

    @classmethod
    def save_topo(cls, *args, **kwargs):
        g = nx.node_link_graph(cls.generate_topo(*args))
        graph.calculate_utilization(g)
        if 'filename' in kwargs:
            filename = kwargs['filename']
        else:
            filename = f'mininet/topo_lib/{g.name}'
        os.makedirs(filename.rpartition('/')[0], exist_ok=True)
        json.dump(nx.node_link_data(g), open(f'{filename}.json', 'w'), indent=kwargs.get('indent', 0))
        ps = None
        if kwargs.get('with_plot'):
            graph.save_topo_graph_svg(g, filename, plot_aspect=kwargs.get('plot_aspect', 1.0))
        if kwargs.get('with_path_stats'):
            ps = graph.path_stats(g, filename=filename, action='save')
        if kwargs.get('with_topo_stats'):
            graph.topo_stats(g, ps=ps, filename=filename, action='save')
        json.encoder.float = RoundingFloat
        json.dump(nx.node_link_data(g), open(f'{filename}.json', 'w'), indent=kwargs.get('indent', 0), default=lambda x: format(x, '.2f'))
        json.encoder.float = float

class SNDLibGenerator(TopoGenerator):

    @classmethod
    def download_topo(cls, name):

        con = http.HTTPConnection("sndlib.zib.de", timeout=5)
        con.request('GET', "/coredata.download.action?objectName=%s&format=native&objectType=network" % name)
        r = con.getresponse()
        data = r.read()
        return data

    @classmethod
    def generate_topo(cls, name):

        mode = None
        nodes = []
        links = []
        pos = {}
        demands = {}

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
                pos[node] = (float(lon), float(lat))
                nodes.append({'id': node, 'pos': (float(lon), float(lat))})

            if mode == 'links':
                if line.startswith(")"):
                    mode = None
                    continue
                node0, node1 = line.split()[2:4]
                distance = graph.haversine(pos[node0], pos[node1])
                links.append({'source': node0, 'target': node1, 'distance': distance})

            if mode == 'demands':
                if line.startswith(")"):
                    mode = None
                    continue
                node0, node1 = line.split()[2:4]
                value = float(line.split()[6])
                if node0 not in demands:
                    demands[node0] = {}
                demands[node0][node1] = value

        name = ''.join([i if i.isalnum() else '_' for i in name.title()])
        name = name.lower()

        return {'directed': False, 'multigraph': False, 'graph': {'name': name, 'demands': demands}, 'nodes': nodes, 'links': links}

class GabrielGenerator(TopoGenerator):

    @classmethod
    def generate_topo(cls, nnodes, seed):

        assert nnodes <= MAX_GABRIEL_NODES

        nodes = []
        links = []
        pos = {}
        demands = {}

        random.seed(seed)

        scale = (nnodes * 10000) ** 0.5
        exclusion = 25.0  # prevent points from being too close
        print(nnodes, seed, scale, exclusion)

        def dist2(p, q):
            return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

        while len(pos) < nnodes:
            p = (random.random() * scale, random.random() * scale)
            if pos:
                nn = min(dist2(p, q) ** 0.5 for q in pos.values())
                if nn < exclusion:
                    continue
            node = 'R' + str(len(nodes))
            pos[node] = p
            nodes.append({'id': node, 'pos': p})

        def neighbors(p, q):
            c = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            dd = dist2(p, c)
            for r in pos.values():
                if r != p and r != q and dist2(r, c) < dd:
                    return False
            return True

        for p, (p_name, p_pos) in enumerate(pos.items()):
            for q, (q_name, q_pos) in enumerate(pos.items()):
                if p < q and neighbors(p_pos, q_pos):
                    distance = dist2(p_pos, q_pos) ** 0.5
                    links.append({'source': p_name, 'target': q_name, 'distance': distance})

        # nps = []
        # nss = []
        # nns = []
        # for pn, (p_name, p) in enumerate(pos.items()):
        #     for qn, (q_name, q) in enumerate(pos.items()):
        #         if p < q:
        #             nps.append(tuple(sorted((p_name, q_name))))
        #         if p_name < q_name:
        #             nss.append(tuple(sorted((p_name, q_name))))
        #         if pn < qn:
        #             nns.append(tuple(sorted((p_name, q_name))))
        #
        # assert(set(nps) == set(nss) == set(nns))

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'links': links}


class NumpyGabrielGenerator(TopoGenerator):

    @classmethod
    def generate_topo(cls, nnodes, seed):
        import numpy as np

        assert nnodes <= MAX_GABRIEL_NODES

        nodes = []
        links = []
        pos = {}
        demands = {}

        random.seed(seed)

        scale = (nnodes * 10000) ** 0.5
        exclusion = 25.0  # prevent points from being too close
        print(nnodes, seed, scale, exclusion)

        pos = np.empty((nnodes, 2))
        pos.fill(np.nan)

        def dist2(p, q):
            x = (p - q) ** 2
            return x[:, 0] + x[:, 1]

        n = 0
        exclusion_2 = exclusion ** 2
        while n < nnodes:
            p = (random.random() * scale, random.random() * scale)
            if nodes:
                if np.nanmin(dist2(p, pos)) < exclusion_2:
                    continue
            node = f'R{n}'
            pos[n] = p
            nodes.append({'id': node, 'pos': p})
            n += 1

        def neighbors(p, q):
            c = (pos[p] + pos[q]) / 2
            dd = (pos[p] - c) ** 2
            dd = dd[0] + dd[1]
            # print(np.nanmin(dist2(c, pos)), dd)
            if dist2(pos, c).min() < dd:
                return False
            return True

        for p in range(nnodes):
            for q in range(nnodes):
                if p < q and neighbors(p, q):
                    distance = (pos[p] - pos[q]) ** 2
                    distance = (distance[0] + distance[1]) ** 0.5
                    links.append({'source': nodes[p]['id'], 'target': nodes[q]['id'], 'distance': distance})

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'links': links}


if __name__ == '__main__':

    try:
        topo_names = sys.argv[1:]
    except IndexError:
        raise ValueError("Correct syntax is: %s topo_name" % sys.argv[0])

    # for topo_name in topo_names:
    #     SNDLibGenerator.save_topo(topo_name, with_plot=True, with_path_stats=True, with_topo_stats=True, plot_aspect=0.625)

    for n in range(25, 525, 25):
        ts = time.time()
        for i in range(10):
            GabrielGenerator.save_topo(n, (i * MAX_GABRIEL_NODES) + n, filename='mininet/topo_lib/gabriel2/%s/%s' % (n, i), indent=0, with_plot=True, with_topo_stats=True, with_path_stats=True)
            exit()
        print(time.time() - ts)
