from __future__ import annotations

from dataclasses import dataclass

from astergard.database.connections import SQLiteConnectionFactory


@dataclass(frozen=True, slots=True)
class AuditEvent:
    username: str
    event_type: str
    payload_json: str
    created_at: str


class AuditRepository:
    def __init__(self, connection_factory: SQLiteConnectionFactory) -> None:
        self.connection_factory = connection_factory

    def record(self, username: str, event_type: str, payload_json: str = "{}") -> None:
        with self.connection_factory.connection() as con:
            con.execute(
                "INSERT INTO audit_events(username,event_type,payload_json) VALUES(?,?,?)",
                (username, event_type, payload_json),
            )

    def recent(self, username: str, limit: int = 20) -> list[AuditEvent]:
        with self.connection_factory.connection() as con:
            rows = con.execute(
                """
                SELECT username,event_type,payload_json,created_at
                FROM audit_events
                WHERE username=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (username, limit),
            ).fetchall()
        return [AuditEvent(str(row[0]), str(row[1]), str(row[2]), str(row[3])) for row in rows]
