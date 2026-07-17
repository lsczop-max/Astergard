from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.characters.models import Character, CharacterStats
from astergard.combat.manager import CombatManager, normalize_combat_style
from astergard.items.models import Item
from astergard.database.repository import PlayerRepository


class FixedRandom:
    def __init__(self, randint_values: list[int] | None = None, random_values: list[float] | None = None) -> None:
        self.randint_values = randint_values or [10]
        self.random_values = random_values or [0.99]

    def randint(self, a: int, b: int) -> int:
        if self.randint_values:
            return self.randint_values.pop(0)
        return max(a, min(b, 10))

    def random(self) -> float:
        if self.random_values:
            return self.random_values.pop(0)
        return 0.99


class D15CombatStyleTests(unittest.TestCase):
    def test_normalize_combat_style_accepts_polish_aliases(self) -> None:
        self.assertEqual(normalize_combat_style("atak"), "ofensywny")
        self.assertEqual(normalize_combat_style("obrona"), "defensywny")
        self.assertEqual(normalize_combat_style("zrównoważony"), "zrownowazony")

    def test_offensive_style_costs_more_stamina_than_defensive_style(self) -> None:
        attacker = Character("atakujacy")
        defender = Character("obronca")
        attacker.stats = CharacterStats(zrecznosc=15, kondycja=100)
        defender.stats = CharacterStats(zrecznosc=1, kondycja=100)
        attacker.combat_style = "ofensywny"
        combat = CombatManager(FixedRandom(randint_values=[20, 1, 50], random_values=[0.99, 0.99]))
        combat.attack(attacker, defender)
        offensive_stamina = attacker.stats.kondycja

        cautious = Character("ostrozny")
        target = Character("cel")
        cautious.stats = CharacterStats(zrecznosc=15, kondycja=100)
        target.stats = CharacterStats(zrecznosc=1, kondycja=100)
        cautious.combat_style = "defensywny"
        combat = CombatManager(FixedRandom(randint_values=[20, 1, 50], random_values=[0.99, 0.99]))
        combat.attack(cautious, target)
        self.assertLess(offensive_stamina, cautious.stats.kondycja)

    def test_round_result_exposes_observer_message(self) -> None:
        attacker = Character("atakujacy")
        defender = Character("obronca")
        attacker.stats.zrecznosc = 20
        defender.stats.zrecznosc = 1
        attacker.combat_style = "brutalny"
        attacker.equipment["prawa_reka"] = Item("miecz", "", 1.0, 1, "brutal_sword", item_type="weapon", slot="prawa_reka", weapon_type="miecz", base_damage=4, parry_bonus=1)
        combat = CombatManager(FixedRandom(randint_values=[20, 1, 1, 50], random_values=[0.99, 0.99, 0.99]))
        result = combat.attack(attacker, defender)
        self.assertIn("gwałtow", result.observer_message or result.message)

    def test_combat_style_is_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = PlayerRepository(str(Path(tmp) / "mud.db"))
            self.assertTrue(repo.register("lukan", "secret"))
            char = repo.load("lukan")
            char.combat_style = "defensywny"
            repo.save(char)
            loaded = repo.load("lukan")
            self.assertEqual(loaded.combat_style, "defensywny")


if __name__ == "__main__":
    unittest.main()
