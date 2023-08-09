# TopoHub: A repository of reference Gabriel graph and real-world topologies for networking research

This project aims to create a repository of reference network topologies based on Gabriel graphs. It offers 200 Gabriel graph topologies with linearly increasing sizes ranging from 25 to 500 vertices. These topologies were generated in a reproducible manner to model the properties of long-haul optical transport networks. The topologies are available in the code repository and can be previewed and downloaded through a web interface, which allows visualization of individual topologies and exploration of their network properties. An important additional feature is the visualization of pre-computed link loads in the network using the Equal-Cost Multipath (ECMP) shortest path routing algorithm under different traffic demand models.

The web interface is available at: https://www.topohub.org

The package also includes a module that can be imported into the popular network emulator Mininet, enabling automatic usage of the topologies from the repository. It is also important, that apart from synthetic Gabriel topologies, we included all existing topologies from The Internet Topology Zoo and SNDLib into our repository as well. This enables the possibility to study their pre-computed ECMP link loads and import them automatically into the Mininet.

The Python package can be installed from [Python Package Index (PyPI)](https://pypi.org/project/topohub/) using the following command:

    pip install topohub

A detailed documentation, including API reference and Mininet usage example, is available at: https://topohub.readthedocs.io
