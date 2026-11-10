#!/usr/bin/env python3
"""Sovereign Geospatial Evidence Audit Server.

Runs as a standalone microservice on port 8090 providing cryptographic
adjudication, deterministic trajectory replay, and benchmark execution.
"""
import http.server
import json
import socketserver
import sys
import time

from benchmark_throughput import simulate_stream_latency_benchmark
from benchmark_risk_coverage import run_all_evaluations

PORT = 8090


class AuditHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

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
                    "/audit/status"
                ]
            })
        elif self.path == "/audit/benchmark/throughput":
            report = simulate_stream_latency_benchmark()
            self._send_json(200, report)
        elif self.path == "/audit/benchmark/risk":
            report = run_all_evaluations(episodes_count=100)
            self._send_json(200, report)
        elif self.path == "/audit/status":
            self._send_json(200, {
                "engine": "Ed25519 DSSE In-Toto Sealer",
                "spatial_uncertainty": "3D Covariance Matrix Propagator",
                "postgis_indexing": "ST_DWithin sub-meter trajectory lookup",
                "status": "READY"
            })
        else:
            self._send_json(404, {"error": "Endpoint not found", "path": self.path})

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[AuditServer :8090] {self.address_string()} - {format % args}\n")


def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), AuditHTTPRequestHandler) as httpd:
        print(f"[Geospatial Evidence Audit Server] Listening on http://127.0.0.1:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run()
