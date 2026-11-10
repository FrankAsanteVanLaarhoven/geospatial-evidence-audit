import copy
import json
import unittest
from pathlib import Path
from replay import comparison, digest, replay_at

DATA = json.loads(Path(__file__).with_name("usgs_snapshots.json").read_text(encoding="utf-8"))
EARLY, LATE = DATA["snapshots"]
FIRST = EARLY["feed_generated_utc"]
LAST = LATE["feed_generated_utc"]
EVENT = "ci41359359"


class PublishedRevisionTests(unittest.TestCase):
    def test_real_early_and_late_versions_remain_distinct(self):
        a = replay_at(DATA["snapshots"], FIRST)[EVENT]["record"]
        b = replay_at(DATA["snapshots"], LAST)[EVENT]["record"]
        self.assertEqual((a["magnitude"], a["review_status"]), (0.43, "automatic"))
        self.assertEqual((b["magnitude"], b["review_status"]), (0.36, "reviewed"))

    def test_only_one_of_the_six_shared_ids_changed(self):
        result = comparison(DATA)
        self.assertEqual(result["matched_event_count"], 6)
        self.assertEqual([c["event_id"] for c in result["revised_events"]], [EVENT])

    def test_archive_event_time_does_not_make_a_record_available_early(self):
        self.assertEqual(replay_at(DATA["snapshots"], "2026-11-06T18:45:00Z"), {})

    def test_revision_time_does_not_publish_the_later_snapshot_early(self):
        state = replay_at(DATA["snapshots"], "2026-11-06T21:00:00Z")
        self.assertEqual(state[EVENT]["record"]["magnitude"], 0.43)

    def test_reordered_and_repeated_inputs_have_identical_state(self):
        reordered = copy.deepcopy([LATE, EARLY, EARLY])
        for s in reordered:
            s["records"].reverse()
        self.assertEqual(digest(replay_at(reordered, LAST)), digest(replay_at([EARLY, LATE], LAST)))

    def test_older_revision_delivered_late_cannot_regress_state(self):
        delayed = copy.deepcopy(EARLY)
        delayed["feed_generated_utc"] = "2026-11-06T22:50:00Z"
        cutoff = delayed["feed_generated_utc"]
        self.assertEqual(replay_at([LATE, delayed], cutoff)[EVENT]["record"]["magnitude"], 0.36)

    def test_future_conflict_has_no_effect_on_an_earlier_query(self):
        bad = copy.deepcopy(EARLY)
        bad["feed_generated_utc"] = LAST
        bad["records"][0]["magnitude"] = 99
        self.assertEqual(replay_at([EARLY, bad], FIRST), replay_at([EARLY], FIRST))
        with self.assertRaisesRegex(ValueError, "Conflicting payloads"):
            replay_at([EARLY, bad], LAST)

    def test_an_absent_id_in_a_windowed_feed_is_not_a_deletion(self):
        empty = dict(LATE, records=[])
        self.assertEqual(replay_at([EARLY, empty], LAST), replay_at([EARLY], FIRST))

    def test_repeated_upstream_records_retain_their_first_seen_release(self):
        other = EARLY["records"][0]["event_id"]
        state = replay_at([EARLY, LATE], LAST)
        self.assertEqual(state[other]["first_release_in_fixture_with_this_revision"], FIRST)
        self.assertEqual(state[EVENT]["first_release_in_fixture_with_this_revision"], LAST)

    def test_timezone_is_required_and_equivalent_instants_match(self):
        with self.assertRaises(ValueError):
            replay_at([EARLY], "2026-11-06T18:51:30")
        self.assertEqual(replay_at([EARLY], FIRST), replay_at([EARLY], "2026-11-06T19:51:30+01:00"))


if __name__ == "__main__":
    unittest.main()
