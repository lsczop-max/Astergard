from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.application.bootstrap import GameBootstrapper


class SaveLoadEngineTests(unittest.TestCase):
    def test_flush_all_records_manifests_and_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "mud.db"
            services = GameBootstrapper(str(db)).build()
            self.assertEqual(services.repo.current_schema_version(), 11)
            self.assertTrue(services.repo.register("tester", "secret"))
            character = services.repo.load("tester")
            character.gold = 123
            result = services.save_load.flush_all([character], "unit_test_flush")
            self.assertTrue(result.ok)
            self.assertEqual(result.saved_characters, 1)
            self.assertTrue(result.saved_world)
            loaded = services.repo.load("tester")
            self.assertEqual(loaded.gold, 123)
            self.assertGreaterEqual(services.repo.save_manifests.count(), 3)
            latest = services.repo.save_manifests.latest("full")
            self.assertIsNotNone(latest)
            assert latest is not None
            self.assertEqual(latest.status, "ok")
            self.assertEqual(latest.reason, "unit_test_flush")

    def test_checkpoint_and_restore_round_trip_database_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "mud.db"
            services = GameBootstrapper(str(db)).build()
            self.assertTrue(services.repo.register("tester", "secret"))
            character = services.repo.load("tester")
            character.gold = 10
            services.save_load.save_character(character, "before_checkpoint")
            checkpoint = services.save_load.create_checkpoint("unit_test", Path(tmp) / "backups")
            character.gold = 999
            services.save_load.save_character(character, "after_checkpoint")
            self.assertEqual(services.repo.load("tester").gold, 999)
            services.save_load.restore_checkpoint(checkpoint)
            restored = services.repo.load("tester")
            self.assertEqual(restored.gold, 10)

    def test_recover_world_reports_snapshot_presence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "mud.db"
            services = GameBootstrapper(str(db)).build()
            self.assertTrue(services.save_load.recover_world())
            latest = services.repo.save_manifests.latest("world_recovery")
            self.assertIsNotNone(latest)
            assert latest is not None
            self.assertEqual(latest.status, "ok")


if __name__ == "__main__":
    unittest.main()
