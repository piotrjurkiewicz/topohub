Web interface
*************

The web interface was built as a single-page web application and is contained in the ``index.html`` file. This interface facilitates browsing, visualization, and downloading of topologies. It is automatically deployed on each commit using GitHub Pages infrastructure and can be accessed at https://www.topohub.org.

A distinctive feature of the web interface is the visualization of link utilization for scenarios where ECMP (Equal-Cost Multi-Path) shortest path routing is utilized in the network. This reflects the current state of the art in networking, as most interior gateway routing protocols (e.g., OSPF or IS-IS) inherently provide multiple equal-cost shortest paths. The web interface offers visualization for three different traffic demand models:

- ``uniform``, which assumes a constant traffic demand between all pairs of nodes,
- ``degree``, in which the demand between nodes is proportional to the product of the degrees of these nodes, and
- ``original``, based on the original traffic demand matrices provided by the SNDlib project (applicable only for SNDlib topologies).

Users have the capability to select their desired traffic model for visualization from a dropdown menu. The link utilization is represented on the topology graph by varying the width, color, or opacity of the links, with these visual attributes adjustable by the user. By hovering the mouse over a link, users can obtain the exact percentage utilization values. Furthermore, a histogram illustrating the 20 most utilized links is provided, and users can explore the details by hovering the mouse over the bars.

Alternative link to the web interface: https://piotrjurkiewicz.github.io/topohub

.. toctree::
   :maxdepth: 2

