from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from astergard.database.account_repository import AccountRepository
from astergard.database.audit_repository import AuditRepository
from astergard.database.backup import BackupService
from astergard.database.character_state_repository import CharacterStateRepository
from astergard.database.connections import SQLiteConnectionFactory
from astergard.database.repository import PlayerRepository


class RepositorySplitTests(unittest.TestCase):
    def test_player_repository_exposes_split_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = PlayerRepository(str(Path(tmp) / "mud.db"))
            self.assertIsInstance(repo.accounts, AccountRepository)
            self.assertIsInstance(repo.characters, CharacterStateRepository)
            self.assertIsInstance(repo.audit, AuditRepository)
            self.assertIsInstance(repo.backups, BackupService)
            self.assertIsInstance(repo.connection_factory, SQLiteConnectionFactory)

    def test_audit_records_registration_verification_and_save(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = PlayerRepository(str(Path(tmp) / "mud.db"))
            self.assertTrue(repo.register("audited", "pw"))
            self.assertTrue(repo.verify("audited", "pw"))
            char = repo.load("audited")
            char.gold = 77
            repo.save(char)
            events = repo.audit.recent("audited", limit=10)
            event_types = [event.event_type for event in events]
            self.assertIn("account_registered", event_types)
            self.assertIn("account_verified", event_types)
            self.assertIn("character_saved", event_types)

    def test_backup_and_restore_preserve_character_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "mud.db"
            backup_path = Path(tmp) / "backup.db"
            repo = PlayerRepository(str(db_path))
            self.assertTrue(repo.register("backup", "pw"))
            char = repo.load("backup")
            char.gold = 123
            repo.save(char)
            repo.create_backup(backup_path)
            char.gold = 1
            repo.save(char)
            repo.restore_backup(backup_path)
            restored = repo.load("backup")
            self.assertEqual(restored.gold, 123)


if __name__ == "__main__":
    unittest.main()
