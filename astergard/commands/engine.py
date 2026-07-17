from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from difflib import get_close_matches
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from astergard.commands.polish import normalize_phrase

CommandHandler = Callable[[Any, str | None, int], Awaitable[str]]


class PermissionLevel(str, Enum):
    PLAYER = "player"
    HELPER = "helper"
    GM = "gm"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass(frozen=True, slots=True)
class CommandArgumentSpec:
    required: bool = False
    name: str = "argument"
    description: str = ""


@dataclass(frozen=True, slots=True)
class CommandMetadata:
    canonical_name: str
    description: str
    usage: str
    group: str = "Ogólne"
    cooldown_seconds: float = 0.0
    permission: PermissionLevel = PermissionLevel.PLAYER
    argument: CommandArgumentSpec = field(default_factory=CommandArgumentSpec)


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    handler: CommandHandler
    metadata: CommandMetadata
    aliases: tuple[str, ...]


class CommandRegistry:
    def __init__(self) -> None:
        self._specs: dict[str, CommandSpec] = {}
        self._canonical_specs: dict[str, CommandSpec] = {}

    def register(self, aliases: list[str], handler: CommandHandler, metadata: CommandMetadata) -> None:
        if not aliases:
            raise ValueError("Command must have at least one alias.")
        spec = CommandSpec(name=metadata.canonical_name, handler=handler, metadata=metadata, aliases=tuple(aliases))
        self._canonical_specs[metadata.canonical_name] = spec
        seen_in_command: set[str] = set()
        for alias in aliases:
            normalized = normalize_phrase(alias)
            if not normalized:
                raise ValueError("Command alias cannot be empty.")
            if normalized in seen_in_command:
                continue
            seen_in_command.add(normalized)
            if normalized in self._specs:
                raise ValueError(f"Duplicate command alias: {normalized}")
            self._specs[normalized] = spec

    def get(self, alias: str) -> CommandSpec | None:
        normalized = normalize_phrase(alias)
        spec = self._specs.get(normalized)
        if spec is not None:
            return spec
        matches = get_close_matches(normalized, self._specs.keys(), n=1, cutoff=0.84)
        if matches:
            return self._specs[matches[0]]
        return None

    def all_specs(self) -> list[CommandSpec]:
        return sorted(self._canonical_specs.values(), key=lambda spec: (spec.metadata.group, spec.name))

    def aliases_for(self, canonical_name: str) -> tuple[str, ...]:
        spec = self._canonical_specs[canonical_name]
        return spec.aliases


class CooldownTracker:
    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._last_used: dict[tuple[str, str], float] = {}

    def remaining(self, actor_id: str, command_name: str, cooldown_seconds: float) -> float:
        if cooldown_seconds <= 0:
            return 0.0
        last_used = self._last_used.get((actor_id, command_name))
        if last_used is None:
            return 0.0
        return max(0.0, cooldown_seconds - (self._clock() - last_used))

    def mark_used(self, actor_id: str, command_name: str) -> None:
        self._last_used[(actor_id, command_name)] = self._clock()


def actor_identifier(context: Any) -> str:
    character = getattr(context, "character", None)
    username = getattr(character, "username", None)
    return str(username or id(context))


def has_permission(context: Any, required: PermissionLevel) -> bool:
    if required is PermissionLevel.PLAYER:
        return True
    character = getattr(context, "character", None)
    try:
        from astergard.admin.permissions import has_role

        return has_role(character, required.value)
    except Exception:
        return bool(getattr(character, "is_admin", False) or getattr(character, "username", "") == "admin")


def render_help(registry: CommandRegistry, command_name: str | None = None, context: Any | None = None) -> str:
    if command_name:
        normalized = normalize_phrase(command_name)
        if normalized in {"zbroja", "wyposazenie", "wyposażenie", "armor", "pancerz"}:
            return (
                "Jak nosisz rzeczy:\n"
                "O rynsztunku:\n"
                "Na ciele możesz nosić hełm, pancerz, rękawice, pas, buty i drobiazgi przy sobie.\n"
                "Bronie trzymasz w dłoniach, tarcza odpoczywa przy boku, a pierścienie i amulet spoczywają osobno.\n"
                "Gdy chcesz coś wziąć na siebie, użyj komendy załóż. Gdy chcesz to zdjąć, użyj zdejmij."
            )
        spec = registry.get(command_name)
        if spec is None:
            return "Nie odnajdujesz takiej komendy w księdze."
        aliases = ", ".join(spec.aliases)
        return f"{spec.metadata.canonical_name}: {spec.metadata.description}\nJak to zrobić: {spec.metadata.usage}\nZnane nazwy: {aliases}"

    grouped: dict[str, list[CommandSpec]] = {}
    for spec in registry.all_specs():
        if context is not None and not has_permission(context, spec.metadata.permission):
            continue
        grouped.setdefault(spec.metadata.group, []).append(spec)
    lines = ["Księga podróżnika", "", "Co możesz zrobić:"]
    for group, specs in grouped.items():
        lines.append(f"\n{group}")
        for spec in specs:
            primary = spec.aliases[0]
            lines.append(f"  {primary:<14} - {spec.metadata.description}")
    lines.append("\nDla szczegółów wpisz: pomoc <komenda>.")
    return "\n".join(lines)
