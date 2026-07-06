from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import Deque


@dataclass(eq=False)
class FakeWriter:
    """Minimal StreamWriter-compatible fake for deterministic tests."""

    chunks: list[bytes] = field(default_factory=list)
    closed: bool = False
    drains: int = 0

    def write(self, data: bytes) -> None:
        if self.closed:
            raise RuntimeError("Cannot write to closed FakeWriter.")
        self.chunks.append(bytes(data))

    async def drain(self) -> None:
        self.drains += 1
        await asyncio.sleep(0)

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        await asyncio.sleep(0)

    def text(self) -> str:
        return b"".join(self.chunks).decode("utf-8", errors="replace")

    def clear(self) -> None:
        self.chunks.clear()


@dataclass
class FakeReader:
    """Minimal StreamReader-compatible fake backed by queued lines."""

    lines: Deque[bytes] = field(default_factory=deque)
    eof: bool = False

    @classmethod
    def from_text_lines(cls, lines: list[str]) -> "FakeReader":
        encoded = deque((line if line.endswith("\n") else f"{line}\n").encode("utf-8") for line in lines)
        return cls(encoded)

    async def readline(self) -> bytes:
        await asyncio.sleep(0)
        if self.lines:
            return self.lines.popleft()
        self.eof = True
        return b""

    def at_eof(self) -> bool:
        return self.eof or not self.lines

    def feed_line(self, line: str) -> None:
        self.eof = False
        self.lines.append((line if line.endswith("\n") else f"{line}\n").encode("utf-8"))
