graph [
  name "nordu1989"
  directed 0
  stats [
    nodes 5
    links 4
    demands 20
    min_degree 1
    avg_degree 1.6
    std_degree 0.8
    max_degree 3
    gini 0.25
    min_link_len 395.86
    avg_link_len 908.63
    max_link_len 2104.79
    diameter_len 3238.66
    diameter_hops 3
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 1.8
    avg_sdp_len 1558.31
    avg_adp_num 1.0
    max_adp_num 1
    avg_adp_hops 1.8
    avg_adp_len 1558.31
  ]
  node [
    id 0
    label "Trondheim"
    lon 10.4
    lat 63.43
  ]
  node [
    id 1
    label "Stockholm"
    lon 18.06
    lat 59.33
  ]
  node [
    id 2
    label "Helsinki"
    lon 24.94
    lat 60.17
  ]
  node [
    id 3
    label "Copenhagen"
    lon 12.57
    lat 55.68
  ]
  node [
    id 4
    label "Reykjavik"
    lon -21.9
    lat 64.14
  ]
  edge [
    source 0
    target 1
    dist 611.33
  ]
  edge [
    source 1
    target 2
    dist 395.86
  ]
  edge [
    source 1
    target 3
    dist 522.53
  ]
  edge [
    source 3
    target 4
    dist 2104.79
  ]
]