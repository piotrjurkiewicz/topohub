Python package
**************

The Python package consists of a top-level helper function `topohub.get()` and three Python modules: ``topohub.generate``, ``topohub.graph``, and ``topohub.mininet``.

The helper function can be used to obtain topologies dicts from JSON files stored in the repository and create NetworkX graph objects basing on them:

.. code-block:: python

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

The ``topohub.generate`` executable module was used to generate all the topology data stored in the repository. Its purpose is to generate topology JSON definition and SVG visualization files. It can generate synthetic Gabriel graphs of a given size, or download topology files from SNDlib or the Topology Zoo and generate graphs basing on the downloaded data.

The ``topohub.graph`` module contains functions for performing operations and calculations on network graphs. In particular, it allows determining all shortest paths and all disjoint paths between any node pair in a graph. It uses Dijkstra and Edmonds-Karp algorithms implementations provided by the ``networkx`` library for these purposes, respectively. Based on the computed disjoint paths, it provides the ability to calculate statistics of paths between all node pairs in the network, including the number of disjoint shortest paths and the number of all disjoint paths, and store them in a CSV file. These files are not provided in the repository due to their large size, but users can generate them locally. The ``topohub.graph`` module also offers functionalities for calculating topology statistical properties and generating their SVG visualizations.

The package also includes a ``topohub.mininet`` module that can be imported into the popular network emulator `Mininet <http://mininet.org/>`_, enabling the automatic creation of Mininet Topo classes for topologies in the repository.

The package, along with JSON topology definitions, is available in the Python Package Index (PyPI) (https://pypi.org/project/topohub/) and can be installed using the ``pip install topohub`` command.

.. toctree::
   :maxdepth: 2
