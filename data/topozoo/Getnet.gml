graph [
  name "getnet"
  directed 0
  stats [
    nodes 7
    links 8
    demands 42
    min_degree 1
    avg_degree 2.29
    std_degree 1.03
    max_degree 4
    gini 0.25
    min_link_len 57.22
    avg_link_len 1671.76
    max_link_len 3894.02
    diameter_len 5070.86
    diameter_hops 3
    avg_sdp_num 1.1
    max_sdp_num 2
    avg_sdp_hops 1.81
    avg_sdp_len 2407.16
    avg_adp_num 1.52
    max_adp_num 3
    avg_adp_hops 2.1
    avg_adp_len 3491.66
  ]
  node [
    id 0
    label "Seattle"
    lon -122.33
    lat 47.61
  ]
  node [
    id 1
    label "Santa Clara"
    lon -121.96
    lat 37.35
  ]
  node [
    id 2
    label "Phoenix"
    lon -112.07
    lat 33.45
  ]
  node [
    id 3
    label "Tucson"
    lon -110.93
    lat 32.22
  ]
  node [
    id 4
    label "Washington, DC"
    lon -77.04
    lat 38.9
  ]
  node [
    id 5
    label "Baltimore"
    lon -76.61
    lat 39.29
  ]
  node [
    id 6
    label "Pittsburgh"
    lon -80.0
    lat 40.44
  ]
  edge [
    source 0
    target 1
    dist 1140.72
  ]
  edge [
    source 1
    target 2
    dist 994.9
  ]
  edge [
    source 1
    target 4
    dist 3894.02
  ]
  edge [
    source 1
    target 6
    dist 3614.24
  ]
  edge [
    source 2
    target 3
    dist 173.54
  ]
  edge [
    source 2
    target 4
    dist 3183.54
  ]
  edge [
    source 4
    target 5
    dist 57.22
  ]
  edge [
    source 5
    target 6
    dist 315.91
  ]
]