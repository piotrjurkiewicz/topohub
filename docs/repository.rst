Topology repository
*******************

The topology repository contains 200 Gabriel graph topologies, with linearly increasing node counts ranging from 25 to 500 nodes, in steps of 25 nodes. For each network size (the number of nodes), ten different topologies were generated, each with a different, but controlled seed. This ensures their reproducibility.

Two constraints were applied to the generated Gabriel graphs. The positions of nodes (and thus distances between them) were scaled in such a way as to ensure that the average link length will be equal to 100 km. Additionally, we imposed a limitation on the minimal distance between nodes, which was set to 25 km. The number of graph edges was not considered as an input parameter because, in Gabriel graphs, it depends on the location of vertices and cannot be directly controlled.

The definition of each topology is stored in a JSON file constructed according to the ``networkx`` node-link format. This JSON object contains the following fields:

- The ``graph`` field, consisting of: the topology ``name``, the ``demands`` object holding demands between pairs of nodes if given by the original source topology, and the ``stats`` object, containing pre-calculated topology statistical properties.

- The ``nodes`` field, containing a list of nodes in the topology, along with their positions, stored as latitude and longitude pairs in the ``pos`` arrays.

- The ``links`` field, containing a list of links in the topology, defined by ``source`` and ``target`` node names. The links objects also contain the ``dist`` field providing the link length in kilometers, and ``ecmp_fwd`` and ``ecmp_bwd`` fields. They contain pre-calculated links percentage utilization in forward and backward directions for the case of ECMP shortest path routing being used in the network.


Additionally, in addition to the synthetic Gabriel graph topologies, we also generated JSON definitions and SVG visualizations for topologies from the `Internet Topology Zoo <https://topology-zoo.org/>`_ and `SNDlib <https://sndlib.put.poznan.pl/>`_ and also provide them in the repository. This gives the possibility to explore their properties using the web interface and allows using them interchangeably with the synthetic Gabriel graph topologies, for example in Mininet with the help of the automatic import feature.

.. toctree::
   :maxdepth: 2
