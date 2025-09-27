"""Tests for Mininet topology class construction."""

from topohub.mininet import TOPO_CLS, TOPO_NAMED_CLS

def test_mininet():
    """Instantiate a few topologies and verify basic API works."""
    for topo_cls in [TOPO_CLS['gabriel/25/0'], TOPO_CLS['sndlib/germany50'], TOPO_NAMED_CLS['sndlib/polska']]:
        topo = topo_cls()
        print(topo, topo.nodes(), topo.links())


if __name__ == '__main__':
    test_mininet()
