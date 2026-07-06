from __future__ import annotations
from astergard.world.manager import WorldManager

class AdminTools:
    def __init__(self, world: WorldManager) -> None:
        self.world = world
        self.audit_log: list[str] = []

    def teleport_room(self, username: str, room_id: int) -> str:
        if self.world.get_location(room_id) is None:
            return "Nie ma takiej lokacji."
        self.audit_log.append(f"teleport:{username}:{room_id}")
        return f"Teleportowano {username} do {room_id}."

    def world_stats(self) -> dict[str, int]:
        return {"locations": len(self.world.locations), "respawn_queue": len(self.world.respawn_queue)}
