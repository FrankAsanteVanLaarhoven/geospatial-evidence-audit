#!/usr/bin/env python3
"""Antwerp AIS Trajectory Replay & Reconstruction Engine (S16, S17).

Follows the blueprint protocol for trip-level evaluation:
- Simulates replay of sparse observation streams with synthetic gaps.
- Computes canonical state hashes invariant to arrival order and duplication.
- Flags track breaks when observation gap exceeds threshold.
- Computes horizontal error (great-circle meters) against held-out complete observations.
"""
from datetime import datetime, timezone
import math
from replay import digest, utc


def haversine_meters(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points on WGS84 sphere in meters."""
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def replay_trip_stream(observations, cutoff_time_utc, gap_threshold_seconds=600):
    """Replay an observation stream up to cutoff_time_utc.

    Returns the canonical latest state for each vessel, handling duplicates,
    out-of-order deliveries, and detecting observation gaps.
    """
    cutoff_dt = utc(cutoff_time_utc)
    vessel_states = {}
    known_event_hashes = set()

    # Sort strictly by arrival/availability time then record ID for deterministic intake
    admissible_stream = []
    for obs in observations:
        available_dt = utc(obs["available_utc"])
        if available_dt <= cutoff_dt:
            admissible_stream.append(obs)

    admissible_stream.sort(key=lambda x: (utc(x["available_utc"]), x["id"]))

    for obs in admissible_stream:
        obs_hash = digest(obs)
        if obs_hash in known_event_hashes:
            # Duplicate receipt - skip without corrupting state
            continue
        known_event_hashes.add(obs_hash)

        vessel_id = obs["vessel_id"]
        obs_time = utc(obs["observed_utc"])

        if vessel_id not in vessel_states:
            vessel_states[vessel_id] = {
                "vessel_id": vessel_id,
                "latest_fix": obs,
                "latest_observed_utc": obs["observed_utc"],
                "fix_count": 1,
                "gap_detected": False,
                "track_history": [obs["id"]],
            }
        else:
            prev = vessel_states[vessel_id]
            prev_time = utc(prev["latest_observed_utc"])

            # Detect gap if time difference exceeds threshold
            interval = (obs_time - prev_time).total_seconds()
            gap = interval > gap_threshold_seconds

            # Only update latest fix if observation is strictly newer chronologically
            if obs_time >= prev_time:
                prev["latest_fix"] = obs
                prev["latest_observed_utc"] = obs["observed_utc"]
                prev["gap_detected"] = gap
            prev["fix_count"] += 1
            prev["track_history"].append(obs["id"])

    # Compute canonical state digest across sorted vessel states
    state_payload = {v_id: vessel_states[v_id] for v_id in sorted(vessel_states.keys())}
    state_hash = digest(state_payload)

    return {
        "cutoff_utc": cutoff_time_utc,
        "active_vessel_count": len(vessel_states),
        "vessels": vessel_states,
        "canonical_state_sha256": state_hash,
    }


def evaluate_interpolation_error(last_fix, held_out_truth, next_fix=None, method="last_position"):
    """Evaluate estimation error against held-out complete reference position.

    method='last_position': Online baseline (zero future leakage).
    method='linear': Offline reconstruction using bounding fixes.
    """
    truth_lat, truth_lon = held_out_truth["lat"], held_out_truth["lon"]
    t_target = utc(held_out_truth["observed_utc"])
    t_prev = utc(last_fix["observed_utc"])

    if method == "last_position":
        est_lat, est_lon = last_fix["lat"], last_fix["lon"]
    elif method == "linear" and next_fix is not None:
        t_next = utc(next_fix["observed_utc"])
        total_dt = (t_next - t_prev).total_seconds()
        if total_dt <= 0:
            est_lat, est_lon = last_fix["lat"], last_fix["lon"]
        else:
            fraction = (t_target - t_prev).total_seconds() / total_dt
            fraction = max(0.0, min(1.0, fraction))
            est_lat = last_fix["lat"] + fraction * (next_fix["lat"] - last_fix["lat"])
            est_lon = last_fix["lon"] + fraction * (next_fix["lon"] - last_fix["lon"])
    else:
        raise ValueError(f"Unsupported method '{method}' or missing next_fix")

    err_meters = haversine_meters(est_lat, est_lon, truth_lat, truth_lon)
    return {
        "method": method,
        "estimated_position": [est_lat, est_lon],
        "truth_position": [truth_lat, truth_lon],
        "error_meters": round(err_meters, 2),
    }

