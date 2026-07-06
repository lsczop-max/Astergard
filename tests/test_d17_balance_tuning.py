from __future__ import annotations

import unittest

from astergard.combat.balance import CombatBalanceSimulator, default_balance_scenarios
from astergard.combat.manager import COMBAT_STYLES
from astergard.npcs.models import NPCFactory


class D17BalanceTuningTests(unittest.TestCase):
    def test_tuned_style_extremes_are_reduced(self) -> None:
        self.assertEqual(COMBAT_STYLES["defensywny"].defense_modifier, 1)
        self.assertEqual(COMBAT_STYLES["brutalny"].attack_modifier, 3)
        self.assertEqual(COMBAT_STYLES["brutalny"].defense_modifier, -1)

    def test_troll_has_real_offensive_equipment(self) -> None:
        troll = NPCFactory().create("mountain_troll", room_id=1)
        weapon = troll.character.weapon()
        self.assertIsNotNone(weapon)
        self.assertEqual(weapon.vnum, "troll_club")
        self.assertGreaterEqual(weapon.base_damage, 8)  # type: ignore[union-attr]

    def test_soldier_has_full_combat_loadout(self) -> None:
        soldier = NPCFactory().create("meekhan_soldier", room_id=1)
        self.assertIsNotNone(soldier.character.weapon())
        self.assertIsNotNone(soldier.character.shield())
        self.assertIsNotNone(soldier.character.armor_for("korpus"))

    def test_ordinary_balance_scenarios_have_no_extreme_win_rate(self) -> None:
        summaries = CombatBalanceSimulator().run_many(default_balance_scenarios(iterations=120))
        for summary in summaries:
            self.assertLess(summary.attacker_win_rate, 0.86, summary)
            self.assertLess(summary.defender_win_rate, 0.86, summary)


if __name__ == "__main__":
    unittest.main()
