from __future__ import annotations

import sqlite3
from pathlib import Path

from astergard.characters.creation import CharacterCreationProfile, create_character_from_profile
from astergard.characters.models import Character
from astergard.database.account_repository import AccountRepository
from astergard.database.audit_repository import AuditRepository
from astergard.database.backup import BackupService
from astergard.database.character_state_repository import CharacterStateRepository
from astergard.database.connections import SQLiteConnectionFactory
from astergard.database.migrations import MigrationRunner
from astergard.database.world_state_repository import WorldStateRepository
from astergard.database.save_manifest_repository import SaveManifestRepository
from astergard.world.manager import STARTING_ROOM_ID


class UsernameTakenError(ValueError):
    def __init__(self, username: str) -> None:
        super().__init__("Ta nazwa użytkownika jest już zajęta.")
        self.username = username


class PlayerRepository:
    """Compatibility facade over explicit persistence repositories.

    D11 keeps the public API used by the game while splitting responsibilities:
    account credentials, durable character state, audit log and backup/restore.
    """

    def __init__(self, path: str = "mud.db", migration_runner: MigrationRunner | None = None) -> None:
        self.connection_factory = SQLiteConnectionFactory(Path(path), migration_runner)
        self.accounts = AccountRepository(self.connection_factory)
        self.characters = CharacterStateRepository(self.connection_factory)
        self.audit = AuditRepository(self.connection_factory)
        self.backups = BackupService(self.connection_factory)
        self.world_state = WorldStateRepository(self.connection_factory)
        self.save_manifests = SaveManifestRepository(self.connection_factory)
        self.init_db()

    @property
    def path(self) -> Path:
        return self.connection_factory.path

    def connection(self):  # intentionally keeps old tests and admin tools compatible
        return self.connection_factory.connection()

    def init_db(self) -> None:
        self.connection_factory.migrate()

    def current_schema_version(self) -> int:
        return self.connection_factory.current_schema_version()

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        return AccountRepository.hash_password(password, salt)

    def player_exists(self, username: str) -> bool:
        return self.accounts.exists(username)

    def register(self, username: str, password: str, profile: CharacterCreationProfile | None = None) -> bool:
        password_hash, salt = self.accounts.create_credentials(username, password)
        character = create_character_from_profile(username, profile) if profile is not None else Character(username=username, room_id=STARTING_ROOM_ID)
        try:
            self.characters.insert_new(username, password_hash, salt, character)
        except sqlite3.IntegrityError as exc:
            if "players.username" not in str(exc) and "UNIQUE constraint failed" not in str(exc):
                raise
            raise UsernameTakenError(username) from exc
        self.audit.record(username, "account_registered")
        return True

    def verify(self, username: str, password: str) -> bool:
        ok = self.accounts.verify(username, password)
        if ok:
            self.audit.record(username, "account_verified")
        return ok

    def load(self, username: str) -> Character:
        return self.characters.load(username)

    def save(self, char: Character) -> None:
        self.characters.save(char)
        self.audit.record(char.username, "character_saved")

    def save_version(self, username: str) -> int:
        return self.characters.save_version(username)

    def create_backup(self, destination: str | Path) -> Path:
        return self.backups.create_backup(destination)

    def restore_backup(self, source: str | Path) -> None:
        self.backups.restore_backup(source)

    def ranking(self, category: str) -> str:
        allowed = {
            "zloto": "gold",
            "gold": "gold",
            "sila": "stats_json",
            "zrecznosc": "stats_json",
        }
        selected = allowed.get(category.strip().lower(), "gold")
        if selected == "gold":
            with self.connection_factory.connection() as con:
                rows = con.execute("SELECT username,gold FROM players ORDER BY gold DESC, username ASC LIMIT 10").fetchall()
            if not rows:
                return "Ranking jest pusty."
            return "\n".join(f"{idx}. {row[0]}: {row[1]}" for idx, row in enumerate(rows, start=1))
        with self.connection_factory.connection() as con:
            rows = con.execute("SELECT username,stats_json FROM players").fetchall()
        import json

        stat_name = category.strip().lower()
        ranked = sorted(
            ((str(row[0]), int(json.loads(row[1]).get(stat_name, 0))) for row in rows),
            key=lambda item: (-item[1], item[0]),
        )[:10]
        if not ranked:
            return "Ranking jest pusty."
        return "\n".join(f"{idx}. {name}: {value}" for idx, (name, value) in enumerate(ranked, start=1))
