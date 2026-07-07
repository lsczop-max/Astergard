from __future__ import annotations

import asyncio

from astergard.application.bootstrap import GameBootstrapper, GameServices
from astergard.application.context_assembler import GameContextAssembler
from astergard.application.heartbeat import HeartbeatService
from astergard.engine.lifecycle import EngineLifecycle
from astergard.application.session_flow import SessionFlow
from astergard.characters.models import Character
from astergard.combat.wounds import overall_health_desc
from astergard.commands.dispatcher import CommandFunc
from astergard.commands.exploration import DIRECTIONS, move_direct_with
from astergard.commands.helpers import find_item, find_npc
from astergard.items.models import Item
from astergard.npcs.models import NPC
from astergard.server.context import GameContext


class GameServer:
    cmd_look: CommandFunc
    cmd_move: CommandFunc
    cmd_say: CommandFunc
    cmd_emote: CommandFunc
    cmd_shout: CommandFunc
    cmd_score: CommandFunc
    cmd_profile: CommandFunc
    cmd_skills: CommandFunc
    cmd_inventory: CommandFunc
    cmd_get: CommandFunc
    cmd_drop: CommandFunc
    cmd_wear: CommandFunc
    cmd_remove: CommandFunc
    cmd_kill: CommandFunc
    cmd_flee: CommandFunc
    cmd_talk: CommandFunc
    cmd_quests: CommandFunc
    cmd_offer: CommandFunc
    cmd_buy: CommandFunc
    cmd_sell: CommandFunc
    cmd_search: CommandFunc
    cmd_consume: CommandFunc
    cmd_cast: CommandFunc
    cmd_craft: CommandFunc
    cmd_reputation: CommandFunc
    cmd_ranking: CommandFunc
    cmd_save: CommandFunc
    cmd_quit: CommandFunc

    """Network-facing orchestration layer.

    D8 keeps command construction inside the bootstrap/CommandBus path. The
    server exposes compatibility methods by binding to dispatcher entries, not
    by importing concrete command functions or the application service graph.
    """

    def __init__(self, db_path: str = "mud.db") -> None:
        self.clients: dict[asyncio.StreamWriter, Character] = {}
        self.services: GameServices = GameBootstrapper(db_path).build()
        self._expose_services()
        self.context_assembler = GameContextAssembler(self.services, self.get_players_in_room, self.move_direct, self.get_all_players)
        self.heartbeat = HeartbeatService(self.services, lambda: list(self.clients.values()))
        self.lifecycle = EngineLifecycle(self.services, lambda: list(self.clients.values()), self.services.event_bus, self.services.scheduler)
        self.session_flow = SessionFlow(self.services, self.make_context, self.prompt)
        self._install_compatibility_methods()

    def _expose_services(self) -> None:
        self.repo = self.services.repo
        self.world = self.services.world
        self.npcs = self.services.npcs
        self.combat = self.services.combat
        self.factions = self.services.factions
        self.quests = self.services.quests
        self.economy = self.services.economy
        self.crafting = self.services.crafting
        self.magic = self.services.magic
        self.weather = self.services.weather
        self.admin = self.services.admin
        self.dispatcher = self.services.dispatcher

    def _install_compatibility_methods(self) -> None:
        aliases = {
            "cmd_look": "look", "cmd_move": "polnoc", "cmd_say": "powiedz",
            "cmd_emote": "em", "cmd_shout": "krzycz", "cmd_score": "cechy",
            "cmd_profile": "profil", "cmd_skills": "umiejetnosci", "cmd_inventory": "ekwipunek", "cmd_get": "wez",
            "cmd_drop": "upusc", "cmd_wear": "zaloz", "cmd_remove": "zdejmij",
            "cmd_kill": "zabij", "cmd_flee": "ucieczka", "cmd_talk": "rozmawiaj",
            "cmd_quests": "zadania", "cmd_offer": "oferta", "cmd_buy": "kup",
            "cmd_sell": "sprzedaj", "cmd_search": "szukaj", "cmd_consume": "zjedz",
            "cmd_cast": "czaruj", "cmd_craft": "craft", "cmd_reputation": "reputacja",
            "cmd_ranking": "ranking", "cmd_save": "zapisz", "cmd_quit": "quit",
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

    def prompt(self, character: Character) -> str:
        max_stamina = character.stats.max_kondycja
        health = overall_health_desc(character.wounds)
        return f"[Kondycja: {character.stats.kondycja}/{max_stamina}] [Stan: {health}] [Złoto: {character.gold}] > "

    async def start(self, host: str = "0.0.0.0", port: int = 4000) -> None:
        heartbeat_task = asyncio.create_task(self.global_heartbeat())
        server = await asyncio.start_server(self.handle_connection, host, port)
        self.services.event_bus.emit("server.started", host=host, port=port)
        print(f"Astergard MUD działa na {host}:{port}")
        try:
            async with server:
                await server.serve_forever()
        finally:
            self.lifecycle.request_shutdown("server_stop")
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        character: Character | None = None
        try:
            login = await self.session_flow.login(reader, writer)
            if login.close_connection or login.character is None:
                return
            character = login.character
            self.clients[writer] = character
            ctx = self.make_context(character)
            await self.session_flow.send_initial_view(writer, ctx)
            await self.session_flow.command_loop(reader, writer, ctx)
        except (ConnectionResetError, asyncio.CancelledError):
            pass
        finally:
            if character is not None:
                self.services.save_load.save_character(character, "session_disconnect")
                self.services.event_bus.emit("session.character_saved", username=character.username)
            self.services.save_load.save_world("session_disconnect")
            self.clients.pop(writer, None)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def global_heartbeat(self) -> None:
        await self.lifecycle.run_forever(self.heartbeat.tick_once)

    def shutdown(self, reason: str = "manual") -> None:
        self.lifecycle.request_shutdown(reason)


__all__ = ["DIRECTIONS", "GameContext", "GameServer"]
