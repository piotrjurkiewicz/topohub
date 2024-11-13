graph [
  name "gblnet"
  directed 0
  stats [
    nodes 8
    links 7
    demands 56
    min_degree 1
    avg_degree 1.75
    std_degree 1.3
    max_degree 5
    gini 0.32
    min_link_len 347.68
    avg_link_len 563.84
    max_link_len 1125.77
    diameter_len 2877.83
    diameter_hops 4
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 2.21
    avg_sdp_len 1431.26
    avg_adp_num 1.0
    max_adp_num 1
    avg_adp_hops 2.21
    avg_adp_len 1431.26
  ]
  node [
    id 0
    label "New York"
    lon -0.14
    lat 53.08
  ]
  node [
    id 1
    label "London"
    lon -0.13
    lat 51.51
  ]
  node [
    id 2
    label "Stockholm"
    lon 18.06
    lat 59.33
  ]
  node [
    id 3
    label "St Petersburg"
    lon 30.26
    lat 59.89
  ]
  node [
    id 4
    label "Moscow"
    lon 37.62
    lat 55.75
  ]
  node [
    id 5
    label "Amsterdam"
    lon 4.89
    lat 52.37
  ]
  node [
    id 6
    label "Frankfurt"
    lon 8.68
    lat 50.12
  ]
  node [
    id 7
    label "Paris"
    lon 2.35
    lat 48.85
  ]
  edge [
    source 0
    target 5
    dist 347.68
  ]
  edge [
    source 1
    target 5
    dist 357.03
  ]
  edge [
    source 2
    target 3
    dist 688.2
  ]
  edge [
    source 2
    target 5
    dist 1125.77
  ]
  edge [
    source 3
    target 4
    dist 633.23
  ]
  edge [
    source 5
    target 6
    dist 364.34
  ]
  edge [
    source 5
    target 7
    dist 430.63
  ]
]