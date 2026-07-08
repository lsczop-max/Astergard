from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.minimap_service import MinimapService
    from astergard.application.services.system_service import SystemCommandService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_system_handlers(service: SystemCommandService, minimap_service: MinimapService) -> dict[str, CommandHandler]:
    async def cmd_ranking(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.ranking(ctx.system_context(), arg)

    async def cmd_save(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.save(ctx.system_context())

    async def cmd_quit(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.quit(ctx.system_context())

    async def cmd_debug_map(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.debug_map(ctx.system_context(), minimap_service)

    return {"ranking": cmd_ranking, "save": cmd_save, "quit": cmd_quit, "debug_map": cmd_debug_map}
