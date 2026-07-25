from __future__ import annotations

import json
from collections import deque
from uuid import uuid4
from typing import Any

from astergard.characters.models import Character
from astergard.gmcp import iter_public_exits, location_room_info
from astergard.protocol.web_v1 import WEB_MESSAGE_MAX_BYTES, build_web_envelope, serialize_web_envelope
from astergard.world.manager import WorldManager

MAP_CONTRACT_VERSION = 1


def _chunk_payload_size(type_: str, payload: dict[str, Any], sequence: int) -> int:
    envelope = build_web_envelope(type_, payload, sequence=sequence)
    return len(serialize_web_envelope(envelope).encode("utf-8"))


class MinimapService:
    """Builds public room projections for debug clients and the web map state."""

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def _room_payload(self, room_id: int, room: Any, world: WorldManager) -> dict[str, Any]:
        info = location_room_info(room, world).to_dict()
        return {
            "room_id": room_id,
            "name": info["name"],
            "zone": info["area"],
            "coords": info["coords"],
            "exits": info["exits"],
        }

    def _public_map_room_payload(self, room: Any) -> dict[str, Any]:
        return {
            "room_id": room.id,
            "name": room.name,
            "region": room.zone,
            "x": room.map_x,
            "y": room.map_y,
            "z": room.map_z,
        }

    def _public_map_edges_from_room(self, room: Any, world: WorldManager, visited_room_ids: set[int]) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []
        for direction, exit_, mudlet_direction in iter_public_exits(room):
            if mudlet_direction is None:
                continue
            if exit_.target_room not in visited_room_ids:
                continue
            if world.get_location(exit_.target_room) is None:
                continue
            edges.append(
                {
                    "from_room_id": room.id,
                    "to_room_id": exit_.target_room,
                    "direction": direction,
                }
            )
        return edges

    def _public_visited_rooms(self, character: Character, world: WorldManager) -> list[Any]:
        visited_room_ids = set(character.visited_room_ids)
        current_room = world.get_location(character.room_id)
        if current_room is not None:
            visited_room_ids.add(current_room.id)
        rooms: list[Any] = []
        for room_id in sorted(visited_room_ids):
            room = world.get_location(room_id)
            if room is not None:
                rooms.append(room)
        return rooms

    def _nearby_rooms(self, world: WorldManager, origin_room_id: int, radius: int = 3) -> dict[str, dict[str, Any]]:
        if radius <= 0:
            return {}
        visited: dict[int, int] = {origin_room_id: 0}
        queue: deque[tuple[int, int]] = deque([(origin_room_id, 0)])
        result: dict[str, dict[str, Any]] = {}
        while queue:
            room_id, distance = queue.popleft()
            room = world.locations.get(room_id)
            if room is None:
                continue
            result[str(room_id)] = self._room_payload(room_id, room, world)
            if distance >= radius:
                continue
            for _direction, exit_data, _mudlet_direction in iter_public_exits(room):
                target_room_id = exit_data.target_room
                next_distance = distance + 1
                if next_distance > radius:
                    continue
                previous_distance = visited.get(target_room_id)
                if previous_distance is not None and previous_distance <= next_distance:
                    continue
                visited[target_room_id] = next_distance
                queue.append((target_room_id, next_distance))
        return dict(sorted(result.items(), key=lambda item: int(item[0])))

    def _build_web_snapshot_chunk(
        self,
        *,
        sync_id: str,
        current_room_id: int,
        rooms: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        chunk_index: int,
        complete: bool,
    ) -> dict[str, Any]:
        return {
            "map_version": MAP_CONTRACT_VERSION,
            "sync_id": sync_id,
            "chunk_index": chunk_index,
            "complete": complete,
            "current_room_id": current_room_id,
            "rooms": rooms,
            "edges": edges,
        }

    def _build_web_update_payload(
        self,
        *,
        sync_id: str,
        current_room_id: int,
        rooms: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "map_version": MAP_CONTRACT_VERSION,
            "sync_id": sync_id,
            "current_room_id": current_room_id,
            "rooms": rooms,
            "edges": edges,
        }

    def build_web_snapshot_payloads(
        self,
        character: Character,
        world: WorldManager,
        *,
        sync_id: str | None = None,
        starting_sequence: int = 1,
        max_bytes: int = WEB_MESSAGE_MAX_BYTES,
    ) -> list[dict[str, Any]]:
        current_location = world.get_location(character.room_id)
        current_room_id = character.room_id if current_location is None else current_location.id
        sync_id = sync_id or uuid4().hex
        visited_rooms = self._public_visited_rooms(character, world)
        if not visited_rooms:
            return [
                self._build_web_snapshot_chunk(
                    sync_id=sync_id,
                    current_room_id=current_room_id,
                    rooms=[],
                    edges=[],
                    chunk_index=0,
                    complete=True,
                )
            ]

        payloads: list[dict[str, Any]] = []
        current_rooms: list[dict[str, Any]] = []
        current_edges: list[dict[str, Any]] = []
        next_sequence = starting_sequence
        visited_room_ids = {room.id for room in visited_rooms}

        for room in visited_rooms:
            room_payload = self._public_map_room_payload(room)
            room_edges = self._public_map_edges_from_room(room, world, visited_room_ids)
            candidate_rooms = [*current_rooms, room_payload]
            candidate_edges = [*current_edges, *room_edges]
            candidate_payload = self._build_web_snapshot_chunk(
                sync_id=sync_id,
                current_room_id=current_room_id,
                rooms=candidate_rooms,
                edges=candidate_edges,
                chunk_index=len(payloads),
                complete=False,
            )
            if current_rooms and _chunk_payload_size("map.snapshot", candidate_payload, next_sequence) > max_bytes:
                payloads.append(
                    self._build_web_snapshot_chunk(
                        sync_id=sync_id,
                        current_room_id=current_room_id,
                        rooms=current_rooms,
                        edges=current_edges,
                        chunk_index=len(payloads),
                        complete=False,
                    )
                )
                next_sequence += 1
                current_rooms = [room_payload]
                current_edges = list(room_edges)
                continue
            current_rooms = candidate_rooms
            current_edges = candidate_edges

        final_payload = self._build_web_snapshot_chunk(
            sync_id=sync_id,
            current_room_id=current_room_id,
            rooms=current_rooms,
            edges=current_edges,
            chunk_index=len(payloads),
            complete=True,
        )
        if _chunk_payload_size("map.snapshot", final_payload, next_sequence) > max_bytes:
            raise ValueError("Map snapshot chunk exceeds transport limit.")
        payloads.append(final_payload)
        return payloads

    def build_web_update_payload(
        self,
        character: Character,
        world: WorldManager,
        *,
        sync_id: str,
        previous_visited_room_ids: set[int],
    ) -> dict[str, Any]:
        current_location = world.get_location(character.room_id)
        current_room_id = character.room_id if current_location is None else current_location.id
        current_visited_room_ids = set(character.visited_room_ids)
        if current_location is not None:
            current_visited_room_ids.add(current_location.id)

        rooms: list[dict[str, Any]] = []
        if current_location is not None and current_location.id not in previous_visited_room_ids:
            rooms.append(self._public_map_room_payload(current_location))

        edges: list[dict[str, Any]] = []
        if current_location is not None and current_location.id not in previous_visited_room_ids:
            edges.extend(self._public_map_edges_from_room(current_location, world, current_visited_room_ids))
            for room_id in sorted(previous_visited_room_ids):
                room = world.get_location(room_id)
                if room is None:
                    continue
                for direction, exit_, mudlet_direction in iter_public_exits(room):
                    if mudlet_direction is None:
                        continue
                    if exit_.target_room != current_room_id:
                        continue
                    if world.get_location(exit_.target_room) is None:
                        continue
                    edges.append(
                        {
                            "from_room_id": room.id,
                            "to_room_id": current_room_id,
                            "direction": direction,
                        }
                    )

        return self._build_web_update_payload(
            sync_id=sync_id,
            current_room_id=current_room_id,
            rooms=rooms,
            edges=self._dedupe_edges(edges),
        )

    def _dedupe_edges(self, edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique: dict[tuple[int, int, str], dict[str, Any]] = {}
        for edge in edges:
            key = (int(edge["from_room_id"]), int(edge["to_room_id"]), str(edge["direction"]))
            unique[key] = edge
        return [unique[key] for key in sorted(unique)]

    def build_payload(
        self,
        character: Character,
        world: WorldManager,
    ) -> dict[str, Any]:
        location = world.get_location(character.room_id)
        rooms: dict[str, dict[str, Any]] = {}
        for room_id, room in sorted(world.locations.items()):
            rooms[str(room_id)] = self._room_payload(room_id, room, world)

        # TODO: DEBUG ONLY - remove full map payload before public alpha.
        return {
            "type": "full_map_debug",
            "current_room_id": character.room_id if location is None else location.id,
            "current_room_name": "" if location is None else location.name,
            "current_zone": "" if location is None else location.zone,
            "current_coords": {
                "x": 0 if location is None else location.map_x,
                "y": 0 if location is None else location.map_y,
                "z": 0 if location is None else location.map_z,
            },
            "rooms": rooms,
        }

    def build_update_payload(
        self,
        character: Character,
        world: WorldManager,
        radius: int = 3,
    ) -> dict[str, Any]:
        location = world.get_location(character.room_id)
        current_room_id = character.room_id if location is None else location.id
        current_room_name = "" if location is None else location.name
        current_zone = "" if location is None else location.zone
        exits = {}
        if location is not None:
            exits = self._room_payload(current_room_id, location, world)["exits"]
        return {
            "type": "map_update",
            "current_room_id": current_room_id,
            "current_room_name": current_room_name,
            "current_zone": current_zone,
            "current_coords": {
                "x": 0 if location is None else location.map_x,
                "y": 0 if location is None else location.map_y,
                "z": 0 if location is None else location.map_z,
            },
            "exits": exits,
            "nearby_rooms": self._nearby_rooms(world, current_room_id, radius=radius),
        }

    def serialize_payload(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"<MAP_JSON>{encoded}</MAP_JSON>"
