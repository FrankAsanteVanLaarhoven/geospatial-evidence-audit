#!/usr/bin/env python3
"""Unit tests for SOTA Decision Risk Benchmark and Selective Classification."""
import unittest
from benchmark_risk_coverage import (
    evaluate_model_performance,
    model_naive_geofence,
    model_proposed_source_aware,
    model_tuned_expiry,
    run_sota_gate_evaluation,
    simulate_episodes,
)


class BenchmarkRiskCoverageTests(unittest.TestCase):
    def test_sota_decision_risk_gate_passes(self):
        report = run_sota_gate_evaluation()

        # Gate requirements from blueprint:
        # 1. 300 predefined/simulated episodes
        self.assertEqual(report["episodes_count"], 300)

        # 2. Strongest baseline identified
        self.assertEqual(report["strongest_baseline"], "tuned_expiry")

        # 3. Relative risk reduction >= 30%
        self.assertGreaterEqual(report["relative_risk_reduction"], 0.30)

        # 4. Paired 95% bootstrap interval excludes zero improvement
        self.assertGreater(report["bootstrap_ci_95"]["ci_95_lower"], 0.0)

        # 5. Gate passed flag
        self.assertTrue(report["gate_passed"])

    def test_abstention_on_adversarial_scenarios(self):
        episodes = simulate_episodes(seed=123, num_episodes=50)

        for ep in episodes:
            scen = ep["scenario"]
            res = model_proposed_source_aware(ep)

            # In ambiguous boundary or conflict scenarios, proposed model MUST abstain
            if scen in {"boundary_ambiguous", "sensor_conflict"}:
                self.assertEqual(
                    res, "insufficient evidence",
                    f"Failed to abstain on scenario '{scen}' in episode {ep['episode_id']}"
                )


if __name__ == "__main__":
    unittest.main()

