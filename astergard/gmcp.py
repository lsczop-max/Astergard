from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from astergard.world.manager import REGION_LABELS

IAC = 255
SB = 250
SE = 240
WILL = 251
GMCP_OPTION = 201

ROOM_INFO_PACKAGE = "Room.Info"
CORE_HELLO_PACKAGE = "Core.Hello"
ASTERGARD_PACKAGE_NAME = "Astergard"
ASTERGARD_PACKAGE_VERSION = "0.1.0"

POLISH_TO_MUDLET_DIRECTION = {
    "polnoc": "n",
    "poludnie": "s",
    "wschod": "e",
    "zachod": "w",
    "polnocny-wschod": "ne",
    "polnocny-zachod": "nw",
    "poludniowy-wschod": "se",
    "poludniowy-zachod": "sw",
    "gora": "up",
    "dol": "down",
}


@dataclass(frozen=True, slots=True)
class RoomInfo:
    num: int
    name: str
    area: str
    coords: dict[str, int]
    exits: dict[str, int]
    area_label: str | None = None
    terrain: str | None = None
    special_exits: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "num": self.num,
            "name": self.name,
            "area": self.area,
            "coords": dict(self.coords),
            "exits": dict(self.exits),
        }
        if self.area_label:
            data["area_label"] = self.area_label
        if self.terrain:
            data["terrain"] = self.terrain
        if self.special_exits:
            data["special_exits"] = list(self.special_exits)
        return data


def mudlet_area_label(area: str) -> str:
    return REGION_LABELS.get(area, area)


def location_room_info(location, world) -> RoomInfo:
    exits: dict[str, int] = {}
    special_exits: list[dict[str, Any]] = []
    for direction, exit_ in sorted(location.exits.items()):
        mudlet_direction = POLISH_TO_MUDLET_DIRECTION.get(direction)
        if mudlet_direction is None:
            special_exits.append(
                {
                    "direction": direction,
                    "target": exit_.target_room,
                    "kind": exit_.kind or direction,
                    "visible": exit_.visible,
                    "door": exit_.is_door,
                    "locked": exit_.is_locked,
                }
            )
            continue
        exits[mudlet_direction] = exit_.target_room
        if exit_.is_door or exit_.kind or not exit_.visible:
            special_exits.append(
                {
                    "direction": mudlet_direction,
                    "target": exit_.target_room,
                    "kind": exit_.kind or ("door" if exit_.is_door else mudlet_direction),
                    "visible": exit_.visible,
                    "door": exit_.is_door,
                    "locked": exit_.is_locked,
                }
            )
    return RoomInfo(
        num=location.id,
        name=location.name,
        area=location.zone,
        coords={"x": location.map_x, "y": location.map_y, "z": location.map_z},
        exits=exits,
        area_label=mudlet_area_label(location.zone),
        terrain=None,
        special_exits=special_exits or None,
    )


def gmcp_payload(package: str, payload: dict[str, Any]) -> bytes:
    json_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body = f"{package} {json_payload}".encode("utf-8")
    return bytes([IAC, SB]) + body + bytes([IAC, SE])


def gmcp_negotiation_packet() -> bytes:
    return bytes([IAC, WILL, GMCP_OPTION])


def core_hello_payload() -> dict[str, str]:
    return {
        "client": ASTERGARD_PACKAGE_NAME,
        "version": ASTERGARD_PACKAGE_VERSION,
        "package": ASTERGARD_PACKAGE_NAME,
    }


def room_info_packet(location, world) -> bytes:
    return gmcp_payload(ROOM_INFO_PACKAGE, room_info_payload(location, world))


def room_info_payload(location, world) -> dict[str, Any]:
    return location_room_info(location, world).to_dict()


def core_hello_packet() -> bytes:
    return gmcp_payload(CORE_HELLO_PACKAGE, core_hello_payload())
