from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from astergard.admin.admin_service import AdminService

AdminHandler = Callable[[Any, str | None, int], Awaitable[str]]


def _confirmed_arg(arg: str | None) -> tuple[str | None, bool]:
    if arg is None:
        return None, False
    parts = arg.rsplit(maxsplit=1)
    if parts and parts[-1].lower() == "confirm":
        return (parts[0] if len(parts) > 1 else ""), True
    return arg, False


def build_admin_handlers(service: AdminService) -> dict[str, AdminHandler]:
    async def inspect(ctx: Any, arg: str | None, index: int) -> str:
        return service.inspect(ctx, arg).message

    async def teleport(ctx: Any, arg: str | None, index: int) -> str:
        return service.teleport(ctx, arg).message

    async def goto(ctx: Any, arg: str | None, index: int) -> str:
        return service.goto(ctx, arg).message

    async def summon(ctx: Any, arg: str | None, index: int) -> str:
        return service.summon(ctx, arg).message

    async def heal(ctx: Any, arg: str | None, index: int) -> str:
        return service.heal(ctx, arg).message

    async def kill(ctx: Any, arg: str | None, index: int) -> str:
        target_arg, confirmed = _confirmed_arg(arg)
        return service.kill(ctx, target_arg, confirmed).message

    async def give(ctx: Any, arg: str | None, index: int) -> str:
        return service.give(ctx, arg).message

    async def setstat(ctx: Any, arg: str | None, index: int) -> str:
        return service.setstat(ctx, arg).message

    async def spawnnpc(ctx: Any, arg: str | None, index: int) -> str:
        return service.spawnnpc(ctx, arg).message

    async def saveworld(ctx: Any, arg: str | None, index: int) -> str:
        return service.saveworld(ctx).message

    async def checkpoint(ctx: Any, arg: str | None, index: int) -> str:
        return service.checkpoint(ctx).message

    async def restore(ctx: Any, arg: str | None, index: int) -> str:
        source, confirmed = _confirmed_arg(arg)
        return service.restore(ctx, source, confirmed).message

    async def worldstats(ctx: Any, arg: str | None, index: int) -> str:
        return service.worldstats(ctx).message

    async def auditlog(ctx: Any, arg: str | None, index: int) -> str:
        return service.auditlog(ctx, arg).message

    async def scheduler(ctx: Any, arg: str | None, index: int) -> str:
        return service.scheduler(ctx).message

    async def listsessions(ctx: Any, arg: str | None, index: int) -> str:
        return service.listsessions(ctx).message


    async def metrics(ctx: Any, arg: str | None, index: int) -> str:
        return service.metrics(ctx).message

    async def events(ctx: Any, arg: str | None, index: int) -> str:
        return service.events(ctx, arg).message

    async def lag(ctx: Any, arg: str | None, index: int) -> str:
        return service.lag(ctx).message

    async def diagnostics(ctx: Any, arg: str | None, index: int) -> str:
        return service.diagnostics(ctx).message
    return {
        "inspect": inspect,
        "teleport": teleport,
        "goto": goto,
        "summon": summon,
        "heal": heal,
        "adminkill": kill,
        "give": give,
        "setstat": setstat,
        "spawnnpc": spawnnpc,
        "saveworld": saveworld,
        "checkpoint": checkpoint,
        "restore": restore,
        "worldstats": worldstats,
        "auditlog": auditlog,
        "scheduler": scheduler,
        "listsessions": listsessions,
        "metrics": metrics,
        "events": events,
        "lag": lag,
        "diagnostics": diagnostics,
    }
