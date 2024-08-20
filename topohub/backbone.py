import re

regions = {
    'north_america': [
        (-49.97423, 53.314387),
        (-126.67538, 55.783007),
        (-131.59553, 36.726018),
        (-104.34612, 13.214851),
        (-87.613578, 26.458425),
        (-80.0595, 24.425375),
        (-78.930573, 26.679747),
        (-49.83998, 47.369642),
        (-49.97423, 53.314387),
    ],
    'south_america': [
        (-68.333188, 18.14895),
        (-80.310544, 12.660617),
        (-82.836502, 6.595508),
        (-119.18913, -7.726251),
        (-69.61395, -60.035491),
        (-31.559683, -36.654839),
        (-21.654288, -5.527582),
        (-47.723013, 19.440204),
        (-67.349866, 20.79968),
    ],
    'americas': [
        (-49.97423, 53.314387),
        (-88.92, 75.45),
        (-164.24822, 74.575045),
        (-119.18913, -7.726251),
        (-69.61395, -60.035491),
        (-31.559683, -36.654839),
        (-21.654288, -5.527582),
        (-42.161382, 20.345371),
        (-49.83998, 47.369642),
    ],
    'atlantica': [
        (-55.571407, 68.908543),
        (-126.67538, 55.783007),
        (-131.59553, 36.726018),
        (-104.34612, 13.214851),
        (-87.613578, 26.458425),
        (-80.0595, 24.425375),
        (-78.930573, 26.679747),
        (-72.681957, 30.930098),
        (-10.007529, 32.137829),
        (-5.848642, 35.869496),
        (-5.395738, 36.014527),
        (-4.964883, 35.847749),
        (-1.790449, 35.695055),
        (2.363345, 37.468275),
        (10.365865, 37.358544),
        (11.209201, 37.067369),
        (11.065253, 36.573809),
        (12.017891, 34.607841),
        (21.411682, 33.075689),
        (27.874084, 32.244816),
        (32.953135, 32.492736),
        (35.689934, 35.7793),
        (42.303229, 37.19837),
        (53.059452, 46.6085),
        (50.573118, 70.148407),
        (29.747652, 74.778931),
    ],
    'europe': [
        (-26.25391, 67.598507),
        (-21.385482, 39.276906),
        (-10.007529, 32.137829),
        (-5.848642, 35.869496),
        (-5.395738, 36.014527),
        (-4.964883, 35.847749),
        (-1.790449, 35.695055),
        (2.363345, 37.468275),
        (10.365865, 37.358544),
        (11.209201, 37.067369),
        (11.065253, 36.573809),
        (12.017891, 34.607841),
        (21.411682, 33.075689),
        (27.874084, 32.244816),
        (32.953135, 32.492736),
        (35.689934, 35.7793),
        (42.303229, 37.19837),
        (53.059452, 46.6085),
        (50.573118, 70.148407),
        (29.747652, 74.778931),
    ],
    'eurasia': [
        (-26.25391, 67.598507),
        (-21.385482, 39.276906),
        (-10.007529, 32.137829),
        (-5.848642, 35.869496),
        (-5.395738, 36.014527),
        (-4.964883, 35.847749),
        (-1.790449, 35.695055),
        (2.363345, 37.468275),
        (10.365865, 37.358544),
        (11.209201, 37.067369),
        (11.065253, 36.573809),
        (12.017891, 34.607841),
        (21.411682, 33.075689),
        (27.874084, 32.244816),
        (30.890616, 29.55177),
        (38.258307, 18.904067),
        (44.814372, 9.368646),
        (72.955867, 7.122307),
        (96.316253, -12.341449),
        (126.70184, -12.53211),
        (124.94764, -3.316593),
        (137.17709, 4.981104),
        (150.31957, 12.712602),
        (149.57595, 67.075228),
        (29.747652, 74.778931),
    ],
    'eurafrasia': [
        (-26.25391, 67.598507),
        (-21.385482, 39.276906),
        (-22.232896, -8.486824),
        (0.161654, -13.477053),
        (0.982468, -38.496287),
        (55.423756, -38.488487),
        (96.316253, -12.341441),
        (126.70184, -12.532102),
        (124.94764, -3.316585),
        (137.17709, 4.981112),
        (150.31957, 12.71261),
        (149.57595, 67.075236),
        (29.747652, 74.778939),
    ],
    'eastern': [
        (-26.25391, 67.598507),
        (-21.385482, 39.276906),
        (-22.232896, -8.486824),
        (0.161654, -13.477053),
        (0.982468, -38.496287),
        (83.979071, -43.021704),
        (178.38507, -54.41807),
        (179.02224, -34.097123),
        (149.57595, 67.075236),
        (29.747652, 74.778939),
    ],
    'emea': [
        (-26.25391, 67.598507),
        (-21.385482, 39.276906),
        (-22.232896, -8.486824),
        (0.161654, -13.477053),
        (0.982468, -38.496287),
        (64.182358, -40.692598),
        (66.965667, 12.796985),
        (63.126111, 30.731367),
        (51.06117, 55.729397),
        (53.499591, 62.429522),
        (41.335945, 71.292964),
        (29.747652, 74.778939),
    ],
    'africa': [
        (-22.025808, 10.915282),
        (-22.037468, 31.018009),
        (-10.338004, 37.213748),
        (-9.175445, 36.481257),
        (-5.629856, 36.089738),
        (-3.96042, 36.026578),
        (-1.973221, 36.703274),
        (2.430482, 38.416307),
        (12.37489, 38.619499),
        (12.45072, 37.241702),
        (14.287322, 36.616086),
        (16.140535, 36.482629),
        (23.623718, 34.936106),
        (28.56955, 34.12499),
        (33.648236, 33.642133),
        (33.378338, 29.473907),
        (38.235661, 24.297879),
        (38.940779, 21.407588),
        (43.270152, 14.13466),
        (45.230984, 12.390183),
        (56.176876, 15.200557),
        (59.327786, -8.29993),
        (60.900668, -23.978625),
        (34.262985, -41.952349),
        (7.517254, -38.32473),
        (-0.097909, -15.600156),
        (-14.550492, -7.262224),
    ]
}

def svg_path_to_coordinates(svg_path):
    # Regular expression to match commands and coordinate pairs
    pattern = r'([MmLl])\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)\s*,?\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)|(-?\d+(?:\.\d+)?(?:e-?\d+)?)\s*,?\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)'

    matches = re.findall(pattern, svg_path)
    coords = []
    current_pos = (0, 0)
    current_command = None

    for match in matches:
        command, x1, y1, x2, y2 = match
        if command:
            current_command = command
            x, y = float(x1), float(y1)
        else:
            x, y = float(x2), float(y2)

        if current_command in ['M', 'L']:  # Absolute coordinates
            coords.append((x, -y))
            current_pos = (x, y)
        elif current_command in ['m', 'l']:  # Relative coordinates
            new_x, new_y = current_pos[0] + x, current_pos[1] + y
            coords.append((new_x, -new_y))
            current_pos = (new_x, new_y)

    # Round to 6 decimal places
    coords = [(round(lon, 6), round(lat, 6)) for lon, lat in coords]

    return coords

def remove_dead_ends(g):
    while True:
        # Find leaf nodes among the dead ends
        leaf_nodes = [node for node in g.nodes() if g.degree(node) == 0 or g.degree(node) == 1 and g.nodes[node].get('type') == 'Seacable Waypoint']
        if not leaf_nodes:
            break
        # Collect edges to remove
        edges_to_remove = list(g.edges(leaf_nodes))
        # Remove nodes and edges
        g.remove_nodes_from(leaf_nodes)
        g.remove_edges_from(edges_to_remove)
    return g

def point_in_polygon(x, y, polygon):
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def geometry_to_path(geometry):
    if geometry.geom_type == 'Polygon':
        return polygon_to_path(geometry.exterior.coords)
    elif geometry.geom_type == 'MultiPolygon':
        return ' '.join(polygon_to_path(poly.exterior.coords) for poly in geometry.geoms)

def polygon_to_path(coords):
    path_data = f'M {coords[0][0]:.2f},{-coords[0][1]:.2f}'
    path_data += ''.join(f' L {x:.2f},{-y:.2f}' for x, y in coords[1:])
    path_data += ' Z'
    return path_data

def filter_contiguous_us(world):
    import geopandas as gpd
    # Filter the GeoDataFrame to include only the United States
    us = world[world['NAME'] == 'United States of America']

    # Extract the geometry of the United States
    us_geom = us.geometry.iloc[0]

    # Define the bounding box for the contiguous US
    minx, miny, maxx, maxy = -125.0, 24.396308, -66.93457, 49.384358

    # Create a list to hold the contiguous US polygons
    polygons = []

    # Check if the geometry is a MultiPolygon or a single Polygon
    if us_geom.geom_type == 'MultiPolygon':
        for poly in us_geom.geoms:  # Access each Polygon in the MultiPolygon
            bounds = poly.bounds
            if bounds[0] >= minx and bounds[2] <= maxx and bounds[1] >= miny and bounds[3] <= maxy:
                polygons.append(poly)
    elif us_geom.geom_type == 'Polygon':
        # Check if the single polygon is within the contiguous US bounding box
        bounds = us_geom.bounds
        if bounds[0] >= minx and bounds[2] <= maxx and bounds[1] >= miny and bounds[3] <= maxy:
            polygons.append(us_geom)

    # Create a GeoDataFrame from the list of polygons
    contiguous_us = gpd.GeoDataFrame(geometry=polygons, crs=world.crs)
    return contiguous_us

def filter_mainland_europe(world):
    import geopandas as gpd
    europe = world[world['CONTINENT'] == 'Europe']

    # Define the bounding box for mainland Europe
    minx, miny, maxx, maxy = -30.0, 34.0, 45.0, 72.0  # Adjusted for mainland Europe

    # Create a GeoDataFrame to hold mainland Europe polygons
    mainland_europe_polygons = []

    # Iterate over the geometries in the world GeoDataFrame
    for _, row in europe.iterrows():
        geometry = row.geometry
        if geometry.geom_type == 'MultiPolygon':
            for poly in geometry.geoms:
                bounds = poly.bounds
                if bounds[0] >= minx and bounds[2] <= maxx and bounds[1] >= miny and bounds[3] <= maxy:
                    mainland_europe_polygons.append(poly)
        elif geometry.geom_type == 'Polygon':
            bounds = geometry.bounds
            if bounds[0] >= minx and bounds[2] <= maxx and bounds[1] >= miny and bounds[3] <= maxy:
                mainland_europe_polygons.append(geometry)

    # Create a GeoDataFrame from the list of mainland Europe polygons
    mainland_europe = gpd.GeoDataFrame(geometry=mainland_europe_polygons, crs=europe.crs)

    return mainland_europe

def filter_countries(world, include_countries=None, include_continents=None, exclude_countries=None):
    import pandas as pd

    # Apply continent filters
    if include_continents:
        if 'all' in include_continents:
            include_continents = ['Europe', 'North America', 'South America', 'Asia', 'Africa', 'Oceania']
        mask_continents = world['CONTINENT'].isin(include_continents)
    else:
        mask_continents = False

    # Apply inclusion filters
    if include_countries:
        mask_countries = world['NAME'].isin(include_countries)
    else:
        mask_countries = False

    filtered = world[mask_continents | mask_countries]

    if include_continents and 'EU' in include_continents:
        # Add mainland EU
        mainland_europe = filter_mainland_europe(world)
        filtered = pd.concat([filtered, mainland_europe], ignore_index=True)

    if include_countries and 'US' in include_countries:
        # Add contiguous US
        contiguous_us = filter_contiguous_us(world)
        filtered = pd.concat([filtered, contiguous_us], ignore_index=True)

    # Apply exclusion filters
    if exclude_countries:
        filtered = filtered[~filtered['NAME'].isin(exclude_countries)]

    return filtered

def generate_map(include_continents=None, include_countries=None, exclude_countries=None):
    import geopandas as gpd
    world = gpd.read_file(open('ne_50m_admin_0_countries_lakes.zip', 'rb'))
    if include_continents or include_countries or exclude_countries:
        filtered_world = filter_countries(world, include_countries, include_continents, exclude_countries)
    else:
        filtered_world = world
    background = []
    for _, country in filtered_world.iterrows():
        path_data = geometry_to_path(country.geometry)
        background.append(f'<path class="country" d="{path_data}"/>\n')
    return background


if __name__ == '__main__':
    coordinates = svg_path_to_coordinates("m -22.025808,-10.915282 -0.01166,-20.102727 11.699464,-6.195739 1.162559,0.732491 3.5455891,0.391519 1.6694363,0.06316 1.9871983,-0.676696 4.4037037,-1.713033 9.9444076,-0.203192 0.07583,1.377797 1.836602,0.625616 1.853213,0.133457 7.483183,1.546523 4.945832,0.811116 5.078686,0.482857 -0.269898,4.168226 4.857323,5.176028 0.705118,2.890291 4.329373,7.272928 1.960832,1.744477 10.945892,-2.810374 3.15091,23.5004867 L 60.900668,23.978625 34.262985,41.952349 7.5172538,38.32473 -0.09790933,15.600156 -14.550492,7.2622238 Z")
    print("[")
    for lon, lat in coordinates:
        print(f"    ({lon}, {lat}),")
    print("]")
