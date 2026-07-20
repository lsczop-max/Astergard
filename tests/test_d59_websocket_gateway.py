from __future__ import annotations

import asyncio
import json
import socket
import unittest
from contextlib import asynccontextmanager
from collections import deque
from typing import Any, cast
from unittest.mock import patch

from websockets.client import connect
from websockets.exceptions import InvalidStatusCode
from websockets.server import serve

from astergard.application.websocket_transport import WebSocketTransportLimits
from astergard.protocol.web_v1 import (
    COMMAND_LENGTH_LIMIT,
    WEB_MESSAGE_MAX_BYTES,
    build_web_envelope,
    parse_web_envelope,
    serialize_web_envelope,
)
from astergard.server.gateway import WebSocketGateway, WebSocketGatewayConfig
from astergard.testing import TestGameHarness


def _frame(message_type: str, payload: dict[str, Any], *, request_id: str) -> str:
    return serialize_web_envelope(build_web_envelope(message_type, payload, request_id=request_id))


def _json_frame(message_type: str, payload: dict[str, Any], *, request_id: str) -> str:
    return json.dumps(
        {"version": 1, "type": message_type, "request_id": request_id, "payload": payload},
        separators=(",", ":"),
        ensure_ascii=False,
    )


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
                login_frames = [parse_web_envelope(await websocket.recv()) for _ in range(5)]
                self.assertEqual(
                    [frame.type for frame in login_frames],
                    ["auth.result", "output.text", "room.info", "output.prompt", "session.ready"],
                )
                self.assertEqual([frame.sequence for frame in login_frames], [2, 3, 4, 5, 6])
                self.assertEqual(login_frames[0].request_id, "login-1")
                self.assertEqual(login_frames[-1].payload["transport"], "web")

                await websocket.send(_frame("command.execute", {"command": "spojrz"}, request_id="cmd-1"))
                command_frames = [parse_web_envelope(await websocket.recv()) for _ in range(3)]
                self.assertEqual([frame.type for frame in command_frames], ["output.text", "command.result", "output.prompt"])
                self.assertEqual([frame.sequence for frame in command_frames], [7, 8, 9])
                self.assertEqual(command_frames[1].request_id, "cmd-1")
                self.assertEqual(
                    [frame.sequence for frame in [greeting] + login_frames + command_frames],
                    list(range(1, 10)),
                )

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
                for _ in range(5):
                    await websocket.recv()

                await websocket.send(_frame("command.execute", {"command": "poludnie"}, request_id="move-1"))
                frames = [parse_web_envelope(await websocket.recv()) for _ in range(4)]
                self.assertEqual([frame.type for frame in frames], ["room.info", "output.text", "command.result", "output.prompt"])
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
                for _ in range(5):
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
                for _ in range(5):
                    await websocket.recv()
                await websocket.send(_frame("command.execute", {"command": "ż" * (COMMAND_LENGTH_LIMIT + 1)}, request_id="cmd-1"))
                error = parse_web_envelope(await websocket.recv())
                self.assertEqual(error.payload["code"], "message_too_large")

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
                for _ in range(5):
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
                    for _ in range(5):
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
