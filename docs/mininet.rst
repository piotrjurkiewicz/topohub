Mininet usage
*************

.. toctree::
   :maxdepth: 2

Here we present a tutorial, which provides a step by step guide through the distribution fitting and model creation process.

First, it must be ensured that the required Python's standard library modules are installed. This applies to `venv` module, which in some distributions is not installed by default with the Python's binaries. On Debian-like system, they can be installed using the following command:

.. code-block:: shell-session

    $ sudo apt-get install python3-venv
    Reading package lists... Done
    Building dependency tree
    Reading state information... Done
    python3-venv is already the newest version (3.8.2-0ubuntu2).
    0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.

We will conduct our experiments in a virtual environment. Alternatively, the ``topohub`` package can be installed systemwide with the ``pip`` command.

The listing below shows the process of virtual environment preparation. The user should first initialize a virtual environment. Then, the ``pip`` command is used to install the ``topohub`` package from `Python Package Index <https://pypi.org/project/flow-models/>`_ along with its dependencies.

.. code-block:: shell-session

    $ python3 -m venv test
    $ cd test
    $ bin/pip install mininet topohub
