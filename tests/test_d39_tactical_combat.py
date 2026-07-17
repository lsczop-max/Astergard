from __future__ import annotations

import unittest
from unittest.mock import patch

from astergard.characters.models import Character, CharacterStats
from astergard.combat.hit_locations import BodyLocation, BodyLocationGroup, HitLocationOutcome
from astergard.combat.balance import CombatBalanceSimulator, profession_balance_scenarios
from astergard.combat.manager import CombatManager
from astergard.combat.tactics import morale_score
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


class TacticalCombatTests(unittest.TestCase):
    def _base_combatant(self, name: str = "tester") -> Character:
        combatant = Character(name)
        combatant.stats = CharacterStats(zrecznosc=10, sila=10, wytrzymalosc=10, percepcja=10, sila_woli=10, kondycja=100)
        combatant.equipment["prawa_reka"] = Item("miecz", "", 1.8, 10, "simple_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1)
        return combatant

    def test_hit_depends_on_skill_level(self) -> None:
        weak = self._base_combatant("weak")
        strong = self._base_combatant("strong")
        weak.skills.values["bron_jednoraczna"]["level"] = 1
        strong.skills.values["bron_jednoraczna"]["level"] = 8
        defender = self._base_combatant("target")
        defender.stats.zrecznosc = 1
        defender.skills.values["uniki"]["level"] = 0
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        weak_result = combat.attack(weak, defender)
        defender = self._base_combatant("target2")
        defender.stats.zrecznosc = 1
        defender.skills.values["uniki"]["level"] = 0
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        strong_result = combat.attack(strong, defender)
        self.assertFalse(weak_result.hit)
        self.assertTrue(strong_result.hit)
        self.assertGreater(strong_result.attack_score, weak_result.attack_score)

    def test_armor_reduces_damage(self) -> None:
        attacker = self._base_combatant("att")
        defender_light = self._base_combatant("light")
        defender_heavy = self._base_combatant("heavy")
        defender_heavy.equipment["korpus"] = Item("zbroja", "", 4.0, 25, "armor", "armor", "korpus", protection=3)
        attacker.skills.values["bron_jednoraczna"]["level"] = 10
        defender_light.stats.zrecznosc = 1
        defender_light.skills.values["uniki"]["level"] = 0
        defender_heavy.stats.zrecznosc = 1
        defender_heavy.skills.values["uniki"]["level"] = 0
        combat = CombatManager(FixedRandom(randint_values=[20, 1, 20, 1], random_values=[0.99, 0.99, 0.99, 0.99]))
        fixed_hit_location = HitLocationOutcome(
            location=BodyLocation.CHEST,
            location_group=BodyLocationGroup.TORSO_GROUP,
            base_weight=1.0,
            weapon_weight_modifier=1.0,
            quality_modifier=1.0,
            attack_type_modifier=1.0,
            final_weight=1.0,
            reason_code="TEST",
        )
        with patch("astergard.combat.manager.resolve_hit_location", return_value=fixed_hit_location):
            light_result = combat.attack(attacker, defender_light)
        combat = CombatManager(FixedRandom(randint_values=[20, 1, 20, 1], random_values=[0.99, 0.99, 0.99, 0.99]))
        with patch("astergard.combat.manager.resolve_hit_location", return_value=fixed_hit_location):
            heavy_result = combat.attack(attacker, defender_heavy)
        self.assertGreater(light_result.effective_damage, heavy_result.effective_damage)
        self.assertEqual(heavy_result.body_part, "korpus")

    def test_heavier_armor_slows_and_opens_defense_windows(self) -> None:
        attacker = self._base_combatant("attacker")
        defender_light = self._base_combatant("light")
        defender_heavy = self._base_combatant("heavy")
        defender_heavy.equipment["glowa"] = Item("hełm", "", 2.8, 18, "helm", "armor", "glowa", protection=1)
        defender_heavy.equipment["korpus"] = Item("zbroja", "", 4.0, 25, "armor", "armor", "korpus", protection=3)

        combat = CombatManager(FixedRandom(randint_values=[10, 1, 10, 1], random_values=[0.99, 0.99, 0.99, 0.99]))
        light_initiative = combat.initiative_score(defender_light)
        combat = CombatManager(FixedRandom(randint_values=[10, 1, 10, 1], random_values=[0.99, 0.99, 0.99, 0.99]))
        heavy_initiative = combat.initiative_score(defender_heavy)
        self.assertLess(heavy_initiative, light_initiative)

        combat = CombatManager(FixedRandom(randint_values=[20, 1, 20, 1], random_values=[0.99, 0.99, 0.99, 0.99]))
        fixed_hit_location = HitLocationOutcome(
            location=BodyLocation.CHEST,
            location_group=BodyLocationGroup.TORSO_GROUP,
            base_weight=1.0,
            weapon_weight_modifier=1.0,
            quality_modifier=1.0,
            attack_type_modifier=1.0,
            final_weight=1.0,
            reason_code="TEST",
        )
        with patch("astergard.combat.manager.resolve_hit_location", return_value=fixed_hit_location):
            light_result = combat.attack(attacker, defender_light)
        combat = CombatManager(FixedRandom(randint_values=[20, 1, 20, 1], random_values=[0.99, 0.99, 0.99, 0.99]))
        with patch("astergard.combat.manager.resolve_hit_location", return_value=fixed_hit_location):
            heavy_result = combat.attack(self._base_combatant("attacker2"), defender_heavy)
        self.assertLess(heavy_result.defense_score, light_result.defense_score)
        self.assertGreaterEqual(light_result.attack_score, heavy_result.attack_score)

    def test_weapon_reach_changes_hit_score(self) -> None:
        spear_fighter = self._base_combatant("spear")
        spear_fighter.equipment["prawa_reka"] = Item("włócznia", "", 2.2, 20, "spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2, initiative_modifier=0, parry_bonus=0)
        sword_fighter = self._base_combatant("sword")
        defender = self._base_combatant("target")
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        spear_result = combat.attack(spear_fighter, defender)
        defender = self._base_combatant("target2")
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        sword_result = combat.attack(sword_fighter, defender)
        self.assertGreater(spear_result.attack_score, sword_result.attack_score)

    def test_fatigue_and_wounds_reduce_combat_effectiveness(self) -> None:
        fresh = self._base_combatant("fresh")
        tired = self._base_combatant("tired")
        tired.stats.kondycja = 20
        wounded = self._base_combatant("wounded")
        wounded.wounds["prawa_noga"] = 2
        wounded.wounds["lewa_noga"] = 1
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        fresh_attack = combat.attack(fresh, self._base_combatant("dummy"))
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        tired_attack = combat.attack(tired, self._base_combatant("dummy2"))
        self.assertGreater(fresh_attack.attack_score, tired_attack.attack_score)
        fresh_initiative = CombatManager(FixedRandom(randint_values=[1])).initiative_score(self._base_combatant("baseline"))
        wounded_initiative = CombatManager(FixedRandom(randint_values=[1])).initiative_score(wounded)
        self.assertLess(wounded_initiative, fresh_initiative)

    def test_morale_changes_tactical_value_in_simple_range(self) -> None:
        low = self._base_combatant("low")
        high = self._base_combatant("high")
        low.skills.values["morale"]["level"] = 1
        high.skills.values["morale"]["level"] = 8
        self.assertLess(morale_score(low), morale_score(high))
        self.assertGreaterEqual(morale_score(high), 10)

    def test_formation_front_back_and_reserve_apply_small_modifiers(self) -> None:
        attacker = self._base_combatant("attacker")
        defender = self._base_combatant("defender")
        defender.formation = "back"
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        flank_result = combat.attack(attacker, defender)
        head_on_attacker = self._base_combatant("attacker2")
        defender = self._base_combatant("defender2")
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        head_on_result = combat.attack(head_on_attacker, defender)
        reserve = self._base_combatant("reserve")
        reserve.formation = "reserve"
        combat = CombatManager(FixedRandom(randint_values=[1, 1, 1, 1]))
        reserve_result = combat.attack(reserve, self._base_combatant("target"))
        self.assertGreater(flank_result.attack_score, head_on_result.attack_score)
        self.assertLess(reserve_result.attack_score, head_on_result.attack_score)

    def test_profession_balance_scenarios_stay_within_reasonable_band(self) -> None:
        simulator = CombatBalanceSimulator()
        summaries = simulator.run_many(profession_balance_scenarios(iterations=40))
        self.assertEqual(len(summaries), 5)
        self.assertTrue(all(summary.iterations == 40 for summary in summaries))
        self.assertTrue(all(abs((summary.attacker_win_rate + summary.defender_win_rate + summary.draw_rate) - 1.0) < 1e-9 for summary in summaries))
        self.assertLessEqual(max(summary.attacker_win_rate for summary in summaries), 0.95)
        self.assertGreater(min(summary.attacker_win_rate for summary in summaries), 0.1)


if __name__ == "__main__":
    unittest.main()
