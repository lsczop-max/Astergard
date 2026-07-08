from __future__ import annotations

import json
from collections import deque
from typing import Any

from astergard.characters.models import Character
from astergard.world.manager import WorldManager


class MinimapService:
    """Temporary debug-only payload builder for Mudlet full-world rendering."""

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def _room_payload(self, room_id: int, room: Any) -> dict[str, Any]:
        return {
            "room_id": room.id,
            "name": room.name,
            "zone": room.zone,
            "exits": {
                direction: exit_data.target_room
                for direction, exit_data in sorted(room.exits.items())
            },
        }

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
            result[str(room_id)] = self._room_payload(room_id, room)
            if distance >= radius:
                continue
            for exit_data in room.exits.values():
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

    def build_payload(
        self,
        character: Character,
        world: WorldManager,
    ) -> dict[str, Any]:
        location = world.get_location(character.room_id)
        rooms: dict[str, dict[str, Any]] = {}
        for room_id, room in sorted(world.locations.items()):
            rooms[str(room_id)] = self._room_payload(room_id, room)

        # TODO: DEBUG ONLY - remove full map payload before public alpha.
        return {
            "type": "full_map_debug",
            "current_room_id": character.room_id if location is None else location.id,
            "current_room_name": "" if location is None else location.name,
            "current_zone": "" if location is None else location.zone,
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
            exits = {
                direction: exit_data.target_room
                for direction, exit_data in sorted(location.exits.items())
            }
        return {
            "type": "map_update",
            "current_room_id": current_room_id,
            "current_room_name": current_room_name,
            "current_zone": current_zone,
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
