from __future__ import annotations

import asyncio
import json
import socket
import unittest
from contextlib import asynccontextmanager
from collections import deque
from typing import Any, Callable, cast
from unittest.mock import patch

from websockets.client import connect
from websockets.exceptions import InvalidStatusCode
from websockets.server import serve

from astergard.application.websocket_transport import WebSocketTransportLimits
from astergard.items.models import Item
from astergard.protocol.web_v1 import (
    COMMAND_LENGTH_LIMIT,
    WEB_MESSAGE_MAX_BYTES,
    build_web_envelope,
    parse_web_envelope,
    serialize_web_envelope,
)
from astergard.server.gateway import WebSocketGateway, WebSocketGatewayConfig
from astergard.testing import TestGameHarness
from astergard.world.manager import STARTING_ROOM_ID
from astergard.world.models import Exit
from astergard.gmcp import POLISH_TO_MUDLET_DIRECTION


def _frame(message_type: str, payload: dict[str, Any], *, request_id: str) -> str:
    return serialize_web_envelope(build_web_envelope(message_type, payload, request_id=request_id))


def _json_frame(message_type: str, payload: dict[str, Any], *, request_id: str) -> str:
    return json.dumps(
        {"version": 1, "type": message_type, "request_id": request_id, "payload": payload},
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _creator_answer(step: dict[str, Any], answers: dict[str, str], *, fallback_choice: bool = True, override: str | None = None) -> str:
    if override is not None:
        return override
    if step["step_id"] in answers:
        return answers[step["step_id"]]
    if step["input_type"] == "choice":
        if not fallback_choice:
            raise KeyError(step["step_id"])
        return step["choices"][0]["value"]
    return answers[step["step_id"]]


async def _drive_web_creator(
    websocket: Any,
    *,
    suffix: str,
    username: str,
    password: str,
    answers: dict[str, str],
    final_override: str | None = None,
) -> tuple[Any, list[Any], str]:
    await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id=f"{suffix}-hello"))
    greeting = parse_web_envelope(await websocket.recv())
    assert greeting.type == "output.text"

    await websocket.send(_frame("creator.start", {"username": username, "password": password}, request_id=f"{suffix}-start"))
    started = parse_web_envelope(await websocket.recv())
    assert started.type == "creator.started"
    step = started.payload["step"]

    while True:
        step_id = step["step_id"]
        request_id = f"{suffix}-{step_id}"
        value = _creator_answer(step, answers, override=final_override if step_id == "special_feature" else None)
        await websocket.send(_frame("creator.submit", {"step_id": step_id, "value": value}, request_id=request_id))
        response = parse_web_envelope(await websocket.recv())
        if response.type == "creator.step":
            step = response.payload
            continue
        if response.type == "creator.finished":
            post_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
            return response, post_frames, request_id
            return response, [], request_id


async def _drive_creator_to_special_feature(
    websocket: Any,
    *,
    suffix: str,
    username: str,
    password: str,
    answers: dict[str, str] | None = None,
    select_answer: Callable[[dict[str, Any]], str] | None = None,
) -> tuple[dict[str, Any], str]:
    await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id=f"{suffix}-hello"))
    greeting = parse_web_envelope(await websocket.recv())
    assert greeting.type == "output.text"

    await websocket.send(_frame("creator.start", {"username": username, "password": password}, request_id=f"{suffix}-start"))
    started = parse_web_envelope(await websocket.recv())
    assert started.type == "creator.started"
    step = started.payload["step"]
    previous_step_id = step["step_id"]

    while step["step_id"] != "special_feature":
        previous_step_id = step["step_id"]
        request_id = f"{suffix}-{previous_step_id}"
        if select_answer is not None:
            value = select_answer(step)
        else:
            value = _creator_answer(step, answers or {})
        await websocket.send(_frame("creator.submit", {"step_id": previous_step_id, "value": value}, request_id=request_id))
        response = parse_web_envelope(await websocket.recv())
        assert response.type == "creator.step"
        step = response.payload

    return step, previous_step_id


async def _read_http_response(reader: asyncio.StreamReader) -> str:
    chunks: list[bytes] = []
    while True:
        chunk = await asyncio.wait_for(reader.read(1024), timeout=2.0)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode("latin-1", errors="replace")


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.value = start

    def monotonic(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class ScriptedWebSocket:
    def __init__(self, clock: FakeClock, incoming: list[str | bytes], *, advance_seconds: float = 0.4) -> None:
        self.clock = clock
        self.incoming = deque(incoming)
        self.advance_seconds = advance_seconds
        self.sent: list[str] = []
        self.closed: list[tuple[int | None, str | None]] = []

    async def recv(self) -> str | bytes:
        self.clock.advance(self.advance_seconds)
        if not self.incoming:
            raise EOFError
        return self.incoming.popleft()

    async def send(self, data: str) -> None:
        self.sent.append(data)

    async def close(self, code: int = 1000, reason: str = "session closed") -> None:
        self.closed.append((code, reason))


@asynccontextmanager
async def websocket_gateway_context(server: Any, config: WebSocketGatewayConfig):
    gateway = WebSocketGateway(server, config)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config.host, 0))
    sock.listen()
    sock.setblocking(False)
    async with serve(
        gateway.handle_websocket_connection,
        sock=sock,
        subprotocols=cast(Any, [config.subprotocol]),
        process_request=gateway._process_request,
        compression=None,
        max_size=config.limits.message_max_bytes,
        max_queue=config.max_pending_messages,
        ping_interval=config.ping_interval_seconds,
        ping_timeout=config.ping_timeout_seconds,
        close_timeout=config.close_timeout_seconds,
    ):
        yield gateway, sock.getsockname()[1]
    await gateway.close_active_connections()


class WebSocketGatewayIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.harness = TestGameHarness().start()
        self.server = self.harness.require_server()

    async def asyncTearDown(self) -> None:
        self.harness.close()

    def _connect(self, port: int, origin: Any, *, subprotocols: Any = None):
        return connect(
            f"ws://127.0.0.1:{port}",
            origin=origin,
            subprotocols=cast(Any, subprotocols or ["astergard.v1"]),
            compression=None,
            ping_interval=None,
            close_timeout=2,
            open_timeout=2,
            max_queue=4,
        )

    async def _wait_for_cleanup(self, gateway: Any | None = None) -> None:
        async def _cleanup_done() -> None:
            while self.server.clients or self.server._active_transports or (gateway is not None and gateway._active_transports):
                await asyncio.sleep(0)

        await asyncio.wait_for(_cleanup_done(), timeout=2.0)

    async def test_successful_login_sequence_and_look_command(self) -> None:
        self.assertTrue(self.server.repo.register("web", "secret"))
        character = self.server.repo.load("web")
        character.room_id = 60
        self.server.repo.save(character)
        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=20, command_rate_limit_count=20),
        )
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                greeting = parse_web_envelope(await websocket.recv())
                self.assertEqual(greeting.type, "output.text")
                self.assertEqual(greeting.sequence, 1)

                await websocket.send(_frame("auth.login", {"username": "web", "password": "secret"}, request_id="login-1"))
                login_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                self.assertEqual(
                    [frame.type for frame in login_frames],
                    ["auth.result", "output.text", "room.info", "character.vitals", "output.prompt", "session.ready"],
                )
                self.assertEqual([frame.sequence for frame in login_frames], [2, 3, 4, 5, 6, 7])
                self.assertEqual(login_frames[0].request_id, "login-1")
                self.assertEqual(login_frames[-1].payload["transport"], "web")
                self.assertEqual(login_frames[3].payload["condition_max"], 12)
                self.assertEqual(login_frames[3].payload["stamina_max"], character.stats.max_kondycja)

                await websocket.send(_frame("command.execute", {"command": "spojrz"}, request_id="cmd-1"))
                command_frames = [parse_web_envelope(await websocket.recv()) for _ in range(3)]
                self.assertEqual([frame.type for frame in command_frames], ["output.text", "command.result", "output.prompt"])
                self.assertEqual([frame.sequence for frame in command_frames], [8, 9, 10])
                self.assertEqual(command_frames[1].request_id, "cmd-1")
                self.assertEqual(
                    [frame.sequence for frame in [greeting] + login_frames + command_frames],
                    list(range(1, 11)),
                )

    async def test_public_room_info_omits_hidden_special_exits(self) -> None:
        self.assertTrue(self.server.repo.register("roominfo", "secret"))
        character = self.server.repo.load("roominfo")
        location = next(loc for loc in self.server.world.locations.values() if "gora" not in loc.exits)
        character.room_id = location.id
        self.server.repo.save(character)
        location.exits["sekretny-most"] = Exit(61, is_door=True, kind="most", description="Jawny most", visible=True)
        location.exits["gora"] = Exit(987654, is_door=True, is_locked=True, kind="Wieża Magów", description="Sekretna brama", visible=False)
        snapshot = {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()}

        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=20, command_rate_limit_count=20),
        )
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "roominfo", "password": "secret"}, request_id="login-1"))
                login_frames_raw = [await websocket.recv() for _ in range(6)]
                login_frames = [parse_web_envelope(raw) for raw in login_frames_raw]
                self.assertEqual(
                    [frame.type for frame in login_frames],
                    ["auth.result", "output.text", "room.info", "character.vitals", "output.prompt", "session.ready"],
                )

                room_raw = login_frames_raw[2]
                room = login_frames[2]
                self.assertEqual(room.type, "room.info")
                self.assertNotIn("Wieża Magów", room_raw)
                self.assertNotIn("987654", room_raw)
                self.assertNotIn("gora", room_raw)
                expected_exits = {
                    POLISH_TO_MUDLET_DIRECTION[direction]: target
                    for direction, (target, _is_door, _is_locked, _kind, _description, visible) in snapshot.items()
                    if visible and direction in POLISH_TO_MUDLET_DIRECTION
                }
                self.assertEqual(
                    room.payload["exits"],
                    expected_exits,
                )
                self.assertEqual(
                    {direction: (exit_.target_room, exit_.is_door, exit_.is_locked, exit_.kind, exit_.description, exit_.visible) for direction, exit_ in location.exits.items()},
                    snapshot,
                )
                self.assertTrue(
                    any(
                        entry["direction"] == "sekretny-most"
                        and entry["target"] == 61
                        and entry["kind"] == "most"
                        and entry["visible"] is True
                        and entry["door"] is True
                        and entry["locked"] is False
                        for entry in room.payload.get("special_exits", [])
                    )
                )
                self.assertFalse(any(entry["direction"] == "up" and entry["target"] == 987654 for entry in room.payload.get("special_exits", [])))

                await websocket.send(_frame("command.execute", {"command": "spojrz"}, request_id="cmd-1"))
                command_frames = [parse_web_envelope(await websocket.recv()) for _ in range(3)]
                self.assertEqual([frame.type for frame in command_frames], ["output.text", "command.result", "output.prompt"])
                self.assertEqual(command_frames[1].request_id, "cmd-1")
                self.assertIsNone(websocket.close_code)

    async def test_ob_siebie_matches_tcp_output_text(self) -> None:
        self.assertTrue(self.server.repo.register("mirror", "secret"))
        character = self.server.repo.load("mirror")
        character.name = "Agran"
        character.gender_id = "m"
        character.room_id = 60
        character.equipment["bron_glowna"] = Item(
            "długi miecz",
            "Miecz.",
            1.2,
            10,
            "mirror_sword",
            item_type="weapon",
            slot="bron_glowna",
            wearable=True,
            weapon_type="miecz",
            weapon_profile_id="garrison_short_sword",
            display_nominative="długi miecz",
            display_accusative="długi miecz",
        )
        character.equipment["tarcza"] = Item(
            "migdałowa tarcza",
            "Tarcza.",
            2.0,
            10,
            "mirror_shield",
            item_type="shield",
            slot="tarcza",
            wearable=True,
            weapon_type="tarcza",
            display_nominative="migdałowa tarcza",
            display_accusative="migdałową tarczę",
        )
        self.server.repo.save(character)
        tcp_output = await self.harness.execute(character, "ob siebie")
        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=20, command_rate_limit_count=20),
        )
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "mirror", "password": "secret"}, request_id="login-1"))
                for _ in range(6):
                    await websocket.recv()
                await websocket.send(_frame("command.execute", {"command": "ob siebie"}, request_id="look-1"))
                frames = [parse_web_envelope(await websocket.recv()) for _ in range(3)]
                self.assertEqual(frames[0].type, "output.text")
                self.assertEqual(frames[0].payload["text"], tcp_output.output)

    async def test_bad_subprotocol_and_bad_origin_are_rejected(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            with self.assertRaises(InvalidStatusCode):
                async with self._connect(port, "http://localhost:3000", subprotocols=["wrong.v1"]):
                    pass
            with self.assertRaises(InvalidStatusCode):
                async with self._connect(port, "http://evil.example"):
                    pass

    async def test_duplicate_origin_handshake_is_rejected_without_session_task_or_client(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        started = asyncio.Event()
        original_run_session = self.server._run_session

        async def marked_run_session(*args: Any, **kwargs: Any) -> Any:
            started.set()
            return await original_run_session(*args, **kwargs)

        self.server._run_session = marked_run_session  # type: ignore[assignment]
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            writer.write(
                (
                    "GET / HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    "Sec-WebSocket-Version: 13\r\n"
                    "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                    "Sec-WebSocket-Protocol: astergard.v1\r\n"
                    "Origin: http://localhost:3000\r\n"
                    "Origin: http://evil.example\r\n"
                    "\r\n"
                ).encode("ascii")
            )
            await writer.drain()
            response = await _read_http_response(reader)
            writer.close()
            await writer.wait_closed()
        self.assertIn("403 Forbidden", response)
        self.assertFalse(started.is_set())
        self.assertEqual(len(self.server.clients), 0)
        self.assertEqual(len(self.server._active_transports), 0)

    async def test_failed_login(self) -> None:
        self.assertTrue(self.server.repo.register("web", "secret"))
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "web", "password": "bad"}, request_id="login-1"))
                first = parse_web_envelope(await websocket.recv())
                second = parse_web_envelope(await websocket.recv())
                self.assertEqual(first.type, "output.text")
                self.assertEqual(second.type, "auth.result")
                self.assertFalse(second.payload["success"])
                self.assertEqual(second.request_id, "login-1")

    async def test_web_creator_flow_creates_character_and_reaches_ready(self) -> None:
        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=500, command_rate_limit_count=500),
        )
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                greeting = parse_web_envelope(await websocket.recv())
                self.assertEqual(greeting.type, "output.text")

                await websocket.send(_frame("creator.start", {"username": "newbie", "password": "secret"}, request_id="start-1"))
                started = parse_web_envelope(await websocket.recv())
                self.assertEqual(started.type, "creator.started")
                step = started.payload["step"]
                self.assertEqual(step["step_id"], "name")

                answers = {
                    "name": "Nowy",
                    "gender_id": "f",
                    "age": "24",
                }

                while True:
                    step_id = step["step_id"]
                    value = _creator_answer(step, answers)
                    request_id = f"submit-{step_id}"
                    await websocket.send(_frame("creator.submit", {"step_id": step_id, "value": value}, request_id=request_id))
                    response = parse_web_envelope(await websocket.recv())
                    if response.type == "creator.step":
                        step = response.payload
                        continue
                    self.assertEqual(response.type, "creator.finished")
                    self.assertEqual(response.request_id, request_id)
                    break

                post_creation_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                frame_types = [frame.type for frame in post_creation_frames]
                self.assertEqual(frame_types, ["output.text", "output.text", "room.info", "character.vitals", "output.prompt", "session.ready"])
                self.assertEqual(frame_types.count("session.ready"), 1)
                self.assertNotIn("auth.result", frame_types)
                self.assertEqual(post_creation_frames[4].payload["prompt"], ">")
                self.assertNotIn("secret", "".join(frame.payload.get("text", "") if frame.type == "output.text" else "" for frame in post_creation_frames))
                character = self.server.repo.load("newbie")
                self.assertEqual(character.name, "Nowy")
                self.assertEqual(character.gender_description, "kobieta")
                self.assertEqual(character.age, 24)
                self.assertEqual(character.room_id, STARTING_ROOM_ID)

    async def test_web_creator_special_feature_submission_uses_public_step_id_and_finishes(self) -> None:
        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=500, command_rate_limit_count=500),
        )
        answers = {
            "name": "Nowy",
            "gender_id": "f",
            "age": "24",
        }
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                step, _ = await _drive_creator_to_special_feature(
                    websocket,
                    suffix="public",
                    username="public-step",
                    password="secret",
                    answers=answers,
                )

                self.assertEqual(step["step_id"], "special_feature")
                request_id = "public-special-feature"
                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "blizna_policzek"}, request_id=request_id))
                finished = parse_web_envelope(await websocket.recv())
                self.assertEqual(finished.type, "creator.finished")
                self.assertEqual(finished.request_id, request_id)

                post_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                frame_types = [frame.type for frame in post_frames]
                self.assertEqual(frame_types.count("session.ready"), 1)
                self.assertNotIn("protocol.error", frame_types)
                self.assertNotIn("Input exceeds the transport limit", "".join(frame.payload.get("text", "") for frame in post_frames if frame.type == "output.text"))

    async def test_web_creator_rejects_stale_step_id_and_recovers(self) -> None:
        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=500, command_rate_limit_count=500),
        )
        answers = {
            "name": "Nowy",
            "gender_id": "f",
            "age": "24",
        }
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                step, stale_step_id = await _drive_creator_to_special_feature(
                    websocket,
                    suffix="stale",
                    username="stale-step",
                    password="secret",
                    answers=answers,
                )

                self.assertEqual(step["step_id"], "special_feature")
                self.assertNotEqual(stale_step_id, step["step_id"])

                stale_request_id = "stale-special-feature"
                await websocket.send(_frame("creator.submit", {"step_id": stale_step_id, "value": "blizna_policzek"}, request_id=stale_request_id))
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.type, "creator.validation_error")
                self.assertEqual(error.request_id, stale_request_id)
                self.assertEqual(error.payload["step_id"], stale_step_id)
                self.assertEqual(error.payload["field"], "step_id")

                recovery_request_id = "stale-recovery"
                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "blizna_policzek"}, request_id=recovery_request_id))
                finished = parse_web_envelope(await websocket.recv())
                self.assertEqual(finished.type, "creator.finished")
                self.assertEqual(finished.request_id, recovery_request_id)
                post_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                self.assertEqual([frame.type for frame in post_frames].count("session.ready"), 1)

    async def test_web_creator_conflict_is_controlled_and_atomic_with_barrier(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        answers = {
            "name": "Nowy",
            "gender_id": "f",
            "age": "24",
        }
        ready_for_final_submit = asyncio.Event()
        ready_count = 0

        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as first, self._connect(port, "http://localhost:3000") as second:
                first_drive_task = asyncio.create_task(
                    _drive_creator_to_special_feature(
                        first,
                        suffix="first",
                        username="dupe",
                        password="secret",
                        answers=answers,
                    )
                )
                second_drive_task = asyncio.create_task(
                    _drive_creator_to_special_feature(
                        second,
                        suffix="second",
                        username="dupe",
                        password="secret",
                        answers=answers,
                    )
                )
                first_step, _ = await first_drive_task
                second_step, _ = await second_drive_task

                async def finalize(websocket: Any, *, suffix: str, step: dict[str, Any]) -> tuple[Any, list[Any], str]:
                    nonlocal ready_count
                    ready_count += 1
                    if ready_count == 2:
                        ready_for_final_submit.set()
                    await ready_for_final_submit.wait()

                    request_id = f"{suffix}-special_feature"
                    await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "blizna_policzek"}, request_id=request_id))
                    response = parse_web_envelope(await websocket.recv())
                    if response.type == "creator.finished":
                        post_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                        return response, post_frames, request_id

                    self.assertEqual(response.type, "creator.validation_error")
                    self.assertEqual(response.request_id, request_id)
                    self.assertEqual(response.payload["step_id"], "special_feature")
                    self.assertEqual(response.payload["field"], "username_taken")
                    return response, [], request_id

                first_finalize_task = asyncio.create_task(
                    finalize(first, suffix="first", step=first_step)
                )
                second_finalize_task = asyncio.create_task(
                    finalize(second, suffix="second", step=second_step)
                )
                first_result, second_result = await asyncio.gather(first_finalize_task, second_finalize_task)

                results = [first_result, second_result]
                finished_results = [result for result in results if result[0].type == "creator.finished"]
                rejected_results = [result for result in results if result[0].type == "creator.validation_error"]
                self.assertEqual(len(finished_results), 1)
                self.assertEqual(len(rejected_results), 1)

                finished_response, post_frames, finished_request_id = finished_results[0]
                self.assertEqual(finished_response.request_id, finished_request_id)
                finished_types = [frame.type for frame in post_frames]
                self.assertEqual(finished_types.count("session.ready"), 1)
                self.assertNotIn("auth.result", finished_types)
                self.assertNotIn("creator.finished", finished_types)
                self.assertEqual(finished_types.count("output.text"), 2)
                self.assertIn("character.vitals", finished_types)
                self.assertIn("room.info", finished_types)
                self.assertIn("output.prompt", finished_types)

                rejected_response, rejected_frames, rejected_request_id = rejected_results[0]
                self.assertEqual(rejected_response.request_id, rejected_request_id)
                self.assertIn(rejected_request_id, {"first-special_feature", "second-special_feature"})
                self.assertEqual(rejected_response.payload["field"], "username_taken")
                self.assertEqual(rejected_response.payload["step_id"], "special_feature")
                self.assertEqual(rejected_frames, [])

                character = self.server.repo.load("dupe")
                self.assertEqual(character.name, "Nowy")
                self.assertEqual(character.gender_description, "kobieta")
                self.assertEqual(character.age, 24)
                self.assertEqual(character.room_id, STARTING_ROOM_ID)
                await first.close()
                await second.close()
                await first.wait_closed()
                await second.wait_closed()
                self.assertNotEqual(first.close_code, 1011)
                self.assertNotEqual(second.close_code, 1011)

    async def test_web_creator_oversized_submit_preserves_request_id_and_socket(self) -> None:
        config = WebSocketGatewayConfig(
            allowed_origins=("http://localhost:3000",),
            limits=WebSocketTransportLimits(message_rate_limit_count=500, command_rate_limit_count=500),
        )
        answers = {
            "name": "Nowy",
            "gender_id": "f",
            "age": "24",
        }
        oversized_value = "ż" * 64 + "a"
        self.assertEqual(len(oversized_value.encode("utf-8")), 129)

        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                step, _ = await _drive_creator_to_special_feature(
                    websocket,
                    suffix="oversize",
                    username="oversize-step",
                    password="secret",
                    answers=answers,
                )

                self.assertEqual(step["step_id"], "special_feature")
                request_id = "oversize-creator-1"
                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": oversized_value}, request_id=request_id))
                raw_error = await websocket.recv()
                error = parse_web_envelope(raw_error)
                self.assertEqual(error.type, "creator.validation_error")
                self.assertEqual(error.request_id, request_id)
                self.assertEqual(error.payload["step_id"], "special_feature")
                self.assertEqual(error.payload["field"], "value")
                self.assertEqual(error.payload["code"], "creator_value_too_long")
                self.assertEqual(error.payload["message"], "Odpowiedź jest zbyt długa.")
                self.assertNotIn("Input exceeds the transport limit", raw_error)

                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "blizna_policzek"}, request_id="oversize-creator-2"))
                finished = parse_web_envelope(await websocket.recv())
                self.assertEqual(finished.type, "creator.finished")
                self.assertEqual(finished.request_id, "oversize-creator-2")

                post_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                self.assertEqual([frame.type for frame in post_frames].count("session.ready"), 1)
                self.assertNotIn("protocol.error", [frame.type for frame in post_frames])
                self.assertNotIn(
                    "Input exceeds the transport limit.",
                    "".join(frame.payload.get("text", "") for frame in post_frames if frame.type == "output.text"),
                )

                await websocket.send(_frame("connection.ping", {}, request_id="oversize-ping"))
                pong = parse_web_envelope(await websocket.recv())
                self.assertEqual(pong.type, "connection.pong")
                self.assertEqual(pong.request_id, "oversize-ping")

    async def test_web_creator_cancel_and_disconnect_do_not_persist(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="cancel-hello"))
                await websocket.recv()

                await websocket.send(_frame("creator.start", {"username": "cancelled", "password": "secret"}, request_id="cancel-start"))
                started = parse_web_envelope(await websocket.recv())
                self.assertEqual(started.type, "creator.started")

                await websocket.send(_frame("creator.cancel", {"step_id": "name"}, request_id="cancel-step"))
                cancelled = parse_web_envelope(await websocket.recv())
                self.assertEqual(cancelled.type, "creator.cancelled")
                self.assertEqual(cancelled.request_id, "cancel-step")
                self.assertFalse(self.server.repo.player_exists("cancelled"))
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(websocket.recv(), timeout=0.2)
                await websocket.close()
                await websocket.wait_closed()
                await self._wait_for_cleanup()

            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="disconnect-hello"))
                await websocket.recv()
                await websocket.send(_frame("creator.start", {"username": "disconnect", "password": "secret"}, request_id="disconnect-start"))
                started = parse_web_envelope(await websocket.recv())
                self.assertEqual(started.type, "creator.started")

                step = started.payload["step"]
                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "Rodzic"}, request_id="disconnect-name"))
                step = parse_web_envelope(await websocket.recv())
                self.assertEqual(step.type, "creator.step")
                self.assertEqual(step.payload["step_id"], "gender_id")

                await websocket.close()
                await websocket.wait_closed()
                await self._wait_for_cleanup()
                self.assertFalse(self.server.repo.player_exists("disconnect"))
                self.assertNotEqual(websocket.close_code, 1011)

    async def test_web_creator_allows_relogin_after_finish(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        answers = {
            "name": "Powracajacy",
            "gender_id": "m",
            "age": "26",
        }
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                finished_response, post_frames, _ = await _drive_web_creator(
                    websocket,
                    suffix="return",
                    username="returning",
                    password="secret",
                    answers=answers,
                )
                self.assertEqual(finished_response.type, "creator.finished")
                post_types = [frame.type for frame in post_frames]
                self.assertEqual(post_types.count("output.text"), 2)
                self.assertEqual(post_types.count("session.ready"), 1)
                await websocket.close()
                await websocket.wait_closed()
                await self._wait_for_cleanup()

            character = self.server.repo.load("returning")
            self.assertEqual(character.name, "Powracajacy")
            self.assertEqual(character.gender_description, "mężczyzna")
            self.assertEqual(character.age, 26)
            self.assertEqual(character.room_id, STARTING_ROOM_ID)

            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="relogin-hello"))
                greeting = parse_web_envelope(await websocket.recv())
                self.assertEqual(greeting.type, "output.text")

                await websocket.send(_frame("auth.login", {"username": "returning", "password": "secret"}, request_id="relogin-login"))
                frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                self.assertEqual([frame.type for frame in frames], ["auth.result", "output.text", "room.info", "character.vitals", "output.prompt", "session.ready"])
                self.assertEqual(frames[0].request_id, "relogin-login")
                self.assertEqual(frames[-1].payload["username"], "returning")

    async def test_web_command_changes_emit_updated_vitals(self) -> None:
        self.assertTrue(self.server.repo.register("walker", "secret"))
        character = self.server.repo.load("walker")
        character.room_id = 60
        self.server.repo.save(character)
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "walker", "password": "secret"}, request_id="login-1"))
                login_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                initial_vitals = login_frames[3]

                await websocket.send(_frame("command.execute", {"command": "szukaj"}, request_id="search-1"))
                command_frames = [parse_web_envelope(await websocket.recv()) for _ in range(4)]
                self.assertEqual([frame.type for frame in command_frames], ["output.text", "command.result", "character.vitals", "output.prompt"])
                updated_vitals = command_frames[2]
                self.assertLess(updated_vitals.payload["stamina_current"], initial_vitals.payload["stamina_current"])

    async def test_web_creator_invalid_final_answer_preserves_request_id(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        answers = {
            "name": "Bledny",
            "gender_id": "f",
            "age": "22",
        }
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                step, _ = await _drive_creator_to_special_feature(
                    websocket,
                    suffix="invalid",
                    username="invalid-final",
                    password="secret",
                    answers=answers,
                )
                self.assertEqual(step["step_id"], "special_feature")

                request_id = "invalid-final-special-feature"
                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "nieprawidlowy-wybor"}, request_id=request_id))
                response = parse_web_envelope(await websocket.recv())
                self.assertEqual(response.type, "creator.validation_error")
                self.assertEqual(response.request_id, request_id)
                self.assertEqual(response.payload["step_id"], "special_feature")
                self.assertEqual(response.payload["field"], "special_feature")
                self.assertFalse(self.server.repo.player_exists("invalid-final"))

                await websocket.send(_frame("creator.submit", {"step_id": step["step_id"], "value": "blizna_policzek"}, request_id="invalid-final-retry"))
                finished = parse_web_envelope(await websocket.recv())
                self.assertEqual(finished.type, "creator.finished")
                post_frames = [parse_web_envelope(await websocket.recv()) for _ in range(6)]
                self.assertEqual([frame.type for frame in post_frames].count("session.ready"), 1)

    async def test_creator_back_and_cancel_keep_user_on_the_current_step(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()

                await websocket.send(_frame("creator.start", {"username": "retry", "password": "secret"}, request_id="start-1"))
                started = parse_web_envelope(await websocket.recv())
                self.assertEqual(started.type, "creator.started")

                await websocket.send(_frame("creator.submit", {"step_id": "name", "value": ""}, request_id="submit-bad"))
                invalid = parse_web_envelope(await websocket.recv())
                self.assertEqual(invalid.type, "creator.validation_error")
                self.assertEqual(invalid.payload["step_id"], "name")

                await websocket.send(_frame("creator.submit", {"step_id": "name", "value": "Retry"}, request_id="submit-good"))
                step = parse_web_envelope(await websocket.recv())
                self.assertEqual(step.type, "creator.step")
                self.assertEqual(step.payload["step_id"], "gender_id")

                await websocket.send(_frame("creator.back", {"step_id": "gender_id"}, request_id="back-1"))
                back = parse_web_envelope(await websocket.recv())
                self.assertEqual(back.type, "creator.step")
                self.assertEqual(back.payload["step_id"], "name")

                await websocket.send(_frame("creator.cancel", {"step_id": "name"}, request_id="cancel-1"))
                cancelled = parse_web_envelope(await websocket.recv())
                self.assertEqual(cancelled.type, "creator.cancelled")
                self.assertEqual(cancelled.payload["username"], "retry")

    async def test_move_emits_room_info_before_command_text(self) -> None:
        self.assertTrue(self.server.repo.register("walker", "secret"))
        character = self.server.repo.load("walker")
        character.room_id = 60
        self.server.repo.save(character)
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "walker", "password": "secret"}, request_id="login-1"))
                for _ in range(6):
                    await websocket.recv()

                await websocket.send(_frame("command.execute", {"command": "poludnie"}, request_id="move-1"))
                frames = [parse_web_envelope(await websocket.recv()) for _ in range(5)]
                self.assertEqual([frame.type for frame in frames], ["room.info", "output.text", "command.result", "character.vitals", "output.prompt"])
                self.assertLess(frames[0].sequence or 0, frames[1].sequence or 0)
                self.assertLess(frames[1].sequence or 0, frames[2].sequence or 0)
                self.assertLess(frames[2].sequence or 0, frames[3].sequence or 0)

    async def test_ping_pong_preserves_request_id(self) -> None:
        self.assertTrue(self.server.repo.register("ping", "secret"))
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "ping", "password": "secret"}, request_id="login-1"))
                for _ in range(6):
                    await websocket.recv()
                await websocket.send(_frame("connection.ping", {"nonce": "abc"}, request_id="ping-1"))
                pong = parse_web_envelope(await websocket.recv())
                self.assertEqual(pong.type, "connection.pong")
                self.assertEqual(pong.request_id, "ping-1")

    async def test_invalid_json_binary_version_and_oversize_are_rejected(self) -> None:
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send("{not-json}")
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.payload["code"], "invalid_json")

            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(b"\x00\x01\x02")
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.payload["code"], "invalid_binary")

            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(
                    _json_frame(
                        "session.hello",
                        {"client": "tests", "transport": "websocket"},
                        request_id="hello-1",
                    ).replace('"version":1', '"version":2', 1)
                )
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.payload["code"], "unsupported_version")

            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send("x" * (WEB_MESSAGE_MAX_BYTES + 1))
                try:
                    error = parse_web_envelope(await asyncio.wait_for(websocket.recv(), timeout=1.0))
                    self.assertEqual(error.payload["code"], "message_too_large")
                except Exception:
                    self.assertIn(websocket.close_code, {1009, 1008})

    async def test_command_length_limit_is_rejected(self) -> None:
        self.assertTrue(self.server.repo.register("len", "secret"))
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "len", "password": "secret"}, request_id="login-1"))
                for _ in range(6):
                    await websocket.recv()
                await websocket.send(_frame("command.execute", {"command": "ż" * (COMMAND_LENGTH_LIMIT + 1)}, request_id="cmd-1"))
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.payload["code"], "message_too_large")

    async def test_whitespace_command_is_rejected_without_closing_socket(self) -> None:
        self.assertTrue(self.server.repo.register("blank", "secret"))
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "blank", "password": "secret"}, request_id="login-1"))
                for _ in range(6):
                    await websocket.recv()

                await websocket.send(_frame("command.execute", {"command": "   "}, request_id="cmd-blank"))
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.type, "protocol.error")
                self.assertEqual(error.payload["code"], "invalid_command")
                self.assertEqual(error.payload["message"], "Command must contain non-whitespace characters.")
                self.assertEqual(error.request_id, "cmd-blank")

                await websocket.send(_frame("command.execute", {"command": "spojrz"}, request_id="cmd-good"))
                frames = [parse_web_envelope(await websocket.recv()) for _ in range(3)]
                self.assertEqual([frame.type for frame in frames], ["output.text", "command.result", "output.prompt"])
                self.assertEqual(frames[1].request_id, "cmd-good")
                self.assertIsNone(websocket.close_code)

    async def test_disconnect_during_login_and_command(self) -> None:
        self.assertTrue(self.server.repo.register("disconnect", "secret"))
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.close()
            await asyncio.wait_for(websocket.wait_closed(), timeout=2.0)
            await self._wait_for_cleanup()
            self.assertEqual(len(self.server.clients), 0)

            async with self._connect(port, "http://localhost:3000") as websocket:
                await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                await websocket.recv()
                await websocket.send(_frame("auth.login", {"username": "disconnect", "password": "secret"}, request_id="login-1"))
                for _ in range(6):
                    await websocket.recv()
                await websocket.close()
            await asyncio.wait_for(websocket.wait_closed(), timeout=2.0)
            await self._wait_for_cleanup()
            self.assertEqual(len(self.server.clients), 0)

    async def test_identical_usernames_do_not_cross_route(self) -> None:
        self.assertTrue(self.server.repo.register("same", "secret"))
        character = self.server.repo.load("same")
        character.room_id = 60
        self.server.repo.save(character)
        config = WebSocketGatewayConfig(allowed_origins=("http://localhost:3000",))
        async with websocket_gateway_context(self.server, config) as (_gateway, port):
            async with self._connect(port, "http://localhost:3000") as first, self._connect(port, "http://localhost:3000") as second:
                for websocket in (first, second):
                    await websocket.send(_frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"))
                    await websocket.recv()
                    await websocket.send(_frame("auth.login", {"username": "same", "password": "secret"}, request_id="login-1"))
                    for _ in range(6):
                        await websocket.recv()

                await first.send(_frame("command.execute", {"command": "spojrz"}, request_id="cmd-1"))
                first_frames = [parse_web_envelope(await first.recv()) for _ in range(3)]
                self.assertEqual([frame.type for frame in first_frames], ["output.text", "command.result", "output.prompt"])
                with self.assertRaises(asyncio.TimeoutError):
                    await asyncio.wait_for(second.recv(), timeout=0.2)


class WebSocketGatewayDeadlineTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.harness = TestGameHarness().start()
        self.server = self.harness.require_server()
        self.clock = FakeClock()
        self._wait_for_patch = patch(
            "astergard.application.websocket_transport.asyncio.wait_for",
            side_effect=self._passthrough_wait_for,
        )
        self._monotonic_patch = patch(
            "astergard.application.websocket_transport.monotonic",
            new=self.clock.monotonic,
        )
        self._wait_for_patch.start()
        self._monotonic_patch.start()

    async def asyncTearDown(self) -> None:
        self._wait_for_patch.stop()
        self._monotonic_patch.stop()
        self.harness.close()

    async def _passthrough_wait_for(self, awaitable: Any, timeout: float | None = None) -> Any:
        return await awaitable

    async def _login_with_script(
        self,
        frames: list[str | bytes],
        *,
        limits: WebSocketTransportLimits,
    ) -> tuple[Any, ScriptedWebSocket]:
        websocket = ScriptedWebSocket(self.clock, frames)
        from astergard.application.websocket_transport import WebSocketSessionTransport

        transport = WebSocketSessionTransport(cast(Any, websocket), limits=limits)
        result = await self.server.session_flow.login(transport)
        return result, websocket

    def _parse_sent(self, websocket: ScriptedWebSocket) -> list[Any]:
        return [parse_web_envelope(frame) for frame in websocket.sent]

    async def test_ping_before_hello_is_protocol_error_and_does_not_extend_deadline(self) -> None:
        limits = WebSocketTransportLimits(
            hello_timeout_seconds=1.0,
            login_timeout_seconds=1.0,
            max_protocol_errors=50,
            message_rate_limit_count=50,
            command_rate_limit_count=50,
        )
        result, websocket = await self._login_with_script(
            [
                _frame("connection.ping", {"nonce": "1"}, request_id="ping-1"),
                _frame("connection.ping", {"nonce": "2"}, request_id="ping-2"),
                _frame("connection.ping", {"nonce": "3"}, request_id="ping-3"),
                _frame("connection.ping", {"nonce": "4"}, request_id="ping-4"),
            ],
            limits=limits,
        )
        self.assertTrue(result.close_connection)
        self.assertIsNone(result.character)
        frames = self._parse_sent(websocket)
        invalid_state_errors = [frame for frame in frames if frame.type == "protocol.error" and frame.payload["code"] == "invalid_state"]
        self.assertGreaterEqual(len(invalid_state_errors), 1)
        self.assertTrue(any(frame.type == "protocol.error" and frame.payload["code"] == "timeout_hello" for frame in frames))
        self.assertFalse(any(frame.type == "connection.pong" for frame in frames))

    async def test_correct_hello_before_deadline_and_ping_after_hello(self) -> None:
        self.assertTrue(self.server.repo.register("web", "secret"))
        limits = WebSocketTransportLimits(
            hello_timeout_seconds=1.0,
            login_timeout_seconds=1.0,
            max_protocol_errors=50,
            message_rate_limit_count=50,
            command_rate_limit_count=50,
        )
        result, websocket = await self._login_with_script(
            [
                _frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"),
                _frame("connection.ping", {"nonce": "pong"}, request_id="ping-1"),
                _frame("auth.login", {"username": "web", "password": "secret"}, request_id="login-1"),
            ],
            limits=limits,
        )
        self.assertFalse(result.close_connection)
        self.assertIsNotNone(result.character)
        frames = self._parse_sent(websocket)
        self.assertTrue(any(frame.type == "connection.pong" and frame.request_id == "ping-1" for frame in frames))
        self.assertTrue(any(frame.type == "auth.result" and frame.request_id == "login-1" for frame in frames))
        self.assertFalse(any(frame.type == "protocol.error" for frame in frames))

    async def test_login_deadline_is_not_extended_by_bad_messages(self) -> None:
        self.assertTrue(self.server.repo.register("rate", "secret"))
        limits = WebSocketTransportLimits(
            hello_timeout_seconds=1.0,
            login_timeout_seconds=1.0,
            max_protocol_errors=50,
            message_rate_limit_count=50,
            command_rate_limit_count=50,
        )
        result, websocket = await self._login_with_script(
            [
                _frame("session.hello", {"client": "tests", "transport": "websocket"}, request_id="hello-1"),
                _frame("command.execute", {"command": "spojrz"}, request_id="bad-1"),
                _frame("command.execute", {"command": "idz"}, request_id="bad-2"),
                _frame("command.execute", {"command": "mow"}, request_id="bad-3"),
            ],
            limits=limits,
        )
        self.assertTrue(result.close_connection)
        self.assertIsNone(result.character)
        frames = self._parse_sent(websocket)
        self.assertTrue(any(frame.type == "protocol.error" and frame.payload["code"] == "invalid_state" for frame in frames))
        self.assertTrue(any(frame.type == "protocol.error" and frame.payload["code"] == "timeout_login" for frame in frames))
        self.assertFalse(any(frame.type == "connection.pong" for frame in frames))

    def test_gateway_config_validates_timeout_values(self) -> None:
        config = WebSocketGatewayConfig()
        self.assertGreater(config.ping_timeout_seconds, 0)
        self.assertGreater(config.close_timeout_seconds, 0)
        with self.assertRaises(ValueError):
            WebSocketGatewayConfig(ping_interval_seconds=0)
        with self.assertRaises(ValueError):
            WebSocketGatewayConfig(ping_timeout_seconds=0)
        with self.assertRaises(ValueError):
            WebSocketGatewayConfig(ping_timeout_seconds=False)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            WebSocketGatewayConfig(close_timeout_seconds=float("inf"))
        with self.assertRaises(ValueError):
            WebSocketGatewayConfig(close_timeout_seconds=False)  # type: ignore[arg-type]

    async def test_gateway_run_passes_websocket_timeouts_to_serve(self) -> None:
        fake_lifecycle = type("Lifecycle", (), {"shutdown_requested": True})()
        fake_server = type("Server", (), {"lifecycle": fake_lifecycle})()
        gateway = WebSocketGateway(
            fake_server,
            WebSocketGatewayConfig(
                port=0,
                ping_timeout_seconds=17.0,
                close_timeout_seconds=6.0,
            ),
        )
        with patch("astergard.server.gateway.serve", wraps=serve) as serve_mock:
            await gateway.run()
        self.assertTrue(serve_mock.called)
        kwargs = serve_mock.call_args.kwargs
        self.assertEqual(kwargs["ping_timeout"], 17.0)
        self.assertEqual(kwargs["close_timeout"], 6.0)
