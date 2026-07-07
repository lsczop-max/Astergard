from __future__ import annotations

import json
from typing import Any

from astergard.characters.models import Character
from astergard.world.manager import WorldManager


class MinimapService:
    """Temporary debug-only payload builder for Mudlet full-world rendering."""

    def build_payload(
        self,
        character: Character,
        world: WorldManager,
    ) -> dict[str, Any]:
        location = world.get_location(character.room_id)
        rooms: dict[str, dict[str, Any]] = {}
        for room_id, room in sorted(world.locations.items()):
            rooms[str(room_id)] = {
                "room_id": room.id,
                "name": room.name,
                "zone": room.zone,
                "exits": {
                    direction: exit_data.target_room
                    for direction, exit_data in sorted(room.exits.items())
                },
            }

        # TODO: DEBUG ONLY - remove full map payload before public alpha.
        return {
            "type": "full_map_debug",
            "current_room_id": character.room_id if location is None else location.id,
            "current_room_name": "" if location is None else location.name,
            "current_zone": "" if location is None else location.zone,
            "rooms": rooms,
        }

    def serialize_payload(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"<MAP_JSON>{encoded}</MAP_JSON>"
