from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.location_narrative.generator import (
    LocationNarrativeGenerator,
    build_pilot_review,
    compare_location_results,
    export_review,
    load_review,
)
from astergard.location_narrative.models import DataCompleteness, LocalDistinctiveness
from astergard.location_narrative.world_adapter import WorldNarrativeAdapter, select_fingerprint_pilot_locations
from astergard.world.manager import WorldManager


class D56LocationNarrativeGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.world = WorldManager()
        self.world.generate_world()
        self.generator = LocationNarrativeGenerator.default(self.world)

    def test_generation_is_deterministic_for_same_location(self) -> None:
        first = self.generator.generate(0)
        second = self.generator.generate(0)
        self.assertEqual(first.short_description, second.short_description)
        self.assertEqual(first.long_description, second.long_description)

    def test_generated_text_is_accepted_for_authored_location(self) -> None:
        result = self.generator.generate(0)
        self.assertGreaterEqual(result.quality_score, 82)
        self.assertFalse(result.validation_report.critical_errors)
        self.assertTrue(result.examinable_details)
        self.assertIn("Brama", result.short_description)

    def test_compare_and_export_round_trip(self) -> None:
        left = self.generator.generate(0)
        right = self.generator.generate(2)
        comparison = compare_location_results(left, right)
        self.assertIn("similarity", comparison)
        self.assertGreaterEqual(comparison["similarity"], 0.0)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "review.json"
            export_review([left, right], path)
            payload = load_review(path)
            self.assertEqual(len(payload), 2)
            self.assertEqual(payload[0]["location_id"], 0)

    def test_pilot_review_samples_thirty_rooms(self) -> None:
        pilot = build_pilot_review(self.world, tuple(range(30)))
        self.assertEqual(len(pilot), 30)
        self.assertTrue(all(result.generator_version for result in pilot))

    def test_negative_samples_are_rejected(self) -> None:
        negatives = [
            (390, "Ty widzisz tu błękitny pałac i czujesz, że twoje emocje rosną.", ()),
            (390, "Stąd można ruszyć na południe, choć droga nie istnieje.", ()),
            (425, "Na dziedzińcu stoi rzeka i jezioro, a woda spływa po murach.", ()),
            (0, "Miasto zaczyna się tutaj i prowadzi na zachód, chociaż nie ma tam wyjścia.", ()),
            (0, "Ty, ty i jeszcze raz ty. Ciebie widać wszędzie, a twoje kroki niosą się po placu.", ()),
            (390, "Stąd można ruszyć na zachód, choć droga nie istnieje.", ()),
            (425, "Na dziedzińcu stoi rzeka i jezioro, a woda spływa po murach.", ()),
            (390, "Ty patrzysz na północ, ale nic tam nie ma.", ()),
            (390, "Stąd można ruszyć na południe, choć droga nie istnieje.", ()),
            (0, "Ty, ty, ty. Ciebie widać i ciebie słychać.", ()),
        ]
        rejected = 0
        for location_id, text, existing in negatives:
            result = self.generator.generate(location_id, manual_description=text, existing_texts=existing)
            if not result.validation_report.is_accepted:
                rejected += 1
        self.assertGreaterEqual(rejected, 9)

    def test_identity_axes_are_reported_separately(self) -> None:
        adapter = WorldNarrativeAdapter(self.world)
        audit = adapter.audit_identity()
        self.assertEqual(len(audit), 500)
        self.assertTrue(any(entry.data_completeness in {DataCompleteness.COMPLETE, DataCompleteness.SUFFICIENT} for entry in audit))
        self.assertTrue(any(entry.local_distinctiveness in {LocalDistinctiveness.UNIQUE, LocalDistinctiveness.DISTINCT, LocalDistinctiveness.GENERIC} for entry in audit))

    def test_pilot_selection_returns_sixty_locations(self) -> None:
        location_ids = select_fingerprint_pilot_locations(self.world)
        self.assertEqual(len(location_ids), 60)
        self.assertEqual(len(set(location_ids)), 60)

    def test_fingerprint_changes_generation_when_enabled(self) -> None:
        without = self.generator.generate(0, use_local_fingerprint=False)
        with_fp = self.generator.generate(0, use_local_fingerprint=True)
        self.assertNotEqual(without.long_description, with_fp.long_description)
        self.assertTrue(with_fp.validation_report.is_accepted or with_fp.quality_score >= without.quality_score - 20)


if __name__ == "__main__":
    unittest.main()
