from __future__ import annotations

from enum import IntEnum
from typing import Any


class AdminRole(IntEnum):
    PLAYER = 0
    HELPER = 10
    GM = 20
    ADMIN = 30
    OWNER = 40


_ROLE_NAMES = {
    "player": AdminRole.PLAYER,
    "helper": AdminRole.HELPER,
    "gm": AdminRole.GM,
    "admin": AdminRole.ADMIN,
    "owner": AdminRole.OWNER,
}


def parse_role(value: str | AdminRole | None) -> AdminRole:
    if isinstance(value, AdminRole):
        return value
    if value is None:
        return AdminRole.PLAYER
    return _ROLE_NAMES.get(str(value).strip().lower(), AdminRole.PLAYER)


def role_for_actor(actor: Any) -> AdminRole:
    username = str(getattr(actor, "username", "")).lower()
    if username == "admin":
        return AdminRole.OWNER
    explicit = getattr(actor, "admin_role", None)
    if explicit is not None:
        return parse_role(explicit)
    if bool(getattr(actor, "is_admin", False)):
        return AdminRole.ADMIN
    return AdminRole.PLAYER


def has_role(actor: Any, required: AdminRole | str | None) -> bool:
    return role_for_actor(actor) >= parse_role(required)
