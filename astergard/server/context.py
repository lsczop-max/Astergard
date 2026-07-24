from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from astergard.application.use_case_contexts import (
    CombatContext,
    CommunicationContext,
    EconomyContext,
    ExplorationContext,
    InventoryContext,
    LocationChangeOutbox,
    QuestContext,
    SystemContext,
    AdminContext,
)
from astergard.characters.models import Character


@dataclass(slots=True)
class GameContext:
    """Per-command context composed from explicit use-case ports.

    D9 removes service-container knowledge from this object. It is no longer a
    factory over ``GameServices`` and it does not know how dependencies are
    assembled. The bootstrap/application assembly layer builds the concrete
    use-case contexts and passes them here as explicit ports.
    """

    character: Character
    exploration_port: ExplorationContext
    inventory_port: InventoryContext
    combat_port: CombatContext
    quest_port: QuestContext
    economy_port: EconomyContext
    system_port: SystemContext
    communication_port: CommunicationContext
    admin_port: AdminContext
    players_in_room: Callable[[int], list[Character]]
    location_changes: LocationChangeOutbox
    observability: Any | None = None

    def players_in_current_room(self) -> list[Character]:
        return self.players_in_room(self.character.room_id)

    def exploration(self) -> ExplorationContext:
        return self.exploration_port

    def inventory(self) -> InventoryContext:
        return self.inventory_port

    def combat_context(self) -> CombatContext:
        return self.combat_port

    def quest_context(self) -> QuestContext:
        return self.quest_port

    def economy_context(self) -> EconomyContext:
        return self.economy_port

    def system_context(self) -> SystemContext:
        return self.system_port

    def communication_context(self) -> CommunicationContext:
        return self.communication_port

    def admin_context(self) -> AdminContext:
        return self.admin_port

    @property
    def admin(self) -> AdminContext:
        return self.admin_port

    @property
    def world(self):
        return self.exploration_port.world

    @property
    def repo(self):
        return self.system_port.repo
