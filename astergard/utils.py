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


def describe_gold(gold: int) -> str:
    if gold <= 0:
        return "bez pieniędzy"
    if gold < 10:
        return "z kilkoma monetami"
    if gold < 50:
        return "z sakiewką monet"
    if gold < 150:
        return "z cięższą sakiewką"
    return "z zasobnym mieszkiem"


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")


async def send_text(writer: Any, text: str) -> None:
    payload = _normalize_newlines(colorize(text))
    if not payload.endswith("\r\n"):
        payload += "\r\n"
    try:
        writer.write(payload.encode("utf-8"))
        await writer.drain()
    except (ConnectionResetError, BrokenPipeError, RuntimeError, asyncio.CancelledError):
        raise


async def send_prompt(writer: Any, prompt: str) -> None:
    payload = colorize(prompt).rstrip("\r\n")
    try:
        writer.write(payload.encode("utf-8"))
        await writer.drain()
    except (ConnectionResetError, BrokenPipeError, RuntimeError, asyncio.CancelledError):
        raise


async def send_to_client(writer: Any, text: str, prompt: str | None = None) -> None:
    await send_text(writer, text)
    if prompt is not None:
        await send_prompt(writer, prompt)


# asyncio intentionally imported late enough for static tools and explicit enough for runtime exception matching.
import asyncio  # noqa: E402
