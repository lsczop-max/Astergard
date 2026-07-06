from __future__ import annotations

import shutil
from pathlib import Path

from astergard.database.connections import SQLiteConnectionFactory


class BackupService:
    def __init__(self, connection_factory: SQLiteConnectionFactory) -> None:
        self.connection_factory = connection_factory

    def create_backup(self, destination: str | Path) -> Path:
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        source = self.connection_factory.path
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, target)
        return target

    def restore_backup(self, source: str | Path) -> None:
        src = Path(source)
        if not src.exists():
            raise FileNotFoundError(src)
        self.connection_factory.path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, self.connection_factory.path)
        self.connection_factory.migrate()
