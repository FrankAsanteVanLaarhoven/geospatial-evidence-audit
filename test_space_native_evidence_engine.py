#!/usr/bin/env python3
"""Unit tests for Space-Native AI Evidence Engine and Benchmark Suite."""
import unittest
from space_native_evidence_engine import (
    CanonicalEvidenceContract,
    MerkleTransparencyTree,
    DSSESealer,
    TangentPlaneTracker,
    OrbitalCLExpEngine,
    run_space_native_benchmarks,
)


class TestSpaceNativeEvidenceEngine(unittest.TestCase):
    def test_canonical_contract_4_properties(self):
        event = CanonicalEvidenceContract.create_event(
            source_id="vessel-01",
            observed_at="2024-01-01T00:00:00Z",
            geometry={"type": "Point", "coordinates": [4.3, 51.2]},
            has_native_signature=False
        )
        # Check strict separation of the 4 properties
        self.assertTrue(event["evidence_availability"])
        self.assertEqual(event["source_authenticity"], "ingest_receipt")
        self.assertEqual(event["time_confidence"], "source_reported")
        self.assertAlmostEqual(event["sensor_reliability"], 0.85)
        self.assertIn("sha256:", event["artifact_digest"])

    def test_dsse_sealer_and_verification(self):
        event = CanonicalEvidenceContract.create_event(
            source_id="sat-01",
            observed_at="2024-01-01T00:00:00Z",
            geometry={"type": "Point", "coordinates": [4.3, 51.2]},
            has_native_signature=True,
            enrolled_key_id="key-01"
        )
        envelope = DSSESealer.sign_payload(event, key_id="key-01")
        valid, reason = DSSESealer.verify_envelope(envelope)
        self.assertTrue(valid)
        self.assertEqual(reason, "VALID_WITNESSED")

        # Test key revocation detection
        valid_revoked, reason_revoked = DSSESealer.verify_envelope(envelope, revoked_keys={"key-01"})
        self.assertFalse(valid_revoked)
        self.assertIn("KEY_REVOKED", reason_revoked)

        # Test payload tampering detection
        envelope_tampered = dict(envelope)
        envelope_tampered["payload"]["observed_at"] = "2025-01-01T00:00:00Z"
        valid_tampered, reason_tampered = DSSESealer.verify_envelope(envelope_tampered)
        self.assertFalse(valid_tampered)

    def test_merkle_transparency_tree(self):
        tree = MerkleTransparencyTree()
        h1 = tree.add_leaf(b"leaf1")
        h2 = tree.add_leaf(b"leaf2")
        h3 = tree.add_leaf(b"leaf3")
        root = tree.get_root()
        self.assertTrue(len(root) == 64)
        proof = tree.get_inclusion_proof(1)
        self.assertEqual(proof["leaf_index"], 1)
        self.assertEqual(proof["root"], root)

    def test_tangent_plane_tracker(self):
        tracker = TangentPlaneTracker()
        dx, dy = tracker.wgs84_to_local_meters(51.2850, 4.3280)
        lat_rec, lon_rec = tracker.local_meters_to_wgs84(dx, dy)
        self.assertAlmostEqual(lat_rec, 51.2850, places=5)
        self.assertAlmostEqual(lon_rec, 4.3280, places=5)

        state = tracker.propagate_state(0.0, 0.0, 5.0, 2.0, 300)
        self.assertGreater(state["sigma_x_m"], 0.0)
        self.assertGreater(state["sigma_y_m"], 0.0)

    def test_orbital_federated_learning(self):
        engine = OrbitalCLExpEngine()
        res = engine.run_federated_round(baseline="proposed_evidence_gated")
        self.assertEqual(res["round"], 1)
        self.assertGreater(res["bandwidth_saving_pct"], 50.0)
        self.assertIn("merkle_root", res)

    def test_full_benchmark_suite_kpis(self):
        bench = run_space_native_benchmarks()
        self.assertEqual(bench["E0_evidence_reproducibility"]["status"], "PASS")
        self.assertEqual(bench["E1_trajectory_reconstruction"]["status"], "PASS")
        self.assertEqual(bench["E2_evidence_chain_integrity"]["status"], "PASS")
        self.assertEqual(bench["E3_intermittent_federation"]["status"], "PASS")
        self.assertEqual(bench["E4_proposed_coupling_ablation"]["status"], "PASS")
        self.assertEqual(bench["E5_human_forensic_replay"]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()

