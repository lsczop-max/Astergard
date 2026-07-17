from __future__ import annotations

import unittest
from random import Random

from astergard.location_narrative.generator import LocationNarrativeGenerator
from astergard.location_narrative.models import DynamicLocationState
from astergard.location_narrative.regional_knowledge import (
    REGIONAL_KNOWLEDGE_BANKS,
    audit_region_generation,
    audit_region_texts,
    bank_for_region,
    build_style_guide,
    pick_sensory_phrases,
    pick_surface_phrases,
    region_style_profile,
)
from astergard.world.manager import WorldManager


class D57RegionalKnowledgeBankTests(unittest.TestCase):
    def setUp(self) -> None:
        self.world = WorldManager()
        self.world.generate_world()
        self.generator = LocationNarrativeGenerator.default(self.world)

    def test_all_known_regions_have_banks_with_full_category_coverage(self) -> None:
        self.assertEqual(len(REGIONAL_KNOWLEDGE_BANKS), 15)
        for region_id, bank in REGIONAL_KNOWLEDGE_BANKS.items():
            self.assertEqual(bank.region_id, region_id)
            self.assertEqual(len(bank.material_entries), 2, region_id)
            self.assertEqual(len(bank.construction_entries), 2, region_id)
            self.assertEqual(len(bank.trace_entries), 2, region_id)
            self.assertEqual(len(bank.natural_entries), 2, region_id)
            self.assertEqual(len(bank.economy_culture_entries), 2, region_id)
            self.assertEqual(region_style_profile(region_id).region_id, region_id)

    def test_surface_selection_is_deterministic_and_region_specific(self) -> None:
        state = DynamicLocationState(time_of_day="dzień", weather="bezchmurnie", season="lato", lighting="pełne światło")
        first = pick_surface_phrases(bank_for_region("Puszcza_Ciszy"), location_type="ścieżka", terrain="leśny", state=state, rng=Random(7))
        second = pick_surface_phrases(bank_for_region("Puszcza_Ciszy"), location_type="ścieżka", terrain="leśny", state=state, rng=Random(7))
        third = pick_surface_phrases(bank_for_region("Bagna_Hookri"), location_type="bagno", terrain="bagienny", state=state, rng=Random(7))
        self.assertEqual(first, second)
        self.assertNotEqual(first, third)

    def test_sensory_selection_stays_region_tied(self) -> None:
        state = DynamicLocationState(time_of_day="noc", weather="mgła", season="jesień", lighting="półmrok")
        forest_senses = pick_sensory_phrases(bank_for_region("Puszcza_Ciszy"), location_type="ścieżka", terrain="leśny", state=state, rng=Random(2))
        swamp_senses = pick_sensory_phrases(bank_for_region("Bagna_Hookri"), location_type="bagno", terrain="bagienny", state=state, rng=Random(2))
        self.assertNotEqual(forest_senses, swamp_senses)
        self.assertTrue(forest_senses)
        self.assertTrue(swamp_senses)

    def test_generation_audit_can_sample_a_region(self) -> None:
        report = audit_region_generation(self.generator, self.world, "Puszcza_Ciszy", sample_size=12)
        self.assertEqual(report.region_id, "Puszcza_Ciszy")
        self.assertEqual(report.sample_size, 12)
        self.assertGreater(report.accepted_count, 0)
        self.assertEqual(report.accepted_count + report.rejected_count, 12)
        self.assertGreater(report.average_score, 0.0)
        self.assertTrue(report.text_audit.top_nouns)
        self.assertTrue(report.text_audit.top_structures)

    def test_style_guide_and_text_audit_are_buildable(self) -> None:
        bank = bank_for_region("Centrum_Twierdza")
        sample_texts = [self.generator.generate(room_id).long_description for room_id in (0, 1, 2, 3)]
        audit = audit_region_texts("Centrum_Twierdza", sample_texts, bank)
        guide = build_style_guide("Centrum_Twierdza", bank, audit)
        self.assertEqual(guide.region_id, "Centrum_Twierdza")
        self.assertTrue(guide.material_identity)
        self.assertTrue(guide.frequent_elements)
        self.assertTrue(guide.forbidden_elements)
        self.assertTrue(audit.repeated_openings)


if __name__ == "__main__":
    unittest.main()
