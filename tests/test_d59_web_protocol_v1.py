from __future__ import annotations

import asyncio
import json
import unittest
from typing import Any, cast

from astergard.application.session_transport import (
    SessionCapability,
    SessionEvent,
    SessionInputKind,
    TcpSessionTransport,
)
from astergard.gmcp import core_hello_packet, gmcp_negotiation_packet, room_info_packet
from astergard.protocol.web_v1 import (
    WebProtocolError,
    build_web_envelope,
    parse_web_envelope,
    serialize_web_envelope,
)
from astergard.testing import FakeReader, FakeWriter, MemorySessionTransport, TestGameHarness


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


class WebProtocolV1Tests(unittest.TestCase):
    def test_all_contract_messages_round_trip(self) -> None:
        envelopes = [
            build_web_envelope("session.hello", {"client": "test"}, request_id="1"),
            build_web_envelope("auth.login", {"username": "tester", "password": "secret"}, request_id="2"),
            build_web_envelope("creator.start", {"username": "newbie", "password": "secret"}, request_id="2a"),
            build_web_envelope("creator.submit", {"step_id": "name", "value": "Ala"}, request_id="2b"),
            build_web_envelope("creator.back", {"step_id": "age"}, request_id="2c"),
            build_web_envelope("creator.cancel", {"step_id": "age"}, request_id="2d"),
            build_web_envelope("command.execute", {"command": "spojrz"}, request_id="3"),
            build_web_envelope("connection.ping", {"nonce": "abc"}, request_id="4"),
            build_web_envelope("session.ready", {"transport": "web", "username": "tester"}, sequence=1),
            build_web_envelope("auth.result", {"success": True, "username": "tester"}, request_id="2", sequence=2),
            build_web_envelope(
                "character.vitals",
                {
                    "condition_current": 10,
                    "condition_max": 12,
                    "condition_label": "jest lekko ranny",
                    "stamina_current": 88,
                    "stamina_max": 100,
                    "stamina_label": "Jesteś w pełni sił.",
                },
                sequence=3,
            ),
            build_web_envelope(
                "creator.started",
                {
                    "username": "newbie",
                    "step": {
                        "step_id": "name",
                        "title": "Imię",
                        "prompt": "— Jak cię zwać?",
                        "input_type": "text",
                        "back_available": False,
                        "cancel_available": True,
                    },
                },
                request_id="2a",
                sequence=4,
            ),
            build_web_envelope(
                "creator.step",
                {
                    "step_id": "age",
                    "title": "Wiek",
                    "prompt": "— Ile masz lat?",
                    "input_type": "number",
                    "back_available": True,
                    "cancel_available": True,
                },
                request_id="2b",
                sequence=5,
            ),
            build_web_envelope(
                "creator.validation_error",
                {"step_id": "name", "field": "name", "message": "Imię nie może być puste."},
                request_id="2c",
                sequence=6,
            ),
            build_web_envelope(
                "creator.cancelled",
                {"username": "newbie", "reason": "cancelled_by_user"},
                request_id="2d",
                sequence=7,
            ),
            build_web_envelope(
                "creator.finished",
                {"username": "newbie", "character_name": "Ala"},
                request_id="2e",
                sequence=8,
            ),
            build_web_envelope("output.text", {"text": "Witaj"}, sequence=9),
            build_web_envelope("output.prompt", {"prompt": ">"}, sequence=10),
            build_web_envelope(
                "room.info",
                {
                    "num": 14,
                    "name": "Karczma",
                    "area": "Astergard",
                    "coords": {"x": 1, "y": 2, "z": 0},
                    "exits": {},
                },
                sequence=11,
            ),
            build_web_envelope("command.result", {"command": "spojrz", "success": True}, request_id="3", sequence=12),
            build_web_envelope("connection.pong", {"nonce": "abc"}, request_id="4", sequence=13),
            build_web_envelope("protocol.error", {"code": "invalid_json", "message": "Protocol message is not valid JSON."}, request_id="5", sequence=14),
        ]
        for envelope in envelopes:
            encoded = serialize_web_envelope(envelope)
            decoded = parse_web_envelope(encoded)
            self.assertEqual(decoded, envelope)

    def test_bool_version_sequence_and_empty_request_id_are_rejected(self) -> None:
        cases = [
            {"version": True, "type": "session.hello", "payload": {}, "request_id": "1"},
            {"version": 1, "type": "command.execute", "payload": {"command": "x"}, "request_id": ""},
            {"version": 1, "type": "session.ready", "payload": {"transport": "web"}, "sequence": True},
            {"version": 1, "type": "session.ready", "payload": {"transport": "web"}, "sequence": -1},
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises(WebProtocolError):
                    parse_web_envelope(json.dumps(raw, separators=(",", ":")))

    def test_unknown_type_is_rejected(self) -> None:
        raw = json.dumps({"version": 1, "type": "session.wut", "payload": {}}, separators=(",", ":"))
        with self.assertRaises(WebProtocolError):
            parse_web_envelope(raw)

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaises(WebProtocolError):
            parse_web_envelope("{not-json}")

    def test_non_finite_numbers_are_rejected_in_nested_payloads(self) -> None:
        raw = (
            '{"version":1,"type":"session.hello","request_id":"1","payload":'
            '{"client":"test","capabilities":[1,NaN,Infinity,-Infinity]}}'
        )
        with self.assertRaises(WebProtocolError):
            parse_web_envelope(raw)

    def test_unexpected_envelope_fields_are_rejected(self) -> None:
        raw = json.dumps(
            {"version": 1, "type": "session.hello", "payload": {}, "request_id": "1", "extra": 1},
            separators=(",", ":"),
        )
        with self.assertRaises(WebProtocolError):
            parse_web_envelope(raw)

    def test_payload_shape_and_length_limits_are_rejected(self) -> None:
        with self.assertRaises(WebProtocolError):
            parse_web_envelope(
                json.dumps(
                    {"version": 1, "type": "command.execute", "payload": {"command": "ż" * 260}, "request_id": "1"},
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
            )
        with self.assertRaises(WebProtocolError):
            parse_web_envelope(
                json.dumps(
                    {"version": 1, "type": "command.result", "payload": {"command": "spojrz", "success": True, "output": "x"}, "request_id": "1"},
                    separators=(",", ":"),
                )
            )
        with self.assertRaises(WebProtocolError):
            parse_web_envelope(
                json.dumps(
                    {"version": 1, "type": "command.execute", "payload": "not-an-object", "request_id": "1"},
                    separators=(",", ":"),
                )
            )

    def test_whitespace_command_execute_is_rejected_with_request_id(self) -> None:
        raw = json.dumps(
            {"version": 1, "type": "command.execute", "payload": {"command": "   "}, "request_id": "cmd-1"},
            separators=(",", ":"),
        )
        with self.assertRaises(WebProtocolError) as ctx:
            parse_web_envelope(raw)
        self.assertEqual(ctx.exception.code, "invalid_command")
        self.assertEqual(ctx.exception.request_id, "cmd-1")

    def test_command_protocol_errors_preserve_request_id_and_do_not_mix(self) -> None:
        async def run_bad_command(payload: dict[str, object], request_id: str) -> SessionEvent:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("tester", "secret"))
                transport = MemorySessionTransport()
                transport.queue_input(SessionInputKind.HELLO, {})
                transport.queue_input(
                    SessionInputKind.CREDENTIALS,
                    {"username": "tester", "password": "secret"},
                    request_id="login-1",
                )
                transport.queue_input(SessionInputKind.COMMAND, payload, request_id=request_id)

                login = await server.session_flow.login(transport)
                self.assertIsNotNone(login.character)
                assert login.character is not None
                await server.session_flow.send_initial_view(transport, server.make_context(login.character))
                await server.session_flow.command_loop(transport, server.make_context(login.character))
                return next(event for event in transport.outbound_events if event.type == "protocol.error")

        overlong = asyncio.run(run_bad_command({"command": "ż" * 260}, "overlong-1"))
        invalid = asyncio.run(run_bad_command({"command": 123}, "invalid-2"))
        self.assertEqual(overlong.request_id, "overlong-1")
        self.assertEqual(invalid.request_id, "invalid-2")
        self.assertNotEqual(overlong.request_id, invalid.request_id)

    def test_password_is_redacted_from_repr_and_errors(self) -> None:
        envelope = build_web_envelope("auth.login", {"username": "tester", "password": "secret"}, request_id="1")
        self.assertNotIn("secret", repr(envelope))
        self.assertNotIn("secret", repr(SessionEvent("protocol.error", {"code": "invalid", "message": "safe"})))
        error = WebProtocolError("invalid_json", "Protocol message is not valid JSON.")
        self.assertNotIn("secret", repr(error))
        self.assertNotIn("secret", str(error))

    def test_tcp_transport_remains_compatible_and_gmcp_order_is_stable(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("tcp", "secret"))
            character = server.repo.load("tcp")
            character.room_id = 60
            server.repo.save(character)

            login_reader = FakeReader.from_text_lines(["tcp", "secret"])
            login_writer = TrackingWriter()
            login_transport = TcpSessionTransport(cast(Any, login_reader), cast(Any, login_writer))
            login = asyncio.run(server.session_flow.login(login_transport))
            self.assertIsNotNone(login.character)
            assert login.character is not None

            initial_writer = TrackingWriter()
            initial_transport = TcpSessionTransport(cast(Any, FakeReader()), cast(Any, initial_writer))
            asyncio.run(server.session_flow.send_initial_view(initial_transport, server.make_context(login.character)))

            location = server.world.get_location(60)
            assert location is not None
            actions = initial_writer.actions
            self.assertEqual(actions[0], ("write", gmcp_negotiation_packet()))
            self.assertEqual(actions[1][0], "drain")
            self.assertEqual(actions[2], ("write", core_hello_packet()))
            self.assertEqual(actions[3][0], "drain")
            self.assertTrue(actions[4][0] == "write" and actions[4][1].endswith(b"\r\n"))
            self.assertEqual(actions[5][0], "drain")
            self.assertEqual(actions[6], ("write", room_info_packet(location, server.world)))
            self.assertEqual(actions[7][0], "drain")
            self.assertTrue(actions[8][0] == "write" and actions[8][1].endswith(b" > "))
            self.assertEqual(actions[9][0], "drain")

    def test_empty_web_command_reprompts_with_exact_prompt(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("web", "secret"))
            transport = MemorySessionTransport()
            transport.queue_input(SessionInputKind.HELLO, {})
            transport.queue_input(
                SessionInputKind.CREDENTIALS,
                {"username": "web", "password": "secret"},
                request_id="login-1",
            )
            transport.queue_input(SessionInputKind.COMMAND, {"command": ""}, request_id="cmd-1")

            login = asyncio.run(server.session_flow.login(transport))
            self.assertIsNotNone(login.character)
            assert login.character is not None
            asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
            asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))

            self.assertGreaterEqual(len(transport.outbound_prompts), 2)
            self.assertEqual(transport.outbound_prompts[-1], ">")
            self.assertTrue(all(prompt == ">" for prompt in transport.outbound_prompts))

    def test_movement_emits_room_info_before_command_text(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("walker", "secret"))
            character = server.repo.load("walker")
            character.room_id = 60
            server.repo.save(character)

            login_reader = FakeReader.from_text_lines(["walker", "secret"])
            login_writer = TrackingWriter()
            login_transport = TcpSessionTransport(cast(Any, login_reader), cast(Any, login_writer))
            login = asyncio.run(server.session_flow.login(login_transport))
            assert login.character is not None

            move_writer = TrackingWriter()
            move_transport = TcpSessionTransport(cast(Any, FakeReader.from_text_lines(["poludnie"])), cast(Any, move_writer))
            server.clients[move_transport] = login.character
            asyncio.run(server.session_flow.command_loop(move_transport, server.make_context(login.character)))

            payload_actions = [action for action in move_writer.actions if action[0] == "write"]
            location = server.world.get_location(login.character.room_id)
            assert location is not None
            room_info = room_info_packet(location, server.world)
            room_index = next(i for i, action in enumerate(payload_actions) if action[1] == room_info)
            text_index = next(i for i, action in enumerate(payload_actions) if b"Kierujesz si" in action[1])
            prompt_index = next(i for i, action in enumerate(payload_actions) if action[1].endswith(b" > "))
            self.assertLess(room_index, text_index)
            self.assertLess(text_index, prompt_index)

    def test_memory_transport_full_flow_omits_full_map_debug_and_preserves_sequences(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            self.assertTrue(server.repo.register("web", "secret"))
            character = server.repo.load("web")
            character.room_id = 60
            server.repo.save(character)

            transport = MemorySessionTransport()
            transport.queue_input(SessionInputKind.HELLO, {})
            transport.queue_input(
                SessionInputKind.CREDENTIALS,
                {"username": "web", "password": "secret"},
                request_id="login-1",
            )
            transport.queue_input(SessionInputKind.COMMAND, {"command": "spojrz"}, request_id="cmd-1")

            login = asyncio.run(server.session_flow.login(transport))
            self.assertIsNotNone(login.character)
            assert login.character is not None
            asyncio.run(server.session_flow.send_initial_view(transport, server.make_context(login.character)))
            asyncio.run(server.session_flow.command_loop(transport, server.make_context(login.character)))

            self.assertNotIn("<MAP_JSON>", "".join(transport.outbound_text))
            self.assertEqual(transport.outbound_prompts[-1], ">")

            event_types = [event.type for event in transport.outbound_events]
            self.assertIn("auth.result", event_types)
            self.assertIn("character.vitals", event_types)
            self.assertIn("room.info", event_types)
            self.assertIn("session.ready", event_types)
            self.assertIn("command.result", event_types)

            auth_event = next(event for event in transport.outbound_events if event.type == "auth.result")
            vitals_event = next(event for event in transport.outbound_events if event.type == "character.vitals")
            command_event = next(event for event in transport.outbound_events if event.type == "command.result")
            self.assertEqual(auth_event.request_id, "login-1")
            self.assertEqual(vitals_event.payload["condition_max"], 12)
            self.assertEqual(vitals_event.payload["stamina_max"], 100)
            self.assertEqual(command_event.request_id, "cmd-1")
            self.assertEqual(auth_event.sequence, 1)
            self.assertEqual(
                [event.sequence for event in transport.outbound_events if event.sequence is not None],
                sorted(event.sequence for event in transport.outbound_events if event.sequence is not None),
            )
            self.assertNotIn(SessionCapability.DEBUG_MAP, transport.capabilities)


if __name__ == "__main__":
    unittest.main()
