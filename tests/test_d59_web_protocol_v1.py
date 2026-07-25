from __future__ import annotations

import asyncio
import json
import unittest
from typing import Any, cast

from astergard.application.session_transport import (
    SessionCapability,
    SessionEvent,
    SessionInput,
    SessionInputKind,
    TcpSessionTransport,
)
from astergard.application.session_flow import utf8_byte_length
from astergard.application.web_creator_flow import WebCreatorFlow
from astergard.gmcp import core_hello_packet, gmcp_negotiation_packet, room_info_packet
from astergard.protocol.web_v1 import (
    MAX_SAFE_INTEGER,
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
                {"step_id": "name", "field": "name", "code": "name_required", "message": "Imię nie może być puste."},
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
            build_web_envelope(
                "map.snapshot",
                {
                    "map_version": 1,
                    "sync_id": "sync-1",
                    "chunk_index": 0,
                    "complete": True,
                    "current_room_id": 14,
                    "rooms": [{"room_id": 14, "name": "Karczma", "region": "Astergard", "x": 1, "y": 2, "z": 0}],
                    "edges": [],
                },
                sequence=12,
            ),
            build_web_envelope(
                "map.update",
                {
                    "map_version": 1,
                    "sync_id": "sync-1",
                    "current_room_id": 14,
                    "rooms": [],
                    "edges": [],
                },
                sequence=13,
            ),
            build_web_envelope("command.result", {"command": "spojrz", "success": True}, request_id="3", sequence=14),
            build_web_envelope("connection.pong", {"nonce": "abc"}, request_id="4", sequence=15),
            build_web_envelope("protocol.error", {"code": "invalid_json", "message": "Protocol message is not valid JSON."}, request_id="5", sequence=16),
        ]
        for envelope in envelopes:
            encoded = serialize_web_envelope(envelope)
            decoded = parse_web_envelope(encoded)
            self.assertEqual(decoded, envelope)

    def test_room_info_keeps_public_special_exits_only(self) -> None:
        special_exit: dict[str, Any] = {
            "direction": "sekretny-most",
            "target": 61,
            "kind": "most",
            "visible": True,
            "door": True,
            "locked": False,
        }
        payload: dict[str, Any] = {
            "num": 7,
            "name": "Most przy bramie",
            "area": "Centrum_Twierdza",
            "coords": {"x": 1, "y": 2, "z": 0},
            "exits": {"n": 8},
            "special_exits": [special_exit],
        }
        encoded = serialize_web_envelope(build_web_envelope("room.info", payload, sequence=1))
        parsed = parse_web_envelope(encoded)
        self.assertEqual(parsed.payload["special_exits"][0]["direction"], "sekretny-most")
        self.assertEqual(parsed.payload["special_exits"][0]["target"], 61)

        with self.assertRaises(WebProtocolError):
            parse_web_envelope(
                json.dumps(
                    {
                        "version": 1,
                        "type": "room.info",
                        "sequence": 1,
                        "payload": {
                            **payload,
                            "special_exits": [{**special_exit, "hidden": True}],
                        },
                    },
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
            )

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

    def test_safe_integer_bounds_for_map_payloads_are_enforced(self) -> None:
        snapshot = {
            "map_version": 1,
            "sync_id": "sync-safe",
            "chunk_index": MAX_SAFE_INTEGER,
            "complete": False,
            "current_room_id": MAX_SAFE_INTEGER,
            "rooms": [
                {
                    "room_id": MAX_SAFE_INTEGER,
                    "name": "Pokoj bezpieczny",
                    "region": "Astergard",
                    "x": -MAX_SAFE_INTEGER,
                    "y": 0,
                    "z": MAX_SAFE_INTEGER,
                },
            ],
            "edges": [],
        }
        parsed_snapshot = parse_web_envelope(
            json.dumps({"version": 1, "type": "map.snapshot", "payload": snapshot, "sequence": 1}, separators=(",", ":"), ensure_ascii=False)
        )
        self.assertEqual(parsed_snapshot.payload, snapshot)

        update = {
            "map_version": 1,
            "sync_id": "sync-safe",
            "current_room_id": MAX_SAFE_INTEGER,
            "rooms": [
                {
                    "room_id": MAX_SAFE_INTEGER,
                    "name": "Pokoj bezpieczny",
                    "region": "Astergard",
                    "x": -MAX_SAFE_INTEGER,
                    "y": 0,
                    "z": MAX_SAFE_INTEGER,
                },
            ],
            "edges": [],
        }
        parsed_update = parse_web_envelope(
            json.dumps({"version": 1, "type": "map.update", "payload": update, "sequence": 2}, separators=(",", ":"), ensure_ascii=False)
        )
        self.assertEqual(parsed_update.payload, update)

        invalid_cases = [
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "chunk_index": MAX_SAFE_INTEGER + 1}, "sequence": 1}, "chunk_index", None),
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "current_room_id": MAX_SAFE_INTEGER + 1}, "sequence": 1}, "current_room_id", None),
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "rooms": [{"room_id": MAX_SAFE_INTEGER + 1, "name": "Start", "region": "Astergard", "x": 0, "y": 0, "z": 0}]}, "sequence": 1}, "room_id", None),
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "rooms": [{"room_id": 1, "name": "Start", "region": "Astergard", "x": -MAX_SAFE_INTEGER - 1, "y": 0, "z": 0}]}, "sequence": 1}, "x", None),
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "map_version": 2}, "sequence": 1}, "map_version", None),
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "rooms": [{"room_id": True, "name": "Start", "region": "Astergard", "x": 0, "y": 0, "z": 0}]}, "sequence": 1}, "room_id", None),
            ({"version": 1, "type": "map.snapshot", "payload": {**snapshot, "rooms": [{"room_id": 1.5, "name": "Start", "region": "Astergard", "x": 0, "y": 0, "z": 0}]}, "sequence": 1}, "room_id", None),
            ({"version": 1, "type": "map.update", "payload": {**update, "current_room_id": MAX_SAFE_INTEGER + 1}, "sequence": 2}, "current_room_id", None),
            ({"version": 1, "type": "map.update", "payload": {**update, "rooms": [{"room_id": MAX_SAFE_INTEGER + 1, "name": "Start", "region": "Astergard", "x": 0, "y": 0, "z": 0}]}, "sequence": 2}, "room_id", None),
            ({"version": 1, "type": "map.update", "payload": {**update, "rooms": [{"room_id": 1, "name": "Start", "region": "Astergard", "x": 0, "y": 0, "z": float("inf")}]}, "sequence": 2}, None, "invalid_json"),
            ({"version": 1, "type": "map.update", "payload": {**update, "rooms": [{"room_id": 1, "name": "Start", "region": "Astergard", "x": 0, "y": 0, "z": float("nan")}]}, "sequence": 2}, None, "invalid_json"),
        ]
        for raw, field, code in invalid_cases:
            with self.subTest(field=field):
                with self.assertRaises(WebProtocolError) as ctx:
                    parse_web_envelope(json.dumps(raw, separators=(",", ":"), ensure_ascii=False))
                if field is not None:
                    self.assertIn(field, str(ctx.exception))
                if code is not None:
                    self.assertEqual(ctx.exception.code, code)

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

    def test_creator_submit_value_limit_is_128_bytes_and_recovers_on_retry(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                username = "limit-check"
                password = "secret"
                self.assertFalse(server.repo.player_exists(username))

                short_value = "ż" * 64
                long_value = f"{short_value}a"
                command_512 = "ż" * 256
                command_513 = f"{command_512}a"
                self.assertEqual(utf8_byte_length(short_value), 128)
                self.assertEqual(utf8_byte_length(long_value), 129)
                self.assertEqual(utf8_byte_length(command_512), 512)
                self.assertEqual(utf8_byte_length(command_513), 513)

                command_message = SessionInput(
                    SessionInputKind.COMMAND,
                    {"command": command_512},
                    request_id="cmd-1",
                )
                self.assertEqual(
                    server.session_flow._string_payload(command_message, "command", allow_empty=True, max_bytes=512),
                    command_512,
                )
                with self.assertRaises(ValueError):
                    server.session_flow._string_payload(
                        SessionInput(
                            SessionInputKind.COMMAND,
                            {"command": command_513},
                            request_id="cmd-2",
                        ),
                        "command",
                        allow_empty=True,
                        max_bytes=512,
                    )

                creator_value_message = SessionInput(
                    SessionInputKind.CREATOR_SUBMIT,
                    {"step_id": "special_feature", "value": short_value},
                    request_id="submit-1",
                )
                self.assertEqual(
                    server.session_flow._string_payload(creator_value_message, "value", allow_empty=True, max_bytes=128),
                    short_value,
                )
                with self.assertRaises(ValueError) as ctx:
                    server.session_flow._string_payload(
                        SessionInput(
                            SessionInputKind.CREATOR_SUBMIT,
                            {"step_id": "special_feature", "value": long_value},
                            request_id="submit-2",
                        ),
                        "value",
                        allow_empty=True,
                        max_bytes=128,
                    )
                self.assertIn("Input exceeds the transport limit", str(ctx.exception))

                flow = WebCreatorFlow(username, password)
                queued_inputs: list[tuple[SessionInputKind, dict[str, object], str | None]] = [
                    (SessionInputKind.HELLO, {}, "hello-1"),
                    (SessionInputKind.CREATOR_START, {"username": username, "password": password}, "start-1"),
                ]
                while True:
                    step = flow.current_step()
                    step_id = step.step_id
                    if step_id == "special_feature":
                        queued_inputs.append((SessionInputKind.CREATOR_SUBMIT, {"step_id": step_id, "value": long_value}, "submit-long"))
                        queued_inputs.append((SessionInputKind.CREATOR_SUBMIT, {"step_id": step_id, "value": "blizna_policzek"}, "submit-retry"))
                        break
                    value_map = {
                        "name": "Nowy",
                        "gender_id": "f",
                        "age": "24",
                    }
                    if step.input_type == "choice" and step_id not in value_map:
                        value = step.choices[0].value if step.choices else ""
                    else:
                        value = value_map[step_id]
                    queued_inputs.append((SessionInputKind.CREATOR_SUBMIT, {"step_id": step_id, "value": value}, f"submit-{step_id}"))
                    flow.submit(step_id, value)

                transport = MemorySessionTransport()
                for kind, payload, request_id in queued_inputs:
                    transport.queue_input(kind, payload, request_id=request_id)

                login = await server.session_flow.login(transport)
                self.assertIsNotNone(login.character)
                assert login.character is not None
                await server.session_flow.send_initial_view(transport, server.make_context(login.character))

                event_types = [event.type for event in transport.outbound_events]
                self.assertEqual(event_types.count("creator.validation_error"), 1)
                self.assertEqual(event_types.count("creator.finished"), 1)
                self.assertEqual(event_types.count("session.ready"), 1)
                validation_error = next(event for event in transport.outbound_events if event.type == "creator.validation_error")
                self.assertEqual(validation_error.request_id, "submit-long")
                self.assertEqual(validation_error.payload["step_id"], "special_feature")
                self.assertEqual(validation_error.payload["field"], "value")
                self.assertEqual(validation_error.payload["code"], "creator_value_too_long")
                self.assertEqual(validation_error.payload["message"], "Odpowiedź jest zbyt długa.")
                finished = next(event for event in transport.outbound_events if event.type == "creator.finished")
                self.assertEqual(finished.request_id, "submit-retry")

        asyncio.run(run())

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
            self.assertIn("map.snapshot", event_types)
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

    def test_web_map_snapshot_chunks_500_visited_rooms_and_stays_under_transport_limit(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                server = harness.require_server()
                self.assertTrue(server.repo.register("mapper", "secret"))
                character = server.repo.load("mapper")
                character.room_id = 60
                character.visited_room_ids = set(server.world.locations)
                server.repo.save(character)

                transport = MemorySessionTransport()
                transport.queue_input(SessionInputKind.HELLO, {})
                transport.queue_input(
                    SessionInputKind.CREDENTIALS,
                    {"username": "mapper", "password": "secret"},
                    request_id="login-1",
                )

                login = await server.session_flow.login(transport)
                self.assertIsNotNone(login.character)
                assert login.character is not None
                server.session_flow._web_map_sync_by_transport[id(transport)] = "sync-500"
                transport._sequence = 997

                await server.session_flow.send_initial_view(transport, server.make_context(login.character))

                snapshot_events = [event for event in transport.outbound_events if event.type == "map.snapshot"]
                self.assertGreater(len(snapshot_events), 1)
                self.assertEqual(snapshot_events[0].sequence, 999)
                self.assertEqual(snapshot_events[1].sequence, 1000)

                payloads = [event.payload for event in snapshot_events]
                expected_payloads = server.services.minimap_service.build_web_snapshot_payloads(
                    login.character,
                    server.world,
                    sync_id="sync-500",
                    starting_sequence=999,
                )
                self.assertEqual(payloads, expected_payloads)
                self.assertEqual(payloads, server.services.minimap_service.build_web_snapshot_payloads(
                    login.character,
                    server.world,
                    sync_id="sync-500",
                    starting_sequence=999,
                ))
                self.assertEqual(
                    len({room["room_id"] for payload in payloads for room in payload["rooms"]}),
                    len(server.world.locations),
                )
                self.assertTrue(
                    all(
                        len(
                            serialize_web_envelope(
                                build_web_envelope("map.snapshot", payload, sequence=event.sequence),
                            ).encode("utf-8")
                        )
                        <= 8192
                        for event, payload in zip(snapshot_events, payloads, strict=True)
                    )
                )

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
