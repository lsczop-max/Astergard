from __future__ import annotations

from astergard.application.use_case_contexts import SystemContext
from astergard.engine.events import DomainEventType
from astergard.application.services.minimap_service import MinimapService


class SystemCommandService:
    def ranking(self, ctx: SystemContext, arg: str | None) -> str:
        return ctx.repo.ranking(arg or "gold")

    def save(self, ctx: SystemContext) -> str:
        ctx.repo.save(ctx.character)
        ctx.event_bus.emit(DomainEventType.CHARACTER_SAVED, username=ctx.character.username, room_id=ctx.character.room_id)
        return "Postać została zapisana."

    def quit(self, ctx: SystemContext) -> str:
        ctx.repo.save(ctx.character)
        ctx.event_bus.emit(DomainEventType.CHARACTER_SAVED, username=ctx.character.username, room_id=ctx.character.room_id, reason="quit")
        ctx.character.die()
        return "Twoja postać odchodzi w ciszę."

    def debug_map(self, ctx: SystemContext, minimap_service: MinimapService) -> str:
        if not minimap_service.enabled:
            return "Podgląd mapy jest jeszcze ukryty."
        return "Wysyłam podgląd mapy."
