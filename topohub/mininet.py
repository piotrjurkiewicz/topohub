import json

import mininet
import mininet.node
import mininet.topo

class Demands(dict):
    def __missing__(self, key):
        return 0.0

    @property
    def maximum(self):
        try:
            return self.__maximum
        except AttributeError:
            try:
                self.__maximum = max(self.values())
            except ValueError:
                self.__maximum = 0.0
            return self.__maximum

    def get(self, k, default=0.0, sym=False, norm=False):
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
            self.addSwitch(str(node['id']), **{k: v for k, v in node.items() if k != 'id'})
        for link in topo['links']:
            self.addLink(str(link['source']), str(link['target']), **{k: v for k, v in link.items() if k not in ['source', 'target']})

        super(JSONTopo, self).build(**params)

def make_topo_class_from_json(topo):
    name = topo['graph']['name']
    cls_name = name.title().replace('_', '')
    cls = type(str(cls_name), (JSONTopo,), {'name': name, 'topo_json': topo})
    return cls

class TopoDict(dict):
    def __missing__(self, key):
        try:
            topo = json.load(open('data/%s.json' % key))
            cls = make_topo_class_from_json(topo)
            self[key] = cls
            return cls
        except IOError:
            raise KeyError

TOPOS = TopoDict()

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
