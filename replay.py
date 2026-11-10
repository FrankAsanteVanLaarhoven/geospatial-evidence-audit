#!/usr/bin/env python3
"""Replay two public USGS feed snapshots by their publication time.

Python 3.9+, standard library only. Input records in this fixture are USGS
upserts. A windowed feed omitting a record does not retract that event.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def utc(value):
    if not isinstance(value, str):
        raise ValueError("A timestamp must be an ISO 8601 string with a time zone")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    value_dt = datetime.fromisoformat(text)
    if value_dt.tzinfo is None:
        raise ValueError("An explicit UTC offset is required")
    return value_dt.astimezone(timezone.utc)


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def replay_at(snapshots, cutoff):
    """Return latest provider revisions that were present in an eligible release."""
    cutoff_time = utc(cutoff)
    state = {}
    known_versions = {}
    releases = sorted(snapshots, key=lambda s: (utc(s["feed_generated_utc"]), s["feed_url"]))
    for release in releases:
        publication_time = utc(release["feed_generated_utc"])
        if publication_time > cutoff_time:
            break
        for record in release["records"]:
            event_id = record["event_id"]
            revised = utc(record["revision_time"])
            if not event_id or not utc(record["event_time"]) <= revised <= publication_time:
                raise ValueError("Invalid event ID or chronology in an eligible release")
            version_key = (event_id, revised)
            fingerprint = digest(record)
            if version_key in known_versions:
                if known_versions[version_key] != fingerprint:
                    raise ValueError(f"Conflicting payloads for event {event_id} at {revised.isoformat()}")
                continue
            known_versions[version_key] = fingerprint
            if event_id in state and revised < utc(state[event_id]["record"]["revision_time"]):
                continue
            state[event_id] = {
                "record": record,
                "record_sha256": fingerprint,
                "first_release_in_fixture_with_this_revision": release["feed_generated_utc"],
                "feed_url": release["feed_url"],
            }
    return state


def comparison(fixture):
    releases = fixture["snapshots"]
    clocks = sorted({r["feed_generated_utc"] for r in releases}, key=utc)
    if len(clocks) < 2:
        raise ValueError("The comparison requires two distinct publication times")
    early = replay_at(releases, clocks[0])
    late = replay_at(releases, clocks[-1])
    shared_ids = sorted(early.keys() & late.keys())
    changes = []
    for key in shared_ids:
        before = early[key]["record"]
        after = late[key]["record"]
        changed = {k: [before[k], after[k]] for k in before if before[k] != after[k]}
        if changed:
            changes.append({"event_id": key, "changed_fields": changed})
    return {
        "scope": fixture["record_selection"],
        "cutoff_basis": fixture["time_basis"],
        "first_cutoff": clocks[0],
        "last_cutoff": clocks[-1],
        "matched_event_count": len(shared_ids),
        "revised_events": changes,
        "first_state_sha256": digest(early),
        "last_state_sha256": digest(late),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("usgs_snapshots.json"))
    parser.add_argument("--at", metavar="ISO_TIME", help="UTC release cutoff, inclusive")
    parser.add_argument("--event", metavar="USGS_ID", help="select one event (requires --at)")
    args = parser.parse_args()
    if args.event and not args.at:
        parser.error("--event requires --at")
    try:
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        if args.at:
            state = replay_at(fixture["snapshots"], args.at)
            if args.event:
                result = {"cutoff": args.at, "visible": args.event in state,
                          "event": state.get(args.event)}
            else:
                result = {"cutoff": args.at, "state": state, "state_sha256": digest(state)}
        else:
            result = comparison(fixture)
    except (OSError, ValueError, KeyError, TypeError) as err:
        parser.error(str(err))
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
