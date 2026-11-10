#!/usr/bin/env python3
"""Record contract and freshness evaluation engine following the SpatialForge 3D specification.

Enforces:
1. Strict schema compliance against proposed_record_contract.
2. Deterministic freshness evaluation with ZERO false "current" labels on adversarial inputs.
"""
from datetime import datetime, timedelta, timezone
from replay import utc


VALID_KINDS = {
    "reported_event",
    "reported_position",
    "camera_still",
    "camera_stream",
    "propagated_position",
    "derived_area",
    "reference_geometry",
}

VALID_DELIVERY_MODES = {
    "current_feed",
    "snapshot_replay",
}

VALID_FRESHNESS_STATUSES = {
    "current_within_source_policy",
    "stale",
    "unknown",
    "historical",
    "offline",
}

# Default freshness tolerances by layer
DEFAULT_FRESHNESS_POLICIES = {
    "vessels": {"max_age_seconds": 300, "allow_prediction": False},
    "aircraft": {"max_age_seconds": 60, "allow_prediction": False},
    "public_cameras": {"max_age_seconds": 900, "allow_prediction": False},
    "satellites": {"max_element_age_seconds": 86400 * 3, "allow_prediction": True},
    "earthquakes": {"max_age_seconds": 86400 * 7, "allow_prediction": False},
    "gnss_interference": {"max_age_seconds": 86400, "window_seconds": 86400, "min_support_count": 5},
}


def validate_record_contract(record):
    """Validate that a record conforms to the SpatialForge proposed record contract."""
    errors = []

    # Identity
    for field in ("source_id", "source_record_id", "layer"):
        if not record.get(field):
            errors.append(f"Missing required identity field: {field}")

    # Enums
    kind = record.get("kind")
    if kind not in VALID_KINDS:
        errors.append(f"Invalid kind '{kind}'; must be one of {sorted(VALID_KINDS)}")

    delivery_mode = record.get("delivery_mode")
    if delivery_mode not in VALID_DELIVERY_MODES:
        errors.append(f"Invalid delivery_mode '{delivery_mode}'; must be one of {sorted(VALID_DELIVERY_MODES)}")

    freshness = record.get("freshness_status")
    if freshness not in VALID_FRESHNESS_STATUSES:
        errors.append(f"Invalid freshness_status '{freshness}'; must be one of {sorted(VALID_FRESHNESS_STATUSES)}")

    # Time fields: if supplied, must be ISO 8601 strings with timezone
    for time_key in ("source_time_or_null", "source_updated_at_or_null", "retrieved_at_utc"):
        val = record.get(time_key)
        if val is not None:
            try:
                utc(val)
            except Exception as err:
                errors.append(f"Invalid timestamp in '{time_key}': {err}")

    # Retrieved at is mandatory
    if not record.get("retrieved_at_utc"):
        errors.append("Missing required field: retrieved_at_utc")

    # Rights
    if not record.get("rights_profile"):
        errors.append("Missing required field: rights_profile")

    return errors


def evaluate_freshness(record, evaluation_time_utc, policy=None):
    """Determine the true freshness status of a record at a given evaluation time.

    Rule: Never assign 'current_within_source_policy' if there is staleness,
    clock ambiguity, prediction, historical replay, or offline status.
    """
    eval_dt = utc(evaluation_time_utc)
    layer = record.get("layer", "")
    policy = policy or DEFAULT_FRESHNESS_POLICIES.get(layer, {"max_age_seconds": 300, "allow_prediction": False})

    # 1. Delivery mode check: Replay modes are historical by definition
    if record.get("delivery_mode") == "snapshot_replay" or record.get("is_historical_replay"):
        return "historical", "delivery mode is snapshot/historical replay"

    # 2. Offline / retracted check
    if record.get("is_offline") or record.get("is_retracted"):
        return "offline", "provider is offline or record is retracted"

    # 3. Source permission check
    if record.get("permitted") is False:
        return "offline", "data classification or tenant grant does not permit this view"

    # 4. Source time availability
    source_time_str = record.get("source_time_or_null")
    if not source_time_str:
        return "unknown", "source capture time is null or unspecified"

    try:
        source_dt = utc(source_time_str)
    except Exception:
        return "unknown", "source timestamp cannot be parsed with explicit UTC timezone"

    # 5. Future clock skew check (source time cannot be ahead of evaluation time + tolerance)
    clock_skew_tolerance = timedelta(seconds=policy.get("clock_skew_tolerance_seconds", 5))
    if source_dt > eval_dt + clock_skew_tolerance:
        return "unknown", "source timestamp is in the future relative to evaluation clock"

    # 6. Propagation / prediction check
    kind = record.get("kind")
    if kind == "propagated_position":
        if not policy.get("allow_prediction", False):
            return "historical", "predicted or propagated position cannot qualify as current observation"
        epoch_str = record.get("orbital_element_epoch_utc")
        if not epoch_str:
            return "unknown", "orbital element epoch missing"
        epoch_dt = utc(epoch_str)
        max_element_age = timedelta(seconds=policy.get("max_element_age_seconds", 86400 * 3))
        if abs((eval_dt - epoch_dt).total_seconds()) > max_element_age.total_seconds():
            return "stale", "orbital element epoch exceeds validity threshold"

    # 7. Aggregated interference layer check: minimum distinct support
    if layer == "gnss_interference":
        support = record.get("support_aircraft_count", 0)
        min_support = policy.get("min_support_count", 5)
        if support < min_support:
            return "unknown", f"support count ({support}) below minimum threshold ({min_support})"

    # 8. Restamped receipt / staleness check:
    max_age = timedelta(seconds=policy.get("max_age_seconds", 300))
    age = eval_dt - source_dt
    if age < timedelta(0):
        age = timedelta(0)

    if age > max_age:
        return "stale", f"observation age ({int(age.total_seconds())}s) exceeds policy limit ({int(max_age.total_seconds())}s)"

    return "current_within_source_policy", "observation is fresh, permitted, and within policy thresholds"
