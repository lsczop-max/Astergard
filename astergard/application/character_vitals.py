from __future__ import annotations

from typing import Any

from astergard.characters.models import Character
from astergard.combat.wounds import overall_health_desc


def build_character_vitals_payload(character: Character) -> dict[str, Any]:
    total_wounds = sum(max(0, int(level)) for level in character.wounds.values())
    condition_max = 12
    condition_current = max(0, condition_max - total_wounds)
    stamina_max = max(0, int(character.stats.max_kondycja))
    stamina_current = max(0, min(int(character.stats.kondycja), stamina_max))
    return {
        "condition_current": condition_current,
        "condition_max": condition_max,
        "condition_label": overall_health_desc(character.wounds),
        "stamina_current": stamina_current,
        "stamina_max": stamina_max,
        "stamina_label": character.stats.describe_kondycja(),
    }
