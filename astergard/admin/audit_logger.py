from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from astergard.engine.events import DomainEventType, EventBus
from astergard.database.repository import PlayerRepository


@dataclass(frozen=True, slots=True)
class AdminAuditEntry:
    actor: str
    action: str
    payload: dict[str, Any]
    created_at: str


class AdminAuditLogger:
    def __init__(self, repo: PlayerRepository, event_bus: EventBus) -> None:
        self.repo = repo
        self.event_bus = event_bus
        self.entries: list[AdminAuditEntry] = []

    def record(self, actor: str, action: str, **payload: Any) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        entry = AdminAuditEntry(actor=actor, action=action, payload=dict(payload), created_at=created_at)
        self.entries.append(entry)
        payload_json = json.dumps({"action": action, "payload": payload, "created_at": created_at}, ensure_ascii=False, sort_keys=True)
        try:
            self.repo.audit.record(actor, f"admin.{action}", payload_json)
        except Exception:
            # Audit persistence must never break a GM action during tests or emergency recovery.
            pass
        self.event_bus.emit("admin.action", actor=actor, action=action, payload=payload)

    def recent(self, limit: int = 20) -> list[AdminAuditEntry]:
        return list(reversed(self.entries[-limit:]))
