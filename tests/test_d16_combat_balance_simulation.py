from __future__ import annotations

import unittest

from astergard.combat.balance import (
    CombatBalanceSimulator,
    CombatScenario,
    default_balance_scenarios,
    make_npc_character,
    make_player_duelist,
    render_balance_report,
)
from astergard.npcs.combat_profiles import combat_style_for_vnum
from astergard.npcs.models import NPCFactory


class D16CombatBalanceSimulationTests(unittest.TestCase):
    def test_default_scenarios_run_at_least_1000_iterations_each_when_requested(self) -> None:
        scenarios = default_balance_scenarios(iterations=1000)
        self.assertGreaterEqual(len(scenarios), 8)
        self.assertTrue(all(scenario.iterations == 1000 for scenario in scenarios))

    def test_simulation_summary_has_rates_that_sum_to_one(self) -> None:
        simulator = CombatBalanceSimulator()
        summary = simulator.run(
            CombatScenario(
                "smoke_style_balance",
                lambda: make_player_duelist("ofensywny"),
                lambda: make_player_duelist("defensywny"),
                iterations=40,
                seed=777,
            )
        )
        total = summary.attacker_win_rate + summary.defender_win_rate + summary.draw_rate
        self.assertAlmostEqual(total, 1.0)
        self.assertEqual(summary.iterations, 40)
        self.assertGreater(summary.average_rounds, 0)

    def test_report_renders_markdown_table(self) -> None:
        simulator = CombatBalanceSimulator()
        summary = simulator.run(
            CombatScenario(
                "report_smoke",
                lambda: make_player_duelist("zrownowazony"),
                lambda: make_npc_character("wolf"),
                iterations=20,
                seed=778,
            )
        )
        report = render_balance_report([summary])
        self.assertIn("# Combat Balance Report", report)
        self.assertIn("| report_smoke |", report)
        self.assertIn("Avg rounds", report)

    def test_npc_factory_assigns_combat_style_profiles(self) -> None:
        self.assertEqual(combat_style_for_vnum("mountain_troll"), "brutalny")
        troll = NPCFactory().create("mountain_troll", room_id=1)
        soldier = NPCFactory().create("meekhan_soldier", room_id=1)
        wolf = NPCFactory().create("wolf", room_id=1)
        self.assertEqual(troll.character.combat_style, "brutalny")
        self.assertEqual(soldier.character.combat_style, "defensywny")
        self.assertEqual(wolf.character.combat_style, "ofensywny")


if __name__ == "__main__":
    unittest.main()
