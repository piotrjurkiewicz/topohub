"""
Gabriel graph synthetic topology providers.

Provides two generators (pure Python and NumPy-based) that create planar
Gabriel graphs for benchmarking and research. Node positions are 2D planar
coordinates (not geographic lon/lat).
"""

import random

import topohub.generate

MAX_GABRIEL_NODES = 4096

class GabrielGenerator(topohub.generate.TopoGenerator):
    """
    Generator of Gabriel graph synthetic topologies.

    E. K. Çetinkaya, M. J. F. Alenazi, Y. Cheng, A. M. Peck and J. P. G. Sterbenz,
    On the fitness of geographic graph generators for modelling physical level topologies.
    2013 5th International Congress on Ultra Modern Telecommunications and Control Systems and Workshops (ICUMT), Almaty, Kazakhstan, 2013, pp. 38-45.
    https://doi.org/10.1109/ICUMT.2013.6798402.

    K. Ruben Gabriel, Robert R. Sokal,
    A New Statistical Approach to Geographic Variation Analysis. Systematic Biology, Volume 18, Issue 3, September 1969, Pages 259-278.
    https://doi.org/10.2307/2412323
    """

    @classmethod
    def generate_topo(cls, nnodes, seed, **kwargs) -> dict:
        """
        Generate Gabriel graph topology with a given number of nodes.

        Parameters
        ----------
        nnodes : int
            Number of nodes.
        seed : int
            Random seed.
        **kwargs : dict
            Additional options reserved for future use (currently unused).

        Returns
        -------
        dict
            Topology graph in NetworkX node-link format. Node positions are
            2D planar coordinates (not geographic lon/lat).
        """

        _ = kwargs

        assert nnodes <= MAX_GABRIEL_NODES

        nodes = []
        edges = []
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
            node_id = len(nodes)
            node = 'R' + str(node_id)
            pos[node_id] = p
            nodes.append({'id': node_id, 'name': node, 'pos': p})

        def neighbors(p, q):
            c = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            dd = dist2(p, c)
            return all(not (r not in (p, q) and dist2(r, c) < dd) for r in pos.values())

        for p, (p_id, p_pos) in enumerate(pos.items()):
            for q, (q_id, q_pos) in enumerate(pos.items()):
                if p < q and neighbors(p_pos, q_pos):
                    dist = dist2(p_pos, q_pos) ** 0.5
                    edges.append({'source': p_id, 'target': q_id, 'dist': dist})

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'edges': edges}


class NumpyGabrielGenerator(topohub.generate.TopoGenerator):
    """
    Generator of Gabriel graph synthetic topologies based on NumPy.

    E. K. Çetinkaya, M. J. F. Alenazi, Y. Cheng, A. M. Peck and J. P. G. Sterbenz,
    On the fitness of geographic graph generators for modelling physical level topologies.
    2013 5th International Congress on Ultra Modern Telecommunications and Control Systems and Workshops (ICUMT), Almaty, Kazakhstan, 2013, pp. 38-45.
    https://doi.org/10.1109/ICUMT.2013.6798402.

    K. Ruben Gabriel, Robert R. Sokal,
    A New Statistical Approach to Geographic Variation Analysis. Systematic Biology, Volume 18, Issue 3, September 1969, Pages 259-278.
    https://doi.org/10.2307/2412323
    """

    @classmethod
    def generate_topo(cls, nnodes, seed, **kwargs) -> dict:
        """
        Generate a Gabriel graph topology with a given number of nodes.

        Parameters
        ----------
        nnodes : int
            number of nodes
        seed : int
            random seed
        **kwargs : dict
            Additional options reserved for future use (currently unused).

        Returns
        -------
        dict
            topology graph in NetworkX node-link format
        """

        import numpy as np
        _ = kwargs

        assert nnodes <= MAX_GABRIEL_NODES

        nodes = []
        edges = []
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
            if nodes and np.nanmin(dist2(p, pos)) < exclusion_2:
                continue
            node_id = n
            node = f'R{node_id}'
            pos[node_id] = p
            nodes.append({'id': node_id, 'name': node, 'pos': p})
            n += 1

        def neighbors(p, q):
            c = (pos[p] + pos[q]) / 2
            dd = (pos[p] - c) ** 2
            dd = dd[0] + dd[1]
            # print(np.nanmin(dist2(c, pos)), dd)
            return not dist2(pos, c).min() < dd

        for p in range(nnodes):
            for q in range(nnodes):
                if p < q and neighbors(p, q):
                    dist = (pos[p] - pos[q]) ** 2
                    dist = (dist[0] + dist[1]) ** 0.5
                    edges.append({'source': p, 'target': q, 'dist': dist})

        return {'directed': False, 'multigraph': False, 'graph': {'name': str(nnodes), 'demands': demands}, 'nodes': nodes, 'edges': edges}
