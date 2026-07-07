from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from astergard.characters.models import Effect
from astergard.database.migrations import MigrationRunner
from astergard.database.repository import PlayerRepository
from astergard.items.models import Item


class PersistenceMigrationTests(unittest.TestCase):
    def test_migrations_are_applied_once_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "mud.db"
            repo = PlayerRepository(str(db))
            self.assertEqual(repo.current_schema_version(), 7)
            repo.init_db()
            con = sqlite3.connect(db)
            try:
                rows = con.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
            finally:
                con.close()
            self.assertEqual([row[0] for row in rows], [1, 2, 3, 4, 5, 6, 7])
            self.assertEqual(len(rows), 7)

    def test_save_increments_save_version_and_preserves_nested_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = PlayerRepository(str(Path(tmp) / "mud.db"))
            self.assertTrue(repo.register("Lukas", "secret"))
            char = repo.load("Lukas")
            char.room_id = 17
            char.gold = 123
            pouch = Item("sakiewka", "Mała sakiewka.", 0.1, is_container=True, capacity=2.0)
            pouch.contains.append(Item("srebrna moneta", "Zmatowiała moneta.", 0.01, value=1, vnum="silver_coin"))
            char.inventory.append(pouch)
            char.equipment["prawa_reka"] = Item(
                "topór testowy", "Ciężki topór.", 3.2, value=40, item_type="weapon", slot="prawa_reka", base_damage=6
            )
            char.active_effects.append(Effect("Próba", "sila", 1, 3))
            repo.save(char)
            repo.save(char)
            loaded = repo.load("Lukas")
            self.assertEqual(loaded.room_id, 17)
            self.assertEqual(loaded.gold, 123)
            self.assertEqual(loaded.inventory[-1].contains[0].name, "srebrna moneta")
            self.assertEqual(loaded.equipment["prawa_reka"].name, "topór testowy")  # type: ignore[union-attr]
            self.assertEqual(loaded.active_effects[0].name, "Próba")
            with repo.connection() as con:
                version = con.execute("SELECT save_version FROM players WHERE username=?", ("Lukas",)).fetchone()[0]
            self.assertEqual(version, 3)

    def test_migration_runner_rejects_invalid_file_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            migrations = Path(tmp)
            (migrations / "bad.sql").write_text("SELECT 1;", encoding="utf-8")
            runner = MigrationRunner(migrations)
            with self.assertRaises(RuntimeError):
                runner.discover()


if __name__ == "__main__":
    unittest.main()
