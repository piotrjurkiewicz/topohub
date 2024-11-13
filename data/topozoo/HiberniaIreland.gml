graph [
  name "hiberniaireland"
  directed 0
  stats [
    nodes 6
    links 6
    demands 30
    min_degree 1
    avg_degree 2.0
    std_degree 0.58
    max_degree 3
    gini 0.14
    min_link_len 73.32
    avg_link_len 95.0
    max_link_len 133.45
    diameter_len 261.68
    diameter_hops 3
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 1.73
    avg_sdp_len 110.56
    avg_adp_num 1.67
    max_adp_num 2
    avg_adp_hops 2.4
    avg_adp_len 226.46
  ]
  node [
    id 0
    label "Dublin"
    lon -6.27
    lat 53.34
  ]
  node [
    id 1
    label "Galway"
    lon -9.05
    lat 53.27
  ]
  node [
    id 2
    label "Limerick"
    lon -8.62
    lat 52.66
  ]
  node [
    id 3
    label "Cork"
    lon -8.5
    lat 51.9
  ]
  node [
    id 4
    label "Waterford"
    lon -7.11
    lat 52.26
  ]
  node [
    id 5
    label "Portlaioise"
    lon -7.3
    lat 53.03
  ]
  edge [
    source 0
    target 4
    dist 133.45
  ]
  edge [
    source 0
    target 5
    dist 76.95
  ]
  edge [
    source 1
    target 2
    dist 73.32
  ]
  edge [
    source 2
    target 3
    dist 85.65
  ]
  edge [
    source 2
    target 5
    dist 97.93
  ]
  edge [
    source 3
    target 4
    dist 102.71
  ]
]