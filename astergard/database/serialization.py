from __future__ import annotations

import json
import re
import warnings
from typing import Any

from astergard.characters.appearance import CharacterAppearanceProfile, normalize_gender_id
from astergard.characters.models import Character, CharacterSkills, CharacterStats, Effect
from astergard.characters.careers import CareerLookupError, resolve_career, resolve_organization, resolve_school
from astergard.characters.professions import migrate_legacy_profession_selection
from astergard.items.models import EquipmentSet, Item, EQUIPMENT_SLOTS
from astergard.rules.combat_specialization import CombatSpecializationLoadout
from astergard.rules.combat_specialization import resolve_active_defense_style


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    return int(text)


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_active_defense_style(value: object) -> str | None:
    if value is None:
        resolved = None
    elif isinstance(value, str):
        resolved = resolve_active_defense_style(value)
    else:
        resolved = resolve_active_defense_style(str(value))
    if value is not None and resolved is None:
        warnings.warn(f"Nieznany aktywny styl obrony w zapisie postaci: {value}. Wpis został wyczyszczony.", stacklevel=2)
    return resolved.value if resolved is not None else None


def _clean_career_path(data: object) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"career_id": None, "organization_id": None, "school_id": None, "organization_rank": None}

    career_id = _optional_text(data.get("career_id"))
    organization_id = _optional_text(data.get("organization_id"))
    school_id = _optional_text(data.get("school_id"))
    rank_raw = data.get("organization_rank", data.get("awans"))
    organization_rank = _optional_int(rank_raw)

    if career_id is not None:
        try:
            resolve_career(career_id)
        except CareerLookupError:
            warnings.warn(f"Nieznane powołanie w zapisie postaci: {career_id}. Wpis został wyczyszczony.", stacklevel=2)
            return {"career_id": None, "organization_id": None, "school_id": None, "organization_rank": None}

    if organization_id is not None:
        try:
            organization = resolve_organization(organization_id)
        except CareerLookupError:
            warnings.warn(f"Nieznana organizacja w zapisie postaci: {organization_id}. Wpis został wyczyszczony.", stacklevel=2)
            organization_id = None
            school_id = None
            organization_rank = None
        else:
            if career_id is None or organization.career_id != career_id:
                warnings.warn(
                    f"Organizacja {organization_id} nie pasuje do powołania {career_id}. Organizacja została wyczyszczona.",
                    stacklevel=2,
                )
                organization_id = None
                school_id = None
                organization_rank = None

    if school_id is not None:
        try:
            school = resolve_school(school_id)
        except CareerLookupError:
            warnings.warn(f"Nieznana szkoła w zapisie postaci: {school_id}. Wpis został wyczyszczony.", stacklevel=2)
            school_id = None
        else:
            if organization_id is None or school.organization != organization_id:
                warnings.warn(
                    f"Szkoła {school_id} nie pasuje do organizacji {organization_id}. Szkoła została wyczyszczona.",
                    stacklevel=2,
                )
                school_id = None

    if organization_rank is not None and organization_id is None:
        warnings.warn("Ranga bez organizacji w zapisie postaci została wyczyszczona.", stacklevel=2)
        organization_rank = None

    return {
        "career_id": career_id,
        "organization_id": organization_id,
        "school_id": school_id,
        "organization_rank": organization_rank,
    }


def _is_legacy_ranged_item(item: Item | None) -> bool:
    if item is None:
        return False
    tokens = {
        token
        for value in (item.name, item.vnum or "", item.weapon_type or "", item.damage_type or "")
        for token in re.findall(r"[0-9a-ząćęłńóśźż]+", str(value).casefold())
        if token
    }
    return item.vnum in {
        "hunting_bow",
        "light_crossbow",
        "bowyer_tools",
        "bowyer_blank_npc",
        "straznica_scout_bow",
        "straznica_hunter_bow",
        "trakty_hunter_bow",
        "puszcza_hunter_bow",
        "puszcza_bandit_bow",
        "bagna_hunter_bow",
        "hunter_bow_100",
    } or any(
        token in {"bow", "crossbow", "bowyer", "łuk", "luk", "kusza", "kusz"}
        or token.startswith(("strzał", "strzal", "bełt", "belt"))
        for token in tokens
    )


def _migrate_profession_profile(profile_raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    migrated = dict(profile_raw)
    warnings_out: list[str] = []
    main_raw, secondary_raw = migrate_legacy_profession_selection(
        str(profile_raw.get("main_profession", "")).strip(),
        str(profile_raw.get("secondary_profession", "")).strip() or None,
    )
    if main_raw != str(profile_raw.get("main_profession", "")).strip():
        warnings_out.append(
            f"Zapis profilu postaci został zmigrowany: main_profession {profile_raw.get('main_profession', '')!r} -> {main_raw!r}."
        )
    if secondary_raw != (str(profile_raw.get("secondary_profession", "")).strip() or None):
        warnings_out.append(
            f"Zapis profilu postaci został zmigrowany: secondary_profession {profile_raw.get('secondary_profession', '')!r} -> {secondary_raw!r}."
        )
    migrated["main_profession"] = main_raw
    migrated["secondary_profession"] = secondary_raw or ""
    combat_learning = migrated.get("combat_learning", {})
    if isinstance(combat_learning, dict):
        combat_learning = dict(combat_learning)
        for key in ("known_weapon_specializations", "known_defense_specializations", "known_additional_skills", "known_techniques"):
            value = combat_learning.get(key, [])
            if isinstance(value, list):
                combat_learning[key] = [str(entry).strip() for entry in value if str(entry).strip()]
        migrated["combat_learning"] = combat_learning
    return migrated, warnings_out


def _purge_legacy_ranged_items(items: list[Item], *, context: str, username: str) -> list[Item]:
    kept: list[Item] = []
    for item in items:
        if _is_legacy_ranged_item(item):
            warnings.warn(
                f"Usunięto legacy przedmiot dystansowy z {context} postaci {username}: {item.vnum or item.name}.",
                stacklevel=2,
            )
            continue
        kept.append(item)
    return kept


def _warn_invalid_effects_json(username: str, *, skipped: int | None = None) -> None:
    if skipped is None:
        message = f"Nieprawidłowe effects_json w zapisie postaci {username}; użyto pustej listy efektów."
    else:
        message = f"Nieprawidłowe elementy effects_json w zapisie postaci {username}; pominięto {skipped} element(ów)."
    warnings.warn(message, stacklevel=2)


def _decode_active_effects(raw_value: object, *, username: str) -> list[Effect]:
    if raw_value is None or raw_value == "":
        _warn_invalid_effects_json(username)
        return []
    if not isinstance(raw_value, (str, bytes, bytearray)):
        _warn_invalid_effects_json(username)
        return []
    try:
        decoded = json.loads(raw_value)
    except (json.JSONDecodeError, TypeError):
        _warn_invalid_effects_json(username)
        return []
    if not isinstance(decoded, list):
        _warn_invalid_effects_json(username)
        return []
    active_effects: list[Effect] = []
    skipped = 0
    for effect_data in decoded:
        if not isinstance(effect_data, dict):
            skipped += 1
            continue
        try:
            active_effects.append(Effect.from_dict(effect_data))
        except (KeyError, TypeError, ValueError, OverflowError):
            skipped += 1
    if skipped:
        _warn_invalid_effects_json(username, skipped=skipped)
    return active_effects


def _resolve_legacy_gender_id(profile_raw: dict[str, Any]) -> str:
    raw_gender_id = profile_raw.get("gender_id")
    gender_source = raw_gender_id if raw_gender_id not in {None, ""} else profile_raw.get("gender_description", "")
    gender_id = normalize_gender_id(gender_source)
    appearance_raw = profile_raw.get("appearance_profile")
    legacy_appearance_gender = ""
    if isinstance(appearance_raw, dict):
        legacy_appearance_gender = normalize_gender_id(appearance_raw.get("gender"))
        if gender_id and legacy_appearance_gender and gender_id != legacy_appearance_gender:
            warnings.warn(
                f"Konflikt legacy płci w zapisie postaci: gender_description={profile_raw.get('gender_description', profile_raw.get('gender_id', ''))!r} "
                f"oraz appearance.gender={appearance_raw.get('gender')!r}. Użyto pola głównego.",
                stacklevel=2,
            )
    if gender_id:
        return gender_id
    return legacy_appearance_gender


class CharacterStateSerializer:
    """Serializes the durable character state to explicit SQLite JSON columns."""

    @staticmethod
    def to_payload(char: Character) -> tuple[Any, ...]:
        inventory = [item.to_dict() for item in char.inventory]
        equipment = char.equipment.to_dict() if hasattr(char.equipment, "to_dict") else {slot: item.to_dict() if item is not None else None for slot, item in char.equipment.items()}
        effects = [effect.to_dict() for effect in char.active_effects]
        creator_profile = {
            "name": char.name,
            "gender_id": char.gender_id,
            "gender_description": char.gender_description,
            "age": char.age,
            "origin": char.origin,
            "childhood": char.childhood,
            "birth_region": char.birth_region,
            "culture": char.culture,
            "religion": char.religion,
            "main_profession": char.main_profession,
            "secondary_profession": char.secondary_profession,
            "appearance": char.appearance,
            "appearance_profile": char.appearance_profile.to_dict() if char.appearance_profile is not None else None,
            "history": char.history,
            "starting_reputation": char.starting_reputation,
            "career_path": {
                "career_id": char.career_id,
                "organization_id": char.organization_id,
                "school_id": char.school_id,
                "organization_rank": char.organization_rank,
            },
            "active_defense_style": char.active_defense_style,
            "combat_learning": {
                "known_weapon_specializations": list(char.combat_specializations.weapon_specializations),
                "known_defense_specializations": list(char.combat_specializations.defense_specializations),
                "known_additional_skills": list(char.combat_specializations.additional_skills),
                "known_techniques": list(char.known_techniques),
            },
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
        char.inventory = _purge_legacy_ranged_items([Item.from_dict(item) for item in json.loads(row[15])], context="ekwipunku", username=username)
        equipment_raw = json.loads(row[16]) if len(row) > 16 and row[16] else {}
        char.equipment = EquipmentSet.from_dict(equipment_raw) if isinstance(equipment_raw, dict) else EquipmentSet.default()
        equipment_items = list(char.equipment.all_items()) if isinstance(char.equipment, EquipmentSet) else [item for item in char.equipment.values() if item is not None]
        for item in equipment_items:
            if item is None:
                continue
            if _is_legacy_ranged_item(item):
                warnings.warn(
                    f"Usunięto legacy przedmiot dystansowy z wyposażenia postaci {username}: {item.vnum or item.name}.",
                    stacklevel=2,
                )
                char.equipment.remove_item(item)
        for slot in EQUIPMENT_SLOTS:
            char.equipment.setdefault(slot, None)
        char.resolve_equipment_conflicts()
        char.active_effects = _decode_active_effects(row[17] if len(row) > 17 else None, username=username)
        if len(row) > 18 and row[18]:
            char.combat_style = str(row[18])
        profile_raw = json.loads(row[19]) if len(row) > 19 and row[19] else {}
        if isinstance(profile_raw, dict):
            profile_raw, migration_warnings = _migrate_profession_profile(profile_raw)
            for message in migration_warnings:
                warnings.warn(message, stacklevel=2)
            char.name = str(profile_raw.get("name", ""))
            char.gender_id = _resolve_legacy_gender_id(profile_raw)
            char.age = int(profile_raw.get("age", 0) or 0)
            char.origin = str(profile_raw.get("origin", ""))
            char.childhood = str(profile_raw.get("childhood", ""))
            char.birth_region = str(profile_raw.get("birth_region", ""))
            char.culture = str(profile_raw.get("culture", ""))
            char.religion = str(profile_raw.get("religion", ""))
            char.main_profession = str(profile_raw.get("main_profession", ""))
            char.secondary_profession = str(profile_raw.get("secondary_profession", ""))
            char.appearance = str(profile_raw.get("appearance", ""))
            appearance_profile_raw = profile_raw.get("appearance_profile")
            if isinstance(appearance_profile_raw, dict):
                cleaned_profile = dict(appearance_profile_raw)
                cleaned_profile.pop("gender", None)
                try:
                    char.appearance_profile = CharacterAppearanceProfile.from_dict(cleaned_profile)
                except ValueError:
                    warnings.warn(
                        f"Nieprawidłowy profil wyglądu w zapisie postaci {username}. Użyto neutralnego fallbacku.",
                        stacklevel=2,
                    )
                    char.appearance_profile = None
                else:
                    if char.gender_id == "f" and char.appearance_profile.beard != "brak":
                        char.appearance_profile = None
            else:
                char.appearance_profile = None
            char.history = str(profile_raw.get("history", ""))
            char.starting_reputation = int(profile_raw.get("starting_reputation", 0) or 0)
            career_path = _clean_career_path(profile_raw.get("career_path", {}))
            char.career_id = career_path["career_id"]
            char.organization_id = career_path["organization_id"]
            char.school_id = career_path["school_id"]
            char.organization_rank = career_path["organization_rank"]
            char.active_defense_style = _optional_active_defense_style(profile_raw.get("active_defense_style"))
            combat_learning = profile_raw.get("combat_learning", {})
            if isinstance(combat_learning, dict):
                char.combat_specializations = CombatSpecializationLoadout(
                    weapon_specializations=tuple(str(value) for value in combat_learning.get("known_weapon_specializations", []) if str(value).strip()),
                    defense_specializations=tuple(str(value) for value in combat_learning.get("known_defense_specializations", []) if str(value).strip()),
                    additional_skills=tuple(str(value) for value in combat_learning.get("known_additional_skills", []) if str(value).strip()),
                )
                char.known_techniques = tuple(
                    text
                    for text in (str(value).strip() for value in combat_learning.get("known_techniques", []) if str(value).strip())
                    if text
                )
        visited_raw = json.loads(row[20]) if len(row) > 20 and row[20] else []
        if isinstance(visited_raw, list):
            char.visited_room_ids = {int(room_id) for room_id in visited_raw}
        else:
            char.visited_room_ids = set()
        char.sync_state_from_flags()
        if char.in_combat:
            warnings.warn(
                f"Przejściowy stan walki postaci {username} został wyczyszczony podczas odczytu.",
                stacklevel=2,
            )
            char.in_combat = False
            char.sync_state_from_flags()
        return char
