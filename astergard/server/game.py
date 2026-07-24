from __future__ import annotations

import asyncio

from astergard.application.bootstrap import GameBootstrapper, GameServices
from astergard.application.context_assembler import GameContextAssembler
from astergard.application.heartbeat import HeartbeatService
from astergard.engine.lifecycle import EngineLifecycle
from astergard.application.session_flow import SessionFlow
from astergard.application.session_transport import SessionTransport, SessionTransportKind, TcpSessionTransport
from astergard.server.gateway import WebSocketGateway, WebSocketGatewayConfig
from astergard.server.game_support import GameServerSupportMixin
from astergard.characters.models import Character
from astergard.commands.dispatcher import CommandFunc


class GameServer(GameServerSupportMixin):
    cmd_look: CommandFunc
    cmd_move: CommandFunc
    cmd_say: CommandFunc
    cmd_emote: CommandFunc
    cmd_shout: CommandFunc
    cmd_sense: CommandFunc
    cmd_score: CommandFunc
    cmd_profile: CommandFunc
    cmd_postac: CommandFunc
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
    cmd_craft: CommandFunc
    cmd_reputation: CommandFunc
    cmd_ranking: CommandFunc
    cmd_save: CommandFunc
    cmd_quit: CommandFunc

    def __init__(self, db_path: str = "mud.db", mudlet_map_enabled: bool | None = None) -> None:
        self.clients: dict[SessionTransport, Character] = {}
        self._active_transports: set[SessionTransport] = set()
        self.services: GameServices = GameBootstrapper(db_path).build()
        self.services.server = self
        self.mudlet_map_enabled = self._resolve_mudlet_map_enabled(mudlet_map_enabled)
        self.services.minimap_service.enabled = self.mudlet_map_enabled
        self._expose_services()
        self.context_assembler = GameContextAssembler(self.services, self.get_players_in_room, self.move_direct, self.get_all_players)
        self.heartbeat = HeartbeatService(self.services, lambda: list(self.clients.values()))
        self.lifecycle = EngineLifecycle(self.services, lambda: list(self.clients.values()), self.services.event_bus, self.services.scheduler)
        self.session_flow = SessionFlow(self.services, self.make_context, self.prompt)
        self._install_compatibility_methods()

    async def start(
        self,
        host: str = "0.0.0.0",
        port: int = 4000,
        websocket_config: WebSocketGatewayConfig | None = None,
    ) -> None:
        websocket_gateway = WebSocketGateway(self, websocket_config or WebSocketGatewayConfig(allow_localhost_origin=True))
        heartbeat_task = asyncio.create_task(self.global_heartbeat())
        websocket_task = asyncio.create_task(websocket_gateway.run())
        self.services.event_bus.emit(
            "server.started",
            host=host,
            port=port,
            websocket_host=websocket_gateway.config.host,
            websocket_port=websocket_gateway.config.port,
        )
        print(
            f"Astergard MUD działa na {host}:{port} "
            f"oraz WebSocket na {websocket_gateway.config.host}:{websocket_gateway.config.port}"
        )
        tcp_server = await asyncio.start_server(self.handle_connection, host, port)
        try:
            while not self.lifecycle.shutdown_requested:
                if websocket_task.done():
                    websocket_error = websocket_task.exception()
                    if websocket_error is not None:
                        raise websocket_error
                    break
                if heartbeat_task.done():
                    heartbeat_error = heartbeat_task.exception()
                    if heartbeat_error is not None:
                        raise heartbeat_error
                    break
                await asyncio.sleep(0.1)
        finally:
            self.lifecycle.request_shutdown("server_stop")
            tcp_server.close()
            try:
                await tcp_server.wait_closed()
            except Exception:
                pass
            await websocket_gateway.close_active_connections()
            await self._close_active_transports()
            websocket_task.cancel()
            heartbeat_task.cancel()
            for task in (websocket_task, heartbeat_task):
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await self._run_session(TcpSessionTransport(reader, writer))

    async def _run_session(self, transport: SessionTransport) -> None:
        character: Character | None = None
        self._register_transport(transport)
        try:
            login = await self.session_flow.login(transport)
            if login.close_connection or login.character is None:
                return
            character = login.character
            self.clients[transport] = character
            context = self.make_context(character)
            await self.session_flow.send_initial_view(transport, context)
            await self.session_flow.command_loop(transport, context)
        except ConnectionResetError:
            pass
        except asyncio.CancelledError:
            raise
        finally:
            if character is not None:
                self.services.save_load.save_character(character, "session_disconnect")
                self.services.event_bus.emit("session.character_saved", username=character.username)
            self.services.save_load.save_world("session_disconnect")
            self.clients.pop(transport, None)
            self.session_flow.clear_transport_state(transport)
            self._unregister_transport(transport)
            try:
                await transport.close()
            except Exception:
                pass

    async def global_heartbeat(self) -> None:
        await self.lifecycle.run_forever(self.heartbeat.tick_once, self._flush_heartbeat_vitals)

    async def _flush_heartbeat_vitals(self, changed_characters: list[Character]) -> None:
        if not changed_characters:
            return
        changed_ids = {id(character) for character in changed_characters}
        for transport, character in list(self.clients.items()):
            if id(character) not in changed_ids:
                continue
            if transport.kind != SessionTransportKind.WEB:
                continue
            if self.clients.get(transport) is not character:
                continue
            try:
                await self.session_flow.send_character_vitals(transport, character)
            except Exception:
                self.clients.pop(transport, None)
                self.session_flow.clear_transport_state(transport)
                self._unregister_transport(transport)
                try:
                    await transport.close()
                except Exception:
                    pass

    def shutdown(self, reason: str = "manual") -> None:
        self.lifecycle.request_shutdown(reason)


__all__ = ["GameServer"]
