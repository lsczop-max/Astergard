from __future__ import annotations

import asyncio
import random
from collections.abc import Callable

from astergard.application.bootstrap import GameServices
from astergard.application.character_vitals import build_character_vitals_payload
from astergard.characters.models import Character
from astergard.items.models import Item


class HeartbeatService:
    """Runs periodic world, NPC, weather, regeneration and effect updates."""

    def __init__(self, services: GameServices, players: Callable[[], list[Character]]) -> None:
        self.services = services
        self.players = players

    async def run_forever(self) -> None:
        while True:
            await asyncio.sleep(4)
            self.tick_once()

    def tick_once(self) -> list[Character]:
        players = list(self.players())
        before_by_id = {id(character): build_character_vitals_payload(character) for character in players}
        zones = list({loc.zone for loc in self.services.world.locations.values()})
        self.services.weather.tick(zones)
        if zones:
            zone = random.choice(zones)
            ambient = self.services.weather.ambient_event(zone)
            if ambient:
                self.services.world.set_ambient_message(zone, ambient)
        self.services.npcs.ai_tick(
            self.players(),
            self.services.combat,
            self.services.factions,
            hour=self.services.weather.hour,
            weather_by_zone=dict(self.services.weather.weather_by_zone),
        )
        self.process_combat_rounds()
        self.services.npcs.respawn_tick()
        self.services.event_bus.emit("world.respawn_tick_completed", npc_count=len(self.services.npcs.npcs))
        for character in players:
            try:
                self.tick_character(character)
            except Exception:
                continue
        changed_characters: list[Character] = []
        for character in players:
            before = before_by_id.get(id(character))
            if before is None:
                continue
            after = build_character_vitals_payload(character)
            if after != before:
                changed_characters.append(character)
        return changed_characters

    def tick_character(self, character: Character) -> None:
        loc = self.services.world.get_location(character.room_id)
        modifier = self.services.weather.regen_modifier(loc.zone if loc else "")
        regen = int((2 + character.stats.wytrzymalosc // 4) * modifier)
        character.stats.kondycja = min(character.stats.max_kondycja, character.stats.kondycja + regen)
        self.services.event_bus.emit("character.tick_completed", username=character.username, room_id=character.room_id)

    def process_combat_rounds(self) -> None:
        entities: dict[str, Character] = {player.username: player for player in self.players()}
        entities.update({getattr(npc.character, "combat_identity", npc.id): npc.character for npc in self.services.npcs.npcs.values()})
        self.services.combat.process_active_round(entities)
        for npc in list(self.services.npcs.npcs.values()):
            if not npc.character.is_alive:
                loc = self.services.world.get_location(npc.room_id)
                if loc is not None:
                    loc.items.append(
                        Item(
                            f"zwłoki {npc.name}",
                            "Ciało pokonanego przeciwnika.",
                            5.0,
                            0,
                            f"corpse_{npc.vnum}",
                            is_container=True,
                            capacity=999,
                            contains=list(npc.character.inventory),
                        )
                    )
                self.services.npcs.remove_dead(npc)
                self.services.event_bus.emit("npc.died", npc_id=npc.id, vnum=npc.vnum, room_id=npc.room_id)
        for player in self.players():
            if not player.is_alive:
                self.services.combat.end_fight(player.username, reason="DEATH", entities=entities)
