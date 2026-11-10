#!/usr/bin/env python3
"""Active sensor selection and observation request generator (Denzler & Brown 2002, DOI 10.1109/34.982896).

Blueprint requirement:
'Rank authorised views by expected error reduction per second under a fixed cost and sightline constraint.
Compare with the nearest eligible camera. A later live view answers a new time window.'
'Evidence requests: After the operator pilot, let an authorised user request a fresh frame or read-only robot
observation through VectorLink. Carry site, purpose, expiry and device clock.'
"""
from datetime import datetime, timedelta, timezone
import math
from antwerp_replay import haversine_meters
from replay import digest, utc


def calculate_line_of_sight(sensor_coords, target_coords, occlusions=None):
    """Determine if a direct line-of-sight exists between sensor and target."""
    if not occlusions:
        return True, "Clear sightline"
    # Simple segment-bounding intersection check against declared occlusion zones
    for occ in occlusions:
        min_lon, min_lat, max_lon, max_lat = occ["bbox"]
        t_lon, t_lat = target_coords
        s_lon, s_lat = sensor_coords
        if min_lon <= (t_lon + s_lon) / 2.0 <= max_lon and min_lat <= (t_lat + s_lat) / 2.0 <= max_lat:
            return False, f"Sightline blocked by structure: {occ.get('name', 'terrain/crane')}"
    return True, "Clear sightline"


def rank_candidate_sensors(
    target_coords,
    current_uncertainty_meters,
    candidate_sensors,
    max_cost=100.0,
    occlusions=None
):
    """Rank candidate sensors by expected error reduction per second under cost & sightline constraints.

    Compares against the nearest eligible camera.
    """
    t_lon, t_lat = target_coords
    evaluated = []

    for s in candidate_sensors:
        if not s.get("permitted", True):
            continue

        cost = s.get("cost_units", 0.0)
        if cost > max_cost:
            continue

        s_lon, s_lat = s["coordinates"]
        dist_m = haversine_meters(s_lat, s_lon, t_lat, t_lon)

        # Check max sensor range
        max_range_m = s.get("max_range_meters", 2000.0)
        if dist_m > max_range_m:
            continue

        # Line of sight constraint
        has_sightline, sightline_reason = calculate_line_of_sight((s_lon, s_lat), (t_lon, t_lat), occlusions)
        if not has_sightline:
            continue

        # Acquisition time: mechanical slew time + network capture roundtrip
        slew_rate_deg_s = s.get("slew_rate_deg_per_sec", 60.0)
        bearing = math.degrees(math.atan2(t_lon - s_lon, t_lat - s_lat)) % 360
        current_heading = s.get("current_heading_deg", 0.0)
        angular_dist = abs((bearing - current_heading + 180) % 360 - 180)

        slew_time_s = angular_dist / slew_rate_deg_s
        network_latency_s = s.get("network_latency_seconds", 0.5)
        total_time_s = slew_time_s + network_latency_s

        # Expected error reduction: high-resolution sensor close to target yields high uncertainty reduction
        sensor_resolution_error_m = s.get("resolution_error_meters", 5.0) + (dist_m * 0.01)
        if sensor_resolution_error_m < current_uncertainty_meters:
            expected_error_reduction_m = current_uncertainty_meters - sensor_resolution_error_m
        else:
            expected_error_reduction_m = 0.0

        # Information utility per second (Denzler & Brown metric)
        utility_per_second = expected_error_reduction_m / total_time_s if total_time_s > 0 else 0.0

        evaluated.append({
            "sensor_id": s["sensor_id"],
            "type": s.get("type", "camera"),
            "distance_meters": round(dist_m, 1),
            "total_time_seconds": round(total_time_s, 2),
            "expected_error_reduction_meters": round(expected_error_reduction_m, 2),
            "utility_per_second": round(utility_per_second, 3),
            "cost_units": cost,
            "sightline": sightline_reason,
        })

    # Sort by utility per second descending
    evaluated.sort(key=lambda x: x["utility_per_second"], reverse=True)

    # Find the nearest eligible camera for comparison
    nearest_camera = min(evaluated, key=lambda x: x["distance_meters"]) if evaluated else None

    return {
        "ranked_sensors": evaluated,
        "recommended_sensor": evaluated[0] if evaluated else None,
        "nearest_eligible_camera": nearest_camera,
    }


def create_vectorlink_evidence_request(
    case_id,
    site,
    sensor_id,
    purpose,
    current_device_clock_utc,
    expiry_seconds=120
):
    """Generate an authorized VectorLink evidence request following platform contract."""
    clock_dt = utc(current_device_clock_utc)
    expiry_dt = clock_dt + timedelta(seconds=expiry_seconds)

    payload = {
        "protocol": "VectorLink/1.0",
        "case_id": case_id,
        "site": site,
        "target_sensor_id": sensor_id,
        "purpose": purpose,
        "device_clock": clock_dt.isoformat().replace("+00:00", "Z"),
        "expires_at": expiry_dt.isoformat().replace("+00:00", "Z"),
        "access_mode": "read_only_observation",
        "independent_execution_control": "asset_owner",
    }
    payload["request_digest_sha256"] = digest(payload)
    return payload

