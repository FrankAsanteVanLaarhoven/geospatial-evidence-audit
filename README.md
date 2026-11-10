# Geospatial Evidence Audit & Cryptographic Sealing Engine

Enterprise cryptographic verification, deterministic replay, and multi-sensor validation engine for sovereign geospatial intelligence.

## Core Capabilities
- **Ed25519 DSSE Attestation Contracts**: In-toto compliant deterministic envelope sealing with canonical JSON serialization.
- **Multi-Sensor Spatial Uncertainty**: 3D covariance matrix propagation, error ellipse derivation, and kinematic consistency checks.
- **Port of Antwerp Maritime Replay**: Historical and real-time AIS trajectory reconstruction with kinematic anomaly alarms.
- **PostGIS Integration**: Spatial bounding indexing, ST_DWithin trajectory correlation, and sub-meter GIS queries.
- **Zero-Trust Sealing**: SHA-256 Merkle root verification ensuring non-repudiation across air-gapped forensic audits.

## Test Suite Execution
```bash
python3 -m unittest discover -s . -p "test_*.py"
```

## Throughput & Risk Coverage Benchmarking
```bash
python3 benchmark_throughput.py
python3 benchmark_risk_coverage.py
```
