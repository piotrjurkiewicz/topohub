graph [
  name "cynet"
  directed 0
  stats [
    nodes 4
    links 3
    demands 12
    min_degree 1
    avg_degree 1.5
    std_degree 0.5
    max_degree 2
    gini 0.17
    min_link_len 0.0
    avg_link_len 41.92
    max_link_len 63.19
    diameter_len 125.76
    diameter_hops 3
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 1.67
    avg_sdp_len 73.31
    avg_adp_num 1.0
    max_adp_num 1
    avg_adp_hops 1.67
    avg_adp_len 73.31
  ]
  node [
    id 1
    label "Intercollege"
    lon 33.64
    lat 34.94
  ]
  node [
    id 20
    label "Limassol PoP"
    lon 33.03
    lat 34.67
  ]
  node [
    id 22
    label "Border Router"
    lon 33.37
    lat 35.17
  ]
  node [
    id 29
    label "Nicosia PoP"
    lon 33.37
    lat 35.17
  ]
  edge [
    source 1
    target 20
    dist 63.19
  ]
  edge [
    source 20
    target 22
    dist 62.57
  ]
  edge [
    source 22
    target 29
    dist 0.0
  ]
]