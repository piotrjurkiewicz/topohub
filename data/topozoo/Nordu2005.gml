graph [
  name "nordu2005"
  directed 0
  stats [
    nodes 6
    links 6
    demands 30
    min_degree 1
    avg_degree 2.0
    std_degree 1.15
    max_degree 4
    gini 0.31
    min_link_len 395.86
    avg_link_len 768.54
    max_link_len 2104.79
    diameter_len 3315.53
    diameter_hops 3
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 1.73
    avg_sdp_len 1372.29
    avg_adp_num 1.2
    max_adp_num 2
    avg_adp_hops 1.83
    avg_adp_len 1467.12
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
  node [
    id 7
    label "St Petersburg"
    lon 30.26
    lat 59.89
  ]
  node [
    id 8
    label "Oslo"
    lon 10.75
    lat 59.91
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
    source 1
    target 7
    dist 688.2
  ]
  edge [
    source 1
    target 8
    dist 416.46
  ]
  edge [
    source 3
    target 8
    dist 483.38
  ]
  edge [
    source 3
    target 4
    dist 2104.79
  ]
]