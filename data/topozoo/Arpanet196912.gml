graph [
  name "arpanet196912"
  directed 0
  stats [
    nodes 4
    links 4
    demands 12
    min_degree 1
    avg_degree 2.0
    std_degree 0.71
    max_degree 3
    gini 0.19
    min_link_len 139.89
    avg_link_len 506.06
    max_link_len 960.57
    diameter_len 1479.63
    diameter_hops 2
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 1.33
    avg_sdp_len 722.89
    avg_adp_num 1.5
    max_adp_num 2
    avg_adp_hops 1.58
    avg_adp_len 900.17
  ]
  node [
    id 0
    label "SRI"
    lon -122.18
    lat 37.45
  ]
  node [
    id 1
    label "USCB"
    lon -119.7
    lat 34.42
  ]
  node [
    id 2
    label "UCLA"
    lon -118.24
    lat 34.05
  ]
  node [
    id 3
    label "UTAH"
    lon -111.89
    lat 40.76
  ]
  edge [
    source 0
    target 1
    dist 404.74
  ]
  edge [
    source 0
    target 2
    dist 519.06
  ]
  edge [
    source 0
    target 3
    dist 960.57
  ]
  edge [
    source 1
    target 2
    dist 139.89
  ]
]