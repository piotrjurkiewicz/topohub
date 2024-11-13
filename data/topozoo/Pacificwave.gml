graph [
  name "pacificwave"
  directed 0
  stats [
    nodes 3
    links 3
    demands 6
    min_degree 2
    avg_degree 2.0
    std_degree 0.0
    max_degree 2
    gini 0.0
    min_link_len 503.3
    avg_link_len 1062.65
    max_link_len 1545.74
    diameter_len 1545.74
    diameter_hops 1
    avg_sdp_num 1.0
    max_sdp_num 1
    avg_sdp_hops 1.0
    avg_sdp_len 531.33
    avg_adp_num 2.0
    max_adp_num 2
    avg_adp_hops 1.5
    avg_adp_len 1593.98
  ]
  node [
    id 10
    label "Pacific Wave Sunnyvale"
    lon -122.04
    lat 37.37
  ]
  node [
    id 11
    label "Pacific Wave Seattle"
    lon -122.33
    lat 47.61
  ]
  node [
    id 15
    label "Pacific Wave Los Angeles"
    lon -118.24
    lat 34.05
  ]
  edge [
    source 10
    target 11
    dist 1138.92
  ]
  edge [
    source 10
    target 15
    dist 503.3
  ]
  edge [
    source 11
    target 15
    dist 1545.74
  ]
]