from __future__ import annotations

from astergard.application.use_case_contexts import CommunicationContext
from astergard.engine.events import DomainEventType


class CommunicationService:
    def say(self, ctx: CommunicationContext, message: str | None) -> str:
        if not message:
            return "Co chcesz powiedzieć?"
        ctx.event_bus.emit(DomainEventType.CHARACTER_SPOKE, username=ctx.character.username, room_id=ctx.character.room_id, message=message)
        return f"Mówisz: {message}"

    def emote(self, ctx: CommunicationContext, message: str | None) -> str:
        if not message:
            return "Co chcesz zrobić?"
        ctx.event_bus.emit(DomainEventType.CHARACTER_EMOTED, username=ctx.character.username, room_id=ctx.character.room_id, message=message)
        return f"<yellow>{ctx.character.username} {message}</yellow>"

    def shout(self, ctx: CommunicationContext, message: str | None) -> str:
        if not message:
            return "Co chcesz krzyknąć?"
        if ctx.character.stats.kondycja < 10:
            return "Brakuje ci kondycji."
        ctx.character.stats.kondycja -= 10
        ctx.event_bus.emit(DomainEventType.CHARACTER_SHOUTED, username=ctx.character.username, room_id=ctx.character.room_id, zone="unknown", message=message, stamina_cost=10)
        return f"<yellow>Krzyczysz: {message}</yellow>"
