from __future__ import annotations

import tempfile
import unittest

from astergard.characters.models import Effect
from astergard.database.repository import PlayerRepository
from astergard.items.models import Item


class PersistenceTests(unittest.TestCase):
    def test_full_character_state_roundtrip(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("persist", "secret"))
            char = repo.load("persist")
            char.room_id = 123
            char.gold = 77
            char.stats.sila = 14
            char.skills.train("bron_cieta", 10)
            char.wounds["prawa_noga"] = 3
            char.reputation["MEEKHAN"] = -600
            char.active_quests["wolf_pelt"] = {"current": 1}
            char.completed_quests.append("intro")
            sword = next(item for item in char.inventory if item.vnum == "simple_sword")
            char.inventory.remove(sword)
            char.equipment["prawa_reka"] = sword
            backpack = Item("plecak", "Stary plecak.", 0.8, 5, "backpack", "container", is_container=True, capacity=20.0)
            backpack.contains.append(Item("krzemień", "Mały krzemień.", 0.1, 1, "flint"))
            char.inventory.append(backpack)
            char.active_effects.append(Effect("Wzmocnienie", "sila", 4, 19))
            repo.save(char)

            loaded = repo.load("persist")
            self.assertEqual(loaded.room_id, 123)
            self.assertEqual(loaded.gold, 77)
            self.assertEqual(loaded.stats.sila, 14)
            self.assertEqual(loaded.wounds["prawa_noga"], 3)
            self.assertEqual(loaded.reputation["MEEKHAN"], -600)
            self.assertIn("wolf_pelt", loaded.active_quests)
            self.assertIn("intro", loaded.completed_quests)
            equipped = loaded.equipment["prawa_reka"]
            assert equipped is not None
            self.assertEqual(equipped.vnum, "simple_sword")
            loaded_pack = next(item for item in loaded.inventory if item.vnum == "backpack")
            self.assertEqual(loaded_pack.contains[0].vnum, "flint")
            self.assertEqual(loaded.active_effects[0].name, "Wzmocnienie")

    def test_repository_closes_connections_under_resource_warning_as_error(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            repo = PlayerRepository(tmp.name)
            self.assertTrue(repo.register("clean", "secret"))
            self.assertTrue(repo.verify("clean", "secret"))
            char = repo.load("clean")
            repo.save(char)


if __name__ == "__main__":
    unittest.main()
