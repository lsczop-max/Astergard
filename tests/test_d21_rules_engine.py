from __future__ import annotations

import unittest

from astergard.characters.models import Character
from astergard.combat.manager import CombatManager
from astergard.economy.services import EconomyService
from astergard.factions.reputation import FactionManager
from astergard.rules.combat import CombatRules
from astergard.rules.economy import EconomyRules
from astergard.rules.engine import RuleSet
from astergard.rules.movement import MovementRules, SearchRules
from astergard.rules.reputation import ReputationRules


class D21RulesEngineTests(unittest.TestCase):
    def test_ruleset_groups_all_rule_domains(self) -> None:
        rules = RuleSet()
        self.assertIsInstance(rules.combat, CombatRules)
        self.assertIsInstance(rules.economy, EconomyRules)
        self.assertIsInstance(rules.movement, MovementRules)
        self.assertIsInstance(rules.search, SearchRules)
        self.assertIsInstance(rules.reputation, ReputationRules)

    def test_movement_rules_compute_leg_wound_costs(self) -> None:
        rules = MovementRules(base_move_stamina_cost=4, severe_leg_cost_multiplier=5)
        self.assertEqual(rules.move_cost(0, 0), 4)
        self.assertEqual(rules.move_cost(3, 0), 20)
        self.assertTrue(rules.movement_blocked(4, 4))
        self.assertFalse(rules.movement_blocked(4, 3))

    def test_economy_service_uses_injected_rules(self) -> None:
        economy = EconomyService(EconomyRules(maximum_reputation_discount_percent=50))
        from astergard.items.models import Item
        item = Item("test", "", 0.0, 100)
        self.assertEqual(economy.buy_price(item, 5000), 50)
        self.assertEqual(economy.sell_price(item), 50)

    def test_faction_manager_uses_injected_reputation_rules(self) -> None:
        manager = FactionManager(ReputationRules(guard_hostility_threshold=-100))
        char = Character("tester")
        char.reputation[manager.MEEKHAN] = -101
        self.assertTrue(manager.hostile_to_guards(char))

    def test_combat_manager_uses_injected_attack_cost_rule(self) -> None:
        rules = CombatRules(base_attack_stamina_cost=9)
        manager = CombatManager(rules=rules)
        style = rules.style("zrownowazony")
        self.assertEqual(manager._attack_stamina_cost(1, style), 9)


if __name__ == "__main__":
    unittest.main()
