from __future__ import annotations

import json
import warnings
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, TYPE_CHECKING

from astergard.rules.combat_specialization import CombatSpecializationLookupError, WeaponClass, resolve_weapon_specialization

if TYPE_CHECKING:
    from astergard.characters.models import Character
    from astergard.items.models import Item


class WeaponProfileError(ValueError):
    pass


class WeaponProfileConfigurationError(WeaponProfileError):
    pass


class WeaponProfileLookupError(WeaponProfileError):
    pass


class DamageType(StrEnum):
    SLASH = "SLASH"
    THRUST = "THRUST"
    BLUNT = "BLUNT"
    PROJECTILE = "PROJECTILE"


class HandRequirement(StrEnum):
    ONE_HANDED = "ONE_HANDED"
    TWO_HANDED = "TWO_HANDED"
    VERSATILE = "VERSATILE"


TAG_DEFINITIONS: dict[str, str] = {
    "blade": "Ostrze o krawędzi tnącej.",
    "blunt": "Broń oparta na sile uderzenia i masie.",
    "pointed": "Broń zakończona wyraźnym grotem.",
    "shafted": "Broń osadzona na drzewcu lub trzonku.",
    "flexible": "Broń wykorzystująca elastyczne połączenie lub łańcuch.",
    "hooked": "Broń z hakiem, zakrzywionym zakończeniem albo zaczepem.",
    "agile": "Broń lekka i wygodna do szybkiej pracy.",
    "parry_capable": "Broń nadająca się do jawnego parowania.",
    "crushing": "Broń nastawiona na zgniatanie lub miażdżenie.",
    "armor_breaker": "Broń szczególnie nastawiona na przełamywanie osłony.",
    "shield_breaker": "Broń dobrze radząca sobie z tarczą lub blokiem.",
    "reach": "Broń zapewniająca większy dystans kontroli.",
    "close_quarters": "Broń wygodna w bardzo bliskim kontakcie.",
    "disarm_capable": "Broń nadająca się do podbierania lub wybijania oręża.",
    "stun_capable": "Broń mogąca wspierać ogłuszenie uderzeniem.",
    "one_handed": "Broń używana jedną ręką.",
    "two_handed": "Broń wymagająca obu rąk.",
    "versatile": "Broń mogąca być używana w więcej niż jednym chwycie.",
}


def _fold(text: str) -> str:
    return "".join(ch for ch in text.casefold().strip() if ch.isalnum() or ch == "_")


def _normalize_text(value: object) -> str:
    return str(value).strip()


def _unique_preserve_order(values: Sequence[str]) -> tuple[str, ...]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        folded = _fold(normalized)
        if folded in seen:
            continue
        seen.add(folded)
        unique.append(normalized)
    return tuple(unique)


def _coerce_weapon_class(value: object) -> WeaponClass:
    text = str(value).strip().upper()
    try:
        return WeaponClass(text)
    except ValueError as exc:
        raise WeaponProfileConfigurationError(f"Nieznana klasa broni: {value}") from exc


def _coerce_hand_requirement(value: object) -> HandRequirement:
    text = str(value).strip().upper()
    try:
        return HandRequirement(text)
    except ValueError as exc:
        raise WeaponProfileConfigurationError(f"Nieznane wymaganie dłoni: {value}") from exc


def _coerce_damage_type(value: object) -> DamageType:
    text = str(value).strip().upper()
    aliases = {
        "CIETA": DamageType.SLASH,
        "CIĘTA": DamageType.SLASH,
        "KLUTA": DamageType.THRUST,
        "OBUCHOWA": DamageType.BLUNT,
        "POCISKOWA": DamageType.PROJECTILE,
        "SLASH": DamageType.SLASH,
        "THRUST": DamageType.THRUST,
        "BLUNT": DamageType.BLUNT,
        "PROJECTILE": DamageType.PROJECTILE,
    }
    if text in aliases:
        return aliases[text]
    try:
        return DamageType(text)
    except ValueError as exc:
        raise WeaponProfileConfigurationError(f"Nieznany typ obrażeń: {value}") from exc


def _coerce_tag(value: object) -> str:
    tag = str(value).strip().casefold().replace(" ", "_").replace("-", "_")
    if not tag:
        raise WeaponProfileConfigurationError("Tag broni nie może być pusty.")
    return tag


def _float_value(value: object, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        return float(text)
    return default


@dataclass(frozen=True, slots=True)
class TagRegistry:
    definitions: Mapping[str, str] = field(default_factory=lambda: MappingProxyType(dict(TAG_DEFINITIONS)))

    def __post_init__(self) -> None:
        normalized: dict[str, str] = {}
        for tag, description in self.definitions.items():
            normalized[_fold(tag)] = str(description).strip()
        object.__setattr__(self, "definitions", MappingProxyType(normalized))

    @classmethod
    def default(cls) -> "TagRegistry":
        return cls()

    def normalize(self, tag: object) -> str:
        normalized = _coerce_tag(tag)
        if normalized not in self.definitions:
            raise WeaponProfileConfigurationError(f"Nieznany tag broni: {tag}")
        return normalized

    def validate(self, tags: Sequence[object]) -> tuple[str, ...]:
        normalized = [_coerce_tag(tag) for tag in tags]
        unique = _unique_preserve_order(normalized)
        for tag in unique:
            if tag not in self.definitions:
                raise WeaponProfileConfigurationError(f"Nieznany tag broni: {tag}")
        return unique

    def describe(self, tag: str) -> str:
        normalized = self.normalize(tag)
        return self.definitions[normalized]


@dataclass(frozen=True, slots=True)
class WeaponProfile:
    id: str
    name: str
    specialization_id: str
    weapon_class: WeaponClass
    tags: tuple[str, ...] = ()
    hand_requirement: HandRequirement = HandRequirement.ONE_HANDED
    damage_types: tuple[DamageType, ...] = ()
    base_speed: float = 1.0
    base_accuracy: float = 1.0
    base_damage: float = 1.0
    armor_penetration: float = 1.0
    reach: float = 1.0
    parry_modifier: float = 1.0
    enabled: bool = True
    legacy: bool = False

    def __post_init__(self) -> None:
        profile_id = _normalize_text(self.id)
        profile_name = _normalize_text(self.name)
        specialization_id = _normalize_text(self.specialization_id)
        if not profile_id:
            raise ValueError("WeaponProfile.id nie może być pusty.")
        if not profile_name:
            raise ValueError("WeaponProfile.name nie może być puste.")
        if not specialization_id:
            raise ValueError("WeaponProfile.specialization_id nie może być puste.")
        try:
            resolve_weapon_specialization(specialization_id)
        except CombatSpecializationLookupError as exc:
            raise WeaponProfileConfigurationError(f"Nieznana specjalizacja broni: {specialization_id}") from exc
        tags = TagRegistry.default().validate(self.tags)
        damage_types = tuple(_coerce_damage_type(value) for value in self.damage_types)
        damage_types = tuple(dict.fromkeys(damage_types))
        object.__setattr__(self, "id", profile_id)
        object.__setattr__(self, "name", profile_name)
        object.__setattr__(self, "specialization_id", specialization_id)
        object.__setattr__(self, "tags", tags)
        object.__setattr__(self, "damage_types", damage_types)
        object.__setattr__(self, "base_speed", _float_value(self.base_speed, 1.0))
        object.__setattr__(self, "base_accuracy", _float_value(self.base_accuracy, 1.0))
        object.__setattr__(self, "base_damage", _float_value(self.base_damage, 1.0))
        object.__setattr__(self, "armor_penetration", _float_value(self.armor_penetration, 1.0))
        object.__setattr__(self, "reach", _float_value(self.reach, 1.0))
        object.__setattr__(self, "parry_modifier", max(0.0, _float_value(self.parry_modifier, 1.0)))
        if self.hand_requirement == HandRequirement.ONE_HANDED and "one_handed" not in tags and not self.legacy:
            raise ValueError(f"Profil {self.id} wymaga tagu one_handed.")
        if self.hand_requirement == HandRequirement.TWO_HANDED and "two_handed" not in tags and not self.legacy:
            raise ValueError(f"Profil {self.id} wymaga tagu two_handed.")
        if self.hand_requirement == HandRequirement.VERSATILE and "versatile" not in tags and not self.legacy:
            raise ValueError(f"Profil {self.id} wymaga tagu versatile.")

    @property
    def supports_parry(self) -> bool:
        return not self.legacy and self.enabled and "parry_capable" in self.tags

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "specialization_id": self.specialization_id,
            "weapon_class": self.weapon_class.value,
            "tags": list(self.tags),
            "hand_requirement": self.hand_requirement.value,
            "damage_types": [damage_type.value for damage_type in self.damage_types],
            "base_speed": self.base_speed,
            "base_accuracy": self.base_accuracy,
            "base_damage": self.base_damage,
            "armor_penetration": self.armor_penetration,
            "reach": self.reach,
            "parry_modifier": self.parry_modifier,
            "enabled": self.enabled,
            "legacy": self.legacy,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "WeaponProfile":
        tags_raw = data.get("tags", [])
        damage_types_raw = data.get("damage_types", [])
        if not isinstance(tags_raw, Sequence) or isinstance(tags_raw, (str, bytes)):
            raise WeaponProfileConfigurationError("WeaponProfile.tags musi być listą.")
        if not isinstance(damage_types_raw, Sequence) or isinstance(damage_types_raw, (str, bytes)):
            raise WeaponProfileConfigurationError("WeaponProfile.damage_types musi być listą.")
        return cls(
            id=_normalize_text(data.get("id", "")),
            name=_normalize_text(data.get("name", "")),
            specialization_id=_normalize_text(data.get("specialization_id", "")),
            weapon_class=_coerce_weapon_class(data.get("weapon_class", "")),
            tags=tuple(_coerce_tag(tag) for tag in tags_raw),
            hand_requirement=_coerce_hand_requirement(data.get("hand_requirement", HandRequirement.ONE_HANDED.value)),
            damage_types=tuple(_coerce_damage_type(value) for value in damage_types_raw),
            base_speed=_float_value(data.get("base_speed", 1.0), 1.0),
            base_accuracy=_float_value(data.get("base_accuracy", 1.0), 1.0),
            base_damage=_float_value(data.get("base_damage", 1.0), 1.0),
            armor_penetration=_float_value(data.get("armor_penetration", 1.0), 1.0),
            reach=_float_value(data.get("reach", 1.0), 1.0),
            parry_modifier=_float_value(data.get("parry_modifier", 1.0), 1.0),
            enabled=bool(data.get("enabled", True)),
            legacy=bool(data.get("legacy", False)),
        )


@dataclass(frozen=True, slots=True)
class WeaponProfileSnapshot:
    weapon_profile_id: str | None = None
    weapon_tags: tuple[str, ...] = ()
    hand_requirement: HandRequirement | None = None
    parry_modifier: float = 1.0

    def to_dict(self) -> dict[str, object]:
        return {
            "weapon_profile_id": self.weapon_profile_id,
            "weapon_tags": list(self.weapon_tags),
            "hand_requirement": self.hand_requirement.value if self.hand_requirement is not None else None,
            "parry_modifier": self.parry_modifier,
        }


@dataclass(frozen=True, slots=True)
class ArmorProfile:
    id: str
    name: str
    dodge_modifier: float = 1.0
    block_modifier: float = 1.0
    parry_modifier: float = 1.0
    enabled: bool = True
    legacy: bool = False

    def __post_init__(self) -> None:
        profile_id = _normalize_text(self.id)
        profile_name = _normalize_text(self.name)
        if not profile_id:
            raise ValueError("ArmorProfile.id nie może być pusty.")
        if not profile_name:
            raise ValueError("ArmorProfile.name nie może być puste.")
        object.__setattr__(self, "id", profile_id)
        object.__setattr__(self, "name", profile_name)
        object.__setattr__(self, "dodge_modifier", max(0.0, _float_value(self.dodge_modifier, 1.0)))
        object.__setattr__(self, "block_modifier", max(0.0, _float_value(self.block_modifier, 1.0)))
        object.__setattr__(self, "parry_modifier", max(0.0, _float_value(self.parry_modifier, 1.0)))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "dodge_modifier": self.dodge_modifier,
            "block_modifier": self.block_modifier,
            "parry_modifier": self.parry_modifier,
            "enabled": self.enabled,
            "legacy": self.legacy,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ArmorProfile":
        return cls(
            id=_normalize_text(data.get("id", "")),
            name=_normalize_text(data.get("name", "")),
            dodge_modifier=_float_value(data.get("dodge_modifier", 1.0), 1.0),
            block_modifier=_float_value(data.get("block_modifier", 1.0), 1.0),
            parry_modifier=_float_value(data.get("parry_modifier", 1.0), 1.0),
            enabled=bool(data.get("enabled", True)),
            legacy=bool(data.get("legacy", False)),
        )


@dataclass(frozen=True, slots=True)
class ShieldProfile:
    id: str
    name: str
    block_modifier: float = 1.0
    enabled: bool = True
    legacy: bool = False

    def __post_init__(self) -> None:
        profile_id = _normalize_text(self.id)
        profile_name = _normalize_text(self.name)
        if not profile_id:
            raise ValueError("ShieldProfile.id nie może być pusty.")
        if not profile_name:
            raise ValueError("ShieldProfile.name nie może być puste.")
        object.__setattr__(self, "id", profile_id)
        object.__setattr__(self, "name", profile_name)
        object.__setattr__(self, "block_modifier", max(0.0, _float_value(self.block_modifier, 1.0)))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "block_modifier": self.block_modifier,
            "enabled": self.enabled,
            "legacy": self.legacy,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ShieldProfile":
        return cls(
            id=_normalize_text(data.get("id", "")),
            name=_normalize_text(data.get("name", "")),
            block_modifier=_float_value(data.get("block_modifier", 1.0), 1.0),
            enabled=bool(data.get("enabled", True)),
            legacy=bool(data.get("legacy", False)),
        )


def _legacy_weapon_profile() -> WeaponProfile:
    return WeaponProfile(
        id="legacy_weapon",
        name="legacy weapon",
        specialization_id="miecze",
        weapon_class=WeaponClass.MEDIUM,
        tags=(),
        hand_requirement=HandRequirement.ONE_HANDED,
        damage_types=(),
        base_speed=1.0,
        base_accuracy=1.0,
        base_damage=1.0,
        armor_penetration=1.0,
        reach=1.0,
        enabled=True,
        legacy=True,
    )


@dataclass(frozen=True, slots=True)
class WeaponProfileCatalog:
    profiles: tuple[WeaponProfile, ...]
    tag_registry: TagRegistry = field(default_factory=TagRegistry.default)
    legacy_profile: WeaponProfile = field(default_factory=_legacy_weapon_profile, repr=False, compare=False)
    profiles_by_id: Mapping[str, WeaponProfile] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_id: dict[str, WeaponProfile] = {}
        for profile in self.profiles:
            key = _fold(profile.id)
            if key in by_id:
                raise WeaponProfileConfigurationError(f"Zduplikowany identyfikator profilu broni: {profile.id}")
            by_id[key] = profile
        object.__setattr__(self, "profiles", tuple(self.profiles))
        object.__setattr__(self, "profiles_by_id", MappingProxyType(by_id))

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, object]]) -> "WeaponProfileCatalog":
        profiles = tuple(WeaponProfile.from_dict(record) for record in records)
        return cls(profiles=profiles)

    @classmethod
    def from_json(cls, path: str | Path) -> "WeaponProfileCatalog":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise WeaponProfileConfigurationError("Katalog profili broni musi być listą.")
        records: list[Mapping[str, object]] = []
        for entry in raw:
            if not isinstance(entry, Mapping):
                raise WeaponProfileConfigurationError("Każdy profil broni musi być obiektem JSON.")
            records.append(entry)
        return cls.from_records(records)

    @classmethod
    def load_default(cls) -> "WeaponProfileCatalog":
        return load_default_weapon_profile_catalog()

    def __iter__(self) -> Iterator[WeaponProfile]:
        return iter(self.profiles)

    def get(self, profile_id: str | None) -> WeaponProfile | None:
        if profile_id is None:
            return None
        return self.profiles_by_id.get(_fold(profile_id))

    def resolve(self, weapon: "Item | None") -> WeaponProfile | None:
        if weapon is None or getattr(weapon, "item_type", None) != "weapon" or getattr(weapon, "durability", 0) <= 0:
            return None
        profile_id = getattr(weapon, "weapon_profile_id", None)
        if profile_id is None:
            return self.legacy_profile
        profile = self.get(profile_id)
        if profile is None:
            warnings.warn(
                f"Nieznany profil broni {profile_id} dla przedmiotu {getattr(weapon, 'id', '?')}. Użyto profilu legacy.",
                stacklevel=2,
            )
            return self.legacy_profile
        return profile

    def snapshot(self, weapon: "Item | None") -> WeaponProfileSnapshot:
        profile = self.resolve(weapon)
        if profile is None or profile.legacy:
            return WeaponProfileSnapshot()
        return WeaponProfileSnapshot(
            weapon_profile_id=profile.id,
            weapon_tags=profile.tags,
            hand_requirement=profile.hand_requirement,
            parry_modifier=profile.parry_modifier,
        )


@dataclass(frozen=True, slots=True)
class ArmorProfileCatalog:
    profiles: tuple[ArmorProfile, ...]
    legacy_profile: ArmorProfile = field(default_factory=lambda: ArmorProfile("legacy_armor", "legacy armor", legacy=True), repr=False, compare=False)
    profiles_by_id: Mapping[str, ArmorProfile] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_id: dict[str, ArmorProfile] = {}
        for profile in self.profiles:
            key = _fold(profile.id)
            if key in by_id:
                raise WeaponProfileConfigurationError(f"Zduplikowany identyfikator profilu pancerza: {profile.id}")
            by_id[key] = profile
        object.__setattr__(self, "profiles", tuple(self.profiles))
        object.__setattr__(self, "profiles_by_id", MappingProxyType(by_id))

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, object]]) -> "ArmorProfileCatalog":
        profiles = tuple(ArmorProfile.from_dict(record) for record in records)
        return cls(profiles=profiles)

    @classmethod
    def from_json(cls, path: str | Path) -> "ArmorProfileCatalog":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise WeaponProfileConfigurationError("Katalog profili pancerzy musi być listą.")
        records: list[Mapping[str, object]] = []
        for entry in raw:
            if not isinstance(entry, Mapping):
                raise WeaponProfileConfigurationError("Każdy profil pancerza musi być obiektem JSON.")
            records.append(entry)
        return cls.from_records(records)

    def __iter__(self) -> Iterator[ArmorProfile]:
        return iter(self.profiles)

    def get(self, profile_id: str | None) -> ArmorProfile | None:
        if profile_id is None:
            return None
        return self.profiles_by_id.get(_fold(profile_id))

    def resolve(self, armor: "Item | None") -> ArmorProfile | None:
        if armor is None or getattr(armor, "item_type", None) != "armor" or getattr(armor, "durability", 0) <= 0:
            return None
        profile_id = getattr(armor, "armor_profile_id", None)
        if profile_id is None:
            return self.legacy_profile
        profile = self.get(profile_id)
        if profile is None:
            warnings.warn(
                f"Nieznany profil pancerza {profile_id} dla przedmiotu {getattr(armor, 'id', '?')}. Użyto profilu legacy.",
                stacklevel=2,
            )
            return self.legacy_profile
        return profile


@dataclass(frozen=True, slots=True)
class ShieldProfileCatalog:
    profiles: tuple[ShieldProfile, ...]
    legacy_profile: ShieldProfile = field(default_factory=lambda: ShieldProfile("legacy_shield", "legacy shield", legacy=True), repr=False, compare=False)
    profiles_by_id: Mapping[str, ShieldProfile] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        by_id: dict[str, ShieldProfile] = {}
        for profile in self.profiles:
            key = _fold(profile.id)
            if key in by_id:
                raise WeaponProfileConfigurationError(f"Zduplikowany identyfikator profilu tarczy: {profile.id}")
            by_id[key] = profile
        object.__setattr__(self, "profiles", tuple(self.profiles))
        object.__setattr__(self, "profiles_by_id", MappingProxyType(by_id))

    @classmethod
    def from_records(cls, records: Sequence[Mapping[str, object]]) -> "ShieldProfileCatalog":
        profiles = tuple(ShieldProfile.from_dict(record) for record in records)
        return cls(profiles=profiles)

    @classmethod
    def from_json(cls, path: str | Path) -> "ShieldProfileCatalog":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise WeaponProfileConfigurationError("Katalog profili tarcz musi być listą.")
        records: list[Mapping[str, object]] = []
        for entry in raw:
            if not isinstance(entry, Mapping):
                raise WeaponProfileConfigurationError("Każdy profil tarczy musi być obiektem JSON.")
            records.append(entry)
        return cls.from_records(records)

    def __iter__(self) -> Iterator[ShieldProfile]:
        return iter(self.profiles)

    def get(self, profile_id: str | None) -> ShieldProfile | None:
        if profile_id is None:
            return None
        return self.profiles_by_id.get(_fold(profile_id))

    def resolve(self, shield: "Item | None") -> ShieldProfile | None:
        if shield is None or getattr(shield, "item_type", None) != "shield" or getattr(shield, "durability", 0) <= 0:
            return None
        profile_id = getattr(shield, "shield_profile_id", None)
        if profile_id is None:
            return self.legacy_profile
        profile = self.get(profile_id)
        if profile is None:
            warnings.warn(
                f"Nieznany profil tarczy {profile_id} dla przedmiotu {getattr(shield, 'id', '?')}. Użyto profilu legacy.",
                stacklevel=2,
            )
            return self.legacy_profile
        return profile


def weapon_profile_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "weapon_profiles.json"


def armor_profile_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "armor_profiles.json"


def shield_profile_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "shield_profiles.json"


@lru_cache(maxsize=1)
def load_default_weapon_profile_catalog() -> WeaponProfileCatalog:
    return WeaponProfileCatalog.from_json(weapon_profile_catalog_path())


@lru_cache(maxsize=1)
def load_default_armor_profile_catalog() -> ArmorProfileCatalog:
    return ArmorProfileCatalog.from_json(armor_profile_catalog_path())


@lru_cache(maxsize=1)
def load_default_shield_profile_catalog() -> ShieldProfileCatalog:
    return ShieldProfileCatalog.from_json(shield_profile_catalog_path())


def resolve_weapon_profile(weapon: "Item | None", catalog: WeaponProfileCatalog | None = None) -> WeaponProfile | None:
    active_catalog = catalog or load_default_weapon_profile_catalog()
    return active_catalog.resolve(weapon)


def snapshot_weapon_profile(weapon: "Item | None", catalog: WeaponProfileCatalog | None = None) -> WeaponProfileSnapshot:
    active_catalog = catalog or load_default_weapon_profile_catalog()
    return active_catalog.snapshot(weapon)


def resolve_armor_profile(armor: "Item | None", catalog: ArmorProfileCatalog | None = None) -> ArmorProfile | None:
    active_catalog = catalog or load_default_armor_profile_catalog()
    return active_catalog.resolve(armor)


def resolve_shield_profile(shield: "Item | None", catalog: ShieldProfileCatalog | None = None) -> ShieldProfile | None:
    active_catalog = catalog or load_default_shield_profile_catalog()
    return active_catalog.resolve(shield)


def active_combat_weapon_and_shield(character: "Character", catalog: WeaponProfileCatalog | None = None) -> tuple["Item | None", "Item | None", WeaponProfile | None]:
    active_catalog = catalog or load_default_weapon_profile_catalog()
    weapon = character.weapon()
    shield = character.shield()
    profile = active_catalog.resolve(weapon)
    if shield is not None and profile is not None and not profile.legacy and profile.hand_requirement == HandRequirement.TWO_HANDED:
        warnings.warn(
            f"Postać {character.username} ma broń dwuręczną {weapon.id if weapon is not None else '?'} i tarczę. Tarcza zostaje pominięta w walce.",
            stacklevel=2,
        )
        shield = None
    return weapon, shield, profile
