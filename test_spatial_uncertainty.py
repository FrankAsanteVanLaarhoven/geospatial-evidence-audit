#!/usr/bin/env python3
"""Unit tests for Spatial Uncertainty & Polygon Boundary Intersection."""
import unittest
from spatial_uncertainty import (
    evaluate_spatial_relation,
    min_distance_to_polygon_boundary_meters,
    point_in_polygon,
)


# Simple square polygon (1 deg x 1 deg around 0, 0)
SQUARE_ZONE = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
]


class SpatialUncertaintyTests(unittest.TestCase):
    def test_point_deep_inside_polygon(self):
        self.assertTrue(point_in_polygon(0.5, 0.5, SQUARE_ZONE))
        dist = min_distance_to_polygon_boundary_meters(0.5, 0.5, SQUARE_ZONE)
        self.assertGreater(dist, 50000.0)  # ~55 km from boundary

        res = evaluate_spatial_relation(0.5, 0.5, error_bound_meters=100.0, zone_polygon_coords=SQUARE_ZONE)
        self.assertEqual(res["relation"], "inside")

    def test_point_deep_outside_polygon(self):
        self.assertFalse(point_in_polygon(2.0, 2.0, SQUARE_ZONE))
        res = evaluate_spatial_relation(2.0, 2.0, error_bound_meters=100.0, zone_polygon_coords=SQUARE_ZONE)
        self.assertEqual(res["relation"], "outside")

    def test_boundary_intersecting_yields_unresolved_spatial_relation(self):
        """Blueprint requirement: A boundary intersecting a position's uncertainty region yields an unresolved spatial relation."""
        # Point just inside the boundary (10 meters from west edge at lon=0.0)
        # 1 deg lon at lat 0 is 111320 meters, so 10 meters is ~0.00009 deg
        lon_near_edge = 0.00009
        lat_mid = 0.5
        self.assertTrue(point_in_polygon(lon_near_edge, lat_mid, SQUARE_ZONE))

        dist = min_distance_to_polygon_boundary_meters(lon_near_edge, lat_mid, SQUARE_ZONE)
        self.assertLess(dist, 15.0)

        # If uncertainty radius is 50 meters, the circle intersects the boundary -> unresolved
        res = evaluate_spatial_relation(lon_near_edge, lat_mid, error_bound_meters=50.0, zone_polygon_coords=SQUARE_ZONE)
        self.assertEqual(res["relation"], "unresolved")
        self.assertIn("intersects boundary", res["reason"])

    def test_negative_error_bound_raises_error(self):
        with self.assertRaises(ValueError):
            evaluate_spatial_relation(0.5, 0.5, error_bound_meters=-10.0, zone_polygon_coords=SQUARE_ZONE)


if __name__ == "__main__":
    unittest.main()

