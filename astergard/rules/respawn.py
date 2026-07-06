from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RespawnRules:
    max_npcs_per_room: int = 3
    default_delay_seconds: int = 300
    minimum_delay_seconds: int = 30
    patrol_move_chance: float = 0.25

    def can_spawn(self, current_count: int) -> bool:
        return current_count < self.max_npcs_per_room

    def normalized_delay(self, delay: float | int | None) -> float:
        if delay is None:
            return float(self.default_delay_seconds)
        return max(0.0, float(delay))


def default_respawn_rules() -> RespawnRules:
    return RespawnRules()
