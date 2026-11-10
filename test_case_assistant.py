#!/usr/bin/env python3
"""Unit tests for Grounded Case Assistant & Templated Explanations."""
import copy
import json
from pathlib import Path
import unittest

from case_assistant import generate_case_briefing, verify_briefing_factual_grounding
from port_case import export_bundle


CASE = json.loads(Path(__file__).with_name("port_case.json").read_text(encoding="utf-8"))
EARLY, LATE = CASE["cutoffs"]


class CaseAssistantTests(unittest.TestCase):
    def test_assistant_explicitly_abstains_at_early_cutoff(self):
        briefing = generate_case_briefing(CASE, EARLY)
        self.assertTrue(briefing["is_abstained"])
        self.assertEqual(briefing["decision"], "insufficient evidence")
        self.assertIn("[ABSTENTION]", briefing["briefing_text"])
        self.assertIn("fewer than two independent origins", briefing["briefing_text"])

        # Check citations present for admitted fixes
        bundle = export_bundle(CASE, EARLY)
        is_valid, msg = verify_briefing_factual_grounding(briefing, bundle)
        self.assertTrue(is_valid, msg)

    def test_assistant_confirms_with_citations_at_late_cutoff(self):
        briefing = generate_case_briefing(CASE, LATE)
        self.assertFalse(briefing["is_abstained"])
        self.assertEqual(briefing["decision"], "confirmed")
        self.assertIn("[CONFIRMED]", briefing["briefing_text"])

        # Both origins cited
        self.assertIn("[AIS-1 @ 2026-11-06T14:04:59Z]", briefing["briefing_text"])
        self.assertIn("[CAM-NEW @ 2026-11-06T14:05:01Z]", briefing["briefing_text"])

        bundle = export_bundle(CASE, LATE)
        is_valid, msg = verify_briefing_factual_grounding(briefing, bundle)
        self.assertTrue(is_valid, msg)

    def test_factual_grounding_verifier_rejects_hallucinations(self):
        briefing = generate_case_briefing(CASE, EARLY)
        bundle = export_bundle(CASE, EARLY)

        # Tamper briefing text with hallucinated citation
        tampered = copy.deepcopy(briefing)
        tampered["briefing_text"] += "\nFictitious report [GHOST-RADAR @ 2026-11-06T14:05:00Z] confirmed position."

        is_valid, msg = verify_briefing_factual_grounding(tampered, bundle)
        self.assertFalse(is_valid)
        self.assertIn("Hallucinated or unadmitted citation: GHOST-RADAR", msg)


if __name__ == "__main__":
    unittest.main()
