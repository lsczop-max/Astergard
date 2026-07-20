from __future__ import annotations

import asyncio
import socket
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from http import HTTPStatus
from math import isfinite
from typing import Any, cast
from urllib.parse import urlparse

from websockets.server import serve

from astergard.application.websocket_transport import WebSocketSessionTransport, WebSocketTransportLimits


@dataclass(frozen=True, slots=True)
class WebSocketGatewayConfig:
    host: str = "127.0.0.1"
    port: int = 4001
    subprotocol: str = "astergard.v1"
    allowed_origins: tuple[str, ...] = ()
    allow_localhost_origin: bool = False
    limits: WebSocketTransportLimits = field(default_factory=WebSocketTransportLimits)
    max_pending_messages: int = 16
    ping_interval_seconds: float | None = None
    ping_timeout_seconds: float = 20.0
    close_timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        self._validate_timeout(self.ping_interval_seconds, "ping_interval_seconds", allow_none=True)
        self._validate_timeout(self.ping_timeout_seconds, "ping_timeout_seconds")
        self._validate_timeout(self.close_timeout_seconds, "close_timeout_seconds")

    @staticmethod
    def _validate_timeout(value: float | None, field_name: str, *, allow_none: bool = False) -> None:
        if value is None:
            if allow_none:
                return
            raise ValueError(f"{field_name} must be a positive finite number.")
        if type(value) is bool or type(value) not in {int, float}:
            raise ValueError(f"{field_name} must be a positive finite number.")
        numeric = float(value)
        if not isfinite(numeric) or numeric <= 0:
            raise ValueError(f"{field_name} must be a positive finite number.")


def _origin_hostname_allowed(origin: str) -> bool:
    parsed = urlparse(origin)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def _origin_allowed(origin: str | None, config: WebSocketGatewayConfig) -> bool:
    if origin is None or origin == "":
        return False
    if origin in config.allowed_origins:
        return True
    if config.allow_localhost_origin and _origin_hostname_allowed(origin):
        return True
    return False


def _subprotocol_allowed(requested: str | None, expected: str) -> bool:
    if requested is None or requested == "":
        return False
    candidates = [part.strip() for part in requested.split(",")]
    return expected in candidates


@dataclass(slots=True)
class WebSocketGateway:
    server: Any
    config: WebSocketGatewayConfig = field(default_factory=WebSocketGatewayConfig)
    _listen_socket: socket.socket | None = None
    _active_transports: set[WebSocketSessionTransport] = field(default_factory=set)

    def _register_transport(self, transport: WebSocketSessionTransport) -> None:
        self._active_transports.add(transport)

    def _unregister_transport(self, transport: WebSocketSessionTransport) -> None:
        self._active_transports.discard(transport)

    async def _process_request(self, path: str, headers: Any) -> tuple[HTTPStatus, list[tuple[str, str]], bytes] | None:
        origins = headers.get_all("Origin")
        if len(origins) != 1:
            return (
                HTTPStatus.FORBIDDEN,
                [("Content-Type", "text/plain; charset=utf-8")],
                b"Origin rejected.",
            )
        origin = origins[0]
        if not _origin_allowed(origin, self.config):
            return (
                HTTPStatus.FORBIDDEN,
                [("Content-Type", "text/plain; charset=utf-8")],
                b"Origin rejected.",
            )
        requested_subprotocol = headers.get("Sec-WebSocket-Protocol")
        if not _subprotocol_allowed(requested_subprotocol, self.config.subprotocol):
            return (
                HTTPStatus.FORBIDDEN,
                [("Content-Type", "text/plain; charset=utf-8")],
                b"WebSocket subprotocol rejected.",
            )
        return None

    async def handle_websocket_connection(self, websocket: Any, path: str | None = None) -> None:
        transport = WebSocketSessionTransport(websocket, limits=self.config.limits)
        self._register_transport(transport)
        try:
            await self.server._run_session(transport)
        except asyncio.CancelledError:
            raise
        except Exception:
            await transport.close(close_code=1011, reason="internal server error")
        finally:
            self._unregister_transport(transport)
            try:
                await transport.close()
            except Exception:
                pass

    async def run(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.host, self.config.port))
        sock.listen()
        sock.setblocking(False)
        self._listen_socket = sock
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(serve(
                self.handle_websocket_connection,
                sock=sock,
                subprotocols=cast(Any, [cast(Any, self.config.subprotocol)]),
                process_request=self._process_request,
                compression=None,
                max_size=self.config.limits.message_max_bytes,
                max_queue=self.config.max_pending_messages,
                ping_interval=self.config.ping_interval_seconds,
                ping_timeout=self.config.ping_timeout_seconds,
                close_timeout=self.config.close_timeout_seconds,
            ))
            await self._wait_for_shutdown()

    async def _wait_for_shutdown(self) -> None:
        while not self.server.lifecycle.shutdown_requested:
            await asyncio.sleep(0.1)
        await self.close_active_connections()

    async def close_active_connections(self) -> None:
        transports = list(self._active_transports)
        for transport in transports:
            try:
                await transport.close(close_code=1001, reason="server shutdown")
            except Exception:
                pass
