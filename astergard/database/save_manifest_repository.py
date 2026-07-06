from __future__ import annotations

from dataclasses import dataclass

from astergard.database.connections import SQLiteConnectionFactory


@dataclass(frozen=True, slots=True)
class SaveManifest:
    scope: str
    reason: str
    status: str
    username: str | None = None
    world_save_version: int = 0
    character_save_version: int = 0
    error: str = ""


class SaveManifestRepository:
    """Append-only save/load manifest used by D23 save engine.

    The manifest is intentionally small. It gives the engine an auditable trail
    of what was flushed, why, with which save version and whether recovery had
    to tolerate an error.
    """

    def __init__(self, connection_factory: SQLiteConnectionFactory) -> None:
        self.connection_factory = connection_factory

    def record(self, manifest: SaveManifest) -> int:
        with self.connection_factory.connection() as con:
            cur = con.execute(
                """
                INSERT INTO save_manifests(
                    scope, reason, username, world_save_version,
                    character_save_version, status, error
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    manifest.scope,
                    manifest.reason,
                    manifest.username,
                    manifest.world_save_version,
                    manifest.character_save_version,
                    manifest.status,
                    manifest.error,
                ),
            )
            lastrowid = cur.lastrowid
            if lastrowid is None:
                raise RuntimeError("SQLite nie zwrócił lastrowid.")
            return int(lastrowid)

    def latest(self, scope: str | None = None) -> SaveManifest | None:
        query = (
            "SELECT scope,reason,status,username,world_save_version,character_save_version,error "
            "FROM save_manifests"
        )
        params: tuple[object, ...] = ()
        if scope is not None:
            query += " WHERE scope=?"
            params = (scope,)
        query += " ORDER BY id DESC LIMIT 1"
        with self.connection_factory.connection() as con:
            row = con.execute(query, params).fetchone()
        if row is None:
            return None
        return SaveManifest(
            scope=str(row[0]),
            reason=str(row[1]),
            status=str(row[2]),
            username=str(row[3]) if row[3] is not None else None,
            world_save_version=int(row[4]),
            character_save_version=int(row[5]),
            error=str(row[6]),
        )

    def count(self) -> int:
        with self.connection_factory.connection() as con:
            row = con.execute("SELECT COUNT(*) FROM save_manifests").fetchone()
        return int(row[0])
