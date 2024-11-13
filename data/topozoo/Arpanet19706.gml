graph [
  name "arpanet19706"
  directed 0
  stats [
    nodes 9
    links 10
    demands 72
    min_degree 1
    avg_degree 2.22
    std_degree 0.63
    max_degree 3
    gini 0.14
    min_link_len 0.0
    avg_link_len 959.55
    max_link_len 4188.82
    diameter_len 4733.06
    diameter_hops 4
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 2.31
    avg_sdp_len 1943.71
    avg_adp_num 1.36
    max_adp_num 2
    avg_adp_hops 2.62
    avg_adp_len 2800.39
  ]
  node [
    id 0
    label "HARVARD"
    lon -71.12
    lat 42.38
  ]
  node [
    id 1
    label "SRI"
    lon -122.18
    lat 37.45
  ]
  node [
    id 2
    label "UCSB"
    lon -119.7
    lat 34.42
  ]
  node [
    id 3
    label "UCLA"
    lon -118.24
    lat 34.05
  ]
  node [
    id 4
    label "RAND"
    lon -118.49
    lat 34.02
  ]
  node [
    id 5
    label "SDC"
    lon -118.49
    lat 34.02
  ]
  node [
    id 6
    label "UTAH"
    lon -111.89
    lat 40.76
  ]
  node [
    id 7
    label "MIT"
    lon -71.09
    lat 42.36
  ]
  node [
    id 8
    label "BBN"
    lon -71.11
    lat 42.38
  ]
  edge [
    source 0
    target 8
    dist 0.96
  ]
  edge [
    source 1
    target 2
    dist 404.74
  ]
  edge [
    source 1
    target 3
    dist 519.06
  ]
  edge [
    source 2
    target 3
    dist 139.89
  ]
  edge [
    source 3
    target 4
    dist 23.1
  ]
  edge [
    source 4
    target 8
    dist 4188.82
  ]
  edge [
    source 4
    target 5
    dist 0.0
  ]
  edge [
    source 5
    target 6
    dist 949.31
  ]
  edge [
    source 6
    target 7
    dist 3367.5
  ]
  edge [
    source 7
    target 8
    dist 2.07
  ]
]