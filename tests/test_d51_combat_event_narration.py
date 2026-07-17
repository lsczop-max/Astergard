from __future__ import annotations

import unittest

from astergard.characters.models import Character
from astergard.combat.events import normalize_weapon_family
from astergard.combat.manager import CombatManager
from astergard.combat.narration import CombatNarrator
from astergard.items.models import Item


class D51CombatEventNarrationTests(unittest.TestCase):
    def _combatant(self, name: str) -> Character:
        combatant = Character(name)
        combatant.stats.zrecznosc = 12
        combatant.stats.wytrzymalosc = 12
        return combatant

    def test_weapon_family_is_inferred_from_name_when_missing_metadata(self) -> None:
        sword = Item("prosty miecz", "", 1.8, 10, "simple_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4)
        spear = Item("włócznia treningowa", "", 2.2, 10, "training_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2)
        self.assertEqual(normalize_weapon_family(sword), "miecze")
        self.assertEqual(normalize_weapon_family(spear), "wlocznie")

    def test_combat_result_carries_semantic_event_payload(self) -> None:
        attacker = self._combatant("atakujacy")
        defender = self._combatant("obronca")
        attacker.combat_style = "brutalny"
        attacker.equipment["prawa_reka"] = Item("prosty miecz", "", 1.8, 10, "simple_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1)
        manager = CombatManager()
        result = manager.attack(attacker, defender)
        self.assertIsNotNone(result.combat_event)
        assert result.combat_event is not None
        payload = result.combat_event.to_dict()
        self.assertEqual(payload["attacker_name"], "atakujacy")
        self.assertIn(payload["weapon_family"], {"miecze", "bez_broni", "improwizowana", "wlocznie", "topory", "mloty", "bron_drzewcowa", "sztylety", "maczugi"})
        self.assertIn("result", payload)
        self.assertIn("technique", payload)
        self.assertNotIn("None", result.message)
        self.assertNotIn("None", result.observer_message or "")

    def test_narrator_uses_perspectives_and_avoids_repeated_text(self) -> None:
        event = CombatManager()._build_event(  # type: ignore[attr-defined]
            self._combatant("atakujacy"),
            self._combatant("obronca"),
            result="hit",
            defense="none",
            technique="gwałtowne cięcie",
            hit_location="korpus",
            wound_level=2,
        )
        narrator = CombatNarrator()
        attacker_text = narrator.render(event, "attacker")
        defender_text = narrator.render(event, "defender")
        observer_text = narrator.render(event, "observer")
        self.assertNotEqual(attacker_text, defender_text)
        self.assertNotEqual(defender_text, observer_text)
        repeated = narrator.render(event, "attacker")
        self.assertNotEqual(attacker_text, repeated)
        self.assertNotIn("None", attacker_text)
        self.assertNotIn("None", observer_text)


if __name__ == "__main__":
    unittest.main()
