from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from astergard.database.migrations import MigrationRunner


class SQLiteConnectionFactory:
    """Owns SQLite connection lifecycle and schema migration.

    Repositories receive this factory instead of opening raw connections on their
    own. This keeps transaction boundaries explicit and makes backup/restore
    possible without duplicating path logic.
    """

    def __init__(self, path: str | Path, migration_runner: MigrationRunner | None = None) -> None:
        self.path = Path(path)
        self.migration_runner = migration_runner or MigrationRunner()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path)
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def migrate(self) -> None:
        with self.connection() as con:
            self.migration_runner.migrate(con)

    def current_schema_version(self) -> int:
        with self.connection() as con:
            return self.migration_runner.current_version(con)
