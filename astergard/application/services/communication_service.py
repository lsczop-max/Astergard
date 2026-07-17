from __future__ import annotations

from astergard.application.use_case_contexts import CommunicationContext
from astergard.engine.events import DomainEventType


class CommunicationService:
    def say(self, ctx: CommunicationContext, message: str | None) -> str:
        if not message:
            return "Nie wypowiadasz żadnych słów."
        ctx.event_bus.emit(DomainEventType.CHARACTER_SPOKE, username=ctx.character.username, room_id=ctx.character.room_id, message=message)
        return f"Mówisz: {message}"

    def emote(self, ctx: CommunicationContext, message: str | None) -> str:
        if not message:
            return "Nie wykonujesz żadnego gestu."
        ctx.event_bus.emit(DomainEventType.CHARACTER_EMOTED, username=ctx.character.username, room_id=ctx.character.room_id, message=message)
        return f"<yellow>{ctx.character.username} {message}</yellow>"

    def shout(self, ctx: CommunicationContext, message: str | None) -> str:
        if not message:
            return "Nie masz czego krzyczeć."
        if ctx.character.stats.kondycja < 10:
            return "Brakuje ci tchu, by zawołać tak głośno."
        ctx.character.stats.kondycja -= 10
        ctx.event_bus.emit(DomainEventType.CHARACTER_SHOUTED, username=ctx.character.username, room_id=ctx.character.room_id, zone="unknown", message=message, stamina_cost=10)
        return f"<yellow>Twój głos niesie się daleko: {message}</yellow>"
