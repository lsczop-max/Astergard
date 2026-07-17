from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from astergard.combat.actions import CombatAction, CombatActionType, CombatOutcome, CombatOutcomeType, DefenseResolution, DefenseType
from astergard.combat.weapons import (
    TagRegistry,
    WeaponProfileConfigurationError,
    snapshot_weapon_profile,
    resolve_weapon_profile,
)
from astergard.rules.combat_specialization import (
    ActiveDefenseStyle,
    CombatSpecializationLookupError,
    CombatTechniqueLookupError,
    TechniqueUserProfile,
    can_use_technique,
    default_combat_technique_catalog,
    DEFENSE_SPECIALIZATIONS,
    WEAPON_SPECIALIZATIONS,
    resolve_active_defense_style,
    _specialization_skill_key,
    resolve_weapon_specialization,
)

if TYPE_CHECKING:
    from astergard.characters.models import Character


def _fold(text: str) -> str:
    return "".join(ch for ch in text.casefold().strip() if ch.isalnum() or ch == "_")


def _normalize_sequence(values: Sequence[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        folded = _fold(text)
        if folded in seen:
            continue
        seen.add(folded)
        normalized.append(text)
    return tuple(normalized)


def _sanitize_percent_map(values: Mapping[str, int] | None) -> dict[str, int]:
    if values is None:
        return {}
    sanitized: dict[str, int] = {}
    for key, value in values.items():
        try:
            percent = int(value)
        except (TypeError, ValueError):
            continue
        sanitized[str(key).strip()] = max(0, min(100, percent))
    return sanitized


def _skill_percent_from_level(level: int) -> int:
    if level <= 0:
        return 0
    return min(100, level * 5)


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        return int(text)
    return default


def _string_sequence(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _resolve_optional_active_defense_style(value: object) -> ActiveDefenseStyle | None:
    if value in {None, ""}:
        return None
    if isinstance(value, ActiveDefenseStyle):
        return value
    if isinstance(value, str):
        return resolve_active_defense_style(value)
    return resolve_active_defense_style(str(value))


class CombatReactionError(ValueError):
    pass


class CombatReactionConfigurationError(CombatReactionError):
    pass


class CombatReactionLookupError(CombatReactionError):
    pass


class CombatReactionType(StrEnum):
    RIPOSTE = "RIPOSTE"
    COUNTERATTACK = "COUNTERATTACK"
    SHIELD_RESPONSE = "SHIELD_RESPONSE"
    DODGE_RESPONSE = "DODGE_RESPONSE"
    CUSTOM = "CUSTOM"


class ReactionTriggerType(StrEnum):
    SUCCESSFUL_PARRY = "SUCCESSFUL_PARRY"
    SUCCESSFUL_DODGE = "SUCCESSFUL_DODGE"
    SUCCESSFUL_SHIELD_BLOCK = "SUCCESSFUL_SHIELD_BLOCK"
    ATTACK_MISSED = "ATTACK_MISSED"
    ACTOR_HIT = "ACTOR_HIT"
    ACTOR_WOUNDED = "ACTOR_WOUNDED"
    TARGET_DEFEATED = "TARGET_DEFEATED"


@dataclass(frozen=True, slots=True)
class ReactionPolicy:
    max_reaction_depth: int = 1


REACTION_POLICY = ReactionPolicy()


@dataclass(frozen=True, slots=True)
class CombatReactionDefinition:
    id: str
    name: str
    reaction_type: CombatReactionType
    trigger_types: tuple[ReactionTriggerType, ...]
    required_technique_id: str | None = None
    required_defense_style: ActiveDefenseStyle | None = None
    required_weapon_tags: tuple[str, ...] = ()
    required_weapon_specializations: tuple[str, ...] = ()
    enabled: bool = True
    priority: int = 0
    consumes_reaction_window: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("CombatReactionDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("CombatReactionDefinition.name nie może być puste.")
        if not self.trigger_types:
            raise ValueError("CombatReactionDefinition.trigger_types nie może być puste.")
        object.__setattr__(self, "trigger_types", tuple(ReactionTriggerType(trigger.value if isinstance(trigger, ReactionTriggerType) else str(trigger)) for trigger in self.trigger_types))
        object.__setattr__(self, "required_weapon_tags", TagRegistry.default().validate(self.required_weapon_tags))
        object.__setattr__(self, "required_weapon_specializations", _normalize_sequence(self.required_weapon_specializations))
        if self.required_defense_style is not None:
            resolved_style = resolve_active_defense_style(self.required_defense_style)
            if resolved_style is None:
                raise ValueError(f"Nieznany styl obrony w definicji reakcji {self.id}: {self.required_defense_style}")
            object.__setattr__(self, "required_defense_style", resolved_style)
        if self.required_technique_id is not None:
            object.__setattr__(self, "required_technique_id", str(self.required_technique_id).strip() or None)
        if self.required_technique_id is not None:
            default_combat_technique_catalog().by_id(self.required_technique_id)
        for specialization_id in self.required_weapon_specializations:
            resolve_weapon_specialization(specialization_id)
        if self.priority < 0:
            raise ValueError("CombatReactionDefinition.priority nie może być ujemne.")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "reaction_type": self.reaction_type.value,
            "trigger_types": [trigger.value for trigger in self.trigger_types],
            "required_technique_id": self.required_technique_id,
            "required_defense_style": self.required_defense_style.value if self.required_defense_style is not None else None,
            "required_weapon_tags": list(self.required_weapon_tags),
            "required_weapon_specializations": list(self.required_weapon_specializations),
            "enabled": self.enabled,
            "priority": self.priority,
            "consumes_reaction_window": self.consumes_reaction_window,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CombatReactionDefinition":
        reaction_type_raw = str(data.get("reaction_type", "")).strip()
        trigger_types_raw = data.get("trigger_types", [])
        required_defense_style_raw = data.get("required_defense_style")
        required_defense_style = _resolve_optional_active_defense_style(required_defense_style_raw)
        if required_defense_style_raw not in {None, ""} and required_defense_style is None:
            raise CombatReactionConfigurationError(f"Nieznany styl obrony w definicji reakcji: {required_defense_style_raw}")
        if not isinstance(trigger_types_raw, Sequence) or isinstance(trigger_types_raw, (str, bytes)):
            raise CombatReactionConfigurationError("CombatReactionDefinition.trigger_types musi być listą.")
        trigger_types = tuple(ReactionTriggerType(str(trigger).strip()) for trigger in trigger_types_raw)
        if not trigger_types:
            raise CombatReactionConfigurationError("CombatReactionDefinition.trigger_types nie może być puste.")
        required_weapon_tags = _string_sequence(data.get("required_weapon_tags", []))
        required_weapon_specializations = _string_sequence(data.get("required_weapon_specializations", []))
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            reaction_type=CombatReactionType(reaction_type_raw),
            trigger_types=trigger_types,
            required_technique_id=str(data.get("required_technique_id", "")).strip() or None,
            required_defense_style=required_defense_style,
            required_weapon_tags=required_weapon_tags,
            required_weapon_specializations=required_weapon_specializations,
            enabled=bool(data.get("enabled", True)),
            priority=_coerce_int(data.get("priority", 0), 0),
            consumes_reaction_window=bool(data.get("consumes_reaction_window", False)),
        )


@dataclass(frozen=True, slots=True)
class CombatReaction:
    reaction_id: str
    reaction_definition_id: str
    reaction_type: CombatReactionType
    source_action_id: str
    reactor_id: str
    trigger_actor_id: str
    trigger_target_id: str
    technique_id: str | None
    trigger_type: ReactionTriggerType
    automatic: bool
    metadata: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "reaction_id": self.reaction_id,
            "reaction_definition_id": self.reaction_definition_id,
            "reaction_type": self.reaction_type.value,
            "source_action_id": self.source_action_id,
            "reactor_id": self.reactor_id,
            "trigger_actor_id": self.trigger_actor_id,
            "trigger_target_id": self.trigger_target_id,
            "technique_id": self.technique_id,
            "trigger_type": self.trigger_type.value,
            "automatic": self.automatic,
            "metadata": list(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class CombatReactionCatalog:
    definitions: tuple[CombatReactionDefinition, ...]
    definitions_by_id: Mapping[str, CombatReactionDefinition] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_id: dict[str, CombatReactionDefinition] = {}
        for definition in self.definitions:
            key = _fold(definition.id)
            if key in by_id:
                raise CombatReactionConfigurationError(f"Zduplikowany identyfikator reakcji: {definition.id}")
            by_id[key] = definition
        object.__setattr__(self, "definitions", tuple(self.definitions))
        object.__setattr__(self, "definitions_by_id", MappingProxyType(by_id))

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, object]]) -> "CombatReactionCatalog":
        definitions: list[CombatReactionDefinition] = []
        for record in records:
            try:
                definition = CombatReactionDefinition.from_dict(record)
            except (CombatReactionError, CombatSpecializationLookupError, CombatTechniqueLookupError, WeaponProfileConfigurationError, ValueError) as exc:
                raise CombatReactionConfigurationError(str(exc)) from exc
            definitions.append(definition)
        return cls(tuple(definitions))

    @classmethod
    def from_json(cls, path: str | Path) -> "CombatReactionCatalog":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise CombatReactionConfigurationError("Katalog reakcji musi być listą JSON.")
        records: list[Mapping[str, object]] = []
        for entry in raw:
            if not isinstance(entry, Mapping):
                raise CombatReactionConfigurationError("Każda reakcja musi być obiektem JSON.")
            records.append(entry)
        return cls.from_records(records)

    def __iter__(self) -> Iterator[CombatReactionDefinition]:
        return iter(self.definitions)

    def names(self) -> tuple[str, ...]:
        return tuple(definition.id for definition in self.definitions)

    def by_id(self, reaction_id: str) -> CombatReactionDefinition:
        normalized = _fold(reaction_id)
        definition = self.definitions_by_id.get(normalized)
        if definition is None:
            raise CombatReactionLookupError(f"Nieznana reakcja: {reaction_id}")
        return definition

    def to_dict(self) -> dict[str, list[dict[str, object]]]:
        return {"reactions": [definition.to_dict() for definition in self.definitions]}


@dataclass(frozen=True, slots=True)
class ReactionUserProfile:
    reactor_id: str
    known_techniques: tuple[str, ...] = ()
    known_weapon_specializations: tuple[str, ...] = ()
    known_defense_specializations: tuple[str, ...] = ()
    active_defense_style: ActiveDefenseStyle | None = None
    active_weapon_specialization: str | None = None
    active_weapon_profile_id: str | None = None
    active_weapon_tags: tuple[str, ...] = ()
    weapon_specialization_id: str | None = None
    weapon_skill_percent: dict[str, int] = field(default_factory=dict)
    defense_skill_percent: dict[str, int] = field(default_factory=dict)
    additional_skill_percent: dict[str, int] = field(default_factory=dict)
    alive: bool = True
    in_combat: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "reactor_id", str(self.reactor_id).strip())
        object.__setattr__(self, "known_techniques", _normalize_sequence(self.known_techniques))
        object.__setattr__(self, "known_weapon_specializations", _normalize_sequence(self.known_weapon_specializations))
        object.__setattr__(self, "known_defense_specializations", _normalize_sequence(self.known_defense_specializations))
        object.__setattr__(self, "weapon_skill_percent", _sanitize_percent_map(self.weapon_skill_percent))
        object.__setattr__(self, "defense_skill_percent", _sanitize_percent_map(self.defense_skill_percent))
        object.__setattr__(self, "additional_skill_percent", _sanitize_percent_map(self.additional_skill_percent))
        object.__setattr__(self, "active_weapon_tags", TagRegistry.default().validate(self.active_weapon_tags))
        if self.active_defense_style is not None:
            object.__setattr__(self, "active_defense_style", resolve_active_defense_style(self.active_defense_style))
        if self.active_weapon_specialization is not None:
            object.__setattr__(self, "active_weapon_specialization", str(self.active_weapon_specialization).strip() or None)
        if self.weapon_specialization_id is not None:
            object.__setattr__(self, "weapon_specialization_id", str(self.weapon_specialization_id).strip() or None)
        if self.active_weapon_profile_id is not None:
            object.__setattr__(self, "active_weapon_profile_id", str(self.active_weapon_profile_id).strip() or None)


@dataclass(frozen=True, slots=True)
class ReactionTriggerContext:
    source_action: CombatAction
    source_outcome: CombatOutcome
    reactor_profile: ReactionUserProfile
    opponent_profile: ReactionUserProfile | None = None
    reaction_depth: int = 0


@dataclass(frozen=True, slots=True)
class ReactionWindow:
    source_action_id: str
    reactor_id: str
    consumed: bool
    available_reaction_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReactionEligibilityResult:
    allowed: bool
    reason_code: str
    reaction_definition_id: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "reason_code": self.reason_code,
            "reaction_definition_id": self.reaction_definition_id,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class CombatReactionDiscovery:
    source_action_id: str
    available_reactions: tuple[CombatReaction, ...]
    reaction_window: ReactionWindow

    def to_dict(self) -> dict[str, object]:
        return {
            "source_action_id": self.source_action_id,
            "available_reactions": [reaction.to_dict() for reaction in self.available_reactions],
            "reaction_window": {
                "source_action_id": self.reaction_window.source_action_id,
                "reactor_id": self.reaction_window.reactor_id,
                "consumed": self.reaction_window.consumed,
                "available_reaction_ids": list(self.reaction_window.available_reaction_ids),
            },
        }


CombatReactionOutcome = CombatReactionDiscovery


@dataclass(frozen=True, slots=True)
class ReactionExecutionResult:
    executed: bool
    reason_code: str
    reaction: CombatReaction | None
    reaction_action: CombatAction | None
    reaction_outcome: CombatOutcome | None
    reaction_result: Any | None = None
    window_consumed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "executed": self.executed,
            "reason_code": self.reason_code,
            "reaction": self.reaction.to_dict() if self.reaction is not None else None,
            "reaction_action": self.reaction_action.to_dict() if self.reaction_action is not None else None,
            "reaction_outcome": self.reaction_outcome.to_dict() if self.reaction_outcome is not None else None,
            "window_consumed": self.window_consumed,
        }


@dataclass(frozen=True, slots=True)
class CombatActionSequenceOutcome:
    primary_outcome: CombatOutcome
    reaction_executions: tuple[ReactionExecutionResult, ...] = ()


class CombatReactionExecutor:
    def __init__(self, catalog: CombatReactionCatalog | None = None) -> None:
        self.catalog = catalog or default_combat_reaction_catalog()
        self._consumed_windows: set[tuple[str, str]] = set()

    def execute_reaction(
        self,
        discovery: CombatReactionDiscovery,
        source_action: CombatAction,
        source_outcome: CombatOutcome,
        reactor: "Character",
        target: "Character",
        resolve_action: Callable[[CombatAction, "Character" | None, "Character" | None], Any],
    ) -> ReactionExecutionResult:
        window_key = (discovery.reaction_window.source_action_id, discovery.reaction_window.reactor_id)
        if discovery.reaction_window.consumed or window_key in self._consumed_windows:
            return ReactionExecutionResult(False, "REACTION_WINDOW_CONSUMED", None, None, None, window_consumed=True)
        if source_action.reaction_depth >= REACTION_POLICY.max_reaction_depth:
            return ReactionExecutionResult(False, "REACTION_DEPTH_EXCEEDED", None, None, None, window_consumed=True)
        if not discovery.available_reactions:
            return ReactionExecutionResult(False, "REACTION_NOT_AVAILABLE", None, None, None, window_consumed=False)
        reaction = discovery.available_reactions[0]
        if reaction.reaction_type != CombatReactionType.RIPOSTE:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "REACTION_NOT_AVAILABLE", reaction, None, None, window_consumed=True)
        weapon = reactor.weapon()
        if weapon is None or weapon.durability <= 0:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "ACTIVE_WEAPON_MISSING", reaction, None, None, window_consumed=True)
        if not reactor.is_alive:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "REACTOR_DEAD", reaction, None, None, window_consumed=True)
        if not target.is_alive:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "TARGET_DEAD", reaction, None, None, window_consumed=True)
        reactor_identity = getattr(reactor, "combat_identity", None) or reactor.username
        target_identity = getattr(target, "combat_identity", None) or target.username
        if reactor_identity != source_action.target_id or target_identity != source_action.actor_id:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "COMBAT_ENDED", reaction, None, None, window_consumed=True)
        if reactor.room_id != target.room_id:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "NOT_IN_SAME_LOCATION", reaction, None, None, window_consumed=True)
        if not reactor.in_combat:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "COMBAT_ENDED", reaction, None, None, window_consumed=True)
        weapon_profile = resolve_weapon_profile(weapon)
        if weapon_profile is None:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "INCOMPATIBLE_WEAPON_TAGS", reaction, None, None, window_consumed=True)
        if weapon_profile.legacy:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, "INCOMPATIBLE_WEAPON_TAGS", reaction, None, None, window_consumed=True)
        definition = self.catalog.by_id(reaction.reaction_definition_id)
        if definition.required_weapon_tags:
            active_tags = {_fold(value) for value in weapon_profile.tags}
            required_tags = {_fold(value) for value in definition.required_weapon_tags}
            if not required_tags.issubset(active_tags):
                self._consumed_windows.add(window_key)
                return ReactionExecutionResult(False, "REQUIRED_TAGS_MISSING", reaction, None, None, window_consumed=True)
        if reaction.technique_id is not None:
            technique = default_combat_technique_catalog().by_id(reaction.technique_id)
            reactor_profile = build_reaction_user_profile(reactor)
            technique_profile = TechniqueUserProfile(
                active_weapon_specialization=reactor_profile.active_weapon_specialization or weapon_profile.specialization_id,
                known_weapon_specializations=reactor_profile.known_weapon_specializations,
                known_defense_specializations=reactor_profile.known_defense_specializations,
                known_techniques=reactor_profile.known_techniques,
                weapon_skill_percent=reactor_profile.weapon_skill_percent,
                defense_skill_percent=reactor_profile.defense_skill_percent,
                additional_skill_percent=reactor_profile.additional_skill_percent,
            )
            technique_validation = can_use_technique(technique_profile, technique)
            if not technique_validation.allowed:
                self._consumed_windows.add(window_key)
                return ReactionExecutionResult(False, technique_validation.reason_code, reaction, None, None, window_consumed=True)
        validation = evaluate_reaction(
            ReactionTriggerContext(
                source_action=source_action,
                source_outcome=source_outcome,
                reactor_profile=build_reaction_user_profile(reactor),
                opponent_profile=build_reaction_user_profile(target),
                reaction_depth=source_action.reaction_depth,
            ),
            definition,
        )
        if not validation.allowed:
            self._consumed_windows.add(window_key)
            return ReactionExecutionResult(False, validation.reason_code, reaction, None, None, window_consumed=True)
        self._consumed_windows.add(window_key)
        reaction_action = build_reaction_action(source_action, reaction, reactor)
        reaction_result = resolve_action(reaction_action, reactor, target)
        reaction_outcome = getattr(reaction_result, "combat_outcome", None)
        return ReactionExecutionResult(
            True,
            "OK",
            reaction,
            reaction_action,
            reaction_outcome,
            reaction_result=reaction_result,
            window_consumed=True,
        )


def build_reaction_action(source_action: CombatAction, reaction: CombatReaction, reactor: "Character") -> CombatAction:
    weapon = reactor.weapon()
    weapon_snapshot = snapshot_weapon_profile(weapon)
    weapon_profile = resolve_weapon_profile(weapon)
    weapon_specialization_id = None
    if weapon_profile is not None and not weapon_profile.legacy:
        weapon_specialization_id = weapon_profile.specialization_id
    return CombatAction(
        actor_id=getattr(reactor, "combat_identity", None) or reactor.username,
        target_id=source_action.actor_id,
        action_type=CombatActionType.REACTION,
        parent_action_id=source_action.action_id,
        reaction_id=reaction.reaction_id,
        reaction_depth=source_action.reaction_depth + 1,
        weapon_id=weapon.id if weapon is not None else None,
        weapon_profile_id=weapon_snapshot.weapon_profile_id,
        weapon_specialization_id=weapon_specialization_id,
        weapon_tags=weapon_snapshot.weapon_tags,
        hand_requirement=weapon_snapshot.hand_requirement,
        technique_id=reaction.technique_id,
    )


def reaction_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "combat_reactions.json"


def load_combat_reaction_catalog(path: str | Path | None = None) -> CombatReactionCatalog:
    config_path = Path(path) if path is not None else reaction_catalog_path()
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CombatReactionConfigurationError(f"Nie znaleziono pliku reakcji: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise CombatReactionConfigurationError(f"Niepoprawny JSON reakcji: {config_path}") from exc
    if not isinstance(raw, list):
        raise CombatReactionConfigurationError("Katalog reakcji musi być listą JSON.")
    records: list[Mapping[str, object]] = []
    for entry in raw:
        if not isinstance(entry, Mapping):
            raise CombatReactionConfigurationError("Każda reakcja musi być obiektem JSON.")
        records.append(entry)
    return CombatReactionCatalog.from_records(records)


@lru_cache(maxsize=1)
def load_default_combat_reaction_catalog() -> CombatReactionCatalog:
    return load_combat_reaction_catalog(reaction_catalog_path())


def default_combat_reaction_catalog() -> CombatReactionCatalog:
    return load_default_combat_reaction_catalog()


def build_reaction_user_profile(character: "Character") -> ReactionUserProfile:
    weapon = character.weapon()
    weapon_snapshot = snapshot_weapon_profile(weapon)
    weapon_profile = resolve_weapon_profile(weapon)
    known_weapon_specializations = list(character.combat_specializations.weapon_specializations)
    if weapon_profile is not None and not weapon_profile.legacy:
        known_weapon_specializations.append(weapon_profile.specialization_id)
    return ReactionUserProfile(
        reactor_id=getattr(character, "combat_identity", None) or character.username,
        known_techniques=character.known_techniques,
        known_weapon_specializations=tuple(known_weapon_specializations),
        known_defense_specializations=character.combat_specializations.defense_specializations,
        active_defense_style=resolve_active_defense_style(character.active_defense_style),
        active_weapon_specialization=weapon_profile.specialization_id if weapon_profile is not None and not weapon_profile.legacy else None,
        active_weapon_profile_id=weapon_snapshot.weapon_profile_id,
        active_weapon_tags=weapon_snapshot.weapon_tags,
        weapon_specialization_id=weapon_profile.specialization_id if weapon_profile is not None and not weapon_profile.legacy else None,
        weapon_skill_percent={definition.id: _skill_percent_from_level(character.skills.level(_specialization_skill_key("weapon", definition.id))) for definition in WEAPON_SPECIALIZATIONS},
        defense_skill_percent={definition.id: _skill_percent_from_level(character.skills.level(_specialization_skill_key("defense", definition.id))) for definition in DEFENSE_SPECIALIZATIONS},
        additional_skill_percent={},
        alive=character.is_alive,
        in_combat=character.in_combat,
    )


def reaction_trigger_types_from_outcome(outcome: CombatOutcome) -> tuple[ReactionTriggerType, ...]:
    if outcome.result_type == CombatOutcomeType.INVALID or outcome.result_type == CombatOutcomeType.NO_TARGET:
        return ()
    defense_outcome = outcome.defense_outcome
    if outcome.result_type == CombatOutcomeType.DEFENDED and defense_outcome is not None and defense_outcome.successful_defense:
        if defense_outcome.resolution == DefenseResolution.PARRIED:
            return (ReactionTriggerType.SUCCESSFUL_PARRY,)
        if defense_outcome.resolution == DefenseResolution.DODGED:
            return (ReactionTriggerType.SUCCESSFUL_DODGE,)
        if defense_outcome.resolution == DefenseResolution.BLOCKED:
            return (ReactionTriggerType.SUCCESSFUL_SHIELD_BLOCK,)
    if outcome.result_type == CombatOutcomeType.MISS:
        return (ReactionTriggerType.ATTACK_MISSED,)
    if outcome.result_type == CombatOutcomeType.TARGET_DEFEATED:
        return (ReactionTriggerType.TARGET_DEFEATED,)
    if outcome.result_type == CombatOutcomeType.HIT:
        if outcome.wound_ids:
            return (ReactionTriggerType.ACTOR_WOUNDED,)
        return (ReactionTriggerType.ACTOR_HIT,)
    return ()


def _selected_defense_style_from_outcome(outcome: CombatOutcome) -> ActiveDefenseStyle | None:
    defense_outcome = outcome.defense_outcome
    if outcome.result_type != CombatOutcomeType.DEFENDED or defense_outcome is None or not defense_outcome.successful_defense:
        return None
    if defense_outcome.selected_defense == DefenseType.DODGE:
        return ActiveDefenseStyle.DODGE
    if defense_outcome.selected_defense == DefenseType.PARRY:
        return ActiveDefenseStyle.PARRY
    if defense_outcome.selected_defense == DefenseType.SHIELD_BLOCK:
        return ActiveDefenseStyle.SHIELD
    return None


def _source_outcome_reason_code(context: ReactionTriggerContext) -> str | None:
    if context.source_action.action_id != context.source_outcome.action_id:
        return "SOURCE_ACTION_INVALID"
    if context.source_action.actor_id != context.source_outcome.actor_id or context.source_action.target_id != context.source_outcome.target_id:
        return "SOURCE_ACTION_INVALID"
    if context.source_outcome.result_type in {CombatOutcomeType.INVALID, CombatOutcomeType.NO_TARGET}:
        return "SOURCE_OUTCOME_INVALID"
    return None


def evaluate_reaction(
    context: ReactionTriggerContext,
    reaction_definition: CombatReactionDefinition,
) -> ReactionEligibilityResult:
    source_reason = _source_outcome_reason_code(context)
    if source_reason is not None:
        return ReactionEligibilityResult(False, source_reason, reaction_definition.id, "Źródłowa akcja lub wynik są niespójne.")
    if not reaction_definition.enabled:
        return ReactionEligibilityResult(False, "REACTION_DISABLED", reaction_definition.id, "Reakcja jest wyłączona.")
    if context.reaction_depth >= REACTION_POLICY.max_reaction_depth:
        return ReactionEligibilityResult(False, "REACTION_WINDOW_CONSUMED", reaction_definition.id, "Okno reakcji zostało już zużyte.")
    trigger_types = reaction_trigger_types_from_outcome(context.source_outcome)
    if not any(trigger in reaction_definition.trigger_types for trigger in trigger_types):
        return ReactionEligibilityResult(False, "TRIGGER_NOT_MATCHED", reaction_definition.id, "Wynik źródłowej akcji nie uruchamia tej reakcji.")
    reactor = context.reactor_profile
    if not reactor.alive:
        return ReactionEligibilityResult(False, "REACTOR_DEAD", reaction_definition.id, "Reagująca postać nie żyje.")
    if not reactor.in_combat:
        return ReactionEligibilityResult(False, "REACTOR_NOT_IN_COMBAT", reaction_definition.id, "Reagująca postać nie walczy.")
    if reaction_definition.required_technique_id is not None:
        technique = default_combat_technique_catalog().by_id(reaction_definition.required_technique_id)
        normalized_known = {_fold(value) for value in reactor.known_techniques}
        if _fold(technique.id) not in normalized_known and _fold(technique.name) not in normalized_known:
            return ReactionEligibilityResult(False, "TECHNIQUE_NOT_KNOWN", reaction_definition.id, "Postać nie zna wymaganej techniki.")
    if reaction_definition.required_defense_style is not None and _selected_defense_style_from_outcome(context.source_outcome) != reaction_definition.required_defense_style:
        return ReactionEligibilityResult(False, "WRONG_DEFENSE_STYLE", reaction_definition.id, "Aktywny styl obrony nie pasuje do tej reakcji.")
    active_tags = {_fold(value) for value in reactor.active_weapon_tags}
    if not active_tags:
        return ReactionEligibilityResult(False, "INCOMPATIBLE_WEAPON_TAGS", reaction_definition.id, "Aktywna broń nie ma wymaganych tagów.")
    if reaction_definition.required_weapon_tags:
        required_tags = {_fold(value) for value in reaction_definition.required_weapon_tags}
        if not required_tags.issubset(active_tags):
            return ReactionEligibilityResult(False, "INCOMPATIBLE_WEAPON_TAGS", reaction_definition.id, "Aktywna broń nie ma wymaganych tagów.")
    return ReactionEligibilityResult(True, "OK", reaction_definition.id, "Reakcja jest dostępna.")


def build_reaction(
    context: ReactionTriggerContext,
    reaction_definition: CombatReactionDefinition,
) -> CombatReaction | None:
    eligibility = evaluate_reaction(context, reaction_definition)
    if not eligibility.allowed:
        return None
    trigger_types = reaction_trigger_types_from_outcome(context.source_outcome)
    trigger_type = trigger_types[0] if trigger_types else ReactionTriggerType.ACTOR_HIT
    return CombatReaction(
        reaction_id=uuid4().hex,
        reaction_definition_id=reaction_definition.id,
        reaction_type=reaction_definition.reaction_type,
        source_action_id=context.source_action.action_id,
        reactor_id=context.reactor_profile.reactor_id,
        trigger_actor_id=context.source_action.actor_id,
        trigger_target_id=context.source_action.target_id,
        technique_id=reaction_definition.required_technique_id,
        trigger_type=trigger_type,
        automatic=reaction_definition.consumes_reaction_window,
        metadata=(),
    )


def find_available_reactions(
    context: ReactionTriggerContext,
    catalog: CombatReactionCatalog | None = None,
) -> CombatReactionDiscovery:
    active_catalog = catalog or default_combat_reaction_catalog()
    reactions: list[CombatReaction] = []
    for definition in sorted(active_catalog.definitions, key=lambda item: (-item.priority, item.id)):
        reaction = build_reaction(context, definition)
        if reaction is not None:
            reactions.append(reaction)
    window = ReactionWindow(
        source_action_id=context.source_action.action_id,
        reactor_id=context.reactor_profile.reactor_id,
        consumed=context.reaction_depth >= REACTION_POLICY.max_reaction_depth,
        available_reaction_ids=tuple(reaction.reaction_id for reaction in reactions),
    )
    return CombatReactionDiscovery(
        source_action_id=context.source_action.action_id,
        available_reactions=tuple(reactions),
        reaction_window=window,
    )
