from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    sql: str


class MigrationError(RuntimeError):
    pass


class MigrationRunner:
    """Applies versioned SQLite migrations exactly once.

    This replaces ad-hoc CREATE TABLE / ALTER TABLE logic with a durable schema
    history. Migrations are intentionally plain SQL files so the project remains
    standard-library only and easy to inspect.
    """

    def __init__(self, migrations_dir: Path | None = None) -> None:
        self.migrations_dir = migrations_dir or Path(__file__).with_name("migrations")

    def ensure_schema_table(self, con: sqlite3.Connection) -> None:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations(
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def discover(self) -> list[Migration]:
        migrations: list[Migration] = []
        for path in sorted(self.migrations_dir.glob("*.sql")):
            prefix, _, suffix = path.name.partition("_")
            if not prefix.isdigit() or not suffix:
                raise MigrationError(f"Invalid migration filename: {path.name}")
            migrations.append(Migration(version=int(prefix), name=path.name, sql=path.read_text(encoding="utf-8")))
        versions = [migration.version for migration in migrations]
        if len(versions) != len(set(versions)):
            raise MigrationError("Duplicate migration versions detected")
        return migrations

    def applied_versions(self, con: sqlite3.Connection) -> set[int]:
        rows = con.execute("SELECT version FROM schema_migrations").fetchall()
        return {int(row[0]) for row in rows}

    def migrate(self, con: sqlite3.Connection) -> None:
        self.ensure_schema_table(con)
        applied = self.applied_versions(con)
        for migration in self.discover():
            if migration.version in applied:
                continue
            try:
                con.executescript(migration.sql)
                con.execute(
                    "INSERT INTO schema_migrations(version, name) VALUES(?, ?)",
                    (migration.version, migration.name),
                )
            except sqlite3.Error as exc:
                raise MigrationError(f"Migration failed: {migration.name}: {exc}") from exc

    def current_version(self, con: sqlite3.Connection) -> int:
        self.ensure_schema_table(con)
        row = con.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        return int(row[0] or 0)
