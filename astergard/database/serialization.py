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
            char.global_reputation,
            json.dumps(char.local_reputation, ensure_ascii=False),
            char.renown,
            char.title,
            json.dumps(char.crimes, ensure_ascii=False),
            char.wanted_level,
            json.dumps(char.wanted_posts, ensure_ascii=False),
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
        char.global_reputation = int(row[6]) if len(row) > 6 and row[6] is not None else 0
        char.local_reputation = dict(json.loads(row[7])) if len(row) > 7 and row[7] else {}
        char.renown = int(row[8]) if len(row) > 8 and row[8] is not None else 0
        char.title = str(row[9]) if len(row) > 9 and row[9] else "Wędrowiec"
        char.crimes = dict(json.loads(row[10])) if len(row) > 10 and row[10] else {"kradzież": 0, "napaść": 0, "zabójstwo": 0}
        char.wanted_level = int(row[11]) if len(row) > 11 and row[11] is not None else 0
        char.wanted_posts = list(json.loads(row[12])) if len(row) > 12 and row[12] else []
        char.active_quests = dict(json.loads(row[13]))
        char.completed_quests = list(json.loads(row[14]))
        char.inventory = [Item.from_dict(item) for item in json.loads(row[15])]
        equipment_raw = json.loads(row[16])
        char.equipment = {
            slot: Item.from_dict(item) if isinstance(item, dict) else None
            for slot, item in equipment_raw.items()
        }
        for slot in ["prawa_reka", "lewa_reka", "glowa", "korpus", "nogi"]:
            char.equipment.setdefault(slot, None)
        char.active_effects = [Effect.from_dict(effect) for effect in json.loads(row[17])]
        if len(row) > 18 and row[18]:
            char.combat_style = str(row[18])
        char.sync_state_from_flags()
        return char
