graph [
  name "telecomserbia"
  directed 0
  stats [
    nodes 6
    links 6
    demands 30
    min_degree 2
    avg_degree 2.0
    std_degree 0.0
    max_degree 2
    gini 0.0
    min_link_len 54.04
    avg_link_len 142.67
    max_link_len 315.97
    diameter_len 386.1
    diameter_hops 3
    avg_sdp_num 1.2
    max_sdp_num 2
    avg_sdp_hops 1.8
    avg_sdp_len 171.21
    avg_adp_num 2.0
    max_adp_num 2
    avg_adp_hops 3.0
    avg_adp_len 428.02
  ]
  node [
    id 0
    label "Novi Sad"
    lon 19.84
    lat 45.25
  ]
  node [
    id 1
    label "Belgrade"
    lon 20.47
    lat 44.8
  ]
  node [
    id 2
    label "Kragujevac"
    lon 20.92
    lat 44.02
  ]
  node [
    id 3
    label "Nis"
    lon 21.9
    lat 43.32
  ]
  node [
    id 4
    label "Krusevac"
    lon 21.33
    lat 43.58
  ]
  node [
    id 5
    label "Podgorica"
    lon 19.26
    lat 42.44
  ]
  edge [
    source 0
    target 1
    dist 70.13
  ]
  edge [
    source 0
    target 5
    dist 315.97
  ]
  edge [
    source 1
    target 2
    dist 94.64
  ]
  edge [
    source 2
    target 3
    dist 110.56
  ]
  edge [
    source 3
    target 4
    dist 54.04
  ]
  edge [
    source 4
    target 5
    dist 210.7
  ]
]