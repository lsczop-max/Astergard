from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from astergard.world.manager import OPPOSITE, STARTING_ROOM_ID

JSON_TO_RUNTIME_DIRECTION: dict[str, str] = {
    "N": "polnoc",
    "S": "poludnie",
    "E": "wschod",
    "W": "zachod",
    "NE": "polnocny-wschod",
    "NW": "polnocny-zachod",
    "SE": "poludniowy-wschod",
    "SW": "poludniowy-zachod",
    "U": "gora",
    "D": "dol",
}

RUNTIME_TO_JSON_DIRECTION: dict[str, str] = {runtime: json_dir for json_dir, runtime in JSON_TO_RUNTIME_DIRECTION.items()}

REGION_I_ASSET_PATH = Path(__file__).resolve().parent / "data" / "region_i.json"


class RegionIDataError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RegionIRoom:
    id: int
    name: str
    region_id: str
    x: int
    y: int
    z: int
    terrain: str
    function: str
    notes: str = ""


@dataclass(frozen=True, slots=True)
class RegionIEdge:
    id: str
    from_room_id: int
    to_room_id: int
    direction: str
    reverse_direction: str
    bidirectional: bool
    passage_type: str


@dataclass(frozen=True, slots=True)
class RegionIData:
    schema_version: int
    name: str
    updated_at: str
    regions: tuple[dict[str, Any], ...]
    rooms: tuple[RegionIRoom, ...]
    edges: tuple[RegionIEdge, ...]

    @property
    def room_ids(self) -> frozenset[int]:
        return frozenset(room.id for room in self.rooms)

    @property
    def edge_pairs(self) -> frozenset[tuple[int, int]]:
        return frozenset(_ordered_room_pair(edge.from_room_id, edge.to_room_id) for edge in self.edges)


def load_region_i_data(path: Path | None = None, *, require_unique_coords: bool = True) -> RegionIData:
    asset_path = path or REGION_I_ASSET_PATH
    raw = json.loads(asset_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RegionIDataError("Region I asset must be a JSON object.")
    return _parse_region_i_payload(raw, require_unique_coords=require_unique_coords)


def _parse_region_i_payload(payload: dict[str, Any], *, require_unique_coords: bool) -> RegionIData:
    schema_version = _require_int(payload.get("schemaVersion"), "schemaVersion", minimum=1)
    name = _require_str(payload.get("name"), "name")
    updated_at = _require_str(payload.get("updatedAt"), "updatedAt")

    raw_regions = payload.get("regions")
    if not isinstance(raw_regions, list):
        raise RegionIDataError("Region I asset field 'regions' must be a list.")
    regions: tuple[dict[str, Any], ...] = tuple(
        region for region in raw_regions if isinstance(region, dict)
    )
    if len(regions) != len(raw_regions):
        raise RegionIDataError("Region I asset field 'regions' must contain only objects.")

    raw_rooms = payload.get("rooms")
    if not isinstance(raw_rooms, list):
        raise RegionIDataError("Region I asset field 'rooms' must be a list.")
    rooms = _parse_rooms(raw_rooms, require_unique_coords=require_unique_coords)

    raw_edges = payload.get("edges")
    if not isinstance(raw_edges, list):
        raise RegionIDataError("Region I asset field 'edges' must be a list.")
    edges = _parse_edges(raw_edges, rooms)

    _validate_reachability(rooms, edges)

    return RegionIData(
        schema_version=schema_version,
        name=name,
        updated_at=updated_at,
        regions=regions,
        rooms=rooms,
        edges=edges,
    )


def _parse_rooms(raw_rooms: list[Any], *, require_unique_coords: bool) -> tuple[RegionIRoom, ...]:
    seen_room_ids: set[int] = set()
    seen_coords: set[tuple[int, int, int]] = set()
    rooms: list[RegionIRoom] = []
    for index, room in enumerate(raw_rooms):
        if not isinstance(room, dict):
            raise RegionIDataError(f"Region I asset field 'rooms[{index}]' must be an object.")
        room_id = _require_int(room.get("id"), f"rooms[{index}].id", minimum=0)
        if room_id in seen_room_ids:
            raise RegionIDataError(f"Duplicate room id detected: {room_id}.")
        seen_room_ids.add(room_id)
        x = _require_int(room.get("x"), f"rooms[{index}].x")
        y = _require_int(room.get("y"), f"rooms[{index}].y")
        z = _require_int(room.get("z"), f"rooms[{index}].z")
        coords = (x, y, z)
        if require_unique_coords and coords in seen_coords:
            raise RegionIDataError(f"Duplicate room coordinates detected: {coords}.")
        seen_coords.add(coords)
        rooms.append(
            RegionIRoom(
                id=room_id,
                name=_require_str(room.get("name"), f"rooms[{index}].name"),
                region_id=_require_str(room.get("regionId"), f"rooms[{index}].regionId"),
                x=x,
                y=y,
                z=z,
                terrain=_require_str(room.get("terrain"), f"rooms[{index}].terrain"),
                function=_require_str(room.get("function"), f"rooms[{index}].function"),
                notes=_optional_str(room.get("notes")),
            )
        )
    return tuple(rooms)


def _parse_edges(raw_edges: list[Any], rooms: tuple[RegionIRoom, ...]) -> tuple[RegionIEdge, ...]:
    room_ids = {room.id for room in rooms}
    seen_edge_ids: set[str] = set()
    seen_pairs: set[tuple[int, int]] = set()
    edges: list[RegionIEdge] = []
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, dict):
            raise RegionIDataError(f"Region I asset field 'edges[{index}]' must be an object.")
        edge_id = _require_str(edge.get("id"), f"edges[{index}].id")
        if edge_id in seen_edge_ids:
            raise RegionIDataError(f"Duplicate edge id detected: {edge_id}.")
        seen_edge_ids.add(edge_id)
        from_room_id = _require_int(edge.get("from"), f"edges[{index}].from", minimum=0)
        to_room_id = _require_int(edge.get("to"), f"edges[{index}].to", minimum=0)
        if from_room_id == to_room_id:
            raise RegionIDataError(f"Edge {edge_id} cannot connect a room to itself.")
        if from_room_id not in room_ids or to_room_id not in room_ids:
            raise RegionIDataError(f"Edge {edge_id} references a missing room id.")
        pair = _ordered_room_pair(from_room_id, to_room_id)
        if pair in seen_pairs:
            raise RegionIDataError(f"Duplicate logical edge detected for rooms {pair[0]} and {pair[1]}.")
        seen_pairs.add(pair)
        direction_json = _require_str(edge.get("direction"), f"edges[{index}].direction")
        reverse_json = _require_str(edge.get("reverseDirection"), f"edges[{index}].reverseDirection")
        direction = _translate_direction(direction_json, f"edges[{index}].direction")
        reverse_direction = _translate_direction(reverse_json, f"edges[{index}].reverseDirection")
        if OPPOSITE[direction] != reverse_direction:
            raise RegionIDataError(
                f"Edge {edge_id} has inconsistent reverseDirection: {direction_json} -> {reverse_json}."
            )
        bidirectional = _require_bool(edge.get("bidirectional"), f"edges[{index}].bidirectional")
        if not bidirectional:
            raise RegionIDataError(f"Edge {edge_id} must be bidirectional.")
        edges.append(
            RegionIEdge(
                id=edge_id,
                from_room_id=from_room_id,
                to_room_id=to_room_id,
                direction=direction,
                reverse_direction=reverse_direction,
                bidirectional=bidirectional,
                passage_type=_require_str(edge.get("passageType"), f"edges[{index}].passageType"),
            )
        )
    return tuple(edges)


def _validate_reachability(rooms: tuple[RegionIRoom, ...], edges: tuple[RegionIEdge, ...]) -> None:
    if not any(room.id == STARTING_ROOM_ID for room in rooms):
        raise RegionIDataError(f"Region I asset must include the starting room {STARTING_ROOM_ID}.")
    adjacency: dict[int, set[int]] = {room.id: set() for room in rooms}
    for edge in edges:
        adjacency[edge.from_room_id].add(edge.to_room_id)
        adjacency[edge.to_room_id].add(edge.from_room_id)
    visited: set[int] = set()
    queue: deque[int] = deque([STARTING_ROOM_ID])
    while queue:
        room_id = queue.popleft()
        if room_id in visited:
            continue
        visited.add(room_id)
        for neighbor in adjacency.get(room_id, set()):
            if neighbor not in visited:
                queue.append(neighbor)
    missing = {room.id for room in rooms} - visited
    if missing:
        raise RegionIDataError(f"Region I asset has unreachable rooms from {STARTING_ROOM_ID}: {sorted(missing)}")


def _translate_direction(raw_direction: str, field_name: str) -> str:
    direction = JSON_TO_RUNTIME_DIRECTION.get(raw_direction)
    if direction is None:
        raise RegionIDataError(f"{field_name} contains an unknown direction: {raw_direction!r}.")
    return direction


def _ordered_room_pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left <= right else (right, left)


def _require_int(value: Any, field_name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool):
        raise RegionIDataError(f"{field_name} must be an integer.")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        try:
            result = int(value.strip())
        except ValueError as exc:
            raise RegionIDataError(f"{field_name} must be an integer.") from exc
    else:
        raise RegionIDataError(f"{field_name} must be an integer.")
    if minimum is not None and result < minimum:
        raise RegionIDataError(f"{field_name} must be >= {minimum}.")
    return result


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise RegionIDataError(f"{field_name} must be a boolean.")
    return value


def _require_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegionIDataError(f"{field_name} must be a non-empty string.")
    return value


def _optional_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    raise RegionIDataError("notes must be a string when provided.")
