from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from astergard.server.context import GameContext

if TYPE_CHECKING:
    from astergard.application.services.communication_service import CommunicationService

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_communication_handlers(service: CommunicationService) -> dict[str, CommandHandler]:
    async def cmd_say(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.say(ctx.communication_context(), arg)

    async def cmd_emote(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.emote(ctx.communication_context(), arg)

    async def cmd_shout(ctx: GameContext, arg: str | None, index: int) -> str:
        return service.shout(ctx.communication_context(), arg)

    return {"say": cmd_say, "emote": cmd_emote, "shout": cmd_shout}
