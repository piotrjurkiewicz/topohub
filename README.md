# TopoHub: A repository of reference Gabriel graph and real-world topologies for networking research

This project aims to create a repository of reference network topologies based on Gabriel graphs. It offers 200 Gabriel graph topologies with linearly increasing sizes ranging from 25 to 500 vertices. These topologies were generated in a reproducible manner to model the properties of long-haul optical transport networks. The topologies are available in the code repository and can be previewed and downloaded through a web interface, which allows visualization of individual topologies and exploration of their network properties. An important additional feature is the visualization of pre-computed link loads in the network using the Equal-Cost Multipath (ECMP) shortest path routing algorithm under different traffic demand models.

The web interface is available at: https://www.topohub.org

The package also includes a module that can be imported into the popular network emulator Mininet, enabling automatic usage of the topologies from the repository. It is also important, that apart from synthetic Gabriel topologies, we included all existing topologies from The Internet Topology Zoo and SNDlib into our repository as well. This enables the possibility to study their pre-computed ECMP link loads and import them automatically into the Mininet.

You can cite the following paper if you make use of TopoHub in your research:

    @article{topohub,
        title = {TopoHub: A repository of reference Gabriel graph and real-world topologies for networking research},
        journal = {SoftwareX},
        volume = {24},
        pages = {101540},
        year = {2023},
        issn = {2352-7110},
        doi = {10.1016/j.softx.2023.101540},
        author = {Piotr Jurkiewicz}
    }

The Python package can be installed from [Python Package Index (PyPI)](https://pypi.org/project/topohub/) using the following command:

    pip install topohub

Then you can obtain topologies stored in the repository using the `topohub.get()` method and create NetworkX graph objects basing on them:

```python
import networkx as nx
import topohub

# Obtain topology dicts from JSON files stored in the repository
topo = topohub.get('gabriel/25/0')
topo = topohub.get('backbone/africa')
topo = topohub.get('topozoo/Abilene')
topo = topohub.get('sndlib/polska')

# Create NetworkX graph from node-link dict
g = nx.node_link_graph(topo)

# Access graph parameters
print(g.graph['name'])
print(g.graph['demands'])
print(g.graph['stats']['avg_degree'])

# Obtain link length or ECMP routing utilization
print(g.edges['Bydgoszcz', 'Warsaw']['dist'])
print(g.edges['Bydgoszcz', 'Warsaw']['ecmp_fwd']['uni'])
```

For usage in Mininet, you can use a helper which automatically creates Mininet Topo classes for selected topologies:

```python
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
```

A detailed documentation, including API reference and Mininet usage example, is available at: https://topohub.readthedocs.io
