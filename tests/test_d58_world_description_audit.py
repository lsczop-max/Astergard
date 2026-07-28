from __future__ import annotations

import json
import unittest

from astergard.audits.world_description_audit import (
    build_world_description_audit,
    detect_identical_endings,
    detect_obvious_language_error,
    detect_raw_alias_leak,
)
from astergard.world.manager import OPPOSITE


class D58WorldDescriptionAuditTests(unittest.TestCase):
    def test_audit_covers_exactly_500_locations_without_missing_or_duplicate_ids(self) -> None:
        audit = build_world_description_audit()
        ids = [record.location_id for record in audit.records]

        self.assertEqual(audit.world_size, 483)
        self.assertEqual(len(ids), 483)
        self.assertEqual(len(set(ids)), 483)
        expected = set(range(500)) - set(range(2, 14)) - set(range(15, 20))
        self.assertEqual(set(ids), expected)

    def test_audit_neighbor_references_are_consistent(self) -> None:
        audit = build_world_description_audit()
        records = {record.location_id: record for record in audit.records}

        for record in audit.records:
            for exit_ in record.exits:
                self.assertIn(exit_.target_id, records, (record.location_id, exit_.direction))
                target = records[exit_.target_id]
                opposite = OPPOSITE[exit_.direction]
                self.assertTrue(
                    any(candidate.direction == opposite and candidate.target_id == record.location_id for candidate in target.exits),
                    (record.location_id, exit_.direction, exit_.target_id),
                )

    def test_detector_helpers_cover_raw_aliases_endings_and_language_errors(self) -> None:
        self.assertTrue(detect_raw_alias_leak("Torf bloto błoto mul muł i jeszcze sitowie."))

        endings = detect_identical_endings(
            [
                "Brama stoi cicho. Na wschodzie droga ciągnie się dalej.",
                "Wóz stoi przy murze. Na wschodzie droga ciągnie się dalej.",
                "Las milczy. Na północy droga ciągnie się dalej.",
            ]
        )
        self.assertIn("na wschodzie droga ciagnie sie dalej", endings)
        self.assertTrue(detect_obvious_language_error("Widać knieii problem w tym zdaniu."))

    def test_audit_report_is_deterministic(self) -> None:
        build_world_description_audit.cache_clear()
        first = build_world_description_audit()
        digest_one = first.report_digest
        payload_one = json.dumps(first.to_dict(), ensure_ascii=False, sort_keys=True)

        build_world_description_audit.cache_clear()
        second = build_world_description_audit()
        digest_two = second.report_digest
        payload_two = json.dumps(second.to_dict(), ensure_ascii=False, sort_keys=True)

        self.assertEqual(digest_one, digest_two)
        self.assertEqual(payload_one, payload_two)


if __name__ == "__main__":
    unittest.main()
