#!/usr/bin/env python3
"""Unit tests for Responsiveness Gate (Throughput & Latency)."""
import unittest
from benchmark_throughput import simulate_stream_latency_benchmark


class ResponsivenessGateTests(unittest.TestCase):
    def test_responsiveness_p95_under_2_seconds(self):
        res = simulate_stream_latency_benchmark(
            target_rate_events_per_sec=200,
            subscriber_count=50,
            duration_seconds=1.5,
        )

        self.assertEqual(res["target_rate_events_per_sec"], 200)
        self.assertEqual(res["subscriber_count"], 50)
        self.assertLess(res["ingest_to_visible"]["p95_ms"], 2000.0)
        self.assertTrue(res["gate_passed"])


if __name__ == "__main__":
    unittest.main()

