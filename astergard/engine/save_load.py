from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import TYPE_CHECKING

from astergard.characters.models import Character
from astergard.database.save_manifest_repository import SaveManifest

if TYPE_CHECKING:
    from astergard.application.bootstrap import GameServices


@dataclass(slots=True)
class SaveResult:
    scope: str
    reason: str
    saved_characters: int = 0
    saved_world: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(slots=True)
class SavePolicy:
    autosave_interval_ticks: int = 15
    backup_interval_ticks: int = 300
    checkpoint_directory: str = "backups"


class SaveLoadEngine:
    """Coordinates durable save/load operations across repositories.

    D23 centralises the save lifecycle. The lifecycle, admin commands and tests
    should not manually know how to persist characters, world state, manifests
    and backups in the right order.
    """

    def __init__(self, services: "GameServices", policy: SavePolicy | None = None) -> None:
        self.services = services
        self.policy = policy or SavePolicy()

    def save_character(self, character: Character, reason: str) -> SaveResult:
        result = SaveResult(scope="character", reason=reason)
        try:
            self.services.repo.save(character)
            result.saved_characters = 1
            version = self.services.repo.save_version(character.username)
            self.services.repo.save_manifests.record(
                SaveManifest(
                    scope="character",
                    reason=reason,
                    username=character.username,
                    character_save_version=version,
                    status="ok",
                )
            )
            self.services.event_bus.emit("save.character_completed", username=character.username, reason=reason, save_version=version)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            result.errors.append(message)
            self.services.repo.save_manifests.record(
                SaveManifest(scope="character", reason=reason, username=character.username, status="failed", error=message)
            )
            self.services.event_bus.emit("save.character_failed", username=character.username, reason=reason, error=message)
        return result

    def save_world(self, reason: str) -> SaveResult:
        result = SaveResult(scope="world", reason=reason)
        try:
            self.services.repo.world_state.save(self.services.world, self.services.npcs.npcs)
            version = self.services.repo.world_state.save_version()
            result.saved_world = True
            self.services.repo.save_manifests.record(
                SaveManifest(scope="world", reason=reason, world_save_version=version, status="ok")
            )
            self.services.event_bus.emit("save.world_completed", reason=reason, save_version=version)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            result.errors.append(message)
            self.services.repo.save_manifests.record(SaveManifest(scope="world", reason=reason, status="failed", error=message))
            self.services.event_bus.emit("save.world_failed", reason=reason, error=message)
        return result

    def flush_all(self, players: list[Character], reason: str) -> SaveResult:
        aggregate = SaveResult(scope="full", reason=reason)
        self.services.event_bus.emit("save.flush_started", reason=reason, character_count=len(players))
        for player in players:
            if not player.username:
                continue
            character_result = self.save_character(player, reason)
            aggregate.saved_characters += character_result.saved_characters
            aggregate.errors.extend(character_result.errors)
        world_result = self.save_world(reason)
        aggregate.saved_world = world_result.saved_world
        aggregate.errors.extend(world_result.errors)
        self.services.repo.save_manifests.record(
            SaveManifest(
                scope="full",
                reason=reason,
                world_save_version=self.services.repo.world_state.save_version(),
                status="ok" if aggregate.ok else "partial_failed",
                error="; ".join(aggregate.errors),
            )
        )
        self.services.event_bus.emit(
            "save.flush_completed" if aggregate.ok else "save.flush_partial_failed",
            reason=reason,
            saved_characters=aggregate.saved_characters,
            saved_world=aggregate.saved_world,
            errors=list(aggregate.errors),
        )
        return aggregate

    def recover_world(self) -> bool:
        loaded = self.services.repo.world_state.load_into(self.services.world, self.services.npcs.npcs, self.services.npcs.factory)
        self.services.repo.save_manifests.record(SaveManifest(scope="world_recovery", reason="bootstrap", status="ok" if loaded else "empty"))
        self.services.event_bus.emit("save.world_recovered" if loaded else "save.world_recovery_empty")
        return loaded

    def create_checkpoint(self, reason: str, directory: str | Path | None = None) -> Path:
        target_dir = Path(directory or self.policy.checkpoint_directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_reason = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in reason).strip("_") or "checkpoint"
        target = target_dir / f"astergard_{int(time())}_{safe_reason}.db"
        path = self.services.repo.create_backup(target)
        self.services.repo.save_manifests.record(SaveManifest(scope="backup", reason=reason, status="ok"))
        self.services.event_bus.emit("save.backup_created", reason=reason, path=str(path))
        return path

    def restore_checkpoint(self, source: str | Path, reason: str = "manual_restore") -> None:
        self.services.repo.restore_backup(source)
        self.services.repo.save_manifests.record(SaveManifest(scope="restore", reason=reason, status="ok"))
        self.services.event_bus.emit("save.backup_restored", reason=reason, path=str(source))
