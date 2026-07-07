from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.application.services.exploration_service import DIRECTIONS as DIRECTIONS
from astergard.characters.models import Character
from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.exploration_service import ExplorationService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_exploration_handlers(service: ExplorationService) -> dict[str, CommandHandler]:
    async def cmd_look(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.look(ctx.exploration(), arg, index)

    async def cmd_move(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.move_from_command(ctx.exploration(), arg)

    async def cmd_search(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.search(ctx.exploration(), arg, index)

    return {"look": cmd_look, "move": cmd_move, "search": cmd_search}


def move_direct_with(service: ExplorationService, ctx: GameContext, char: Character, direction: str) -> str:
    return service.move_direct(ctx.exploration(), char, direction)


__all__ = ["DIRECTIONS", "build_exploration_handlers", "move_direct_with", "CommandHandler"]
