Python package
**************

The Python package consists of three Python modules: ``generate``, ``graph``, and ``mininet``. The ``generate`` executable module can be used to generate topology JSON definition and SVG visualization files. It can generate synthetic Gabriel graphs of a given size, or create topology definitions from the original topology files downloaded from SNDLib or the Topology Zoo.

The ``graph`` module contains functions for performing operations and calculations on network graphs. In particular, it allows determining all shortest paths and all disjoint paths between any node pair in a graph. It uses Dijkstra and Edmonds-Karp algorithms implementations provided by the ``networkx`` library for these purposes, respectively. Based on the computed disjoint paths, it provides the ability to calculate statistics of paths between all node pairs in the network, including the number of disjoint shortest paths and the number of all disjoint paths, and store them in a CSV file. These files are not provided in the repository due to their large size, but users can generate them locally. The ``graph`` module also offers functionalities for calculating topology statistical properties and generating their SVG visualizations.

The package also includes a ``mininet`` module that can be imported into the popular network emulator `Mininet <http://mininet.org/>`_, enabling the automatic usage of the topologies from the repository.


The package, along with JSON topology definitions, is available in the Python Package Index (PyPI) (https://pypi.org/project/topohub/) and can be installed using the ``pip install topohub`` command.

.. toctree::
   :maxdepth: 2
