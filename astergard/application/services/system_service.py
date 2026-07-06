from __future__ import annotations

from astergard.application.use_case_contexts import SystemContext
from astergard.engine.events import DomainEventType


class SystemCommandService:
    def ranking(self, ctx: SystemContext, arg: str | None) -> str:
        return ctx.repo.ranking(arg or "gold")

    def save(self, ctx: SystemContext) -> str:
        ctx.repo.save(ctx.character)
        ctx.event_bus.emit(DomainEventType.CHARACTER_SAVED, username=ctx.character.username, room_id=ctx.character.room_id)
        return "Zapisano postać."

    def quit(self, ctx: SystemContext) -> str:
        ctx.repo.save(ctx.character)
        ctx.event_bus.emit(DomainEventType.CHARACTER_SAVED, username=ctx.character.username, room_id=ctx.character.room_id, reason="quit")
        ctx.character.die()
        return "Żegnaj."
