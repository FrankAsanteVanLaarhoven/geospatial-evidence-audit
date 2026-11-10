#!/usr/bin/env python3
"""Sovereign Geospatial Evidence Audit Server.

Runs as a standalone microservice on port 8090 providing cryptographic
adjudication, deterministic trajectory replay, and benchmark execution.
Implements the Forensic Research Audit & Implementation Blueprint (10 Nov 2026).
"""
import http.server
import json
import socketserver
import sys
import time

from benchmark_throughput import simulate_stream_latency_benchmark
from benchmark_risk_coverage import run_sota_gate_evaluation
from space_native_evidence_engine import (
    CanonicalEvidenceContract,
    DSSESealer,
    MerkleTransparencyTree,
    OrbitalCLExpEngine,
    run_space_native_benchmarks,
)

PORT = 8090

# Persistent singletons for audit service lifetime
SHARED_FL_ENGINE = OrbitalCLExpEngine()
SHARED_MERKLE_TREE = MerkleTransparencyTree()


class AuditHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/health", "/healthz", "/"):
            self._send_json(200, {
                "service": "geospatial-evidence-audit",
                "status": "HEALTHY",
                "port": PORT,
                "timestamp": time.time(),
                "endpoints": [
                    "/health",
                    "/audit/benchmark/throughput",
                    "/audit/benchmark/risk",
                    "/audit/space-native/benchmarks",
                    "/audit/space-native/overview",
                    "/audit/status"
                ]
            })
        elif self.path == "/audit/benchmark/throughput":
            report = simulate_stream_latency_benchmark()
            self._send_json(200, report)
        elif self.path == "/audit/benchmark/risk":
            report = run_sota_gate_evaluation(episodes_count=100)
            self._send_json(200, report)
        elif self.path == "/audit/space-native/benchmarks":
            report = run_space_native_benchmarks()
            self._send_json(200, report)
        elif self.path == "/audit/space-native/overview":
            self._send_json(200, {
                "title": "Space-Native AI: Evidence-Aware Federated Intelligence",
                "review_date": "10 November 2026",
                "status": "Research design approved for controlled benchmarking; production deployment on HOLD",
                "four_testable_domains": [
                    {"name": "AIS Replay", "description": "Historic Antwerp trajectories (DOI 10.17632/smb56stcdx.1); Ingest receipts, no native sensor signatures."},
                    {"name": "Sentinel-1 SAR", "description": "Historical SAR feasibility; paired only if spatial/temporal tolerance is verified."},
                    {"name": "Orbital Emulator", "description": "Contact windows and outages; not spacecraft telemetry."},
                    {"name": "Controlled Adversarial Injections", "description": "Tamper, replay, key revocation, clock skew, poison updates."}
                ],
                "origin_properties": ["evidence_availability", "source_authenticity", "time_confidence", "sensor_reliability"]
            })
        elif self.path == "/audit/space-native/fl-round":
            round_res = SHARED_FL_ENGINE.run_federated_round(baseline="proposed_evidence_gated")
            self._send_json(200, round_res)
        elif self.path.startswith("/audit/space-native/passport"):
            sample_event = CanonicalEvidenceContract.create_event(
                source_id="vessel-ais-antwerp-9412",
                observed_at="2024-01-14T08:30:00Z",
                geometry={"type": "Point", "coordinates": [4.3180, 51.2750]}
            )
            leaf_hash = SHARED_MERKLE_TREE.add_leaf(json.dumps(sample_event).encode())
            proof = SHARED_MERKLE_TREE.get_inclusion_proof(len(SHARED_MERKLE_TREE.leaves) - 1)
            passport = {
                "passport_id": f"pass-{leaf_hash[:16]}",
                "alert_id": "alert-antwerp-speed-01",
                "event": sample_event,
                "disposition": "ACCEPTED",
                "human_reviewer": "officer-operator-08",
                "merkle_inclusion_proof": proof
            }
            self._send_json(200, passport)
        elif self.path == "/audit/status":
            self._send_json(200, {
                "engine": "Ed25519 DSSE In-Toto Sealer",
                "spatial_uncertainty": "3D Covariance Matrix Propagator",
                "postgis_indexing": "ST_DWithin sub-meter trajectory lookup",
                "space_native_fl": "Active LEO Constellation Contact-Aware Async Engine",
                "status": "READY"
            })
        else:
            self._send_json(404, {"error": "Endpoint not found", "path": self.path})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            req_data = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception:
            req_data = {}

        if self.path == "/audit/space-native/fl-round":
            baseline = req_data.get("baseline", "proposed_evidence_gated")
            round_res = SHARED_FL_ENGINE.run_federated_round(baseline=baseline)
            self._send_json(200, round_res)
        elif self.path == "/audit/space-native/ingest":
            source_id = req_data.get("source_id", "sensor-edge-01")
            observed_at = req_data.get("observed_at", "2024-01-14T10:00:00Z")
            geometry = req_data.get("geometry", {"type": "Point", "coordinates": [4.3180, 51.2750]})
            has_sig = req_data.get("has_native_signature", False)

            event = CanonicalEvidenceContract.create_event(
                source_id=source_id,
                observed_at=observed_at,
                geometry=geometry,
                has_native_signature=has_sig
            )
            envelope = DSSESealer.sign_payload(event)
            self._send_json(200, {"event": event, "envelope": envelope})
        else:
            self._send_json(404, {"error": "POST endpoint not found", "path": self.path})

    def log_message(self, format, *args):
        sys.stderr.write(f"[AuditServer :8090] {self.address_string()} - {format % args}\n")


def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), AuditHTTPRequestHandler) as httpd:
        print(f"[Geospatial Evidence Audit Server] Listening on http://127.0.0.1:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run()
