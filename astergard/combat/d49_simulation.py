from __future__ import annotations

import copy
import json
import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median
from typing import Any

from astergard.characters.models import Character, CharacterStats
from astergard.combat.actions import CombatOutcomeType
from astergard.combat.defense import DefenseContext, build_defense_candidates
from astergard.combat.manager import CombatManager
from astergard.combat.weapons import ArmorProfileCatalog, ShieldProfileCatalog, WeaponProfileCatalog, load_default_armor_profile_catalog, load_default_shield_profile_catalog, load_default_weapon_profile_catalog
from astergard.items.models import EquipmentSet, Item
from astergard.rules.combat_specialization import CombatSpecializationLoadout

BASE_STATS = CharacterStats(sila=12, zrecznosc=12, wytrzymalosc=12, percepcja=10, sila_woli=10, kondycja=120)


@dataclass(frozen=True, slots=True)
class WeaponSpec:
    profile_id: str
    name: str
    weapon_type: str
    damage_type: str
    base_damage: int
    initiative_modifier: int
    parry_bonus: int
    weight: float = 1.0
    value: int = 10
    reach: int = 1


@dataclass(frozen=True, slots=True)
class ArmorSpec:
    profile_id: str
    name: str
    weight: float
    protection: int
    armor_value: int
    value: int = 10


@dataclass(frozen=True, slots=True)
class ShieldSpec:
    profile_id: str
    name: str
    weight: float
    protection: int
    shield_block: int
    value: int = 10


WEAPON_SPECS: dict[str, WeaponSpec] = {
    "garrison_short_sword": WeaponSpec("garrison_short_sword", "prosty miecz garnizonowy", "miecz", "cieta", 4, 1, 1, weight=1.8, value=25),
    "court_sabre": WeaponSpec("court_sabre", "szabla strażnicza", "szpada", "cieta", 4, 2, 2, weight=1.5, value=24),
    "duelist_dagger": WeaponSpec("duelist_dagger", "sztylet pojedynkowy", "sztylet", "cieta", 3, 2, 1, weight=0.6, value=16),
    "duelist_rapier": WeaponSpec("duelist_rapier", "rapier pojedynkowy", "szpada", "cieta", 4, 2, 2, weight=1.2, value=26),
    "battle_axe": WeaponSpec("battle_axe", "topór bojowy", "topór", "cieta", 5, 0, 0, weight=3.4, value=22),
    "war_hammer": WeaponSpec("war_hammer", "młot wojenny", "młot", "obuchowa", 5, 0, 0, weight=4.0, value=28),
    "war_mace": WeaponSpec("war_mace", "buława bojowa", "buława", "obuchowa", 4, 0, 0, weight=3.0, value=24),
    "watch_spear": WeaponSpec("watch_spear", "włócznia strażnicza", "włócznia", "kluta", 4, 0, 0, weight=2.4, value=18, reach=2),
    "watch_halberd": WeaponSpec("watch_halberd", "halabarda strażnicza", "halabarda", "kluta", 5, 0, 0, weight=3.8, value=28, reach=2),
    "war_flail": WeaponSpec("war_flail", "cep bojowy", "cep", "obuchowa", 4, -1, 0, weight=4.2, value=26),
    "war_staff": WeaponSpec("war_staff", "kij bojowy", "kij", "obuchowa", 1, 0, 1, weight=1.8, value=12, reach=2),
}

ARMOR_SPECS: dict[str, ArmorSpec] = {
    "unarmored": ArmorSpec("unarmored", "ubranie", 0.0, 0, 0, value=0),
    "light_armor": ArmorSpec("light_armor", "lekki pancerz", 3.0, 1, 1, value=18),
    "medium_armor": ArmorSpec("medium_armor", "średni pancerz", 7.0, 2, 1, value=28),
    "heavy_armor": ArmorSpec("heavy_armor", "ciężki pancerz", 12.0, 3, 2, value=42),
}

SHIELD_SPECS: dict[str, ShieldSpec] = {
    "small_shield": ShieldSpec("small_shield", "mała tarcza", 2.0, 1, 2, value=12),
    "medium_shield": ShieldSpec("medium_shield", "średnia tarcza", 3.0, 1, 3, value=18),
    "large_shield": ShieldSpec("large_shield", "duża tarcza", 4.0, 2, 4, value=24),
    "pavise": ShieldSpec("pavise", "pawęż", 5.0, 3, 5, value=30),
}


def _weapon_item(profile_id: str) -> Item:
    spec = WEAPON_SPECS[profile_id]
    return Item(
        spec.name,
        f"Profil bojowy {spec.profile_id}.",
        spec.weight,
        spec.value,
        spec.profile_id,
        "weapon",
        "bron_glowna",
        wearable=True,
        weapon_type=spec.weapon_type,
        damage_type=spec.damage_type,
        base_damage=spec.base_damage,
        reach=spec.reach,
        initiative_modifier=spec.initiative_modifier,
        parry_bonus=spec.parry_bonus,
        id=f"{spec.profile_id}:weapon",
        weapon_profile_id=spec.profile_id,
    )


def _armor_item(profile_id: str) -> Item:
    spec = ARMOR_SPECS[profile_id]
    return Item(
        spec.name,
        f"Profil ochronny {spec.profile_id}.",
        spec.weight,
        spec.value,
        spec.profile_id,
        "armor",
        "korpus",
        wearable=True,
        armor_value=spec.armor_value,
        protection=spec.protection,
        id=f"{spec.profile_id}:armor",
        armor_profile_id=spec.profile_id,
    )


def _shield_item(profile_id: str) -> Item:
    spec = SHIELD_SPECS[profile_id]
    return Item(
        spec.name,
        f"Profil tarczy {spec.profile_id}.",
        spec.weight,
        spec.value,
        spec.profile_id,
        "shield",
        "tarcza",
        wearable=True,
        protection=spec.protection,
        shield_block=spec.shield_block,
        id=f"{spec.profile_id}:shield",
        shield_profile_id=spec.profile_id,
    )


def _set_skill_levels(character: Character, levels: dict[str, int]) -> None:
    for name, state in character.skills.values.items():
        state["level"] = 1
        state["progress"] = 0
    for skill_name, level in levels.items():
        character.skills.values[skill_name]["level"] = level


def _clear_equipment(character: Character) -> None:
    character.equipment = EquipmentSet.default()
    for slot in character.equipment:
        character.equipment[slot] = None


@dataclass(frozen=True, slots=True)
class CombatPreset:
    key: str
    name: str
    weapon_profile_id: str
    armor_profile_id: str | None
    shield_profile_id: str | None
    combat_specializations: CombatSpecializationLoadout
    skill_levels: dict[str, int]
    known_techniques: tuple[str, ...] = ()
    stats: CharacterStats = field(default_factory=lambda: copy.deepcopy(BASE_STATS))
    supported: bool = True
    notes: str = ""

    def clone_with(self, **changes: Any) -> "CombatPreset":
        key = str(changes.get("key", self.key))
        name = str(changes.get("name", self.name))
        weapon_profile_id = str(changes.get("weapon_profile_id", self.weapon_profile_id))
        armor_profile_id = changes.get("armor_profile_id", self.armor_profile_id)
        shield_profile_id = changes.get("shield_profile_id", self.shield_profile_id)
        combat_specializations = changes.get("combat_specializations", self.combat_specializations)
        skill_levels = changes.get("skill_levels", self.skill_levels)
        known_techniques = changes.get("known_techniques", self.known_techniques)
        stats = changes.get("stats", self.stats)
        supported = bool(changes.get("supported", self.supported))
        notes = str(changes.get("notes", self.notes))
        return CombatPreset(
            key=key,
            name=name,
            weapon_profile_id=weapon_profile_id,
            armor_profile_id=armor_profile_id if armor_profile_id is None else str(armor_profile_id),
            shield_profile_id=shield_profile_id if shield_profile_id is None else str(shield_profile_id),
            combat_specializations=combat_specializations,
            skill_levels=skill_levels,
            known_techniques=known_techniques,
            stats=stats,
            supported=supported,
            notes=notes,
        )


def _base_skill_levels() -> dict[str, int]:
    return {
        "bron_jednoraczna": 60,
        "bron_dwureczna": 60,
        "wlocznie": 60,
        "uniki": 30,
        "parowanie": 30,
        "tarcze": 30,
        "morale": 10,
        "dowodzenie": 10,
    }


def _build_character(preset: CombatPreset, username: str) -> Character:
    character = Character(username)
    character.stats = copy.deepcopy(preset.stats)
    character.inventory = []
    _clear_equipment(character)
    _set_skill_levels(character, _base_skill_levels() | preset.skill_levels)
    character.combat_specializations = copy.deepcopy(preset.combat_specializations)
    character.known_techniques = tuple(preset.known_techniques)
    character.room_id = 1
    character.formation = "front"
    character.combat_style = "zrownowazony"
    character.combat_identity = username
    if preset.weapon_profile_id:
        character.equipment["bron_glowna"] = _weapon_item(preset.weapon_profile_id)
    if preset.armor_profile_id:
        character.equipment["korpus"] = _armor_item(preset.armor_profile_id)
    if preset.shield_profile_id:
        character.equipment["tarcza"] = _shield_item(preset.shield_profile_id)
    character.sync_state_from_flags()
    return character


REFERENCE_ATTACKER = CombatPreset(
    key="reference_attacker",
    name="atakujący referencyjny",
    weapon_profile_id="garrison_short_sword",
    armor_profile_id="unarmored",
    shield_profile_id=None,
    combat_specializations=CombatSpecializationLoadout(weapon_specializations=("miecze",), defense_specializations=()),
    skill_levels={"uniki": 30, "parowanie": 30, "tarcze": 30, "bron_jednoraczna": 60},
    known_techniques=(),
    notes="Stały napastnik do prób pojedynczych i pojedynków.",
)

BUILD_PRESETS: tuple[CombatPreset, ...] = (
    CombatPreset(
        key="A",
        name="Bez specjalizacji",
        weapon_profile_id="garrison_short_sword",
        armor_profile_id="unarmored",
        shield_profile_id=None,
        combat_specializations=CombatSpecializationLoadout(),
        skill_levels={"uniki": 30, "parowanie": 30, "tarcze": 30, "bron_jednoraczna": 60},
        notes="Bazowy profil bez jawnych specjalizacji bojowych.",
    ),
    CombatPreset(
        key="B",
        name="Tarczownik z młotem",
        weapon_profile_id="war_mace",
        armor_profile_id="heavy_armor",
        shield_profile_id="medium_shield",
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("bulawy",), defense_specializations=("tarcze",)),
        skill_levels={"uniki": 30, "parowanie": 30, "tarcze": 100, "bron_dwureczna": 60},
        notes="Ciężka obrona z bronią obuchową i tarczą.",
    ),
    CombatPreset(
        key="C",
        name="Tarczownik z mieczem",
        weapon_profile_id="garrison_short_sword",
        armor_profile_id="medium_armor",
        shield_profile_id="medium_shield",
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("miecze",), defense_specializations=("tarcze", "parowanie")),
        skill_levels={"uniki": 30, "parowanie": 60, "tarcze": 100, "bron_jednoraczna": 60},
        known_techniques=("riposte",),
        notes="Tarczownik z jawną ripostą.",
    ),
    CombatPreset(
        key="D",
        name="Szermierz",
        weapon_profile_id="duelist_rapier",
        armor_profile_id="light_armor",
        shield_profile_id=None,
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("miecze", "szable"), defense_specializations=("parowanie", "uniki")),
        skill_levels={"uniki": 80, "parowanie": 100, "tarcze": 30, "bron_jednoraczna": 60},
        known_techniques=("riposte",),
        notes="Lekki szermierz nastawiony na parowanie i unik.",
    ),
    CombatPreset(
        key="E",
        name="Dwubroniowiec",
        weapon_profile_id="garrison_short_sword",
        armor_profile_id="light_armor",
        shield_profile_id=None,
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("miecze", "sztylety"), defense_specializations=("parowanie", "uniki")),
        skill_levels={"uniki": 70, "parowanie": 70, "tarcze": 30, "bron_jednoraczna": 60},
        supported=False,
        notes="Walka dwiema broniami nie jest jeszcze bezpiecznie modelowana w tej symulacji.",
    ),
    CombatPreset(
        key="F",
        name="Unikający",
        weapon_profile_id="duelist_dagger",
        armor_profile_id="unarmored",
        shield_profile_id=None,
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("sztylety",), defense_specializations=("uniki", "parowanie")),
        skill_levels={"uniki": 100, "parowanie": 40, "tarcze": 30, "bron_jednoraczna": 60},
        notes="Lekki profil oparty na unikach.",
    ),
    CombatPreset(
        key="G",
        name="Broń drzewcowa",
        weapon_profile_id="watch_halberd",
        armor_profile_id="medium_armor",
        shield_profile_id=None,
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("wlocznie", "halabardy"), defense_specializations=("parowanie", "uniki")),
        skill_levels={"uniki": 50, "parowanie": 70, "tarcze": 30, "wlocznie": 60},
        notes="Profil drzewcowy bez tarczy.",
    ),
)


def _identity(character: Character) -> str:
    return character.combat_identity or character.username


def _defender_profile_for_probe(preset: CombatPreset, *, armor_profile_id: str | None = None, weapon_profile_id: str | None = None, shield_profile_id: str | None = None) -> CombatPreset:
    return preset.clone_with(
        armor_profile_id=preset.armor_profile_id if armor_profile_id is None else armor_profile_id,
        weapon_profile_id=preset.weapon_profile_id if weapon_profile_id is None else weapon_profile_id,
        shield_profile_id=preset.shield_profile_id if shield_profile_id is None else shield_profile_id,
    )


@dataclass(slots=True)
class SingleAttackTotals:
    trials: int = 0
    misses: int = 0
    hits: int = 0
    defended: int = 0
    target_defeated: int = 0
    total_damage: int = 0
    total_wounds: int = 0
    primary_damage: int = 0
    reaction_damage: int = 0
    primary_wounds: int = 0
    reaction_wounds: int = 0
    riposte_available: int = 0
    riposte_executed: int = 0
    riposte_hits: int = 0
    riposte_defended: int = 0
    riposte_kills: int = 0
    defense_attempts_total: int = 0
    defense_first_failures: int = 0
    defense_second_failures: int = 0
    defense_third_failures: int = 0
    defense_first_attempts: int = 0
    defense_second_attempts: int = 0
    defense_third_attempts: int = 0
    defense_success_by_type: Counter[str] = field(default_factory=Counter)
    defense_attempt_by_type: Counter[str] = field(default_factory=Counter)
    defense_position_by_type: dict[str, Counter[int]] = field(default_factory=dict)
    candidate_first_by_type: Counter[str] = field(default_factory=Counter)
    candidate_second_by_type: Counter[str] = field(default_factory=Counter)
    candidate_third_by_type: Counter[str] = field(default_factory=Counter)
    candidate_tried_by_type: Counter[str] = field(default_factory=Counter)
    candidate_effective_sum: dict[str, float] = field(default_factory=dict)
    candidate_effective_count: Counter[str] = field(default_factory=Counter)

    def absorb_candidates(self, candidates: tuple[Any, ...]) -> None:
        for index, candidate in enumerate(candidates):
            key = candidate.defense_type.value
            self.candidate_effective_sum[key] = self.candidate_effective_sum.get(key, 0.0) + float(candidate.effective_value)
            self.candidate_effective_count[key] += 1
            if index == 0:
                self.candidate_first_by_type[key] += 1
            elif index == 1:
                self.candidate_second_by_type[key] += 1
            elif index == 2:
                self.candidate_third_by_type[key] += 1
            if candidate.available:
                self.candidate_tried_by_type[key] += 1

    def absorb_result(self, result: Any, *, source: str) -> None:
        if result.combat_outcome is None:
            return
        self.trials += 1
        outcome = result.combat_outcome
        event = result.combat_event
        if outcome.result_type == CombatOutcomeType.MISS:
            self.misses += 1
        elif outcome.result_type == CombatOutcomeType.DEFENDED:
            self.defended += 1
        else:
            self.hits += 1
        if outcome.target_defeated:
            self.target_defeated += 1
        self.total_damage += int(outcome.damage or 0)
        if source == "primary":
            self.primary_damage += int(outcome.damage or 0)
        else:
            self.reaction_damage += int(outcome.damage or 0)
        if event is not None:
            self.total_wounds += int(getattr(event, "wound_level", 0) or 0)
            if source == "primary":
                self.primary_wounds += int(getattr(event, "wound_level", 0) or 0)
            else:
                self.reaction_wounds += int(getattr(event, "wound_level", 0) or 0)

        defense_outcome = outcome.defense_outcome
        if defense_outcome is not None:
            attempts = defense_outcome.attempts
            self.defense_attempts_total += len(attempts)
            if len(attempts) > 0:
                self.defense_first_attempts += 1
                if not attempts[0].success:
                    self.defense_first_failures += 1
            if len(attempts) > 1:
                self.defense_second_attempts += 1
                if not attempts[1].success:
                    self.defense_second_failures += 1
            if len(attempts) > 2:
                self.defense_third_attempts += 1
                if not attempts[2].success:
                    self.defense_third_failures += 1
            for index, attempt in enumerate(attempts):
                key = attempt.defense_type.value
                self.defense_attempt_by_type[key] += 1
                self.defense_position_by_type.setdefault(key, Counter())[index + 1] += 1
                if attempt.success:
                    self.defense_success_by_type[key] += 1
        reaction_execution = getattr(result, "reaction_execution", None)
        if reaction_execution is not None:
            discovery = getattr(result, "reaction_discovery", None)
            if discovery is not None and discovery.available_reactions:
                self.riposte_available += len(discovery.available_reactions)
            if reaction_execution.executed:
                self.riposte_executed += 1
                reaction_result = reaction_execution.reaction_result
                if reaction_result is not None:
                    reaction_outcome = reaction_result.combat_outcome
                    if reaction_outcome is not None:
                        if reaction_outcome.result_type in {CombatOutcomeType.HIT, CombatOutcomeType.TARGET_DEFEATED}:
                            self.riposte_hits += 1
                        elif reaction_outcome.result_type == CombatOutcomeType.DEFENDED:
                            self.riposte_defended += 1
                        if getattr(reaction_result, "defender_dead", False):
                            self.riposte_kills += 1

    def to_dict(self) -> dict[str, Any]:
        def _mean_for(counter_sum: dict[str, float], counter_count: Counter[str], key: str) -> float:
            count = counter_count.get(key, 0)
            return float(counter_sum.get(key, 0.0)) / count if count else 0.0

        return {
            "trials": self.trials,
            "misses": self.misses,
            "hits": self.hits,
            "defended": self.defended,
            "target_defeated": self.target_defeated,
            "total_damage": self.total_damage,
            "total_wounds": self.total_wounds,
            "primary_damage": self.primary_damage,
            "reaction_damage": self.reaction_damage,
            "primary_wounds": self.primary_wounds,
            "reaction_wounds": self.reaction_wounds,
            "riposte_available": self.riposte_available,
            "riposte_executed": self.riposte_executed,
            "riposte_hits": self.riposte_hits,
            "riposte_defended": self.riposte_defended,
            "riposte_kills": self.riposte_kills,
            "defense_attempts_total": self.defense_attempts_total,
            "defense_first_failures": self.defense_first_failures,
            "defense_second_failures": self.defense_second_failures,
            "defense_third_failures": self.defense_third_failures,
            "defense_first_attempts": self.defense_first_attempts,
            "defense_second_attempts": self.defense_second_attempts,
            "defense_third_attempts": self.defense_third_attempts,
            "defense_success_by_type": dict(self.defense_success_by_type),
            "defense_attempt_by_type": dict(self.defense_attempt_by_type),
            "defense_position_by_type": {key: dict(counter) for key, counter in self.defense_position_by_type.items()},
            "candidate_first_by_type": dict(self.candidate_first_by_type),
            "candidate_second_by_type": dict(self.candidate_second_by_type),
            "candidate_third_by_type": dict(self.candidate_third_by_type),
            "candidate_tried_by_type": dict(self.candidate_tried_by_type),
            "candidate_effective_value_mean": {
                key: _mean_for(self.candidate_effective_sum, self.candidate_effective_count, key)
                for key in ("DODGE", "SHIELD_BLOCK", "PARRY")
            },
        }


@dataclass(slots=True)
class DuelTotals:
    trials: int = 0
    attacker_wins: int = 0
    defender_wins: int = 0
    draws: int = 0
    misses: int = 0
    hits: int = 0
    defended: int = 0
    target_defeated: int = 0
    total_rounds: list[int] = field(default_factory=list)
    total_actions: int = 0
    total_damage: int = 0
    total_wounds: int = 0
    riposte_damage: int = 0
    riposte_wounds: int = 0
    riposte_available: int = 0
    riposte_executed: int = 0
    riposte_hits: int = 0
    riposte_defended: int = 0
    riposte_kill_finishes: int = 0
    defense_attempts: int = 0
    defense_success_by_type: Counter[str] = field(default_factory=Counter)
    defense_attempt_by_type: Counter[str] = field(default_factory=Counter)
    limit_exceeded: int = 0
    winner_remaining_health: list[int] = field(default_factory=list)

    def absorb_trial(self, result: dict[str, Any]) -> None:
        self.trials += 1
        self.total_rounds.append(int(result["rounds"]))
        self.total_actions += int(result["actions"])
        self.misses += int(result["misses"])
        self.hits += int(result["hits"])
        self.defended += int(result["defended"])
        self.target_defeated += int(result["target_defeated"])
        self.total_damage += int(result["total_damage"])
        self.total_wounds += int(result["total_wounds"])
        self.riposte_damage += int(result["riposte_damage"])
        self.riposte_wounds += int(result["riposte_wounds"])
        self.riposte_available += int(result["riposte_available"])
        self.riposte_executed += int(result["riposte_executed"])
        self.riposte_hits += int(result["riposte_hits"])
        self.riposte_defended += int(result["riposte_defended"])
        self.defense_attempts += int(result["defense_attempts"])
        self.defense_success_by_type.update(result["defense_success_by_type"])
        self.defense_attempt_by_type.update(result["defense_attempt_by_type"])
        if result["limit_exceeded"]:
            self.limit_exceeded += 1
        winner = result["winner"]
        if winner == "attacker":
            self.attacker_wins += 1
            self.winner_remaining_health.append(int(result["attacker_health"]))
        elif winner == "defender":
            self.defender_wins += 1
            self.winner_remaining_health.append(int(result["defender_health"]))
        else:
            self.draws += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "trials": self.trials,
            "attacker_wins": self.attacker_wins,
            "defender_wins": self.defender_wins,
            "draws": self.draws,
            "misses": self.misses,
            "hits": self.hits,
            "defended": self.defended,
            "target_defeated": self.target_defeated,
            "attacker_win_rate": self.attacker_wins / self.trials if self.trials else 0.0,
            "defender_win_rate": self.defender_wins / self.trials if self.trials else 0.0,
            "draw_rate": self.draws / self.trials if self.trials else 0.0,
            "average_rounds": mean(self.total_rounds) if self.total_rounds else 0.0,
            "median_rounds": median(self.total_rounds) if self.total_rounds else 0.0,
            "average_actions": self.total_actions / self.trials if self.trials else 0.0,
            "average_total_damage": self.total_damage / self.trials if self.trials else 0.0,
            "average_total_wounds": self.total_wounds / self.trials if self.trials else 0.0,
            "riposte_damage": self.riposte_damage,
            "riposte_wounds": self.riposte_wounds,
            "riposte_available": self.riposte_available,
            "riposte_executed": self.riposte_executed,
            "riposte_hits": self.riposte_hits,
            "riposte_defended": self.riposte_defended,
            "riposte_kill_finishes": self.riposte_kill_finishes,
            "defense_attempts": self.defense_attempts,
            "defense_success_by_type": dict(self.defense_success_by_type),
            "defense_attempt_by_type": dict(self.defense_attempt_by_type),
            "limit_exceeded": self.limit_exceeded,
            "average_winner_remaining_health": mean(self.winner_remaining_health) if self.winner_remaining_health else 0.0,
        }


def _run_primary_attack(manager: CombatManager, attacker: Character, defender: Character) -> Any:
    return manager.attack(attacker, defender)


def _record_result(
    aggregate: SingleAttackTotals,
    result: Any,
    *,
    source: str = "primary",
) -> None:
    aggregate.absorb_result(result, source=source)


def _single_attack_trial(
    defender_preset: CombatPreset,
    seed: int,
    *,
    attacker_preset: CombatPreset = REFERENCE_ATTACKER,
) -> dict[str, Any]:
    rng = random.Random(seed)
    manager = CombatManager(rng)
    attacker = _build_character(attacker_preset, f"attacker_{seed}")
    defender = _build_character(defender_preset, f"defender_{seed}")
    manager.start_fight(attacker, defender)
    candidates = build_defense_candidates(
        DefenseContext(
            attacker=attacker,
            defender=defender,
            hit_score=0,
            dodge_score=0,
            rng=rng,
            rules=manager.rules,
        )
    )
    result = _run_primary_attack(manager, attacker, defender)
    payload = {
        "result": result,
        "candidates": candidates,
        "attacker": attacker,
        "defender": defender,
        "manager": manager,
    }
    return payload


def simulate_single_attacks(
    defender_preset: CombatPreset,
    trials: int,
    *,
    attacker_preset: CombatPreset = REFERENCE_ATTACKER,
    seed_offset: int = 0,
) -> SingleAttackTotals:
    aggregate = SingleAttackTotals()
    for index in range(trials):
        payload = _single_attack_trial(defender_preset, seed_offset + index, attacker_preset=attacker_preset)
        aggregate.absorb_candidates(payload["candidates"])
        _record_result(aggregate, payload["result"], source="primary")
    return aggregate


def _duel_trial(
    attacker_preset: CombatPreset,
    defender_preset: CombatPreset,
    seed: int,
    *,
    max_rounds: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    manager = CombatManager(rng)
    attacker = _build_character(attacker_preset, f"attacker_{seed}")
    defender = _build_character(defender_preset, f"defender_{seed}")
    manager.start_fight(attacker, defender)
    rounds = 0
    total_actions = 0
    total_damage = 0
    total_wounds = 0
    riposte_damage = 0
    riposte_wounds = 0
    riposte_available = 0
    riposte_executed = 0
    riposte_hits = 0
    riposte_defended = 0
    defense_attempts = 0
    misses = 0
    hits = 0
    defended = 0
    target_defeated = 0
    defense_success_by_type: Counter[str] = Counter()
    defense_attempt_by_type: Counter[str] = Counter()
    limit_exceeded = False
    while attacker.is_alive and defender.is_alive and rounds < max_rounds:
        rounds += 1
        round_result = manager.process_pair_round(_identity(attacker), attacker, _identity(defender), defender, {attacker.username: attacker, defender.username: defender})
        total_actions += len(round_result.results)
        for result in round_result.results:
            if result.combat_outcome is not None:
                outcome = result.combat_outcome
                total_damage += int(outcome.damage or 0)
                if outcome.result_type == CombatOutcomeType.MISS:
                    misses += 1
                elif outcome.result_type == CombatOutcomeType.DEFENDED:
                    defended += 1
                else:
                    hits += 1
                if outcome.target_defeated:
                    target_defeated += 1
                defense_outcome = outcome.defense_outcome
                if defense_outcome is not None:
                    defense_attempts += len(defense_outcome.attempts)
                    for attempt in defense_outcome.attempts:
                        defense_attempt_by_type[attempt.defense_type.value] += 1
                    if defense_outcome.successful_defense and defense_outcome.selected_defense is not None:
                        defense_success_by_type[defense_outcome.selected_defense.value] += 1
            if result.combat_event is not None:
                total_wounds += int(getattr(result.combat_event, "wound_level", 0) or 0)
            if result.reaction_discovery is not None:
                riposte_available += len(result.reaction_discovery.available_reactions)
            if result.reaction_execution is not None and result.reaction_execution.executed and result.reaction_execution.reaction_result is not None:
                riposte_executed += 1
                reaction_result = result.reaction_execution.reaction_result
                if reaction_result.combat_outcome is not None:
                    if reaction_result.combat_outcome.result_type in {CombatOutcomeType.HIT, CombatOutcomeType.TARGET_DEFEATED}:
                        riposte_hits += 1
                    elif reaction_result.combat_outcome.result_type == CombatOutcomeType.DEFENDED:
                        riposte_defended += 1
                    riposte_damage += int(reaction_result.combat_outcome.damage or 0)
                if reaction_result.combat_event is not None:
                    riposte_wounds += int(getattr(reaction_result.combat_event, "wound_level", 0) or 0)
        if not manager.has_fight(_identity(attacker), _identity(defender)):
            break
    if rounds >= max_rounds and attacker.is_alive and defender.is_alive:
        limit_exceeded = True
    if attacker.is_alive and not defender.is_alive:
        winner = "attacker"
        remaining = attacker.stats.kondycja
    elif defender.is_alive and not attacker.is_alive:
        winner = "defender"
        remaining = defender.stats.kondycja
    else:
        winner = "draw"
        remaining = max(attacker.stats.kondycja, defender.stats.kondycja)
    return {
        "winner": winner,
        "rounds": rounds,
        "actions": total_actions,
        "misses": misses,
        "hits": hits,
        "defended": defended,
        "target_defeated": target_defeated,
        "total_damage": total_damage,
        "total_wounds": total_wounds,
        "riposte_damage": riposte_damage,
        "riposte_wounds": riposte_wounds,
        "riposte_available": riposte_available,
        "riposte_executed": riposte_executed,
        "riposte_hits": riposte_hits,
        "riposte_defended": riposte_defended,
        "defense_attempts": defense_attempts,
        "defense_success_by_type": dict(defense_success_by_type),
        "defense_attempt_by_type": dict(defense_attempt_by_type),
        "limit_exceeded": limit_exceeded,
        "attacker_health": attacker.stats.kondycja,
        "defender_health": defender.stats.kondycja,
        "winner_remaining_health": remaining,
    }


def simulate_duels(
    attacker_preset: CombatPreset,
    defender_preset: CombatPreset,
    trials: int,
    *,
    max_rounds: int = 80,
    seed_offset: int = 0,
) -> DuelTotals:
    aggregate = DuelTotals()
    for index in range(trials):
        aggregate.absorb_trial(_duel_trial(attacker_preset, defender_preset, seed_offset + index, max_rounds=max_rounds))
    return aggregate


def build_supported_builds() -> tuple[CombatPreset, ...]:
    return tuple(preset for preset in BUILD_PRESETS if preset.supported)


def build_unsupported_builds() -> tuple[CombatPreset, ...]:
    return tuple(preset for preset in BUILD_PRESETS if not preset.supported)


def build_weapon_probe_preset(weapon_profile_id: str) -> CombatPreset:
    return CombatPreset(
        key=f"weapon_{weapon_profile_id}",
        name=f"probe weapon {weapon_profile_id}",
        weapon_profile_id=weapon_profile_id,
        armor_profile_id="unarmored",
        shield_profile_id=None,
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("miecze", "szable", "sztylety", "topory", "mloty", "bulawy", "wlocznie", "halabardy", "cepy", "kije_bojowe"), defense_specializations=("uniki", "parowanie", "tarcze")),
        skill_levels={"uniki": 60, "parowanie": 60, "tarcze": 60, "bron_jednoraczna": 60, "bron_dwureczna": 60, "wlocznie": 60},
        known_techniques=("riposte",),
        notes="Profil testowy do porównania broni.",
    )


def build_armor_probe_preset(armor_profile_id: str) -> CombatPreset:
    return CombatPreset(
        key=f"armor_{armor_profile_id}",
        name=f"probe armor {armor_profile_id}",
        weapon_profile_id="garrison_short_sword",
        armor_profile_id=armor_profile_id,
        shield_profile_id="medium_shield",
        combat_specializations=CombatSpecializationLoadout(weapon_specializations=("miecze",), defense_specializations=("uniki", "parowanie", "tarcze")),
        skill_levels={"uniki": 60, "parowanie": 60, "tarcze": 60, "bron_jednoraczna": 60},
        known_techniques=("riposte",),
        notes="Profil testowy do porównania pancerzy.",
    )


def build_riposte_toggle_preset(base: CombatPreset, *, known: bool) -> CombatPreset:
    return base.clone_with(known_techniques=("riposte",) if known else ())


def as_jsonable(data: Any) -> Any:
    if isinstance(data, dict):
        return {str(key): as_jsonable(value) for key, value in data.items()}
    if isinstance(data, (list, tuple)):
        return [as_jsonable(value) for value in data]
    if isinstance(data, Counter):
        return dict(data)
    if hasattr(data, "to_dict"):
        return data.to_dict()
    return data


def render_single_summary(preset: CombatPreset, totals: SingleAttackTotals) -> dict[str, Any]:
    data = totals.to_dict()
    trials = max(1, totals.trials)
    data.update(
        {
            "accepted_rate": (totals.hits + totals.defended) / trials,
            "neighbor_mean": 0.0,
            "same_area_mean": 0.0,
            "unique_fingerprint_rate": 0.0,
            "fingerprint_expression_rate": 0.0,
            "total_actions": totals.trials,
            "riposte_share_damage": totals.reaction_damage / totals.total_damage if totals.total_damage else 0.0,
            "riposte_share_wounds": totals.reaction_wounds / totals.total_wounds if totals.total_wounds else 0.0,
        }
    )
    return data


def render_duel_summary(totals: DuelTotals) -> dict[str, Any]:
    data = totals.to_dict()
    if totals.total_damage:
        data["riposte_share_damage"] = totals.riposte_damage / totals.total_damage
    else:
        data["riposte_share_damage"] = 0.0
    if totals.total_wounds:
        data["riposte_share_wounds"] = totals.riposte_wounds / totals.total_wounds
    else:
        data["riposte_share_wounds"] = 0.0
    data["average_defenses_per_round"] = totals.defense_attempts / sum(totals.total_rounds) if totals.total_rounds and sum(totals.total_rounds) else 0.0
    return data


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(as_jsonable(data), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def weapon_profile_catalog() -> WeaponProfileCatalog:
    return load_default_weapon_profile_catalog()


def armor_profile_catalog() -> ArmorProfileCatalog:
    return load_default_armor_profile_catalog()


def shield_profile_catalog() -> ShieldProfileCatalog:
    return load_default_shield_profile_catalog()
