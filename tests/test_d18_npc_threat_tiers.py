from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.combat.balance import CombatBalanceSimulator, threat_balance_scenarios
from astergard.database.connections import SQLiteConnectionFactory
from astergard.database.world_state_repository import WorldStateRepository
from astergard.npcs.manager import NPCManager
from astergard.npcs.models import NPCFactory
from astergard.npcs.threat import THREAT_PROFILES, threat_for_vnum
from astergard.world.manager import WorldManager


class D18NPCThreatTierTests(unittest.TestCase):
    def test_vnums_have_expected_threat_tiers(self) -> None:
        self.assertEqual(threat_for_vnum("wolf").tier, "trash")
        self.assertEqual(threat_for_vnum("meekhan_soldier").tier, "standard")
        self.assertEqual(threat_for_vnum("mountain_troll").tier, "elite")
        self.assertEqual(threat_for_vnum("warband_captain").tier, "boss")

    def test_factory_applies_threat_metadata_and_scaling(self) -> None:
        factory = NPCFactory()
        wolf = factory.create("wolf", 1)
        soldier = factory.create("meekhan_soldier", 1)
        troll = factory.create("mountain_troll", 1)
        boss = factory.create("warband_captain", 1)
        self.assertEqual(wolf.threat_tier, "trash")
        self.assertEqual(soldier.threat_tier, "standard")
        self.assertEqual(troll.threat_tier, "elite")
        self.assertEqual(boss.threat_tier, "boss")
        self.assertGreater(boss.character.stats.sila, soldier.character.stats.sila)
        self.assertGreater(boss.character.weapon().base_damage, soldier.character.weapon().base_damage)  # type: ignore[union-attr]
        self.assertGreater(boss.respawn_delay_seconds, troll.respawn_delay_seconds)

    def test_balance_has_threat_scenarios(self) -> None:
        names = {scenario.name for scenario in threat_balance_scenarios(iterations=10)}
        self.assertIn("threat_trash_wolf_vs_player", names)
        self.assertIn("threat_boss_captain_vs_player", names)
        summaries = CombatBalanceSimulator().run_many(threat_balance_scenarios(iterations=30))
        self.assertEqual(len(summaries), 4)
        self.assertTrue(all(summary.iterations == 30 for summary in summaries))

    def test_world_snapshot_persists_threat_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            cf = SQLiteConnectionFactory(str(db_path))
            cf.migrate()
            world = WorldManager()
            world.generate_world()
            manager = NPCManager(world)
            boss = manager.spawn("warband_captain", 101)
            self.assertIsNotNone(boss)
            repo = WorldStateRepository(cf)
            repo.save(world, manager.npcs)

            loaded_world = WorldManager()
            loaded_world.generate_world()
            loaded_npcs = {}
            self.assertTrue(repo.load_into(loaded_world, loaded_npcs, NPCFactory()))
            loaded = next(npc for npc in loaded_npcs.values() if npc.vnum == "warband_captain")
            self.assertEqual(loaded.threat_tier, "boss")
            self.assertEqual(loaded.threat_label, THREAT_PROFILES["boss"].label)


if __name__ == "__main__":
    unittest.main()
