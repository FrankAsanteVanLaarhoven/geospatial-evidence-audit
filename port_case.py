#!/usr/bin/env python3
"""Evaluate and export synthetic, labelled zone-occupancy cases from admitted records only.

Incorporates spatial uncertainty and boundary intersection per platform blueprint:
'A boundary intersecting a position's uncertainty region yields an unresolved spatial relation.'
"""
import argparse
import copy
from datetime import timedelta
import json
from pathlib import Path
from replay import digest, utc
from spatial_uncertainty import evaluate_spatial_relation


def evaluate(case, cutoff):
    target = utc(case["target"])
    available_by = utc(cutoff)
    tolerance = case["tolerance_seconds"]
    if tolerance < 0 or available_by < target:
        raise ValueError("Use a nonnegative tolerance and a decision cutoff at or after target")
    scope = ("site", "subject", "zone")
    roots = {}
    excluded = {}
    for row in sorted(case["observations"], key=lambda entry: entry["id"]):
        if not row.get("permitted") or any(row.get(key) != case[key] for key in scope):
            continue
        admitted = utc(row["available"])
        if admitted > available_by:
            continue
        row_id = row["id"]
        if not row.get("captured"):
            excluded[row_id] = "capture time unknown"
            continue
        captured = utc(row["captured"])
        if captured > admitted or abs((captured - target).total_seconds()) > tolerance:
            excluded[row_id] = "capture time outside the admissible window"
            continue
        root = row.get("root")
        if not root or row.get("kind") not in {"reported", "observed"}:
            excluded[row_id] = "independent observation origin unavailable"
            continue

        # Position evaluation: direct or derived via spatial uncertainty
        position = row.get("position")
        if not position and "geometry" in row and "zone_polygon" in case:
            coords = row["geometry"].get("coordinates", [])
            error_m = row.get("error_bound_meters", 0.0)
            poly = case["zone_polygon"]
            spatial_res = evaluate_spatial_relation(coords[0], coords[1], error_m, poly)
            if spatial_res["relation"] == "unresolved":
                excluded[row_id] = "uncertainty region intersects zone boundary"
                continue
            position = spatial_res["relation"]

        if position not in {"inside", "outside"}:
            excluded[row_id] = "position undetermined"
            continue
        roots.setdefault(root, {}).setdefault(position, []).append(row_id)

    labels = {position for fixes in roots.values() for position in fixes}
    if len(labels) > 1:
        decision, reason = "insufficient evidence", "eligible observations conflict"
    elif len(roots) < 2:
        decision, reason = "insufficient evidence", "fewer than two independent origins"
    else:
        decision = "confirmed" if labels == {"inside"} else "contradicted"
        reason = "two or more distinct origins agree on zone membership"
    return {
        "cutoff": cutoff, "target": case["target"], "decision": decision,
        "reason": reason, "independent_origins": len(roots),
        "source_records": roots, "excluded_records": excluded,
    }


def export_bundle(case, cutoff):
    """Export a versioned evidence bundle with canonical SHA-256 digest and W3C PROV-O linkage."""
    eval_result = evaluate(case, cutoff)
    target_dt = utc(case["target"])
    cutoff_dt = utc(cutoff)
    tol_seconds = case["tolerance_seconds"]
    tol = timedelta(seconds=tol_seconds)
    window_start = (target_dt - tol).isoformat().replace("+00:00", "Z")
    window_end = (target_dt + tol).isoformat().replace("+00:00", "Z")

    scope = ("site", "subject", "zone")
    case_id = case.get("case_id", f"{case['subject']}@{case['zone']}:{case['target']}")
    policy_version = case.get("policy_version", "2026.11-two-origin-consensus")

    admitted_records = []
    for row in sorted(case["observations"], key=lambda entry: entry["id"]):
        if not row.get("permitted") or any(row.get(key) != case[key] for key in scope):
            continue
        admitted = utc(row["available"])
        if admitted > cutoff_dt:
            continue
        if not row.get("captured"):
            continue
        captured = utc(row["captured"])
        if captured > admitted or abs((captured - target_dt).total_seconds()) > tol_seconds:
            continue
        root = row.get("root")
        if not root or row.get("kind") not in {"reported", "observed"}:
            continue

        position = row.get("position")
        if not position and "geometry" in row and "zone_polygon" in case:
            coords = row["geometry"].get("coordinates", [])
            error_m = row.get("error_bound_meters", 0.0)
            poly = case["zone_polygon"]
            spatial_res = evaluate_spatial_relation(coords[0], coords[1], error_m, poly)
            if spatial_res["relation"] == "unresolved":
                continue
            position = spatial_res["relation"]

        if position not in {"inside", "outside"}:
            continue

        # Zero-leakage assertion: observation cannot be first available after decision cutoff
        if admitted > cutoff_dt:
            raise ValueError(f"Information leakage: record {row['id']} available at {admitted} after cutoff {cutoff_dt}")

        rec = copy.deepcopy(row)
        rec["record_sha256"] = digest(row)
        admitted_records.append(rec)

    admitted_ids = [r["id"] for r in admitted_records]

    bundle_body = {
        "case_id": case_id,
        "policy_version": policy_version,
        "site": case["site"],
        "subject": case["subject"],
        "zone": case["zone"],
        "target_time": case["target"],
        "decision_cutoff": cutoff,
        "tolerance_seconds": tol_seconds,
        "time_window": {
            "start": window_start,
            "end": window_end,
        },
        "disposition": {
            "decision": eval_result["decision"],
            "reason": eval_result["reason"],
            "independent_origins": eval_result["independent_origins"],
        },
        "origin_groups": eval_result["source_records"],
        "admitted_record_ids": admitted_ids,
        "admitted_records": admitted_records,
        "excluded_records": eval_result["excluded_records"],
        "prov": {
            "wasDerivedFrom": admitted_ids,
            "generatedAtCutoff": cutoff,
            "targetEntity": f"urn:case:{case_id}",
        },
    }
    return {
        "evidence_bundle_sha256": digest(bundle_body),
        "bundle": bundle_body,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("port_case.json"))
    parser.add_argument("--at", "--as-of", dest="cutoff", metavar="ISO_TIME", help="Decision cutoff time in UTC")
    parser.add_argument("--export", action="store_true", help="Export versioned evidence bundle with SHA-256 digest")
    args = parser.parse_args()
    try:
        case = json.loads(args.fixture.read_text(encoding="utf-8"))
        cutoffs = [args.cutoff] if args.cutoff else case["cutoffs"]
        if args.export:
            results = [export_bundle(case, at) for at in cutoffs]
            output = results[0] if args.cutoff else results
        else:
            output = [evaluate(case, at) for at in cutoffs]
    except (OSError, ValueError, TypeError, KeyError) as err:
        parser.error(str(err))
    print(json.dumps(output, sort_keys=True, indent=2))
