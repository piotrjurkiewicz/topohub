graph [
  name "heanet"
  directed 0
  stats [
    nodes 7
    links 11
    demands 42
    min_degree 2
    avg_degree 3.14
    std_degree 1.55
    max_degree 6
    gini 0.25
    min_link_len 0.0
    avg_link_len 93.23
    max_link_len 220.19
    diameter_len 405.22
    diameter_hops 2
    avg_sdp_num 1.33
    max_sdp_num 2
    avg_sdp_hops 1.48
    avg_sdp_len 104.63
    avg_adp_num 2.24
    max_adp_num 5
    avg_adp_hops 1.87
    avg_adp_len 180.05
  ]
  node [
    id 0
    label "Galway"
    lon -9.05
    lat 53.27
  ]
  node [
    id 1
    label "Limerick"
    lon -8.62
    lat 52.66
  ]
  node [
    id 2
    label "Cork"
    lon -8.5
    lat 51.9
  ]
  node [
    id 3
    label "CityWest"
    lon -6.27
    lat 53.34
  ]
  node [
    id 4
    label "DCU (Dublin City University"
    lon -6.27
    lat 53.34
  ]
  node [
    id 5
    label "TDC (Trinity College Dublin)"
    lon -6.27
    lat 53.34
  ]
  node [
    id 6
    label "Kilcarbery"
    lon -6.27
    lat 53.34
  ]
  edge [
    source 0
    target 3
    dist 185.03
  ]
  edge [
    source 0
    target 6
    dist 185.03
  ]
  edge [
    source 1
    target 2
    dist 85.65
  ]
  edge [
    source 1
    target 3
    dist 174.84
  ]
  edge [
    source 1
    target 6
    dist 174.84
  ]
  edge [
    source 2
    target 3
    dist 220.19
  ]
  edge [
    source 3
    target 4
    dist 0.0
  ]
  edge [
    source 3
    target 5
    dist 0.0
  ]
  edge [
    source 3
    target 6
    dist 0.0
  ]
  edge [
    source 4
    target 6
    dist 0.0
  ]
  edge [
    source 5
    target 6
    dist 0.0
  ]
]