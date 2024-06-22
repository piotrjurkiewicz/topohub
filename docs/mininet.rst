Mininet usage
*************

.. toctree::
   :maxdepth: 2

Here we present a tutorial, which provides a step by step guide for using the automatic Mininet topology import feature.


We will conduct our experiments in a virtual environment. Alternatively, the ``topohub`` package can be installed systemwide with the ``pip`` command.

First, it must be ensured that the required Python's standard library modules are installed. This applies to ``venv`` module, which in some distributions is not installed by default with the Python's binaries. Additionally, the ``mininet`` and ``openvswitch-switch`` and ``openvswitch-testcontroller`` packages are needed. On Debian-like system, they can be installed using the following command:

.. code-block:: shell-session

    $ sudo apt-get install python3-venv mininet openvswitch-switch openvswitch-testcontroller


The listing below shows the process of virtual environment preparation. The user should first initialize a virtual environment. Then, the ``pip`` command is used to install the ``topohub`` package from `Python Package Index <https://pypi.org/project/topohub/>`_ along with its dependencies:

.. code-block:: shell-session

    $ python3 -m venv test
    $ cd test
    $ bin/pip install topohub
    Collecting topohub
      Obtaining dependency information for topohub from https://files.pythonhosted.org/packages/67/32/09ba4c6c1518be61c251c6c746049ffc484713e6fcb5f4174842c4cbe322/topohub-0.4-py3-none-any.whl.metadata
      Downloading topohub-0.4-py3-none-any.whl.metadata (2.6 kB)
    Requirement already satisfied: setuptools in ./lib/python3.11/site-packages (from mininet) (68.0.0)
    Downloading topohub-0.4-py3-none-any.whl (3.5 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.5/3.5 MB 8.9 MB/s eta 0:00:00
    Installing collected packages: topohub
    Successfully installed topohub-0.4

The code block below provides a minimal example of Python code initializing Mininet network with 25 nodes Gabriel graph topology from the repository:

.. code-block:: python

    import mininet.net
    import topohub.mininet

    # Obtain Mininet Topo class for a selected topology from the repository
    topo_cls = topohub.mininet.TOPO_CLS['gabriel/25/0']

    # Initialize Mininet Topo object
    topo = topo_cls()
    # Create Mininet Network using the selected topology
    net = mininet.net.Mininet(topo=topo)
    # Start the network and Mininet shell
    net.interact()

Then in order to build and initialize the network the script should be executed:

.. code-block:: shell-session

    $ sudo bin/python3 example.py
    mininet> net
    R0 lo:  R0-eth1:R16-eth1 R0-eth2:R22-eth1
    R1 lo:  R1-eth1:R7-eth1 R1-eth2:R11-eth1 R1-eth3:R12-eth1 R1-eth4:R23-eth1
    R2 lo:  R2-eth1:R7-eth2 R2-eth2:R8-eth1
    R3 lo:  R3-eth1:R10-eth1 R3-eth2:R16-eth2 R3-eth3:R20-eth1
    R4 lo:  R4-eth1:R9-eth1 R4-eth2:R13-eth1 R4-eth3:R24-eth1
    R5 lo:  R5-eth1:R6-eth1 R5-eth2:R18-eth1 R5-eth3:R22-eth2
    R6 lo:  R6-eth1:R5-eth1 R6-eth2:R9-eth2 R6-eth3:R20-eth2 R6-eth4:R22-eth3
    R7 lo:  R7-eth1:R1-eth1 R7-eth2:R2-eth1 R7-eth3:R8-eth2 R7-eth4:R23-eth2
    R8 lo:  R8-eth1:R2-eth2 R8-eth2:R7-eth3 R8-eth3:R23-eth3
    R9 lo:  R9-eth1:R4-eth1 R9-eth2:R6-eth2 R9-eth3:R18-eth2 R9-eth4:R24-eth2
    R10 lo:  R10-eth1:R3-eth1 R10-eth2:R16-eth3
    R11 lo:  R11-eth1:R1-eth2 R11-eth2:R14-eth1 R11-eth3:R24-eth3
    R12 lo:  R12-eth1:R1-eth3 R12-eth2:R15-eth1 R12-eth3:R19-eth1 R12-eth4:R23-eth4 R12-eth5:R24-eth4
    R13 lo:  R13-eth1:R4-eth2 R13-eth2:R17-eth1 R13-eth3:R21-eth1
    R14 lo:  R14-eth1:R11-eth2 R14-eth2:R21-eth2 R14-eth3:R24-eth5
    R15 lo:  R15-eth1:R12-eth2 R15-eth2:R19-eth2 R15-eth3:R23-eth5
    R16 lo:  R16-eth1:R0-eth1 R16-eth2:R3-eth2 R16-eth3:R10-eth2 R16-eth4:R20-eth3
    R17 lo:  R17-eth1:R13-eth2
    R18 lo:  R18-eth1:R5-eth2 R18-eth2:R9-eth3 R18-eth3:R19-eth3
    R19 lo:  R19-eth1:R12-eth3 R19-eth2:R15-eth2 R19-eth3:R18-eth3
    R20 lo:  R20-eth1:R3-eth3 R20-eth2:R6-eth3 R20-eth3:R16-eth4
    R21 lo:  R21-eth1:R13-eth3 R21-eth2:R14-eth2
    R22 lo:  R22-eth1:R0-eth2 R22-eth2:R5-eth3 R22-eth3:R6-eth4
    R23 lo:  R23-eth1:R1-eth4 R23-eth2:R7-eth4 R23-eth3:R8-eth3 R23-eth4:R12-eth4 R23-eth5:R15-eth3
    R24 lo:  R24-eth1:R4-eth3 R24-eth2:R9-eth4 R24-eth3:R11-eth3 R24-eth4:R12-eth5 R24-eth5:R14-eth3
    c0
    mininet>

