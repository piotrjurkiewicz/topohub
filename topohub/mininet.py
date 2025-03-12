import mininet
import mininet.node
import mininet.topo

import topohub

class Demands(dict):
    """Demands dictionary"""
    def __missing__(self, key):
        return 0.0

    @property
    def maximum(self):
        """
        The maximum demand value in the dictionary.

        Returns
        -------
        float
            maximum demand value
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
        k : (str, str)
            (src, dst) node pair
        default : float, default 0.0
            default demand to return if not specified in the dictionary
        sym: bool, default False
            return demand for (dst, src) instead default if demand for (src, dst) not specified in dictionary
        norm: bool, default False
            normalize returned demands to [0.0 - 1.0]

        Returns
        -------
        float
            demand between pair of nodes
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
    demands = Demands()
    topo_json = {}

    def build(self, *args, **params):
        topo = self.topo_json

        if 'demands' in topo['graph']:
            demands = topo['graph']['demands']
            for src in demands:
                for dst in demands[src]:
                    self.demands[str(src), str(dst)] = demands[src][dst]

        for node in topo['nodes']:
            self.addSwitch(str(node['id']), **{k: v for k, v in node.items() if k not in ['id', 'name']})
        for link in topo['links']:
            self.addLink(str(link['source']), str(link['target']), **{k: v for k, v in link.items() if k not in ['source', 'target']})

        super(JSONTopo, self).build(**params)

def make_topo_class_from_json(name, topo):
    cls_name = name.title().replace('/', '_')
    cls = type(str(cls_name), (JSONTopo,), {'name': name, 'topo_json': topo})
    return cls

class TopoClsDict(dict):
    def __missing__(self, key):
        topo = topohub.get(key)
        cls = make_topo_class_from_json(key, topo)
        self[key] = cls
        return cls

class TopoNamedClsDict(dict):
    def __missing__(self, key):
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
    """Adds k hosts per switch"""

    def build(self, k=1, **params):
        super(AutoHostTopo, self).build(**params)

        for sw in self.switches():
            for i in range(k):
                h = self.addHost("h" + str(i) + "_" + sw)
                self.addLink(h, sw)

class AutoHostBridgeTopo(mininet.topo.Topo):
    """Adds b bridges, each with k hosts, per switch"""

    def build(self, b=1, k=1, **params):
        super(AutoHostBridgeTopo, self).build(**params)

        for sw in self.switches():
            for j in range(b):
                br = self.addSwitch("br" + str(j) + "_" + sw, cls=mininet.node.LinuxBridge, inNamespace=True)
                self.addLink(br, sw)
                for i in range(k):
                    h = self.addHost("h" + str(i) + "_" + br)
                    self.addLink(h, br, cls=mininet.link.TCLink)
