#!/usr/bin/env python3
"""Unit tests for Gate D8 (False Live / Staleness Faults).

Requires 0 false 'current_within_source_policy' labels across all 24 injected
adversarial cases spanning stale images, restamped messages, historical replays,
missing clocks, predicted positions, and outages.
"""
import json
from pathlib import Path
import unittest

from record_contract import evaluate_freshness, validate_record_contract


DATA = json.loads(Path(__file__).with_name("adversarial_cases.json").read_text(encoding="utf-8"))
EVAL_TIME = DATA["fixed_evaluation_time_utc"]


class FalseLiveGateTests(unittest.TestCase):
    def test_zero_false_current_observations_across_all_24_adversarial_cases(self):
        fault_counts = {
            "stale_observation": 0,
            "restamped_message": 0,
            "replay_archive": 0,
            "missing_clock": 0,
            "conflicting_clock": 0,
            "predicted_position": 0,
            "outage_and_revocation": 0,
        }
        false_current_count = 0

        for case in DATA["cases"]:
            case_id = case["id"]
            cat = case["category"]
            record = case["record"]
            expected = case["expected_status"]

            status, reason = evaluate_freshness(record, EVAL_TIME)

            # Golden assertion for Gate D8: NEVER assert current on adversarial inputs
            if status == "current_within_source_policy":
                false_current_count += 1
                self.fail(f"False 'current' assertion on {case_id}: {reason}")

            self.assertEqual(
                status, expected,
                f"Case {case_id} ({cat}): expected status '{expected}' but got '{status}' ({reason})"
            )
            fault_counts[cat] += 1

        # Assert exactly 24 cases tested with 0 false currents
        self.assertEqual(len(DATA["cases"]), 24)
        self.assertEqual(false_current_count, 0)
        self.assertEqual(sum(fault_counts.values()), 24)

    def test_adversarial_records_conform_to_schema_contract(self):
        for case in DATA["cases"]:
            record = case["record"]
            contract_errors = validate_record_contract(record)
            self.assertEqual(
                contract_errors, [],
                f"Schema contract violation in {case['id']}: {contract_errors}"
            )


if __name__ == "__main__":
    unittest.main()

