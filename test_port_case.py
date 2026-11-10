import copy
import json
from pathlib import Path
import unittest

from port_case import evaluate, export_bundle
from replay import utc

CASE = json.loads(Path(__file__).with_name("port_case.json").read_text(encoding="utf-8"))
EARLY, LATE = CASE["cutoffs"]


class SimulatedPortTests(unittest.TestCase):
    def test_duplicate_brokers_are_one_source_and_stale_camera_is_excluded(self):
        result = evaluate(CASE, EARLY)
        self.assertEqual(result["independent_origins"], 1)
        self.assertEqual(result["decision"], "insufficient evidence")
        self.assertIn("CAM-OLD", result["excluded_records"])
        self.assertNotIn("CAM-NEW", str(result))

    def test_later_receipt_of_earlier_frame_confirms_at_second_cutoff(self):
        self.assertEqual(evaluate(CASE, LATE)["decision"], "confirmed")
        self.assertEqual(evaluate(CASE, EARLY)["decision"], "insufficient evidence")

    def test_disagreement_requires_review(self):
        c = copy.deepcopy(CASE)
        c["observations"][-1]["position"] = "outside"
        self.assertEqual(evaluate(c, LATE)["reason"], "eligible observations conflict")

    def test_two_direct_outside_observations_contradict(self):
        c = copy.deepcopy(CASE)
        for row in c["observations"]:
            row["position"] = "outside"
        self.assertEqual(evaluate(c, LATE)["decision"], "contradicted")

    def test_no_view_unknown_clock_prediction_and_revoked_grant_cannot_confirm(self):
        for key, value in [("position", "unseen"), ("captured", None),
                           ("kind", "predicted"), ("permitted", False), ("root", None)]:
            with self.subTest(key=key):
                c = copy.deepcopy(CASE)
                c["observations"][-1][key] = value
                self.assertEqual(evaluate(c, LATE)["decision"], "insufficient evidence")

    def test_wrong_asset_or_other_site_is_invisible(self):
        for key in ("subject", "zone", "site"):
            c = copy.deepcopy(CASE)
            c["observations"][-1][key] = "unrelated"
            result = evaluate(c, LATE)
            self.assertNotIn("CAM-NEW", str(result))
            self.assertEqual(result["decision"], "insufficient evidence")

    def test_camera_captured_later_cannot_validate_the_earlier_window(self):
        c = copy.deepcopy(CASE)
        c["observations"][-1]["captured"] = "2026-11-06T14:05:15Z"
        self.assertEqual(evaluate(c, LATE)["decision"], "insufficient evidence")

    def test_reordering_records_preserves_result(self):
        c = copy.deepcopy(CASE)
        c["observations"].reverse()
        self.assertEqual(evaluate(CASE, LATE), evaluate(c, LATE))

    def test_first_implementation_ticket_reopen_and_export_invariance(self):
        """Ticket: Display fields, export at cutoff 1, add delayed records, reopen cutoff 1; bundle & verdict match."""
        # Step 1: Open case from vessel card at Cutoff 1
        bundle_early = export_bundle(CASE, EARLY)
        inner = bundle_early["bundle"]

        # Verify displayed fields required by ticket
        self.assertEqual(inner["target_time"], "2026-11-06T14:05:00Z")
        self.assertEqual(inner["decision_cutoff"], EARLY)
        self.assertEqual(inner["disposition"]["decision"], "insufficient evidence")
        self.assertEqual(inner["origin_groups"], {"transponder-A": {"inside": ["AIS-1", "AIS-2"]}})
        self.assertEqual(inner["excluded_records"], {"CAM-OLD": "capture time outside the admissible window"})
        self.assertEqual(inner["admitted_record_ids"], ["AIS-1", "AIS-2"])

        # Invariant: assert zero observations first available after decision time
        cutoff_dt = utc(EARLY)
        for rec in inner["admitted_records"]:
            self.assertLessEqual(utc(rec["available"]), cutoff_dt)

        # Step 2: Add delayed observation(s) to the store
        c = copy.deepcopy(CASE)
        c["observations"].append({
            "id": "AIS-DELAYED-3",
            "root": "transponder-A",
            "via": "broker-3",
            "site": "DEMO",
            "subject": "vessel-A",
            "zone": "approach-A",
            "kind": "reported",
            "position": "inside",
            "captured": "2026-11-06T14:05:01Z",
            "available": "2026-11-06T14:05:45Z",
            "permitted": True,
        })

        # Step 3: Reopen at the first cutoff (GET /cases/{id}?as_of=EARLY)
        reopened_bundle = export_bundle(c, EARLY)

        # Step 4: The exported historical evidence, verdict, and bundle hash must match identically
        self.assertEqual(reopened_bundle["evidence_bundle_sha256"], bundle_early["evidence_bundle_sha256"])
        self.assertEqual(reopened_bundle["bundle"]["disposition"], inner["disposition"])
        self.assertEqual(reopened_bundle["bundle"]["admitted_record_ids"], inner["admitted_record_ids"])
        self.assertEqual(reopened_bundle, bundle_early)

    def test_export_bundle_advances_verdict_at_second_cutoff(self):
        """At second cutoff, delayed frame is admitted, advancing verdict to confirmed with a distinct hash."""
        bundle_early = export_bundle(CASE, EARLY)
        bundle_late = export_bundle(CASE, LATE)

        self.assertEqual(bundle_late["bundle"]["disposition"]["decision"], "confirmed")
        self.assertEqual(bundle_late["bundle"]["disposition"]["independent_origins"], 2)
        self.assertEqual(set(bundle_late["bundle"]["origin_groups"].keys()), {"transponder-A", "camera-7"})
        self.assertEqual(bundle_late["bundle"]["admitted_record_ids"], ["AIS-1", "AIS-2", "CAM-NEW"])
        self.assertNotEqual(bundle_late["evidence_bundle_sha256"], bundle_early["evidence_bundle_sha256"])

        # Invariant: zero leakage at second cutoff
        cutoff_dt = utc(LATE)
        for rec in bundle_late["bundle"]["admitted_records"]:
            self.assertLessEqual(utc(rec["available"]), cutoff_dt)

    def test_dynamic_spatial_uncertainty_boundary_intersection(self):
        """Blueprint: A boundary intersecting a position's uncertainty region yields an unresolved spatial relation."""
        c = copy.deepcopy(CASE)
        # Approach zone polygon in local port coordinates
        c["zone_polygon"] = [
            (4.390, 51.240),
            (4.410, 51.240),
            (4.410, 51.250),
            (4.390, 51.250),
        ]

        # Case 1: Point deep inside with small error bound (10m) -> admitted inside
        c["observations"][0].pop("position", None)
        c["observations"][0]["geometry"] = {"type": "Point", "coordinates": [4.400, 51.245]}
        c["observations"][0]["error_bound_meters"] = 10.0

        res1 = evaluate(c, EARLY)
        self.assertIn("AIS-1", res1["source_records"]["transponder-A"]["inside"])

        # Case 2: Point near boundary where error bound (300m) intersects the perimeter -> unresolved
        c["observations"][0]["geometry"] = {"type": "Point", "coordinates": [4.3905, 51.245]}  # ~35m from west boundary
        c["observations"][0]["error_bound_meters"] = 100.0  # 100m error radius intersects 35m boundary

        res2 = evaluate(c, EARLY)
        self.assertIn("AIS-1", res2["excluded_records"])
        self.assertIn("intersects zone boundary", res2["excluded_records"]["AIS-1"])



if __name__ == "__main__":
    unittest.main()
