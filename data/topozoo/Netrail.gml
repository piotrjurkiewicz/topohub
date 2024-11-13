graph [
  name "netrail"
  directed 0
  stats [
    nodes 7
    links 10
    demands 42
    min_degree 2
    avg_degree 2.86
    std_degree 1.12
    max_degree 5
    gini 0.2
    min_link_len 57.22
    avg_link_len 1340.95
    max_link_len 3907.12
    diameter_len 4391.26
    diameter_hops 2
    avg_sdp_num 1.14
    max_sdp_num 2
    avg_sdp_hops 1.52
    avg_sdp_len 1150.77
    avg_adp_num 2.19
    max_adp_num 4
    avg_adp_hops 2.13
    avg_adp_len 2637.35
  ]
  node [
    id 0
    label "Palo Alto"
    lon -122.14
    lat 37.44
  ]
  node [
    id 1
    label "Chicago"
    lon -87.65
    lat 41.85
  ]
  node [
    id 2
    label "New York"
    lon -74.01
    lat 40.71
  ]
  node [
    id 3
    label "Baltimore"
    lon -76.61
    lat 39.29
  ]
  node [
    id 4
    label "Washington, DC"
    lon -77.04
    lat 38.9
  ]
  node [
    id 5
    label "Miami"
    lon -80.19
    lat 25.77
  ]
  node [
    id 6
    label "Atlanta"
    lon -84.39
    lat 33.75
  ]
  edge [
    source 0
    target 4
    dist 3907.12
  ]
  edge [
    source 0
    target 6
    dist 3416.45
  ]
  edge [
    source 1
    target 2
    dist 1146.16
  ]
  edge [
    source 1
    target 6
    dist 945.35
  ]
  edge [
    source 2
    target 3
    dist 272.72
  ]
  edge [
    source 2
    target 4
    dist 328.58
  ]
  edge [
    source 3
    target 4
    dist 57.22
  ]
  edge [
    source 4
    target 5
    dist 1488.95
  ]
  edge [
    source 4
    target 6
    dist 872.17
  ]
  edge [
    source 5
    target 6
    dist 974.8
  ]
]