from __future__ import annotations

from collections.abc import Callable

from astergard.characters.models import Character
from astergard.engine.events import DomainEventType, EngineEvent, EventBus
from astergard.factions.reputation import FactionManager
from astergard.npcs.manager import NPCManager
from astergard.npcs.models import NPC


class WorldReactionService:
    LOCAL_ZONES = {"Centrum_Twierdza", "Podgrodzie", "Straznica_Przeleczy", "Puszcza_Ciszy", "Knieja_Cichych_Sciezek", "Bagna_Hookri"}
    HELP_REP = 5
    THEFT_REP = -2
    ATTACK_REP = -18

    def __init__(
        self,
        event_bus: EventBus,
        factions: FactionManager,
        npcs: NPCManager,
        player_lookup: Callable[[], list[Character]],
    ) -> None:
        self.event_bus = event_bus
        self.factions = factions
        self.npcs = npcs
        self.player_lookup = player_lookup

    def subscribe(self, event_bus) -> None:
        event_bus.subscribe(DomainEventType.QUEST_COMPLETED, self.on_quest_completed)
        event_bus.subscribe(DomainEventType.COMBAT_ATTACKED, self.on_combat_attacked)
        event_bus.subscribe(DomainEventType.ITEM_PICKED_UP, self.on_item_picked_up)

    def on_quest_completed(self, event: EngineEvent) -> None:
        char = self._player(event)
        if char is None:
            return
        rep = int(event.payload.get("rep", 0))
        zone = self._zone(char.room_id)
        if rep:
            self.factions.adjust(char, self.factions.MEEKHAN, rep, zone=zone)
        quest_id = str(event.payload.get("quest_id", ""))
        if quest_id in {"market_delivery", "blacksmith_tools", "fisher_net", "priest_herbs", "city_ring_search", "merchant_price_check", "dockside_rumor", "pilgrim_escort", "wheel_repair", "shield_repair", "wolf_watch", "fish_delivery", "grain_delivery", "wood_delivery", "candles_gather", "well_water_delivery", "haldun_well_bucket", "haldun_forge_coal", "haldun_grain_delivery", "haldun_barn_beam", "haldun_orchard_crate", "haldun_watch_round", "straznica_meldunek", "straznica_manifest", "straznica_lamp_oil", "straznica_rope", "straznica_blanket", "straznica_hunter_report", "trakty_kurier_note", "trakty_manifest", "trakty_lamp_oil", "trakty_rope", "trakty_blanket", "trakty_hunter_report", "puszcza_herbs", "puszcza_camp_token", "puszcza_stream_water", "bagna_herbs", "bagna_stone", "bagna_tracks"}:
            self.factions.adjust(char, self.factions.MEEKHAN, self.HELP_REP, zone=zone)
        self._emit_reputation_changed(char, "quest")

    def on_combat_attacked(self, event: EngineEvent) -> None:
        char = self._player(event)
        if char is None:
            return
        room_id = int(event.payload.get("room_id", char.room_id))
        npc = self._local_npc(room_id, str(event.payload.get("target", "")))
        if npc is None or npc.faction != self.factions.MEEKHAN:
            return
        if self._zone(room_id) not in self.LOCAL_ZONES:
            return
        if bool(event.payload.get("defender_dead", False)):
            return
        penalty = self.ATTACK_REP
        zone = self._zone(room_id)
        self.factions.adjust(char, self.factions.MEEKHAN, penalty, zone=zone)
        self.factions.record_crime(char, "napaść", zone=zone, detail=npc.vnum)
        self._emit_reputation_changed(char, "attack")

    def on_item_picked_up(self, event: EngineEvent) -> None:
        char = self._player(event)
        if char is None:
            return
        room_id = event.payload.get("room_id")
        if room_id is None or self._zone(int(room_id)) not in self.LOCAL_ZONES:
            return
        if not self.npcs.by_room(int(room_id)):
            return
        zone = self._zone(int(room_id))
        self.factions.adjust(char, self.factions.MEEKHAN, self.THEFT_REP, zone=zone)
        self.factions.record_crime(char, "kradzież", zone=zone, detail=str(event.payload.get("item", "")))
        self._emit_reputation_changed(char, "theft")

    def _player(self, event: EngineEvent) -> Character | None:
        character = event.payload.get("character")
        if isinstance(character, Character):
            return character
        username = str(event.payload.get("username", ""))
        return next((player for player in self.player_lookup() if player.username == username), None)

    def _local_npc(self, room_id: int, target: str) -> NPC | None:
        return next((npc for npc in self.npcs.by_room(room_id) if npc.vnum == target or npc.name == target), None)

    def _zone(self, room_id: int) -> str:
        loc = self.npcs.world.get_location(room_id)
        return loc.zone if loc is not None else ""

    def _emit_reputation_changed(self, char: Character, reason: str) -> None:
        self.event_bus.emit(DomainEventType.REPUTATION_CHANGED, username=char.username, faction=self.factions.MEEKHAN, reason=reason, value=char.reputation.get(self.factions.MEEKHAN, 0))
