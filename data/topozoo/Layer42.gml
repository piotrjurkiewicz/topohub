graph [
  name "layer42"
  directed 0
  stats [
    nodes 6
    links 7
    demands 30
    min_degree 1
    avg_degree 2.33
    std_degree 1.11
    max_degree 4
    gini 0.26
    min_link_len 328.58
    avg_link_len 1569.79
    max_link_len 3920.0
    diameter_len 5223.92
    diameter_hops 3
    avg_sdp_num 1.07
    max_sdp_num 2
    avg_sdp_hops 1.67
    avg_sdp_len 2602.08
    avg_adp_num 1.47
    max_adp_num 3
    avg_adp_hops 1.84
    avg_adp_len 3195.14
  ]
  node [
    id 0
    label "Seattle"
    lon -122.33
    lat 47.61
  ]
  node [
    id 1
    label "San Francisco"
    lon -122.42
    lat 37.77
  ]
  node [
    id 2
    label "Los Angeles"
    lon -118.24
    lat 34.05
  ]
  node [
    id 3
    label "Chicago"
    lon -87.65
    lat 41.85
  ]
  node [
    id 4
    label "New York City"
    lon -74.01
    lat 40.71
  ]
  node [
    id 5
    label "Washington DC"
    lon -77.04
    lat 38.9
  ]
  edge [
    source 0
    target 1
    dist 1093.52
  ]
  edge [
    source 1
    target 2
    dist 559.28
  ]
  edge [
    source 1
    target 3
    dist 2984.23
  ]
  edge [
    source 1
    target 5
    dist 3920.0
  ]
  edge [
    source 3
    target 4
    dist 1146.16
  ]
  edge [
    source 3
    target 5
    dist 956.75
  ]
  edge [
    source 4
    target 5
    dist 328.58
  ]
]