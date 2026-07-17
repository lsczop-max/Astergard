from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.combat_service import CombatApplicationService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_combat_handlers(service: CombatApplicationService) -> dict[str, CommandHandler]:
    async def cmd_kill(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.attack_npc(ctx.combat_context(), arg, index)

    async def cmd_flee(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.flee(ctx.combat_context())

    async def cmd_defense_style(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.set_defense_style(ctx.combat_context(), arg)

    return {"kill": cmd_kill, "flee": cmd_flee, "defense_style": cmd_defense_style}
