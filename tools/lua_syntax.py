from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _strip_comments_and_strings(text: str) -> str:
    result: list[str] = []
    i = 0
    length = len(text)
    in_string: str | None = None
    while i < length:
        char = text[i]
        next_char = text[i + 1] if i + 1 < length else ""
        if in_string is not None:
            if char == "\\":
                i += 2
                continue
            if char == in_string:
                in_string = None
            i += 1
            continue
        if char in {"'", '"'}:
            in_string = char
            i += 1
            continue
        if char == "-" and next_char == "-":
            while i < length and text[i] not in "\r\n":
                i += 1
            continue
        result.append(char)
        i += 1
    return "".join(result)


def validate_lua_structure(text: str) -> list[str]:
    cleaned = _strip_comments_and_strings(text)
    stack: list[tuple[str, int]] = []
    errors: list[str] = []
    for match in _TOKEN_RE.finditer(cleaned):
        token = match.group(0)
        if token in {"function", "do", "then", "repeat"}:
            stack.append((token, match.start()))
            continue
        if token == "until":
            if stack and stack[-1][0] == "repeat":
                stack.pop()
            else:
                errors.append(f"Nieoczekiwane `until` przy pozycji {match.start()}")
            continue
        if token == "end":
            if stack:
                stack.pop()
            else:
                errors.append(f"Nieoczekiwane `end` przy pozycji {match.start()}")
    return errors
