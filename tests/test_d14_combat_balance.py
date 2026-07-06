from __future__ import annotations

import unittest

from astergard.characters.models import Character, CharacterStats
from astergard.combat.manager import CombatManager
from astergard.items.models import Item


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


class D14CombatBalanceTests(unittest.TestCase):
    def test_item_serialization_preserves_combat_fields(self) -> None:
        spear = Item(
            "włócznia",
            "Długa broń drzewcowa.",
            2.2,
            30,
            "spear",
            "weapon",
            "prawa_reka",
            damage_type="kluta",
            base_damage=5,
            reach=2,
            initiative_modifier=-1,
            parry_bonus=2,
        )
        clone = Item.from_dict(spear.to_dict())
        self.assertEqual(clone.reach, 2)
        self.assertEqual(clone.initiative_modifier, -1)
        self.assertEqual(clone.parry_bonus, 2)

    def test_shield_can_block_successful_hit(self) -> None:
        attacker = Character("atakujacy")
        defender = Character("obronca")
        attacker.stats = CharacterStats(zrecznosc=10, kondycja=100)
        defender.stats = CharacterStats(zrecznosc=10, kondycja=100)
        defender.equipment["lewa_reka"] = Item(
            "duża tarcza",
            "Ciężka tarcza.",
            4.0,
            20,
            "large_shield",
            "shield",
            "lewa_reka",
            protection=1,
            shield_block=10,
        )
        combat = CombatManager(FixedRandom(randint_values=[10, 1, 20], random_values=[0.99]))
        result = combat.attack(attacker, defender)
        self.assertFalse(result.hit)
        self.assertEqual(result.defended_by, "shield")
        self.assertIn("tarczą", result.message)

    def test_weapon_parry_can_stop_hit_without_shield(self) -> None:
        attacker = Character("atakujacy")
        defender = Character("obronca")
        defender.equipment["prawa_reka"] = Item(
            "rapier",
            "Lekka broń do parowania.",
            1.1,
            30,
            "rapier",
            "weapon",
            "prawa_reka",
            damage_type="kluta",
            base_damage=3,
            parry_bonus=12,
        )
        combat = CombatManager(FixedRandom(randint_values=[10, 1, 20], random_values=[0.99]))
        result = combat.attack(attacker, defender)
        self.assertFalse(result.hit)
        self.assertEqual(result.defended_by, "parry")
        self.assertIn("paruje", result.message)

    def test_round_orders_turns_by_initiative_and_processes_both_sides(self) -> None:
        slow = Character("wolny")
        fast = Character("szybki")
        slow.stats.zrecznosc = 8
        fast.stats.zrecznosc = 15
        combat = CombatManager(FixedRandom(randint_values=[1, 10, 20, 1, 20, 1, 10, 10, 50], random_values=[0.99, 0.99, 0.99, 0.99]))
        result = combat.process_pair_round("slow", slow, "fast", fast)
        self.assertEqual(result.turns[0].attacker_id, "fast")
        self.assertGreaterEqual(len(result.results), 1)
        self.assertLess(slow.stats.kondycja, slow.stats.max_kondycja)
        self.assertLess(fast.stats.kondycja, fast.stats.max_kondycja)

    def test_process_active_round_removes_fights_when_rooms_diverge(self) -> None:
        a = Character("a", room_id=0)
        b = Character("b", room_id=1)
        combat = CombatManager(FixedRandom())
        combat.start("a", "b")
        combat.process_active_round({"a": a, "b": b})
        self.assertEqual(combat.active_fights, [])


if __name__ == "__main__":
    unittest.main()
