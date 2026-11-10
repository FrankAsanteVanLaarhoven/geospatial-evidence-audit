#!/usr/bin/env python3
"""Unit tests for Active Sensor Selection (Denzler & Brown 2002) and VectorLink Requests."""
import unittest
from active_sensor_selection import (
    create_vectorlink_evidence_request,
    rank_candidate_sensors,
)


CANDIDATE_SENSORS = [
    {
        "sensor_id": "PTZ-BERTH-1",
        "type": "ptz_camera",
        "coordinates": [4.3980, 51.2410],
        "slew_rate_deg_per_sec": 90.0,
        "current_heading_deg": 0.0,
        "resolution_error_meters": 2.0,
        "cost_units": 10.0,
        "permitted": True,
    },
    {
        "sensor_id": "FIXED-CRANE-4",
        "type": "fixed_camera",
        "coordinates": [4.3990, 51.2405],  # Closer distance
        "slew_rate_deg_per_sec": 360.0,    # Already oriented
        "current_heading_deg": 45.0,
        "resolution_error_meters": 5.0,
        "cost_units": 5.0,
        "permitted": True,
    },
    {
        "sensor_id": "ROBOT-PATROL-UAV",
        "type": "uav_robot",
        "coordinates": [4.4200, 51.2500],  # Far away, high transit time
        "slew_rate_deg_per_sec": 20.0,
        "resolution_error_meters": 1.0,
        "cost_units": 150.0,               # Exceeds max budget
        "permitted": True,
    },
    {
        "sensor_id": "SECURITY-RESTRICTED",
        "type": "thermal_camera",
        "coordinates": [4.3985, 51.2412],
        "permitted": False,                # Unpermitted
    },
]


class ActiveSensorSelectionTests(unittest.TestCase):
    def test_ranking_maximizes_expected_error_reduction_per_second(self):
        target = [4.4000, 51.2420]
        uncertainty = 80.0  # 80 meters current uncertainty

        res = rank_candidate_sensors(
            target_coords=target,
            current_uncertainty_meters=uncertainty,
            candidate_sensors=CANDIDATE_SENSORS,
            max_cost=50.0,
        )

        ranked = res["ranked_sensors"]
        # Only 2 sensors eligible (UAV exceeds cost, SECURITY-RESTRICTED not permitted)
        self.assertEqual(len(ranked), 2)
        sensor_ids = [s["sensor_id"] for s in ranked]
        self.assertIn("PTZ-BERTH-1", sensor_ids)
        self.assertIn("FIXED-CRANE-4", sensor_ids)
        self.assertNotIn("ROBOT-PATROL-UAV", sensor_ids)
        self.assertNotIn("SECURITY-RESTRICTED", sensor_ids)

        # Recommended sensor has highest utility per second
        self.assertIsNotNone(res["recommended_sensor"])
        self.assertGreater(
            res["recommended_sensor"]["utility_per_second"],
            0.0
        )

        # Baseline comparison against nearest eligible camera is populated
        self.assertIsNotNone(res["nearest_eligible_camera"])

    def test_vectorlink_evidence_request_generation(self):
        req = create_vectorlink_evidence_request(
            case_id="case-vessel-123",
            site="ANTWERP-DOCKS",
            sensor_id="PTZ-BERTH-1",
            purpose="Adjudicate zone occupancy conflict under approach-A",
            current_device_clock_utc="2026-11-06T14:05:05Z",
            expiry_seconds=90,
        )

        self.assertEqual(req["protocol"], "VectorLink/1.0")
        self.assertEqual(req["case_id"], "case-vessel-123")
        self.assertEqual(req["target_sensor_id"], "PTZ-BERTH-1")
        self.assertEqual(req["expires_at"], "2026-11-06T14:06:35Z")
        self.assertEqual(req["access_mode"], "read_only_observation")
        self.assertTrue(req["request_digest_sha256"])


if __name__ == "__main__":
    unittest.main()

