graph [
  name "epoch"
  directed 0
  stats [
    nodes 6
    links 7
    demands 30
    min_degree 2
    avg_degree 2.33
    std_degree 0.47
    max_degree 3
    gini 0.1
    min_link_len 515.69
    avg_link_len 1756.7
    max_link_len 3887.6
    diameter_len 3968.47
    diameter_hops 3
    avg_sdp_num 1.4
    max_sdp_num 2
    avg_sdp_hops 1.67
    avg_sdp_len 2133.69
    avg_adp_num 2.07
    max_adp_num 3
    avg_adp_hops 2.29
    avg_adp_len 4091.91
  ]
  node [
    id 0
    label "Palo Alto"
    lon -122.14
    lat 37.44
  ]
  node [
    id 1
    label "Los Angeles"
    lon -118.24
    lat 34.05
  ]
  node [
    id 2
    label "Denver"
    lon -104.98
    lat 39.74
  ]
  node [
    id 3
    label "Chicago"
    lon -87.65
    lat 41.85
  ]
  node [
    id 4
    label "Vienna"
    lon -77.27
    lat 38.9
  ]
  node [
    id 5
    label "Atlanta"
    lon -84.39
    lat 33.75
  ]
  edge [
    source 0
    target 1
    dist 515.69
  ]
  edge [
    source 0
    target 2
    dist 1510.99
  ]
  edge [
    source 0
    target 4
    dist 3887.6
  ]
  edge [
    source 1
    target 5
    dist 3111.21
  ]
  edge [
    source 2
    target 3
    dist 1475.8
  ]
  edge [
    source 3
    target 4
    dist 938.32
  ]
  edge [
    source 4
    target 5
    dist 857.26
  ]
]