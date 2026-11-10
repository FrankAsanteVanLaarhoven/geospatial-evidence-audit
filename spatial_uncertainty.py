#!/usr/bin/env python3
"""Geospatial uncertainty and zone-boundary intersection engine.

Blueprint requirement:
'A boundary intersecting a position's uncertainty region yields an unresolved spatial relation.'
"""
import math


def point_in_polygon(lon, lat, polygon_coords):
    """Ray casting algorithm to determine if a point (lon, lat) is inside a polygon."""
    num_points = len(polygon_coords)
    inside = False
    p1x, p1y = polygon_coords[0]
    for i in range(1, num_points + 1):
        p2x, p2y = polygon_coords[i % num_points]
        if min(p1y, p2y) < lat <= max(p1y, p2y):
            if lon <= max(p1x, p2x):
                x_inters = (lat - p1y) * (p2x - p1x) / (p2y - p1y + 1e-15) + p1x
                if p1x == p2x or lon <= x_inters:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def point_to_segment_distance_meters(lon, lat, lon1, lat1, lon2, lat2):
    """Calculate minimum great-circle distance in meters from point (lon, lat) to segment (p1, p2)."""
    # Flat approximation using local projection for boundary proximity
    lat_rad = math.radians(lat)
    meters_per_deg_lat = 111320.0
    meters_per_deg_lon = 111320.0 * math.cos(lat_rad)

    px = lon * meters_per_deg_lon
    py = lat * meters_per_deg_lat
    x1 = lon1 * meters_per_deg_lon
    y1 = lat1 * meters_per_deg_lat
    x2 = lon2 * meters_per_deg_lon
    y2 = lat2 * meters_per_deg_lat

    dx = x2 - x1
    dy = y2 - y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - x1, py - y1)

    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg_len_sq))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def min_distance_to_polygon_boundary_meters(lon, lat, polygon_coords):
    """Minimum distance from point to any segment of polygon boundary in meters."""
    num_points = len(polygon_coords)
    min_dist = float("inf")
    p1x, p1y = polygon_coords[0]
    for i in range(1, num_points + 1):
        p2x, p2y = polygon_coords[i % num_points]
        d = point_to_segment_distance_meters(lon, lat, p1x, p1y, p2x, p2y)
        if d < min_dist:
            min_dist = d
        p1x, p1y = p2x, p2y
    return min_dist


def evaluate_spatial_relation(lon, lat, error_bound_meters, zone_polygon_coords):
    """Classify spatial relationship between an uncertain position and a zone polygon.

    Returns:
    - 'inside': Uncertainty region lies entirely inside the zone.
    - 'outside': Uncertainty region lies entirely outside the zone.
    - 'unresolved': Uncertainty region intersects the zone boundary.
    """
    if error_bound_meters < 0:
        raise ValueError("Error bound must be non-negative")

    is_center_inside = point_in_polygon(lon, lat, zone_polygon_coords)
    dist_to_boundary = min_distance_to_polygon_boundary_meters(lon, lat, zone_polygon_coords)

    # If the distance to the boundary is within the error radius, the uncertainty circle intersects
    if dist_to_boundary < error_bound_meters:
        return {
            "relation": "unresolved",
            "is_center_inside": is_center_inside,
            "distance_to_boundary_meters": round(dist_to_boundary, 2),
            "error_bound_meters": error_bound_meters,
            "reason": f"Uncertainty radius ({error_bound_meters}m) intersects boundary (closest edge is {round(dist_to_boundary, 2)}m)"
        }

    relation = "inside" if is_center_inside else "outside"
    return {
        "relation": relation,
        "is_center_inside": is_center_inside,
        "distance_to_boundary_meters": round(dist_to_boundary, 2),
        "error_bound_meters": error_bound_meters,
        "reason": f"Uncertainty radius ({error_bound_meters}m) is strictly {relation} boundary"
    }

