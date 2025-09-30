"""
Mininet helpers for TopoHub.

This module exposes utilities to obtain Mininet ``Topo`` classes directly
from TopoHub's embedded repository. It also provides convenience topologies
that automatically attach hosts/bridges to each switch.

Notes
-----
- Topologies are loaded from node-link dictionaries returned by ``topohub.get``.
- Coordinates in the repository follow the (longitude, latitude) convention.
"""

import mininet
import mininet.node
import mininet.topo

import topohub

class Demands(dict):
    """Dictionary of traffic demands between node pairs with convenience helpers."""

    def __missing__(self, key):
        """Return the default demand value (0.0) when a key is missing."""
        return 0.0

    @property
    def maximum(self):
        """
        Maximum demand value in the dictionary.

        Returns
        -------
        float
            Maximum demand value, or 0.0 if the dictionary is empty.
        """
        try:
            return self.__maximum
        except AttributeError:
            try:
                self.__maximum = max(self.values())
            except ValueError:
                self.__maximum = 0.0
            return self.__maximum

    def get(self, k, default=0.0, sym=False, norm=False):
        """
        Return the demand value for (src, dst) node pair if specified in the dictionary, else default.

        Parameters
        ----------
        k : tuple[str, str]
            Pair ``(src, dst)`` of node identifiers.
        default : float, default 0.0
            Default demand if the pair is not present.
        sym : bool, default False
            If True, return demand for ``(dst, src)`` when ``(src, dst)`` is missing.
        norm : bool, default False
            If True, normalize the returned demand by the maximum demand value to [0.0, 1.0].

        Returns
        -------
        float
            Demand value between the pair of nodes.
        """
        if k in self:
            val = self[k]
        else:
            src, dst = k
            if sym and (dst, src) in self:
                val = self[dst, src]
            else:
                val = default
        if norm:
            try:
                val /= self.maximum
            except ZeroDivisionError:
                val = 1.0
        return val

class JSONTopo(mininet.topo.Topo):
    """
    Mininet Topo built from a NetworkX node-link dictionary.

    Expects ``topo_json`` class attribute to be set to a node-link dictionary
    with keys: ``graph``, ``nodes``, and ``edges``.
    """

    demands = Demands()
    topo_json = {}

    def build(self, *args, **params):
        """Build the topology using the ``topo_json`` node-link dictionary."""
        _ = args
        topo = self.topo_json

        if 'demands' in topo['graph']:
            demands = topo['graph']['demands']
            for src in demands:
                for dst in demands[src]:
                    self.demands[str(src), str(dst)] = demands[src][dst]

        for node in topo['nodes']:
            self.addSwitch(str(node['id']), **{k: v for k, v in node.items() if k not in ['id', 'name']})
        for edge in topo['edges']:
            self.addLink(str(edge['source']), str(edge['target']), **{k: v for k, v in edge.items() if k not in ['source', 'target']})

        super().build(**params)

def make_topo_class_from_json(name, topo):
    """
    Dynamically construct a Mininet ``Topo`` subclass from a node-link dictionary.

    Parameters
    ----------
    name : str
        Topology key or descriptive name.
    topo : dict
        NetworkX node-link dictionary.

    Returns
    -------
    type
        A ``Topo`` subclass with ``name`` and ``topo_json`` attributes set.
    """
    cls_name = name.title().replace('/', '_')
    cls = type(str(cls_name), (JSONTopo,), {'name': name, 'topo_json': topo})
    return cls

class TopoClsDict(dict):
    """Lazy map from repository keys to generated Mininet Topo classes."""

    def __missing__(self, key):
        """Load a topology and construct a ``Topo`` subclass for the given key."""
        topo = topohub.get(key)
        cls = make_topo_class_from_json(key, topo)
        self[key] = cls
        return cls

class TopoNamedClsDict(dict):
    """Lazy map from repository keys to Mininet Topo classes using node names."""

    def __missing__(self, key):
        """Load a topology (using node names) and return a ``Topo`` subclass."""
        topo = topohub.get(key, use_names=True)
        cls = make_topo_class_from_json(key, topo)
        self[key] = cls
        return cls


TOPO_CLS = TopoClsDict()
"""
Use this dictionary to obtain topologies from the repository as Mininet Topo classes.

Example:

.. code-block:: python

    import mininet.net
    import topohub.mininet

    # Obtain Mininet Topo classes for topologies stored in the repository
    topo_cls = topohub.mininet.TOPO_CLS['gabriel/25/0']
    topo_cls = topohub.mininet.TOPO_CLS['backbone/africa']
    topo_cls = topohub.mininet.TOPO_CLS['topozoo/Abilene']
    topo_cls = topohub.mininet.TOPO_CLS['sndlib/polska']

    # Initialize Mininet Topo object
    topo = topo_cls()
    # Create Mininet Network using the selected topology
    net = mininet.net.Mininet(topo=topo)
    # Start the network and Mininet shell
    net.interact()
"""

TOPO_NAMED_CLS = TopoNamedClsDict()
"""
Use this dictionary to obtain topologies from the repository as Mininet Topo classes,
using node names instead integer IDs as node identifiers.

(this will not work for 'backbone' category topologies which have unnamed or duplicated name nodes)

Example:

.. code-block:: python

    import mininet.net
    import topohub.mininet

    # Obtain Mininet Topo classes for topologies stored in the repository
    topo_cls = topohub.mininet.TOPO_NAMED_CLS['gabriel/25/0']
    topo_cls = topohub.mininet.TOPO_NAMED_CLS['topozoo/Abilene']
    topo_cls = topohub.mininet.TOPO_NAMED_CLS['sndlib/polska']

    # Initialize Mininet Topo object
    topo = topo_cls()
    # Create Mininet Network using the selected topology
    net = mininet.net.Mininet(topo=topo)
    # Start the network and Mininet shell
    net.interact()
"""

class AutoHostTopo(mininet.topo.Topo):
    """
    Topology that adds ``k`` hosts per switch.

    Parameters
    ----------
    k : int, default 1
        Number of hosts to attach to each switch.
    """

    def build(self, k=1, **params):
        """Attach ``k`` hosts to every switch in the topology."""
        super().build(**params)

        for sw in self.switches():
            for i in range(k):
                h = self.addHost("h" + str(i) + "_" + sw)
                self.addLink(h, sw)

class AutoHostBridgeTopo(mininet.topo.Topo):
    """
    Topology that adds ``b`` bridges per switch, each with ``k`` hosts.

    Parameters
    ----------
    b : int, default 1
        Number of bridges to attach to each switch.
    k : int, default 1
        Number of hosts to attach to each bridge.
    """

    def build(self, b=1, k=1, **params):
        """Attach ``b`` bridges per switch and ``k`` hosts per bridge."""
        super().build(**params)

        for sw in self.switches():
            for j in range(b):
                br = self.addSwitch("br" + str(j) + "_" + sw, cls=mininet.node.LinuxBridge, inNamespace=True)
                self.addLink(br, sw)
                for i in range(k):
                    h = self.addHost("h" + str(i) + "_" + br)
                    self.addLink(h, br, cls=mininet.link.TCLink)
