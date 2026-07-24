from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from astergard.application.bootstrap import GameBootstrapper, GameServices
from astergard.application.heartbeat import HeartbeatService
from astergard.application.session_transport import SessionCapability, SessionEvent, SessionTransportKind
from astergard.characters.models import Character
from astergard.server.game import GameServer
from astergard.testing import MemorySessionTransport


class D3ApplicationServiceTests(unittest.TestCase):
    def test_bootstrapper_builds_complete_service_graph(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            services = GameBootstrapper(tmp.name).build()
        self.assertIsInstance(services, GameServices)
        self.assertEqual(len(services.world.locations), 500)
        self.assertIn("oferta", services.dispatcher.commands)
        self.assertGreater(sum(len(loc.npc_ids) for loc in services.world.locations.values()), 0)

    def test_heartbeat_tick_is_testable_without_network_server(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            server = GameServer(tmp.name)
        char = Character("tick")
        char.stats.kondycja = 1
        heartbeat = HeartbeatService(server.services, lambda: [char])
        heartbeat.tick_once()
        self.assertGreater(char.stats.kondycja, 1)

    def test_server_game_delegates_bootstrap_and_flow(self) -> None:
        root = Path(__file__).resolve().parents[1]
        text = (root / "astergard" / "server" / "game.py").read_text(encoding="utf-8")
        self.assertIn("GameBootstrapper", text)
        self.assertIn("SessionFlow", text)
        self.assertIn("HeartbeatService", text)
        self.assertLess(len(text.splitlines()), 180)


class _FailingWebTransport:
    kind = SessionTransportKind.WEB
    capabilities = frozenset({SessionCapability.RAW_TEXT, SessionCapability.PROMPT, SessionCapability.STRUCTURED_EVENTS, SessionCapability.WEB_JSON})

    def __init__(self) -> None:
        self.sent: list[SessionEvent] = []
        self.closed = False

    async def send_text(self, text: str) -> None:
        raise AssertionError(text)

    async def send_prompt(self, prompt: str) -> None:
        raise AssertionError(prompt)

    async def send_event(self, event: SessionEvent) -> None:
        self.sent.append(event)
        raise RuntimeError("boom")

    async def close(self) -> None:
        self.closed = True


class HeartbeatFlushTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile()
        self.server = GameServer(self.tmp.name)

    async def asyncTearDown(self) -> None:
        self.tmp.close()

    async def test_heartbeat_flushes_changed_vitals_to_active_web_transport(self) -> None:
        self.assertTrue(self.server.repo.register("web", "secret"))
        character = self.server.repo.load("web")
        character.stats.wytrzymalosc = 0
        character.stats.kondycja = 1
        transport = MemorySessionTransport()
        self.server.clients[transport] = character

        changed = self.server.heartbeat.tick_once()
        self.assertIn(character, changed)
        await self.server._flush_heartbeat_vitals(changed)

        vitals_events = [event for event in transport.outbound_events if event.type == "character.vitals"]
        self.assertEqual(len(vitals_events), 1)
        self.assertEqual(vitals_events[0].payload["stamina_current"], 0)
        self.assertEqual(vitals_events[0].sequence, 1)

        changed_again = self.server.heartbeat.tick_once()
        await self.server._flush_heartbeat_vitals(changed_again)
        vitals_events_after = [event for event in transport.outbound_events if event.type == "character.vitals"]
        self.assertEqual(len(vitals_events_after), 1)

    async def test_heartbeat_without_vitals_change_does_not_flush_or_advance_sequence(self) -> None:
        self.assertTrue(self.server.repo.register("steady", "secret"))
        character = self.server.repo.load("steady")
        character.stats.kondycja = character.stats.max_kondycja
        transport = MemorySessionTransport()
        self.server.clients[transport] = character

        with (
            patch.object(self.server.heartbeat.services.npcs, "ai_tick", return_value=None),
            patch.object(self.server.heartbeat.services.npcs, "respawn_tick", return_value=None),
            patch.object(self.server.heartbeat, "process_combat_rounds", return_value=None),
            patch.object(self.server.heartbeat, "tick_character", wraps=self.server.heartbeat.tick_character) as tick_character,
        ):
            changed = self.server.heartbeat.tick_once()

        tick_character.assert_called_once_with(character)
        self.assertEqual(changed, [])
        self.assertEqual(transport.outbound_events, [])
        self.assertFalse(transport.closed)
        self.assertIs(self.server.clients.get(transport), character)
        self.assertNotIn(id(transport), self.server.session_flow._sequence_by_transport)

        await self.server._flush_heartbeat_vitals(changed)

        self.assertEqual(transport.outbound_events, [])
        self.assertFalse(transport.closed)
        self.assertIs(self.server.clients.get(transport), character)
        self.assertNotIn(id(transport), self.server.session_flow._sequence_by_transport)

    async def test_heartbeat_routes_by_character_identity_and_skips_tcp(self) -> None:
        first = Character("same")
        second = Character("same")
        first.stats.kondycja = 1
        second.stats.kondycja = 20
        active_web = MemorySessionTransport()
        skipped_tcp = MemorySessionTransport(kind=SessionTransportKind.TCP)
        self.server.clients[active_web] = first
        self.server.clients[skipped_tcp] = second

        await self.server._flush_heartbeat_vitals([second])

        self.assertFalse(any(event.type == "character.vitals" for event in active_web.outbound_events))
        self.assertFalse(any(event.type == "character.vitals" for event in skipped_tcp.outbound_events))

        await self.server._flush_heartbeat_vitals([first])
        self.assertEqual(sum(1 for event in active_web.outbound_events if event.type == "character.vitals"), 1)

    async def test_heartbeat_reconnect_survives_old_transport_send_failure(self) -> None:
        self.assertTrue(self.server.repo.register("reconnect", "secret"))
        character = self.server.repo.load("reconnect")
        character.stats.kondycja = 1

        started = asyncio.Event()
        proceed = asyncio.Event()
        transport_a = _BlockingFailingWebTransport(started, proceed)
        transport_b = MemorySessionTransport()
        self.server.clients[transport_a] = character

        flush_task = asyncio.create_task(self.server._flush_heartbeat_vitals([character]))
        await started.wait()
        self.server.clients[transport_b] = character
        proceed.set()
        await flush_task

        self.assertTrue(transport_a.closed)
        self.assertNotIn(transport_a, self.server.clients)
        self.assertIs(self.server.clients.get(transport_b), character)
        self.assertFalse(transport_b.closed)
        self.assertEqual([event for event in transport_b.outbound_events if event.type == "character.vitals"], [])

        await self.server._flush_heartbeat_vitals([character])

        vitals_events = [event for event in transport_b.outbound_events if event.type == "character.vitals"]
        self.assertEqual(len(vitals_events), 1)
        self.assertIs(self.server.clients.get(transport_b), character)
        self.assertFalse(transport_b.closed)
        self.assertEqual(vitals_events[0].sequence, 1)

    async def test_heartbeat_send_failure_triggers_cleanup(self) -> None:
        self.assertTrue(self.server.repo.register("boom", "secret"))
        character = self.server.repo.load("boom")
        character.stats.kondycja = 1
        transport = _FailingWebTransport()
        self.server.clients[transport] = character  # type: ignore[index]

        await self.server._flush_heartbeat_vitals([character])

        self.assertTrue(transport.closed)
        self.assertNotIn(transport, self.server.clients)


class _BlockingFailingWebTransport(MemorySessionTransport):
    def __init__(self, started: asyncio.Event, proceed: asyncio.Event) -> None:
        super().__init__()
        self._started = started
        self._proceed = proceed

    async def send_event(self, event: SessionEvent) -> None:
        self.outbound_events.append(event)
        self._started.set()
        await self._proceed.wait()
        raise RuntimeError("boom")


if __name__ == "__main__":
    unittest.main()
