from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from astergard.characters.models import Character
from astergard.combat.manager import CombatManager
from astergard.crafting.services import CraftingService
from astergard.database.repository import PlayerRepository
from astergard.economy.services import EconomyService
from astergard.factions.reputation import FactionManager
from astergard.magic.services import MagicService
from astergard.npcs.manager import NPCManager
from astergard.quests.manager import QuestManager
from astergard.world.manager import WorldManager
from astergard.engine.events import EventBus
from astergard.weather.time_weather import TimeAndWeatherManager


@dataclass(slots=True)
class LocationChangeOutbox:
    characters: list[Character] = field(default_factory=list)

    def record(self, character: Character) -> None:
        self.characters.append(character)

    def drain(self) -> list[Character]:
        seen: set[int] = set()
        drained: list[Character] = []
        for character in self.characters:
            key = id(character)
            if key in seen:
                continue
            seen.add(key)
            drained.append(character)
        self.characters.clear()
        return drained


@dataclass(slots=True)
class ExplorationContext:
    character: Character
    event_bus: EventBus
    world: WorldManager
    weather: TimeAndWeatherManager
    npcs: NPCManager
    players_in_room: Callable[[int], list[Character]]
    current_command: str | None = None
    location_changes: LocationChangeOutbox = field(default_factory=LocationChangeOutbox)


@dataclass(slots=True)
class InventoryContext:
    character: Character
    event_bus: EventBus
    world: WorldManager


@dataclass(slots=True)
class CombatContext:
    character: Character
    event_bus: EventBus
    world: WorldManager
    npcs: NPCManager
    combat: CombatManager
    factions: FactionManager
    quests: QuestManager
    move_direct: Callable[[Character, str], str]
    players_in_room: Callable[[int], list[Character]] | None = None


@dataclass(slots=True)
class QuestContext:
    character: Character
    event_bus: EventBus
    npcs: NPCManager
    quests: QuestManager


@dataclass(slots=True)
class EconomyContext:
    character: Character
    event_bus: EventBus
    npcs: NPCManager
    economy: EconomyService


@dataclass(slots=True)
class MagicCraftingContext:
    character: Character
    event_bus: EventBus
    npcs: NPCManager
    magic: MagicService
    crafting: CraftingService


@dataclass(slots=True)
class SystemContext:
    character: Character
    event_bus: EventBus
    repo: PlayerRepository


@dataclass(slots=True)
class CommunicationContext:
    character: Character
    event_bus: EventBus


@dataclass(slots=True)
class AdminContext:
    character: Character
    event_bus: EventBus
    repo: PlayerRepository
    world: WorldManager
    npcs: NPCManager
    save_load: Any
    scheduler: Any
    observability: Any
    all_players: Callable[[], list[Character]]
    location_changes: LocationChangeOutbox = field(default_factory=LocationChangeOutbox)
