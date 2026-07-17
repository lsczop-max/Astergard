from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from astergard.characters.models import Character


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).casefold().strip()


def _normalize_sequence(values: Sequence[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return tuple(normalized)


def _normalize_unique_sequence(values: Sequence[str] | None) -> tuple[str, ...]:
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


def _string_values(values: object) -> tuple[str, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return ()
    return tuple(str(value).strip() for value in values if isinstance(value, str) and str(value).strip())


class CombatSpecializationError(ValueError):
    pass


class CombatSpecializationLimitError(CombatSpecializationError):
    pass


class CombatSpecializationLookupError(CombatSpecializationError):
    pass


def _dict_value(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _int_value(value: object, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        return int(text)
    return default


@dataclass(frozen=True, slots=True)
class TrainingStage:
    id: str
    name: str
    minimum_percent: int
    maximum_percent: int

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("TrainingStage.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("TrainingStage.name nie może być puste.")
        if self.minimum_percent < 0 or self.maximum_percent > 100:
            raise ValueError("TrainingStage musi mieścić się w zakresie 0-100.")
        if self.minimum_percent >= self.maximum_percent:
            raise ValueError("TrainingStage.minimum_percent musi być mniejsze od maximum_percent.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "minimum_percent": self.minimum_percent,
            "maximum_percent": self.maximum_percent,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "TrainingStage":
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            minimum_percent=_int_value(data.get("minimum_percent", 0), 0),
            maximum_percent=_int_value(data.get("maximum_percent", 0), 0),
        )


TRAINING_STAGES: tuple[TrainingStage, ...] = (
    TrainingStage("trainer", "trainer", 0, 30),
    TrainingStage("academy", "academy", 30, 60),
    TrainingStage("master", "master", 60, 100),
)


@dataclass(frozen=True, slots=True)
class WeaponSpecializationDefinition:
    id: str
    name: str
    description: str
    techniques: tuple[str, ...] = ()
    master_trainers: tuple[str, ...] = ()
    allowed_actions: tuple[str, ...] = ()
    future_balance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("WeaponSpecializationDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("WeaponSpecializationDefinition.name nie może być puste.")
        object.__setattr__(self, "techniques", _normalize_sequence(self.techniques))
        object.__setattr__(self, "master_trainers", _normalize_sequence(self.master_trainers))
        object.__setattr__(self, "allowed_actions", _normalize_sequence(self.allowed_actions))
        object.__setattr__(self, "future_balance", dict(self.future_balance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "techniques": list(self.techniques),
            "master_trainers": list(self.master_trainers),
            "allowed_actions": list(self.allowed_actions),
            "future_balance": dict(self.future_balance),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "WeaponSpecializationDefinition":
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            techniques=_string_values(data.get("techniques", [])),
            master_trainers=_string_values(data.get("master_trainers", [])),
            allowed_actions=_string_values(data.get("allowed_actions", [])),
            future_balance=_dict_value(data.get("future_balance", {})),
        )


@dataclass(frozen=True, slots=True)
class DefenseSpecializationDefinition:
    id: str
    name: str
    description: str
    techniques: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("DefenseSpecializationDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("DefenseSpecializationDefinition.name nie może być puste.")
        object.__setattr__(self, "techniques", _normalize_sequence(self.techniques))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "techniques": list(self.techniques),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "DefenseSpecializationDefinition":
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            techniques=_string_values(data.get("techniques", [])),
        )


@dataclass(frozen=True, slots=True)
class AdditionalSkillDefinition:
    id: str
    name: str
    description: str
    training_stages: tuple[TrainingStage, ...] = TRAINING_STAGES

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("AdditionalSkillDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("AdditionalSkillDefinition.name nie może być puste.")
        stages = tuple(self.training_stages)
        if len(stages) != 3:
            raise ValueError("AdditionalSkillDefinition musi zawierać dokładnie trzy etapy nauki.")
        object.__setattr__(self, "training_stages", stages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "training_stages": [stage.to_dict() for stage in self.training_stages],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "AdditionalSkillDefinition":
        stages_raw = data.get("training_stages", [])
        stages: tuple[TrainingStage, ...]
        if isinstance(stages_raw, Sequence) and not isinstance(stages_raw, (str, bytes)):
            stages = tuple(TrainingStage.from_dict(stage) for stage in stages_raw if isinstance(stage, Mapping))
        else:
            stages = TRAINING_STAGES
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            training_stages=stages,
        )


@dataclass(frozen=True, slots=True)
class CombatSpecializationRules:
    max_weapon_specializations: int = 2
    max_defense_specializations: int = 2
    max_additional_skills: int = 4

    def to_dict(self) -> dict[str, int]:
        return {
            "max_weapon_specializations": self.max_weapon_specializations,
            "max_defense_specializations": self.max_defense_specializations,
            "max_additional_skills": self.max_additional_skills,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CombatSpecializationRules":
        return cls(
            max_weapon_specializations=_int_value(data.get("max_weapon_specializations", 2), 2),
            max_defense_specializations=_int_value(data.get("max_defense_specializations", 2), 2),
            max_additional_skills=_int_value(data.get("max_additional_skills", 4), 4),
        )


@dataclass(frozen=True, slots=True)
class CombatSpecializationLoadout:
    weapon_specializations: tuple[str, ...] = ()
    defense_specializations: tuple[str, ...] = ()
    additional_skills: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "weapon_specializations", _normalize_sequence(self.weapon_specializations))
        object.__setattr__(self, "defense_specializations", _normalize_sequence(self.defense_specializations))
        object.__setattr__(self, "additional_skills", _normalize_sequence(self.additional_skills))

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "weapon_specializations": list(self.weapon_specializations),
            "defense_specializations": list(self.defense_specializations),
            "additional_skills": list(self.additional_skills),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CombatSpecializationLoadout":
        loadout = cls(
            weapon_specializations=_string_values(data.get("weapon_specializations", [])),
            defense_specializations=_string_values(data.get("defense_specializations", [])),
            additional_skills=_string_values(data.get("additional_skills", [])),
        )
        validate_combat_specialization_loadout(loadout)
        return loadout

    def validate(self, rules: CombatSpecializationRules | None = None) -> None:
        validate_combat_specialization_loadout(self, rules=rules)


def _build_lookup(definitions: Sequence[WeaponSpecializationDefinition | DefenseSpecializationDefinition | AdditionalSkillDefinition]) -> dict[str, object]:
    lookup: dict[str, object] = {}
    for definition in definitions:
        lookup[_fold(definition.id)] = definition
        lookup[_fold(definition.name)] = definition
    return lookup


WEAPON_SPECIALIZATIONS: tuple[WeaponSpecializationDefinition, ...] = (
    WeaponSpecializationDefinition("miecze", "miecze", "Specjalizacja w prowadzeniu mieczy.", future_balance={}),
    WeaponSpecializationDefinition("szable", "szable", "Specjalizacja w prowadzeniu szabel.", future_balance={}),
    WeaponSpecializationDefinition("sztylety", "sztylety", "Specjalizacja w prowadzeniu sztyletów.", future_balance={}),
    WeaponSpecializationDefinition("topory", "topory", "Specjalizacja w prowadzeniu toporów.", future_balance={}),
    WeaponSpecializationDefinition("mloty", "młoty", "Specjalizacja w prowadzeniu młotów.", future_balance={}),
    WeaponSpecializationDefinition("bulawy", "buławy", "Specjalizacja w prowadzeniu buław.", future_balance={}),
    WeaponSpecializationDefinition("wlocznie", "włócznie", "Specjalizacja w prowadzeniu włóczni.", future_balance={}),
    WeaponSpecializationDefinition("halabardy", "halabardy", "Specjalizacja w prowadzeniu halabard.", future_balance={}),
    WeaponSpecializationDefinition("cepy", "cepy", "Specjalizacja w prowadzeniu cepów.", future_balance={}),
    WeaponSpecializationDefinition("kije_bojowe", "kije bojowe", "Specjalizacja w prowadzeniu kijów bojowych.", future_balance={}),
)

DEFENSE_SPECIALIZATIONS: tuple[DefenseSpecializationDefinition, ...] = (
    DefenseSpecializationDefinition("tarcze", "tarcze", "Specjalizacja w używaniu tarczy do obrony."),
    DefenseSpecializationDefinition("parowanie", "parowanie", "Specjalizacja w parowaniu ciosów bronią."),
    DefenseSpecializationDefinition("uniki", "uniki", "Specjalizacja w unikaniu ciosów i wyjściu poza linię ataku."),
)

ADDITIONAL_SKILLS: tuple[AdditionalSkillDefinition, ...] = (
    AdditionalSkillDefinition("tropienie", "tropienie", "Czytanie śladów i ruchu w terenie."),
    AdditionalSkillDefinition("zielarstwo", "zielarstwo", "Rozpoznawanie i zbieranie roślin użytkowych."),
    AdditionalSkillDefinition("targowanie", "targowanie", "Prowadzenie wymiany i negocjacji cen."),
    AdditionalSkillDefinition("pierwsza_pomoc", "pierwsza pomoc", "Udzielanie szybkiej pomocy i stabilizacja ran."),
    AdditionalSkillDefinition("orientacja", "orientacja", "Utrzymywanie kierunku i odnajdywanie się w terenie."),
    AdditionalSkillDefinition("garbarstwo", "garbarstwo", "Wstępna obróbka skór i przygotowanie materiału."),
    AdditionalSkillDefinition("kowalstwo", "kowalstwo", "Praca z metalem, naprawy i prosty wyrób."),
    AdditionalSkillDefinition("skradanie", "skradanie", "Poruszanie się bez zwracania uwagi."),
    AdditionalSkillDefinition("otwieranie_zamkow", "otwieranie zamków", "Obsługa prostych zamków i rygli."),
    AdditionalSkillDefinition("pulapki", "pułapki", "Rozpoznawanie, zakładanie i rozbrajanie pułapek."),
    AdditionalSkillDefinition("wspinaczka", "wspinaczka", "Pokonywanie stromych i pionowych przeszkód."),
    AdditionalSkillDefinition("plywanie", "pływanie", "Poruszanie się w wodzie i utrzymywanie się na powierzchni."),
)


_WEAPON_BY_ID = _build_lookup(WEAPON_SPECIALIZATIONS)
_DEFENSE_BY_ID = _build_lookup(DEFENSE_SPECIALIZATIONS)
_ADDITIONAL_BY_ID = _build_lookup(ADDITIONAL_SKILLS)


def all_weapon_specializations() -> list[WeaponSpecializationDefinition]:
    return list(WEAPON_SPECIALIZATIONS)


def all_defense_specializations() -> list[DefenseSpecializationDefinition]:
    return list(DEFENSE_SPECIALIZATIONS)


def all_additional_skills() -> list[AdditionalSkillDefinition]:
    return list(ADDITIONAL_SKILLS)


def resolve_weapon_specialization(value: str) -> WeaponSpecializationDefinition:
    definition = _WEAPON_BY_ID.get(_fold(value))
    if isinstance(definition, WeaponSpecializationDefinition):
        return definition
    raise CombatSpecializationLookupError(f"Nieznana specjalizacja broni: {value}")


def resolve_defense_specialization(value: str) -> DefenseSpecializationDefinition:
    definition = _DEFENSE_BY_ID.get(_fold(value))
    if isinstance(definition, DefenseSpecializationDefinition):
        return definition
    raise CombatSpecializationLookupError(f"Nieznana specjalizacja obrony: {value}")


def resolve_additional_skill(value: str) -> AdditionalSkillDefinition:
    definition = _ADDITIONAL_BY_ID.get(_fold(value))
    if isinstance(definition, AdditionalSkillDefinition):
        return definition
    raise CombatSpecializationLookupError(f"Nieznana umiejętność dodatkowa: {value}")


def validate_combat_specialization_loadout(
    loadout: CombatSpecializationLoadout,
    *,
    rules: CombatSpecializationRules | None = None,
) -> None:
    active_rules = rules or CombatSpecializationRules()

    def _validate_group(
        values: tuple[str, ...],
        *,
        limit: int,
        kind: str,
        resolver: Any,
    ) -> None:
        if len(values) > limit:
            raise CombatSpecializationLimitError(f"Przekroczono limit dla {kind}: {len(values)} > {limit}.")
        if len(set(values)) != len(values):
            raise CombatSpecializationLimitError(f"Specjalizacje {kind} nie mogą się powtarzać.")
        for value in values:
            resolver(value)

    _validate_group(
        loadout.weapon_specializations,
        limit=active_rules.max_weapon_specializations,
        kind="broni",
        resolver=resolve_weapon_specialization,
    )
    _validate_group(
        loadout.defense_specializations,
        limit=active_rules.max_defense_specializations,
        kind="obrony",
        resolver=resolve_defense_specialization,
    )
    _validate_group(
        loadout.additional_skills,
        limit=active_rules.max_additional_skills,
        kind="umiejętności dodatkowych",
        resolver=resolve_additional_skill,
    )


def combat_specialization_menu_text() -> str:
    lines = [
        "Specjalizacje broni:",
        *[f"- {definition.name}: {definition.description}" for definition in WEAPON_SPECIALIZATIONS],
        "",
        "Specjalizacje obrony:",
        *[f"- {definition.name}: {definition.description}" for definition in DEFENSE_SPECIALIZATIONS],
        "",
        "Umiejętności dodatkowe:",
        *[f"- {definition.name}: {definition.description}" for definition in ADDITIONAL_SKILLS],
    ]
    return "\n".join(lines)


def default_combat_specialization_rules() -> CombatSpecializationRules:
    return CombatSpecializationRules()


class WeaponClass(str, Enum):
    LIGHT = "LIGHT"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"
    POLEARM = "POLEARM"


class TechniqueSkillSource(str, Enum):
    WEAPON_SPECIALIZATION = "WEAPON_SPECIALIZATION"
    DEFENSE_SPECIALIZATION = "DEFENSE_SPECIALIZATION"


class ActiveDefenseStyle(str, Enum):
    DODGE = "DODGE"
    PARRY = "PARRY"
    SHIELD = "SHIELD"


class CombatTechniqueError(ValueError):
    pass


class CombatTechniqueConfigurationError(CombatTechniqueError):
    pass


CombatSpecializationConfigurationError = CombatTechniqueConfigurationError


class CombatTechniqueLookupError(CombatTechniqueError):
    pass


_DEFENSE_STYLE_TO_SPECIALIZATION_ID: dict[ActiveDefenseStyle, str] = {
    ActiveDefenseStyle.DODGE: "uniki",
    ActiveDefenseStyle.PARRY: "parowanie",
    ActiveDefenseStyle.SHIELD: "tarcze",
}

_SPECIALIZATION_ID_TO_DEFENSE_STYLE: dict[str, ActiveDefenseStyle] = {
    "uniki": ActiveDefenseStyle.DODGE,
    "parowanie": ActiveDefenseStyle.PARRY,
    "tarcze": ActiveDefenseStyle.SHIELD,
}

_DEFENSE_STYLE_LABELS: dict[ActiveDefenseStyle, str] = {
    ActiveDefenseStyle.DODGE: "uniki",
    ActiveDefenseStyle.PARRY: "parowanie",
    ActiveDefenseStyle.SHIELD: "tarcza",
}


def resolve_active_defense_style(value: ActiveDefenseStyle | str | None) -> ActiveDefenseStyle | None:
    if value is None:
        return None
    if isinstance(value, ActiveDefenseStyle):
        return value
    text = str(value).strip()
    if not text:
        return None
    folded = _fold(text)
    if folded in {"dodge", "unik", "uniki"}:
        return ActiveDefenseStyle.DODGE
    if folded in {"parry", "parowanie"}:
        return ActiveDefenseStyle.PARRY
    if folded in {"shield", "shield_block", "tarcza", "tarcze"}:
        return ActiveDefenseStyle.SHIELD
    try:
        return ActiveDefenseStyle(text.upper())
    except ValueError:
        return None


def defense_style_from_specialization(specialization_id: str) -> ActiveDefenseStyle | None:
    return _SPECIALIZATION_ID_TO_DEFENSE_STYLE.get(_fold(specialization_id))


def defense_specialization_for_style(style: ActiveDefenseStyle | str | None) -> str | None:
    resolved = resolve_active_defense_style(style)
    if resolved is None:
        return None
    return _DEFENSE_STYLE_TO_SPECIALIZATION_ID[resolved]


def defense_style_label(style: ActiveDefenseStyle | str | None) -> str:
    resolved = resolve_active_defense_style(style)
    if resolved is None:
        return "instynktowny"
    return _DEFENSE_STYLE_LABELS[resolved]


def _weapon_class_for_specialization(specialization_id: str) -> WeaponClass:
    normalized = _fold(specialization_id)
    if normalized in {_fold("sztylety"), _fold("szable")}:
        return WeaponClass.LIGHT
    if normalized in {_fold("miecze"), _fold("topory")}:
        return WeaponClass.MEDIUM
    if normalized in {_fold("młoty"), _fold("mloty"), _fold("buławy"), _fold("bulawy"), _fold("cepy")}:
        return WeaponClass.HEAVY
    if normalized in {_fold("włócznie"), _fold("wlocznie"), _fold("halabardy"), _fold("kije bojowe"), _fold("kije_bojowe")}:
        return WeaponClass.POLEARM
    raise CombatSpecializationLookupError(f"Nieznana specjalizacja broni: {specialization_id}")


def _coerce_weapon_class(value: object) -> WeaponClass:
    try:
        return WeaponClass(str(value).strip().upper())
    except ValueError as exc:
        raise CombatTechniqueConfigurationError(f"Nieznana klasa broni: {value}") from exc


@dataclass(frozen=True, slots=True)
class CombatTechnique:
    id: str
    name: str
    description: str
    required_weapon_classes: tuple[WeaponClass, ...] = ()
    required_weapon_specializations: tuple[str, ...] = ()
    required_defense_specializations: tuple[str, ...] = ()
    required_skill_percent: int = 0
    required_skill_source: TechniqueSkillSource = TechniqueSkillSource.WEAPON_SPECIALIZATION
    enabled: bool = True
    stamina_cost: int = 0
    cooldown_seconds: int = 0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("CombatTechnique.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("CombatTechnique.name nie może być puste.")
        if self.required_skill_percent < 0 or self.required_skill_percent > 100:
            raise ValueError("CombatTechnique.required_skill_percent musi mieścić się w zakresie 0-100.")
        if self.stamina_cost < 0:
            raise ValueError("CombatTechnique.stamina_cost nie może być ujemny.")
        if self.cooldown_seconds < 0:
            raise ValueError("CombatTechnique.cooldown_seconds nie może być ujemny.")
        object.__setattr__(self, "required_weapon_classes", tuple(self.required_weapon_classes))
        object.__setattr__(self, "required_weapon_specializations", _normalize_sequence(self.required_weapon_specializations))
        object.__setattr__(self, "required_defense_specializations", _normalize_sequence(self.required_defense_specializations))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_weapon_classes": [weapon_class.value for weapon_class in self.required_weapon_classes],
            "required_weapon_specializations": list(self.required_weapon_specializations),
            "required_defense_specializations": list(self.required_defense_specializations),
            "required_skill_percent": self.required_skill_percent,
            "required_skill_source": self.required_skill_source.value,
            "enabled": self.enabled,
            "stamina_cost": self.stamina_cost,
            "cooldown_seconds": self.cooldown_seconds,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CombatTechnique":
        required_weapon_classes_raw = data.get("required_weapon_classes", [])
        if isinstance(required_weapon_classes_raw, Sequence) and not isinstance(required_weapon_classes_raw, (str, bytes)):
            required_weapon_classes = tuple(_coerce_weapon_class(value) for value in required_weapon_classes_raw if str(value).strip())
        else:
            required_weapon_classes = ()
        source_raw = str(data.get("required_skill_source", TechniqueSkillSource.WEAPON_SPECIALIZATION.value)).strip().upper()
        try:
            source = TechniqueSkillSource(source_raw)
        except ValueError as exc:
            raise CombatTechniqueConfigurationError(f"Nieznane źródło poziomu umiejętności: {source_raw}") from exc
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            required_weapon_classes=required_weapon_classes,
            required_weapon_specializations=_string_values(data.get("required_weapon_specializations", [])),
            required_defense_specializations=_string_values(data.get("required_defense_specializations", [])),
            required_skill_percent=_int_value(data.get("required_skill_percent", 0), 0),
            required_skill_source=source,
            enabled=bool(data.get("enabled", True)),
            stamina_cost=_int_value(data.get("stamina_cost", 0), 0),
            cooldown_seconds=_int_value(data.get("cooldown_seconds", 0), 0),
        )


@dataclass(frozen=True, slots=True)
class CombatTechniqueCatalog:
    techniques: tuple[CombatTechnique, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "techniques", tuple(self.techniques))

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        return {"techniques": [technique.to_dict() for technique in self.techniques]}

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CombatTechniqueCatalog":
        techniques_raw = data.get("techniques", [])
        if not isinstance(techniques_raw, Sequence) or isinstance(techniques_raw, (str, bytes)):
            raise CombatTechniqueConfigurationError("Katalog technik musi zawierać listę technik.")
        techniques: list[CombatTechnique] = []
        seen_ids: set[str] = set()
        for raw in techniques_raw:
            if not isinstance(raw, Mapping):
                raise CombatTechniqueConfigurationError("Każda technika musi być obiektem JSON.")
            try:
                technique = CombatTechnique.from_dict(raw)
            except CombatSpecializationError:
                raise
            except ValueError as exc:
                raise CombatTechniqueConfigurationError(str(exc)) from exc
            if technique.id in seen_ids:
                raise CombatTechniqueConfigurationError(f"Zduplikowany identyfikator techniki: {technique.id}")
            seen_ids.add(technique.id)
            try:
                _validate_technique_definition(technique)
            except CombatSpecializationLookupError as exc:
                raise CombatTechniqueConfigurationError(str(exc)) from exc
            techniques.append(technique)
        return cls(tuple(techniques))

    def by_id(self, technique_id: str) -> CombatTechnique:
        normalized = _fold(technique_id)
        for technique in self.techniques:
            if _fold(technique.id) == normalized:
                return technique
        raise CombatTechniqueLookupError(f"Nieznana technika: {technique_id}")

    def names(self) -> tuple[str, ...]:
        return tuple(technique.id for technique in self.techniques)


@dataclass(frozen=True, slots=True)
class TechniqueUserProfile:
    active_weapon_specialization: str | None = None
    known_weapon_specializations: tuple[str, ...] = ()
    known_defense_specializations: tuple[str, ...] = ()
    known_techniques: tuple[str, ...] = ()
    weapon_skill_percent: dict[str, int] = field(default_factory=dict)
    defense_skill_percent: dict[str, int] = field(default_factory=dict)
    additional_skill_percent: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "known_weapon_specializations", _normalize_sequence(self.known_weapon_specializations))
        object.__setattr__(self, "known_defense_specializations", _normalize_sequence(self.known_defense_specializations))
        object.__setattr__(self, "known_techniques", _normalize_unique_sequence(self.known_techniques))
        object.__setattr__(self, "weapon_skill_percent", _sanitize_percent_map(self.weapon_skill_percent))
        object.__setattr__(self, "defense_skill_percent", _sanitize_percent_map(self.defense_skill_percent))
        object.__setattr__(self, "additional_skill_percent", _sanitize_percent_map(self.additional_skill_percent))
        if self.active_weapon_specialization is not None:
            object.__setattr__(self, "active_weapon_specialization", str(self.active_weapon_specialization).strip() or None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_weapon_specialization": self.active_weapon_specialization,
            "known_weapon_specializations": list(self.known_weapon_specializations),
            "known_defense_specializations": list(self.known_defense_specializations),
            "known_techniques": list(self.known_techniques),
            "weapon_skill_percent": dict(self.weapon_skill_percent),
            "defense_skill_percent": dict(self.defense_skill_percent),
            "additional_skill_percent": dict(self.additional_skill_percent),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "TechniqueUserProfile":
        return cls(
            active_weapon_specialization=str(data.get("active_weapon_specialization", "")).strip() or None,
            known_weapon_specializations=_string_values(data.get("known_weapon_specializations", [])),
            known_defense_specializations=_string_values(data.get("known_defense_specializations", [])),
            known_techniques=_string_values(data.get("known_techniques", [])),
            weapon_skill_percent=_sanitize_percent_map(data.get("weapon_skill_percent", {})),
            defense_skill_percent=_sanitize_percent_map(data.get("defense_skill_percent", {})),
            additional_skill_percent=_sanitize_percent_map(data.get("additional_skill_percent", {})),
        )


@dataclass(frozen=True, slots=True)
class TechniqueEligibilityResult:
    allowed: bool
    reason_code: str
    message: str


@dataclass(frozen=True, slots=True)
class MasterTrainerRequirements:
    minimum_skill_percent: int = 0
    required_weapon_specializations: tuple[str, ...] = ()
    required_defense_specializations: tuple[str, ...] = ()
    required_reputation: int | None = None
    required_quest_id: str | None = None
    required_item_id: str | None = None
    learning_cost: int | None = None

    def __post_init__(self) -> None:
        if self.minimum_skill_percent < 0 or self.minimum_skill_percent > 100:
            raise ValueError("MasterTrainerRequirements.minimum_skill_percent musi mieścić się w zakresie 0-100.")
        object.__setattr__(self, "required_weapon_specializations", _normalize_sequence(self.required_weapon_specializations))
        object.__setattr__(self, "required_defense_specializations", _normalize_sequence(self.required_defense_specializations))

    def to_dict(self) -> dict[str, Any]:
        return {
            "minimum_skill_percent": self.minimum_skill_percent,
            "required_weapon_specializations": list(self.required_weapon_specializations),
            "required_defense_specializations": list(self.required_defense_specializations),
            "required_reputation": self.required_reputation,
            "required_quest_id": self.required_quest_id,
            "required_item_id": self.required_item_id,
            "learning_cost": self.learning_cost,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "MasterTrainerRequirements":
        return cls(
            minimum_skill_percent=_int_value(data.get("minimum_skill_percent", 0), 0),
            required_weapon_specializations=_string_values(data.get("required_weapon_specializations", [])),
            required_defense_specializations=_string_values(data.get("required_defense_specializations", [])),
            required_reputation=_int_value(data["required_reputation"], 0) if "required_reputation" in data and data["required_reputation"] is not None else None,
            required_quest_id=str(data.get("required_quest_id", "")).strip() or None,
            required_item_id=str(data.get("required_item_id", "")).strip() or None,
            learning_cost=_int_value(data["learning_cost"], 0) if "learning_cost" in data and data["learning_cost"] is not None else None,
        )


@dataclass(frozen=True, slots=True)
class MasterTrainer:
    id: str
    name: str
    description: str
    location_id: str
    school_id: str | None = None
    organization_id: str | None = None
    career_id: str | None = None
    taught_specializations: tuple[str, ...] = ()
    taught_techniques: tuple[str, ...] = ()
    requirements: MasterTrainerRequirements = field(default_factory=MasterTrainerRequirements)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("MasterTrainer.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("MasterTrainer.name nie może być puste.")
        if not self.location_id.strip():
            raise ValueError("MasterTrainer.location_id nie może być pusty.")
        if self.school_id is not None:
            object.__setattr__(self, "school_id", str(self.school_id).strip() or None)
        if self.organization_id is not None:
            object.__setattr__(self, "organization_id", str(self.organization_id).strip() or None)
        if self.career_id is not None:
            object.__setattr__(self, "career_id", str(self.career_id).strip() or None)
        object.__setattr__(self, "taught_specializations", _normalize_sequence(self.taught_specializations))
        object.__setattr__(self, "taught_techniques", _normalize_unique_sequence(self.taught_techniques))
        if not isinstance(self.requirements, MasterTrainerRequirements):
            object.__setattr__(self, "requirements", MasterTrainerRequirements.from_dict(self.requirements))  # type: ignore[arg-type]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location_id": self.location_id,
            "school_id": self.school_id,
            "organization_id": self.organization_id,
            "career_id": self.career_id,
            "taught_specializations": list(self.taught_specializations),
            "taught_techniques": list(self.taught_techniques),
            "requirements": self.requirements.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "MasterTrainer":
        requirements_raw = data.get("requirements", {})
        requirements = MasterTrainerRequirements.from_dict(requirements_raw) if isinstance(requirements_raw, Mapping) else MasterTrainerRequirements()
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            location_id=str(data.get("location_id", "")).strip(),
            school_id=str(data.get("school_id", "")).strip() or None,
            organization_id=str(data.get("organization_id", "")).strip() or None,
            career_id=str(data.get("career_id", "")).strip() or None,
            taught_specializations=_string_values(data.get("taught_specializations", [])),
            taught_techniques=_string_values(data.get("taught_techniques", [])),
            requirements=requirements,
        )

    def can_teach_specialization(self, specialization_id: str) -> bool:
        normalized = _fold(specialization_id)
        return any(_fold(value) == normalized for value in self.taught_specializations)

    def can_teach_technique(self, technique_id: str) -> bool:
        normalized = _fold(technique_id)
        return any(_fold(value) == normalized for value in self.taught_techniques)


@dataclass(frozen=True, slots=True)
class LearningResult:
    allowed: bool
    reason_code: str
    message: str


def _sanitize_percent_map(values: object) -> dict[str, int]:
    if not isinstance(values, Mapping):
        return {}
    sanitized: dict[str, int] = {}
    for raw_key, raw_value in values.items():
        key = str(raw_key).strip()
        if not key:
            continue
        percent = _int_value(raw_value, -1)
        if percent < 0 or percent > 100:
            continue
        sanitized[key] = percent
    return sanitized


def _validate_technique_definition(technique: CombatTechnique) -> None:
    for weapon_class in technique.required_weapon_classes:
        if not isinstance(weapon_class, WeaponClass):
            raise CombatTechniqueConfigurationError(f"Nieznana klasa broni w technice {technique.id}: {weapon_class}")
    for specialization_id in technique.required_weapon_specializations:
        _weapon_class_for_specialization(specialization_id)
    for specialization_id in technique.required_defense_specializations:
        resolve_defense_specialization(specialization_id)


DEFAULT_COMBAT_TECHNIQUE_PATH = Path(__file__).resolve().parents[1] / "data" / "combat_techniques.json"


@lru_cache(maxsize=1)
def _load_default_technique_catalog() -> CombatTechniqueCatalog:
    return load_combat_technique_catalog(DEFAULT_COMBAT_TECHNIQUE_PATH)


def load_combat_technique_catalog(path: str | Path | None = None) -> CombatTechniqueCatalog:
    config_path = Path(path) if path is not None else DEFAULT_COMBAT_TECHNIQUE_PATH
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CombatTechniqueConfigurationError(f"Nie znaleziono pliku technik: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise CombatTechniqueConfigurationError(f"Niepoprawny JSON technik: {config_path}") from exc
    if not isinstance(raw, Mapping):
        raise CombatTechniqueConfigurationError("Katalog technik musi być obiektem JSON.")
    return CombatTechniqueCatalog.from_dict(raw)


def default_combat_technique_catalog() -> CombatTechniqueCatalog:
    return _load_default_technique_catalog()


def can_use_technique(profile: TechniqueUserProfile, technique: CombatTechnique) -> TechniqueEligibilityResult:
    if not technique.enabled:
        return TechniqueEligibilityResult(False, "TECHNIQUE_DISABLED", f"Technika {technique.name} jest wyłączona.")

    active_weapon = profile.active_weapon_specialization
    if not active_weapon:
        return TechniqueEligibilityResult(False, "NO_ACTIVE_WEAPON", "Brak aktywnej broni.")

    try:
        active_weapon_definition = resolve_weapon_specialization(active_weapon)
    except CombatSpecializationLookupError:
        return TechniqueEligibilityResult(False, "INCOMPATIBLE_WEAPON_SPECIALIZATION", "Aktywna broń nie jest znaną specjalizacją.")

    if _fold(active_weapon_definition.id) not in {_fold(value) for value in profile.known_weapon_specializations} and _fold(active_weapon_definition.name) not in {_fold(value) for value in profile.known_weapon_specializations}:
        return TechniqueEligibilityResult(False, "WEAPON_SPECIALIZATION_NOT_LEARNED", "Postać nie zna aktywnej specjalizacji broni.")

    active_weapon_class = _weapon_class_for_specialization(active_weapon_definition.id)
    if technique.required_weapon_classes and active_weapon_class not in technique.required_weapon_classes:
        return TechniqueEligibilityResult(False, "INCOMPATIBLE_WEAPON_CLASS", "Aktywna broń nie pasuje do tej techniki.")

    if technique.required_weapon_specializations:
        normalized_required = {_fold(value) for value in technique.required_weapon_specializations}
        if _fold(active_weapon_definition.id) not in normalized_required and _fold(active_weapon_definition.name) not in normalized_required:
            return TechniqueEligibilityResult(False, "WEAPON_SPECIALIZATION_NOT_LEARNED", "Postać nie zna wymaganej specjalizacji broni.")

    if technique.required_defense_specializations:
        normalized_known_defense = {_fold(value) for value in profile.known_defense_specializations}
        normalized_required_defense = {_fold(value) for value in technique.required_defense_specializations}
        matching_defense = normalized_known_defense & normalized_required_defense
        if not matching_defense:
            return TechniqueEligibilityResult(False, "REQUIRED_DEFENSE_NOT_LEARNED", "Postać nie zna wymaganej specjalizacji obrony.")

    if technique.required_skill_source == TechniqueSkillSource.DEFENSE_SPECIALIZATION:
        percent = max((profile.defense_skill_percent.get(value, 0) for value in technique.required_defense_specializations), default=0)
    else:
        percent = profile.weapon_skill_percent.get(active_weapon_definition.id, 0)
        if percent <= 0:
            percent = profile.weapon_skill_percent.get(active_weapon_definition.name, 0)
    if percent < technique.required_skill_percent:
        return TechniqueEligibilityResult(False, "SKILL_LEVEL_TOO_LOW", "Poziom umiejętności jest zbyt niski.")

    return TechniqueEligibilityResult(True, "OK", "Technika jest dostępna.")


def technique_catalog_as_dict(catalog: CombatTechniqueCatalog | None = None) -> dict[str, list[dict[str, Any]]]:
    active = catalog or default_combat_technique_catalog()
    return active.to_dict()


def _percent_from_map(values: Mapping[str, int], candidates: Sequence[str]) -> int:
    if not values:
        return 0
    folded_values = {_fold(key): int(value) for key, value in values.items()}
    for candidate in candidates:
        raw = values.get(candidate)
        if raw is not None:
            return int(raw)
        folded = _fold(candidate)
        if folded in folded_values:
            return folded_values[folded]
    return 0


def _specialization_candidates(technique: CombatTechnique) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*technique.required_weapon_specializations, *technique.required_defense_specializations)))


def _skill_percent_from_level(level: int) -> int:
    if level <= 0:
        return 0
    return min(100, level * 5)


def _specialization_skill_key(specialization_kind: str, specialization_id: str) -> str:
    kind = _fold(specialization_kind)
    if kind == "weapon":
        return {
            WeaponClass.LIGHT: "bron_jednoraczna",
            WeaponClass.MEDIUM: "bron_jednoraczna",
            WeaponClass.HEAVY: "bron_dwureczna",
            WeaponClass.POLEARM: "wlocznie",
        }[_weapon_class_for_specialization(specialization_id)]
    if kind == "defense":
        normalized = _fold(specialization_id)
        if normalized == _fold("tarcze"):
            return "tarcze"
        if normalized == _fold("parowanie"):
            return "parowanie"
        if normalized == _fold("uniki"):
            return "uniki"
        return specialization_id
    return specialization_id


def _technique_known(profile: TechniqueUserProfile, technique_id: str) -> bool:
    normalized = _fold(technique_id)
    return any(_fold(value) == normalized for value in profile.known_techniques)


def _active_specialization_known(profile: TechniqueUserProfile, specialization_id: str) -> bool:
    normalized = _fold(specialization_id)
    return any(_fold(value) == normalized for value in profile.known_weapon_specializations)


def _defense_specialization_known(profile: TechniqueUserProfile, specialization_id: str) -> bool:
    normalized = _fold(specialization_id)
    return any(_fold(value) == normalized for value in profile.known_defense_specializations)


def can_learn_technique(
    profile: TechniqueUserProfile,
    technique: CombatTechnique | str,
    trainer: MasterTrainer | None = None,
    *,
    catalog: CombatTechniqueCatalog | None = None,
) -> LearningResult:
    active_catalog = catalog or default_combat_technique_catalog()
    resolved = active_catalog.by_id(technique) if isinstance(technique, str) else technique

    if _technique_known(profile, resolved.id):
        return LearningResult(False, "TECHNIQUE_ALREADY_KNOWN", "Postać już zna tę technikę.")
    if trainer is not None and not trainer.can_teach_technique(resolved.id):
        return LearningResult(False, "TRAINER_CANNOT_TEACH", "Ten mistrz nie uczy tej techniki.")

    if resolved.required_weapon_specializations:
        if not any(_active_specialization_known(profile, specialization_id) for specialization_id in resolved.required_weapon_specializations):
            return LearningResult(False, "WEAPON_SPECIALIZATION_NOT_LEARNED", "Postać nie zna wymaganej specjalizacji broni.")

    if resolved.required_defense_specializations:
        if not any(_defense_specialization_known(profile, specialization_id) for specialization_id in resolved.required_defense_specializations):
            return LearningResult(False, "REQUIRED_DEFENSE_NOT_LEARNED", "Postać nie zna wymaganej specjalizacji obrony.")

    if resolved.required_skill_source == TechniqueSkillSource.DEFENSE_SPECIALIZATION:
        percent = _percent_from_map(profile.defense_skill_percent, resolved.required_defense_specializations)
    else:
        percent = _percent_from_map(profile.weapon_skill_percent, _specialization_candidates(resolved))
    if percent < resolved.required_skill_percent:
        return LearningResult(False, "SKILL_LEVEL_TOO_LOW", "Poziom umiejętności jest zbyt niski.")

    return LearningResult(True, "OK", "Technika może zostać nauczona.")


def can_learn_specialization(
    profile: TechniqueUserProfile,
    specialization_kind: str,
    specialization_id: str,
    trainer: MasterTrainer | None = None,
    *,
    current_loadout: CombatSpecializationLoadout | None = None,
) -> LearningResult:
    kind = _fold(specialization_kind)
    loadout = current_loadout or CombatSpecializationLoadout()

    if kind == "weapon":
        if any(_fold(value) == _fold(specialization_id) for value in loadout.weapon_specializations):
            return LearningResult(False, "SPECIALIZATION_ALREADY_KNOWN", "Postać już zna tę specjalizację broni.")
        if len(loadout.weapon_specializations) >= default_combat_specialization_rules().max_weapon_specializations:
            return LearningResult(False, "SPECIALIZATION_LIMIT_REACHED", "Przekroczono limit specjalizacji broni.")
        percent = _percent_from_map(profile.weapon_skill_percent, (specialization_id,))
    elif kind == "defense":
        if any(_fold(value) == _fold(specialization_id) for value in loadout.defense_specializations):
            return LearningResult(False, "SPECIALIZATION_ALREADY_KNOWN", "Postać już zna tę specjalizację obrony.")
        if len(loadout.defense_specializations) >= default_combat_specialization_rules().max_defense_specializations:
            return LearningResult(False, "SPECIALIZATION_LIMIT_REACHED", "Przekroczono limit specjalizacji obrony.")
        percent = _percent_from_map(profile.defense_skill_percent, (specialization_id,))
    else:
        if any(_fold(value) == _fold(specialization_id) for value in loadout.additional_skills):
            return LearningResult(False, "SPECIALIZATION_ALREADY_KNOWN", "Postać już zna tę umiejętność.")
        if len(loadout.additional_skills) >= default_combat_specialization_rules().max_additional_skills:
            return LearningResult(False, "SPECIALIZATION_LIMIT_REACHED", "Przekroczono limit umiejętności dodatkowych.")
        percent = _percent_from_map(profile.additional_skill_percent, (specialization_id,))

    if trainer is not None and not trainer.can_teach_specialization(specialization_id):
        return LearningResult(False, "TRAINER_CANNOT_TEACH", "Ten mistrz nie uczy tej specjalizacji.")

    if percent < (trainer.requirements.minimum_skill_percent if trainer is not None else 0):
        return LearningResult(False, "SKILL_LEVEL_TOO_LOW", "Poziom umiejętności jest zbyt niski.")

    if trainer is not None:
        required_weapon = {_fold(value) for value in trainer.requirements.required_weapon_specializations}
        required_defense = {_fold(value) for value in trainer.requirements.required_defense_specializations}
        if required_weapon and not required_weapon & {_fold(value) for value in loadout.weapon_specializations}:
            return LearningResult(False, "REQUIRED_SPECIALIZATION_NOT_LEARNED", "Postać nie spełnia wymagań mistrza.")
        if required_defense and not required_defense & {_fold(value) for value in loadout.defense_specializations}:
            return LearningResult(False, "REQUIRED_DEFENSE_NOT_LEARNED", "Postać nie spełnia wymagań mistrza.")

    return LearningResult(True, "OK", "Specjalizacja może zostać nauczona.")


def _skill_percent_for_character(character: "Character", specialization_kind: str, specialization_id: str) -> int:
    skill_key = _specialization_skill_key(specialization_kind, specialization_id)
    try:
        level = character.skills.level(skill_key)
    except Exception:
        return 0
    return _skill_percent_from_level(level)


def _profile_from_character(character: "Character") -> TechniqueUserProfile:
    return TechniqueUserProfile(
        active_weapon_specialization=None,
        known_weapon_specializations=character.combat_specializations.weapon_specializations,
        known_defense_specializations=character.combat_specializations.defense_specializations,
        known_techniques=character.known_techniques,
        weapon_skill_percent={definition.id: _skill_percent_for_character(character, "weapon", definition.id) for definition in WEAPON_SPECIALIZATIONS},
        defense_skill_percent={definition.id: _skill_percent_for_character(character, "defense", definition.id) for definition in DEFENSE_SPECIALIZATIONS},
        additional_skill_percent={definition.id: _skill_percent_for_character(character, "additional", definition.id) for definition in ADDITIONAL_SKILLS},
    )


def learn_technique(
    character: "Character",
    technique: CombatTechnique | str,
    trainer: MasterTrainer | None = None,
    *,
    catalog: CombatTechniqueCatalog | None = None,
) -> LearningResult:
    profile = _profile_from_character(character)
    result = can_learn_technique(profile, technique, trainer, catalog=catalog)
    if not result.allowed:
        return result
    resolved = (catalog or default_combat_technique_catalog()).by_id(technique) if isinstance(technique, str) else technique
    character.known_techniques = _normalize_unique_sequence((*character.known_techniques, resolved.id))
    return result


def learn_specialization(
    character: "Character",
    specialization_kind: str,
    specialization_id: str,
    trainer: MasterTrainer | None = None,
) -> LearningResult:
    profile = _profile_from_character(character)
    result = can_learn_specialization(profile, specialization_kind, specialization_id, trainer, current_loadout=character.combat_specializations)
    if not result.allowed:
        return result
    kind = _fold(specialization_kind)
    loadout = character.combat_specializations
    if kind == "weapon":
        character.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=(*loadout.weapon_specializations, specialization_id),
            defense_specializations=loadout.defense_specializations,
            additional_skills=loadout.additional_skills,
        )
    elif kind == "defense":
        character.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=loadout.weapon_specializations,
            defense_specializations=(*loadout.defense_specializations, specialization_id),
            additional_skills=loadout.additional_skills,
        )
        if character.active_defense_style is None:
            defense_style = defense_style_from_specialization(specialization_id)
            if defense_style is not None:
                character.active_defense_style = defense_style.value
    else:
        character.combat_specializations = CombatSpecializationLoadout(
            weapon_specializations=loadout.weapon_specializations,
            defense_specializations=loadout.defense_specializations,
            additional_skills=(*loadout.additional_skills, specialization_id),
        )
    return result


MASTER_TRAINERS: tuple[MasterTrainer, ...] = (
    MasterTrainer(
        id="master_sword",
        name="Mistrz Miecza",
        description="Naucza pracy mieczem i technik opartych na kontroli linii.",
        location_id="arena_miecza",
        school_id="szkola_strazy",
        organization_id="straz_miejska",
        career_id="zolnierz",
        taught_specializations=("miecze", "szable"),
        taught_techniques=("riposte", "disarm", "counterattack"),
        requirements=MasterTrainerRequirements(minimum_skill_percent=60),
    ),
    MasterTrainer(
        id="master_hammer",
        name="Mistrz Młota",
        description="Pokazuje, jak prowadzić ciężką broń bez utraty tempa.",
        location_id="kuznia_mistrza",
        school_id="szkola_kuzni",
        organization_id="cech_kowali",
        career_id="rzemieslnik",
        taught_specializations=("mloty", "bulawy", "cepy"),
        taught_techniques=("stun",),
        requirements=MasterTrainerRequirements(minimum_skill_percent=60),
    ),
    MasterTrainer(
        id="master_halberd",
        name="Mistrz Halabardy",
        description="Uczy walki bronią drzewcową i wykorzystania zasięgu.",
        location_id="plac_wartowni",
        school_id="szkola_najemna",
        organization_id="kompania_najemna",
        career_id="zolnierz",
        taught_specializations=("halabardy", "wlocznie", "kije_bojowe"),
        taught_techniques=("guard_break", "armor_pierce"),
        requirements=MasterTrainerRequirements(minimum_skill_percent=60),
    ),
)


def all_master_trainers() -> list[MasterTrainer]:
    return list(MASTER_TRAINERS)
