from __future__ import annotations

import json
from typing import Any

from astergard.characters.models import Character, CharacterSkills, CharacterStats, Effect
from astergard.items.models import EquipmentSet, Item, EQUIPMENT_SLOTS


class CharacterStateSerializer:
    """Serializes the durable character state to explicit SQLite JSON columns."""

    @staticmethod
    def to_payload(char: Character) -> tuple[Any, ...]:
        inventory = [item.to_dict() for item in char.inventory]
        equipment = {slot: item.to_dict() if item is not None else None for slot, item in char.equipment.items()}
        effects = [effect.to_dict() for effect in char.active_effects]
        creator_profile = {
            "name": char.name,
            "gender_description": char.gender_description,
            "age": char.age,
            "origin": char.origin,
            "birth_region": char.birth_region,
            "culture": char.culture,
            "religion": char.religion,
            "main_profession": char.main_profession,
            "secondary_profession": char.secondary_profession,
            "appearance": char.appearance,
            "history": char.history,
            "starting_reputation": char.starting_reputation,
        }
        return (
            char.room_id,
            char.gold,
            json.dumps(char.stats.__dict__, ensure_ascii=False),
            json.dumps(char.skills.to_dict(), ensure_ascii=False),
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
            json.dumps(creator_profile, ensure_ascii=False),
            json.dumps(sorted(char.visited_room_ids), ensure_ascii=False),
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
        equipment_raw = json.loads(row[16]) if len(row) > 16 and row[16] else {}
        equipment_items = {
            slot: Item.from_dict(item) if isinstance(item, dict) else None
            for slot, item in equipment_raw.items()
        }
        char.equipment = EquipmentSet.from_dict(equipment_items)
        for slot in EQUIPMENT_SLOTS:
            char.equipment.setdefault(slot, None)
        char.active_effects = [Effect.from_dict(effect) for effect in json.loads(row[17])]
        if len(row) > 18 and row[18]:
            char.combat_style = str(row[18])
        profile_raw = json.loads(row[19]) if len(row) > 19 and row[19] else {}
        if isinstance(profile_raw, dict):
            char.name = str(profile_raw.get("name", ""))
            char.gender_description = str(profile_raw.get("gender_description", ""))
            char.age = int(profile_raw.get("age", 0) or 0)
            char.origin = str(profile_raw.get("origin", ""))
            char.birth_region = str(profile_raw.get("birth_region", ""))
            char.culture = str(profile_raw.get("culture", ""))
            char.religion = str(profile_raw.get("religion", ""))
            char.main_profession = str(profile_raw.get("main_profession", ""))
            char.secondary_profession = str(profile_raw.get("secondary_profession", ""))
            char.appearance = str(profile_raw.get("appearance", ""))
            char.history = str(profile_raw.get("history", ""))
            char.starting_reputation = int(profile_raw.get("starting_reputation", 0) or 0)
        visited_raw = json.loads(row[20]) if len(row) > 20 and row[20] else []
        if isinstance(visited_raw, list):
            char.visited_room_ids = {int(room_id) for room_id in visited_raw}
        else:
            char.visited_room_ids = set()
        char.sync_state_from_flags()
        return char
