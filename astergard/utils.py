from __future__ import annotations

from typing import Any


class ANSI:
    GOLD = "\033[1;33m"
    GREY = "\033[0;37m"
    LIGHT_BLUE = "\033[1;34m"
    RED = "\033[1;31m"
    YELLOW = "\033[1;33m"
    GREEN = "\033[1;32m"
    INDIGO = "\033[35m"
    RESET = "\033[0m"

_TAGS = {
    "gold": ANSI.GOLD,
    "grey": ANSI.GREY,
    "light_blue": ANSI.LIGHT_BLUE,
    "red": ANSI.RED,
    "yellow": ANSI.YELLOW,
    "green": ANSI.GREEN,
    "indigo": ANSI.INDIGO,
}


def colorize(text: str) -> str:
    out = text
    for tag, code in _TAGS.items():
        out = out.replace(f"<{tag}>", code).replace(f"</{tag}>", ANSI.RESET)
    return out


async def send_to_client(writer: Any, text: str, prompt: str | None = None) -> None:
    payload = colorize(text)
    if prompt is not None:
        payload = f"{payload}\r\n{prompt}"
    elif not payload.endswith("\r\n"):
        payload += "\r\n"
    try:
        writer.write(payload.encode("utf-8"))
        await writer.drain()
    except (ConnectionResetError, BrokenPipeError, RuntimeError, asyncio.CancelledError):
        raise


# asyncio intentionally imported late enough for static tools and explicit enough for runtime exception matching.
import asyncio  # noqa: E402
