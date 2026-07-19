from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from astergard.application.bootstrap import GameServices
from astergard.application.use_case_contexts import (
    CombatContext,
    CommunicationContext,
    EconomyContext,
    ExplorationContext,
    InventoryContext,
    MagicCraftingContext,
    LocationChangeOutbox,
    QuestContext,
    SystemContext,
    AdminContext,
)
from astergard.characters.models import Character
from astergard.server.context import GameContext


@dataclass(slots=True)
class GameContextAssembler:
    """Assembles command contexts from the application service graph.

    This is the only object allowed to translate the wide ``GameServices``
    graph into narrow use-case contexts. Keeping the assembly here prevents
    command handlers, services, and ``GameContext`` from depending on the full
    container.
    """

    services: GameServices
    players_in_room: Callable[[int], list[Character]]
    move_direct: Callable[[Character, str], str]
    all_players: Callable[[], list[Character]] | None = None

    def build(self, character: Character, current_command: str | None = None) -> GameContext:
        location_changes = LocationChangeOutbox()
        exploration = ExplorationContext(
            character=character,
            event_bus=self.services.event_bus,
            world=self.services.world,
            weather=self.services.weather,
            npcs=self.services.npcs,
            players_in_room=self.players_in_room,
            current_command=current_command,
            location_changes=location_changes,
        )
        return GameContext(
            character=character,
            exploration_port=exploration,
            inventory_port=InventoryContext(character=character, event_bus=self.services.event_bus, world=self.services.world),
            combat_port=CombatContext(
                character=character,
                event_bus=self.services.event_bus,
                world=self.services.world,
                npcs=self.services.npcs,
                combat=self.services.combat,
                factions=self.services.factions,
                quests=self.services.quests,
                move_direct=self.move_direct,
                players_in_room=self.players_in_room,
            ),
            quest_port=QuestContext(character=character, event_bus=self.services.event_bus, npcs=self.services.npcs, quests=self.services.quests),
            economy_port=EconomyContext(character=character, event_bus=self.services.event_bus, npcs=self.services.npcs, economy=self.services.economy),
            magic_crafting_port=MagicCraftingContext(
                character=character,
                event_bus=self.services.event_bus,
                npcs=self.services.npcs,
                magic=self.services.magic,
                crafting=self.services.crafting,
            ),
            system_port=SystemContext(character=character, event_bus=self.services.event_bus, repo=self.services.repo),
            communication_port=CommunicationContext(character=character, event_bus=self.services.event_bus),
            admin_port=AdminContext(
                character=character,
                event_bus=self.services.event_bus,
                repo=self.services.repo,
                world=self.services.world,
                npcs=self.services.npcs,
                save_load=self.services.save_load,
                scheduler=self.services.scheduler,
                observability=self.services.observability,
                all_players=self.all_players or (lambda: []),
                location_changes=location_changes,
            ),
            players_in_room=self.players_in_room,
            location_changes=location_changes,
            observability=self.services.observability,
        )
