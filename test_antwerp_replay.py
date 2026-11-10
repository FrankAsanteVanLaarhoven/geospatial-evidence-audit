#!/usr/bin/env python3
"""Unit tests for Gate D8 (Antwerp AIS Trajectory Replay & Interpolation Benchmark)."""
import copy
import unittest
from antwerp_replay import (
    evaluate_interpolation_error,
    haversine_meters,
    replay_trip_stream,
)


SAMPLE_ANTWERP_STREAM = [
    {
        "id": "AIS-ANTWERP-01",
        "vessel_id": "VESSEL-355",
        "lat": 51.2401,
        "lon": 4.3980,
        "observed_utc": "2024-01-08T12:00:00Z",
        "available_utc": "2024-01-08T12:00:02Z",
    },
    {
        "id": "AIS-ANTWERP-02",
        "vessel_id": "VESSEL-355",
        "lat": 51.2425,
        "lon": 4.4010,
        "observed_utc": "2024-01-08T12:15:00Z",  # 15 min gap (> 10 min threshold)
        "available_utc": "2024-01-08T12:15:03Z",
    },
    {
        "id": "AIS-ANTWERP-03",
        "vessel_id": "VESSEL-355",
        "lat": 51.2440,
        "lon": 4.4035,
        "observed_utc": "2024-01-08T12:20:00Z",
        "available_utc": "2024-01-08T12:20:02Z",
    },
]

HELD_OUT_REFERENCE_POINT = {
    "vessel_id": "VESSEL-355",
    "lat": 51.2413,
    "lon": 4.3995,
    "observed_utc": "2024-01-08T12:07:30Z",  # Midpoint in the 15-minute gap
}


class AntwerpReplayTests(unittest.TestCase):
    def test_canonical_state_hash_is_invariant_to_duplicates_and_shuffling(self):
        cutoff = "2024-01-08T12:30:00Z"

        # Baseline run
        run1 = replay_trip_stream(SAMPLE_ANTWERP_STREAM, cutoff)

        # Injected duplicates and reverse order
        shuffled_with_dupes = copy.deepcopy(SAMPLE_ANTWERP_STREAM)
        shuffled_with_dupes.reverse()
        shuffled_with_dupes.extend(copy.deepcopy(SAMPLE_ANTWERP_STREAM))

        run2 = replay_trip_stream(shuffled_with_dupes, cutoff)

        # Gate D8: Identical canonical state hash and 0 duplicate vessel IDs
        self.assertEqual(run1["canonical_state_sha256"], run2["canonical_state_sha256"])
        self.assertEqual(run1["active_vessel_count"], 1)
        self.assertEqual(run2["active_vessel_count"], 1)
        self.assertEqual(
            run1["vessels"]["VESSEL-355"]["latest_observed_utc"],
            "2024-01-08T12:20:00Z"
        )

    def test_gap_detection_flags_sparse_intervals(self):
        cutoff = "2024-01-08T12:16:00Z"
        result = replay_trip_stream(SAMPLE_ANTWERP_STREAM, cutoff, gap_threshold_seconds=600)
        vessel = result["vessels"]["VESSEL-355"]

        # 15-minute jump should trigger gap_detected
        self.assertTrue(vessel["gap_detected"])
        self.assertEqual(vessel["latest_fix"]["id"], "AIS-ANTWERP-02")

    def test_future_observations_are_strictly_withheld_at_cutoff(self):
        cutoff = "2024-01-08T12:10:00Z"
        result = replay_trip_stream(SAMPLE_ANTWERP_STREAM, cutoff)
        vessel = result["vessels"]["VESSEL-355"]

        # Only the first fix was available by 12:10:00Z
        self.assertEqual(vessel["latest_fix"]["id"], "AIS-ANTWERP-01")
        self.assertEqual(vessel["fix_count"], 1)

    def test_offline_interpolation_vs_online_baseline_error(self):
        prev_fix = SAMPLE_ANTWERP_STREAM[0]
        next_fix = SAMPLE_ANTWERP_STREAM[1]

        # Online baseline: Last-known position
        online = evaluate_interpolation_error(prev_fix, HELD_OUT_REFERENCE_POINT, method="last_position")
        # Offline reconstruction: Linear interpolation
        offline = evaluate_interpolation_error(prev_fix, HELD_OUT_REFERENCE_POINT, next_fix=next_fix, method="linear")

        # Linear interpolation in gap reduces error compared to stale last position
        self.assertLess(offline["error_meters"], online["error_meters"])
        self.assertGreater(online["error_meters"], 100.0)


if __name__ == "__main__":
    unittest.main()

