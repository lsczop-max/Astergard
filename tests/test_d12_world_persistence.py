from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.application.bootstrap import GameBootstrapper
from astergard.items.models import Item
from astergard.npcs.manager import NPCManager
from astergard.world.manager import WorldManager
from astergard.database.repository import PlayerRepository


class D12WorldPersistenceTests(unittest.TestCase):
    def test_world_snapshot_persists_ground_items_hidden_elements_npcs_and_respawn_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "mud.db")
            repo = PlayerRepository(db_path)
            world = WorldManager()
            world.generate_world()
            npcs = NPCManager(world)
            npcs.populate()
            world.locations[0].items.append(Item("testowy kamień", "Leży tu celowo.", 0.2, 1, "test_stone"))
            world.locations[1].hidden_elements.clear()
            world.locations[1].hidden_elements.append({"type": "item", "data": Item("ukryty nóż", "Mały nóż.", 0.3, 4, "hidden_knife"), "difficulty": 7})
            npc = next(iter(npcs.npcs.values()))
            npc.ai_state = "PATROL"
            npc.character.wounds["korpus"] = 2
            world.respawn_queue.append({"vnum": "wolf", "room_id": 101, "time": 123.0})

            repo.world_state.save(world, npcs.npcs)

            loaded_world = WorldManager()
            loaded_world.generate_world()
            loaded_npcs = NPCManager(loaded_world)
            loaded = repo.world_state.load_into(loaded_world, loaded_npcs.npcs, loaded_npcs.factory)

            self.assertTrue(loaded)
            self.assertTrue(any(item.vnum == "test_stone" for item in loaded_world.locations[0].items))
            hidden = loaded_world.locations[1].hidden_elements[0]
            self.assertEqual(hidden["difficulty"], 7)
            self.assertEqual(getattr(hidden["data"], "vnum"), "hidden_knife")
            self.assertEqual(loaded_world.respawn_queue[0]["vnum"], "wolf")
            self.assertTrue(any(npc.ai_state == "PATROL" for npc in loaded_npcs.npcs.values()))
            self.assertTrue(any(npc.character.wounds["korpus"] == 2 for npc in loaded_npcs.npcs.values()))

    def test_bootstrap_loads_existing_world_snapshot_instead_of_repopulating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "mud.db")
            first = GameBootstrapper(db_path).build()
            first.world.locations[0].items.append(Item("znacznik świata", "Dowód zapisu.", 0.1, 1, "world_marker"))
            first.npcs.npcs.clear()
            for loc in first.world.locations.values():
                loc.npc_ids.clear()
            first.repo.world_state.save(first.world, first.npcs.npcs)

            second = GameBootstrapper(db_path).build()

            self.assertTrue(any(item.vnum == "world_marker" for item in second.world.locations[0].items))
            self.assertEqual(second.npcs.npcs, {})
            self.assertGreaterEqual(second.repo.world_state.save_version(), 1)


if __name__ == "__main__":
    unittest.main()
