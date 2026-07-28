from __future__ import annotations

import asyncio
from collections import deque
import unittest
from typing import Any, cast

from astergard.characters.models import Character
from astergard.application.session_transport import SessionInputKind, TcpSessionTransport
from astergard.gmcp import room_info_packet
from astergard.server.gmcp_bridge import send_room_info_for_character
from astergard.testing import FakeReader, FakeWriter, MemorySessionTransport, TestGameHarness


class CountingWriter(FakeWriter):
    def __init__(self) -> None:
        super().__init__()
        self.close_calls = 0
        self.wait_closed_calls = 0

    def close(self) -> None:
        self.close_calls += 1
        super().close()

    async def wait_closed(self) -> None:
        self.wait_closed_calls += 1
        await super().wait_closed()


class ResetOnDrainWriter(FakeWriter):
    async def drain(self) -> None:
        raise ConnectionResetError


class CancelOnDrainWriter(FakeWriter):
    async def drain(self) -> None:
        raise asyncio.CancelledError


class InvalidUtf8Reader:
    def __init__(self, lines: list[bytes]) -> None:
        self.lines = deque(lines)

    async def readline(self) -> bytes:
        await asyncio.sleep(0)
        if self.lines:
            return self.lines.popleft()
        return b""

    def at_eof(self) -> bool:
        return not self.lines


class TrackingWriter(FakeWriter):
    def __init__(self) -> None:
        super().__init__()
        self.actions: list[tuple[str, bytes]] = []

    def write(self, data: bytes) -> None:
        payload = bytes(data)
        self.actions.append(("write", payload))
        super().write(payload)

    async def drain(self) -> None:
        self.actions.append(("drain", b""))
        await super().drain()


async def _login_and_initial_view(server, transport: TcpSessionTransport):
    login = await server.session_flow.login(transport)
    assert login.character is not None
    await server.session_flow.send_initial_view(transport, server.make_context(login.character))
    return login.character


class RoomInfoResetWriter(TrackingWriter):
    def __init__(self) -> None:
        super().__init__()
        self.room_info_drains = 0
        self.close_calls = 0
        self.wait_closed_calls = 0

    def close(self) -> None:
        self.close_calls += 1
        super().close()

    async def wait_closed(self) -> None:
        self.wait_closed_calls += 1
        await super().wait_closed()

    async def drain(self) -> None:
        last_write = self.actions[-1][1] if self.actions else b""
        await super().drain()
        if b"Room.Info" in last_write:
            self.room_info_drains += 1
            if self.room_info_drains >= 2:
                raise ConnectionResetError


class D59SessionResilienceTests(unittest.TestCase):
    def test_login_eof_closes_controlled(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            reader = FakeReader()
            writer = FakeWriter()
            transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
            result = asyncio.run(server.session_flow.login(transport))
            self.assertTrue(result.close_connection)
            self.assertIsNone(result.character)

    def test_command_loop_eof_exits_cleanly(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("eof", "secret"))
            login_reader = FakeReader.from_text_lines(["eof", "secret"])
            login_writer = FakeWriter()
            login_transport = TcpSessionTransport(cast(Any, login_reader), cast(Any, login_writer))
            login = asyncio.run(server.session_flow.login(login_transport))
            assert login.character is not None

            eof_transport = TcpSessionTransport(cast(Any, FakeReader()), cast(Any, login_writer))
            server.clients[eof_transport] = login.character
            asyncio.run(server.session_flow.command_loop(eof_transport, server.make_context(login.character)))

    def test_tcp_quit_reaches_dispatcher_and_saves(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("quitter", "secret"))
            reader = FakeReader.from_text_lines(["quitter", "secret", "quit"])
            writer = CountingWriter()
            asyncio.run(server.handle_connection(cast(Any, reader), cast(Any, writer)))
            self.assertIn("Twoja postać odchodzi w ciszę.", writer.text())
            self.assertTrue(
                any(
                    event.type == "character.saved" and event.payload.get("reason") == "quit"
                    for event in server.services.event_bus.history
                )
            )
            self.assertEqual(writer.close_calls, 1)
            self.assertEqual(writer.wait_closed_calls, 1)

    def test_connection_reset_and_cancelled_error_are_not_swallowed(self) -> None:
        reset_transport = TcpSessionTransport(cast(Any, FakeReader()), cast(Any, ResetOnDrainWriter()))
        cancel_transport = TcpSessionTransport(cast(Any, FakeReader()), cast(Any, CancelOnDrainWriter()))

        with self.assertRaises(ConnectionResetError):
            asyncio.run(reset_transport.send_text("test"))
        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(cancel_transport.send_text("test"))

    def test_invalid_utf8_login_closes_controlled(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            reader = InvalidUtf8Reader([b"good\n", b"\xff\xfe\xff\n"])
            writer = FakeWriter()
            transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
            result = asyncio.run(server.session_flow.login(transport))
            self.assertTrue(result.close_connection)
            self.assertIsNone(result.character)
            self.assertNotIn("Traceback", writer.text())

    def test_connection_cleanup_happens_exactly_once(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            reader = FakeReader()
            writer = CountingWriter()
            asyncio.run(server.handle_connection(cast(Any, reader), cast(Any, writer)))
            self.assertEqual(writer.close_calls, 1)
            self.assertEqual(writer.wait_closed_calls, 1)

    def test_identical_usernames_route_by_exact_character_identity(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            char1 = Character("entry")
            char2 = Character("entry")
            char1.room_id = 60
            char2.room_id = 61

            t1_writer = TrackingWriter()
            t2_writer = TrackingWriter()
            t1 = TcpSessionTransport(cast(Any, FakeReader()), cast(Any, t1_writer))
            t2 = TcpSessionTransport(cast(Any, FakeReader()), cast(Any, t2_writer))
            server.clients[t1] = char1
            server.clients[t2] = char2

            asyncio.run(send_room_info_for_character(server, char2))
            self.assertEqual(len(t1_writer.chunks), 0)
            self.assertTrue(any(b"Room.Info" in chunk for chunk in t2_writer.chunks))

            server.clients.pop(t1, None)
            asyncio.run(send_room_info_for_character(server, char2))
            self.assertEqual(len(t1_writer.chunks), 0)
            t2_room_info_count = 0
            for chunk in t2_writer.chunks:
                if b"Room.Info" in chunk:
                    t2_room_info_count += 1
            self.assertGreaterEqual(t2_room_info_count, 2)

            server.clients.pop(t2, None)
            before_t1 = len(t1_writer.chunks)
            before_t2 = len(t2_writer.chunks)
            asyncio.run(send_room_info_for_character(server, char1))
            self.assertEqual(len(t1_writer.chunks), before_t1)
            self.assertEqual(len(t2_writer.chunks), before_t2)

    def test_teleport_updates_only_target_transport(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("gm", "secret"))
                self.assertTrue(server.repo.register("target", "secret"))
                gm_reader = FakeReader.from_text_lines(["gm", "secret", "teleport target 61"])
                gm_writer = TrackingWriter()
                gm_transport = TcpSessionTransport(cast(Any, gm_reader), cast(Any, gm_writer))
                gm = await _login_and_initial_view(server, gm_transport)
                gm.admin_role = "gm"
                target_reader = FakeReader.from_text_lines(["target", "secret"])
                target_writer = TrackingWriter()
                target_transport = TcpSessionTransport(cast(Any, target_reader), cast(Any, target_writer))
                target = await _login_and_initial_view(server, target_transport)
                target.room_id = 60
                server.repo.save(target)
                server.clients[gm_transport] = gm
                server.clients[target_transport] = target
                gm_writer.clear()
                target_writer.clear()

                await server.session_flow.command_loop(gm_transport, server.make_context(gm))

                target_room_info = room_info_packet(server.world.get_location(target.room_id), server.world)
                self.assertIn(target_room_info, b"".join(target_writer.chunks))
                self.assertNotIn(target_room_info, b"".join(gm_writer.chunks))

        asyncio.run(run())

    def test_summon_updates_target_transport(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("gm", "secret"))
                self.assertTrue(server.repo.register("target", "secret"))
                gm_reader = FakeReader.from_text_lines(["gm", "secret", "summon target"])
                gm_writer = TrackingWriter()
                gm_transport = TcpSessionTransport(cast(Any, gm_reader), cast(Any, gm_writer))
                gm = await _login_and_initial_view(server, gm_transport)
                gm.admin_role = "gm"
                target_reader = FakeReader.from_text_lines(["target", "secret"])
                target_writer = TrackingWriter()
                target_transport = TcpSessionTransport(cast(Any, target_reader), cast(Any, target_writer))
                target = await _login_and_initial_view(server, target_transport)
                target.room_id = 61
                server.repo.save(target)
                server.clients[gm_transport] = gm
                server.clients[target_transport] = target
                gm_writer.clear()
                target_writer.clear()

                await server.session_flow.command_loop(gm_transport, server.make_context(gm))

                target_room_info = room_info_packet(server.world.get_location(gm.room_id), server.world)
                self.assertIn(target_room_info, b"".join(target_writer.chunks))
                self.assertNotIn(target_room_info, b"".join(gm_writer.chunks))

        asyncio.run(run())

    def test_no_location_change_emits_no_room_info(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("walker", "secret"))
                reader = FakeReader.from_text_lines(["walker", "secret", "spojrz"])
                writer = TrackingWriter()
                transport = TcpSessionTransport(cast(Any, reader), cast(Any, writer))
                character = await _login_and_initial_view(server, transport)
                server.clients[transport] = character
                writer.clear()

                await server.session_flow.command_loop(transport, server.make_context(character))

                self.assertNotIn(b"Room.Info", b"".join(writer.chunks))

        asyncio.run(run())

    def test_disconnected_target_before_flush_is_safe(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("gm", "secret"))
                self.assertTrue(server.repo.register("target", "secret"))
                gm_reader = FakeReader.from_text_lines(["gm", "secret", "teleport target 61"])
                gm_writer = TrackingWriter()
                gm_transport = TcpSessionTransport(cast(Any, gm_reader), cast(Any, gm_writer))
                gm = await _login_and_initial_view(server, gm_transport)
                gm.admin_role = "gm"
                target_reader = FakeReader.from_text_lines(["target", "secret"])
                target_writer = TrackingWriter()
                target_transport = TcpSessionTransport(cast(Any, target_reader), cast(Any, target_writer))
                target = await _login_and_initial_view(server, target_transport)
                server.clients[gm_transport] = gm
                server.clients[target_transport] = target
                gm_writer.clear()
                target_writer.clear()
                server.clients.pop(target_transport, None)

                await server.session_flow.command_loop(gm_transport, server.make_context(gm))

                self.assertNotIn(b"Room.Info", b"".join(target_writer.chunks))

        asyncio.run(run())

    def test_movement_room_info_drain_precedes_text_and_cleanup_on_reset(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("runner", "secret"))
            character = server.repo.load("runner")
            character.room_id = 60
            server.repo.save(character)

            reader = FakeReader.from_text_lines(["runner", "secret", "ne"])
            writer = RoomInfoResetWriter()
            asyncio.run(server.handle_connection(cast(Any, reader), cast(Any, writer)))
            self.assertEqual(writer.close_calls, 1)
            self.assertEqual(writer.wait_closed_calls, 1)
            room_info_writes = [
                i for i, action in enumerate(writer.actions) if action[0] == "write" and b"Room.Info" in action[1]
            ]
            self.assertGreaterEqual(len(room_info_writes), 2)
            room_info_write = room_info_writes[-1]
            room_info_drain = room_info_write + 1
            self.assertEqual(writer.actions[room_info_drain][0], "drain")
            tail = writer.actions[room_info_drain + 1 :]
            text_index = room_info_drain + 1 + next(i for i, action in enumerate(tail) if action[0] == "write" and b"Kierujesz" in action[1])
            prompt_index = room_info_drain + 1 + next(i for i, action in enumerate(tail) if action[0] == "write" and action[1].endswith(b" > "))
            self.assertLess(room_info_write, room_info_drain)
            self.assertLess(room_info_drain, text_index)
            self.assertLess(text_index, prompt_index)

    def test_two_clients_keep_separate_sequences(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("alpha", "secret"))
                self.assertTrue(server.repo.register("beta", "secret"))

                t1 = MemorySessionTransport()
                t1.queue_input(SessionInputKind.HELLO, {})
                t1.queue_input(SessionInputKind.CREDENTIALS, {"username": "alpha", "password": "secret"}, request_id="a")
                t2 = MemorySessionTransport()
                t2.queue_input(SessionInputKind.HELLO, {})
                t2.queue_input(SessionInputKind.CREDENTIALS, {"username": "beta", "password": "secret"}, request_id="b")

                login1, login2 = await asyncio.gather(server.session_flow.login(t1), server.session_flow.login(t2))
                assert login1.character is not None and login2.character is not None

                await asyncio.gather(
                    server.session_flow.send_initial_view(t1, server.make_context(login1.character)),
                    server.session_flow.send_initial_view(t2, server.make_context(login2.character)),
                )

                seq1 = [event.sequence for event in t1.outbound_events if event.sequence is not None]
                seq2 = [event.sequence for event in t2.outbound_events if event.sequence is not None]
                self.assertEqual(seq1, sorted(seq1))
                self.assertEqual(seq2, sorted(seq2))
                self.assertEqual(seq1[0], 1)
                self.assertEqual(seq2[0], 1)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
