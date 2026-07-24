from __future__ import annotations

import os
from typing import Any

from astergard.characters.models import Character
from astergard.combat.wounds import overall_health_desc
from astergard.commands.exploration import move_direct_with
from astergard.commands.helpers import find_item, find_npc
from astergard.items.models import Item
from astergard.npcs.models import NPC
from astergard.server.context import GameContext
from astergard.application.session_transport import SessionTransport, SessionTransportKind
from astergard.utils import describe_gold


class GameServerSupportMixin:
    clients: Any
    services: Any
    context_assembler: Any
    dispatcher: Any
    exploration_service: Any
    _active_transports: set[Any]
    mudlet_map_enabled: bool

    def _register_transport(self, transport) -> None:
        self._active_transports.add(transport)

    def _unregister_transport(self, transport) -> None:
        self._active_transports.discard(transport)

    async def _close_active_transports(self) -> None:
        transports = list(self._active_transports)
        for transport in transports:
            try:
                await transport.close()
            except Exception:
                pass

    @staticmethod
    def _resolve_mudlet_map_enabled(mudlet_map_enabled: bool | None) -> bool:
        if mudlet_map_enabled is not None:
            return mudlet_map_enabled
        return os.getenv("ASTERGARD_MUDLET_MAP", "").strip().lower() in {"1", "true", "yes", "on"}

    def _expose_services(self) -> None:
        self.repo = self.services.repo
        self.world = self.services.world
        self.npcs = self.services.npcs
        self.combat = self.services.combat
        self.factions = self.services.factions
        self.quests = self.services.quests
        self.economy = self.services.economy
        self.crafting = self.services.crafting
        self.weather = self.services.weather
        self.admin = self.services.admin
        self.dispatcher = self.services.dispatcher

    def _install_compatibility_methods(self) -> None:
        aliases = {
            "cmd_look": "look",
            "cmd_move": "polnoc",
            "cmd_say": "powiedz",
            "cmd_emote": "em",
            "cmd_shout": "krzycz",
            "cmd_sense": "zbadaj",
            "cmd_score": "cechy",
            "cmd_profile": "profil",
            "cmd_postac": "postac",
            "cmd_skills": "umiejetnosci",
            "cmd_inventory": "ekwipunek",
            "cmd_get": "wez",
            "cmd_drop": "upusc",
            "cmd_wear": "zaloz",
            "cmd_remove": "zdejmij",
            "cmd_kill": "zabij",
            "cmd_flee": "ucieczka",
            "cmd_talk": "rozmawiaj",
            "cmd_quests": "zadania",
            "cmd_offer": "oferta",
            "cmd_buy": "kup",
            "cmd_sell": "sprzedaj",
            "cmd_search": "szukaj",
            "cmd_consume": "zjedz",
            "cmd_craft": "craft",
            "cmd_reputation": "reputacja",
            "cmd_ranking": "ranking",
            "cmd_save": "zapisz",
            "cmd_quit": "quit",
        }
        for public_name, command_name in aliases.items():
            handler = self.dispatcher.commands[command_name]
            setattr(self, public_name, handler)

    def make_context(self, character: Character) -> GameContext:
        return self.context_assembler.build(character)

    def find_item(self, items: list[Item], name: str, index: int = 1) -> Item | None:
        return find_item(items, name, index)

    def find_npc(self, room_id: int, name: str) -> NPC | None:
        return find_npc(self.make_context(Character("lookup")), room_id, name)

    def move_direct(self, char: Character, direction: str) -> str:
        return move_direct_with(self.services.exploration_service, self.make_context(char), char, direction)

    def get_players_in_room(self, room_id: int) -> list[Character]:
        return [char for char in self.clients.values() if char.room_id == room_id and char.is_alive]

    def get_all_players(self) -> list[Character]:
        return list(self.clients.values())

    def prompt(self, character: Character, transport: SessionTransport | None = None) -> str:
        if transport is not None and transport.kind == SessionTransportKind.WEB:
            return ">"
        health = overall_health_desc(character.wounds)
        stamina = character.stats.describe_kondycja()
        gold = describe_gold(character.gold)
        return f"{stamina}, {health}, {gold}. > "
