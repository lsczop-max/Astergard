from __future__ import annotations

from astergard.application.services.exploration_parts import (
    DIRECTIONS,
    ExplorationActionService,
    ExplorationTargetResolver,
)
from astergard.application.services.exploration_perception import ExplorationPerceptionService
from astergard.application.services.exploration_scene import ExplorationSceneRenderer
from astergard.application.use_case_contexts import ExplorationContext
from astergard.characters.models import Character
from astergard.rules.movement import MovementRules, SearchRules, default_movement_rules, default_search_rules


class ExplorationService:
    """Application service for location rendering, movement and searching."""

    def __init__(
        self,
        movement_rules: MovementRules | None = None,
        search_rules: SearchRules | None = None,
        ) -> None:
        self.movement_rules = movement_rules or default_movement_rules()
        self.search_rules = search_rules or default_search_rules()
        self.scene_renderer = ExplorationSceneRenderer()
        self.scene_service = self.scene_renderer
        self.target_resolver = ExplorationTargetResolver()
        self.perception_service = ExplorationPerceptionService(self.target_resolver, self.scene_renderer)
        self.action_service = ExplorationActionService(
            self.movement_rules,
            self.search_rules,
            self.target_resolver,
        )

    def look(self, ctx: ExplorationContext, arg: str | None, index: int) -> str:
        return self.perception_service.look(ctx, arg, index)

    def move_from_command(self, ctx: ExplorationContext, arg: str | None) -> str:
        return self.action_service.move_from_command(ctx, ctx.character, ctx.current_command, arg, self.look)

    def move_direct(self, ctx: ExplorationContext, char: Character, direction: str) -> str:
        return self.action_service.move_direct(ctx, char, direction, self.look)

    def search(self, ctx: ExplorationContext, arg: str | None = None, index: int = 1) -> str:
        return self.action_service.search(ctx, arg, index)

    def sense(self, ctx: ExplorationContext, arg: str | None, index: int) -> str:
        return self.perception_service.sense(ctx, arg, index)


__all__ = ["DIRECTIONS", "ExplorationService"]
