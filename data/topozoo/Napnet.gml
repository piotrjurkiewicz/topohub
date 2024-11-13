graph [
  name "napnet"
  directed 0
  stats [
    nodes 6
    links 7
    demands 30
    min_degree 1
    avg_degree 2.33
    std_degree 1.37
    max_degree 5
    gini 0.31
    min_link_len 571.53
    avg_link_len 1937.28
    max_link_len 3869.85
    diameter_len 4249.33
    diameter_hops 2
    avg_sdp_num 1.07
    max_sdp_num 2
    avg_sdp_hops 1.53
    avg_sdp_len 2160.89
    avg_adp_num 1.47
    max_adp_num 3
    avg_adp_hops 1.71
    avg_adp_len 3040.78
  ]
  node [
    id 0
    label "Seattle"
    lon -122.33
    lat 47.61
  ]
  node [
    id 1
    label "San Jose"
    lon -121.89
    lat 37.34
  ]
  node [
    id 2
    label "Minneapolis"
    lon -93.26
    lat 44.98
  ]
  node [
    id 3
    label "Chicago"
    lon -87.65
    lat 41.85
  ]
  node [
    id 4
    label "Vienna"
    lon -77.27
    lat 38.9
  ]
  node [
    id 5
    label "Dallas"
    lon -96.81
    lat 32.78
  ]
  edge [
    source 0
    target 1
    dist 1142.5
  ]
  edge [
    source 0
    target 3
    dist 2789.45
  ]
  edge [
    source 1
    target 3
    dist 2957.5
  ]
  edge [
    source 1
    target 4
    dist 3869.85
  ]
  edge [
    source 2
    target 3
    dist 571.53
  ]
  edge [
    source 3
    target 4
    dist 938.32
  ]
  edge [
    source 3
    target 5
    dist 1291.83
  ]
]