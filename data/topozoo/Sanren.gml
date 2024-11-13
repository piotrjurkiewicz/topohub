graph [
  name "sanren"
  directed 0
  stats [
    nodes 7
    links 7
    demands 42
    min_degree 2
    avg_degree 2.0
    std_degree 0.0
    max_degree 2
    gini 0.0
    min_link_len 52.88
    avg_link_len 461.53
    max_link_len 909.24
    diameter_len 1570.43
    diameter_hops 3
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 2.0
    avg_sdp_len 461.53
    avg_adp_num 2.0
    max_adp_num 2
    avg_adp_hops 3.5
    avg_adp_len 1615.35
  ]
  node [
    id 0
    label "Johannesburg"
    lon 28.04
    lat -26.2
  ]
  node [
    id 1
    label "Pretoria"
    lon 28.19
    lat -25.74
  ]
  node [
    id 2
    label "Durban"
    lon 31.02
    lat -29.85
  ]
  node [
    id 3
    label "Bloemfontein"
    lon 26.2
    lat -29.13
  ]
  node [
    id 4
    label "East London"
    lon 27.91
    lat -33.02
  ]
  node [
    id 5
    label "Port Elizabeth"
    lon 25.58
    lat -33.97
  ]
  node [
    id 6
    label "Cape Town"
    lon 18.42
    lat -33.92
  ]
  edge [
    source 0
    target 1
    dist 52.88
  ]
  edge [
    source 0
    target 3
    dist 373.17
  ]
  edge [
    source 1
    target 2
    dist 534.69
  ]
  edge [
    source 2
    target 4
    dist 459.06
  ]
  edge [
    source 3
    target 6
    dist 909.24
  ]
  edge [
    source 4
    target 5
    dist 240.49
  ]
  edge [
    source 5
    target 6
    dist 661.19
  ]
]