from __future__ import annotations

import json
from typing import Any

from astergard.characters.models import Character, CharacterSkills, CharacterStats, Effect
from astergard.items.models import Item


class CharacterStateSerializer:
    """Serializes the durable character state to explicit SQLite JSON columns."""

    @staticmethod
    def to_payload(char: Character) -> tuple[Any, ...]:
        inventory = [item.to_dict() for item in char.inventory]
        equipment = {slot: item.to_dict() if item is not None else None for slot, item in char.equipment.items()}
        effects = [effect.to_dict() for effect in char.active_effects]
        return (
            char.room_id,
            char.gold,
            json.dumps(char.stats.__dict__, ensure_ascii=False),
            json.dumps(char.skills.values, ensure_ascii=False),
            json.dumps(char.wounds, ensure_ascii=False),
            json.dumps(char.reputation, ensure_ascii=False),
            json.dumps(char.active_quests, ensure_ascii=False),
            json.dumps(char.completed_quests, ensure_ascii=False),
            json.dumps(inventory, ensure_ascii=False),
            json.dumps(equipment, ensure_ascii=False),
            json.dumps(effects, ensure_ascii=False),
            char.combat_style,
        )

    @staticmethod
    def hydrate(username: str, row: tuple[Any, ...]) -> Character:
        char = Character(username=username)
        char.room_id = int(row[0])
        char.gold = int(row[1])
        char.stats = CharacterStats(**json.loads(row[2]))
        char.skills = CharacterSkills(json.loads(row[3]))
        char.wounds = dict(json.loads(row[4]))
        char.reputation = dict(json.loads(row[5]))
        char.active_quests = dict(json.loads(row[6]))
        char.completed_quests = list(json.loads(row[7]))
        char.inventory = [Item.from_dict(item) for item in json.loads(row[8])]
        equipment_raw = json.loads(row[9])
        char.equipment = {
            slot: Item.from_dict(item) if isinstance(item, dict) else None
            for slot, item in equipment_raw.items()
        }
        for slot in ["prawa_reka", "lewa_reka", "glowa", "korpus", "nogi"]:
            char.equipment.setdefault(slot, None)
        char.active_effects = [Effect.from_dict(effect) for effect in json.loads(row[10])]
        if len(row) > 11 and row[11]:
            char.combat_style = str(row[11])
        char.sync_state_from_flags()
        return char
