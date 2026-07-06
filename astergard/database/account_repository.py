from __future__ import annotations

import hashlib
import uuid

from astergard.database.connections import SQLiteConnectionFactory


class AccountRepository:
    def __init__(self, connection_factory: SQLiteConnectionFactory) -> None:
        self.connection_factory = connection_factory

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

    def exists(self, username: str) -> bool:
        with self.connection_factory.connection() as con:
            row = con.execute("SELECT 1 FROM players WHERE username=?", (username,)).fetchone()
        return row is not None

    def create_credentials(self, username: str, password: str) -> tuple[str, str]:
        salt = uuid.uuid4().hex
        return self.hash_password(password, salt), salt

    def verify(self, username: str, password: str) -> bool:
        with self.connection_factory.connection() as con:
            row = con.execute("SELECT password_hash,salt FROM players WHERE username=?", (username,)).fetchone()
        if not row:
            return False
        return str(row[0]) == self.hash_password(password, str(row[1]))
