from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from astergard.characters.models import Character


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).casefold().strip()


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


def _string_values(values: object) -> tuple[str, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return ()
    return tuple(str(value).strip() for value in values if isinstance(value, str) and str(value).strip())


def _dict_values(values: object) -> dict[str, Any]:
    return dict(values) if isinstance(values, Mapping) else {}


def _optional_text_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int_value(value: object, default: int = 0) -> int:
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


def _optional_int_value(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return int(text)
    return None


class CareerError(ValueError):
    pass


class CareerConfigurationError(CareerError):
    pass


class CareerLookupError(CareerError):
    pass


class CareerJoinError(CareerError):
    pass


@dataclass(frozen=True, slots=True)
class CareerDefinition:
    id: str
    name: str
    description: str
    organizations: tuple[str, ...] = ()
    allowed_schools: tuple[str, ...] = ()
    starting_benefits: tuple[str, ...] = ()
    advancement_path: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("CareerDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("CareerDefinition.name nie może być puste.")
        object.__setattr__(self, "organizations", _normalize_sequence(self.organizations))
        object.__setattr__(self, "allowed_schools", _normalize_sequence(self.allowed_schools))
        object.__setattr__(self, "starting_benefits", _normalize_sequence(self.starting_benefits))
        object.__setattr__(self, "advancement_path", _normalize_sequence(self.advancement_path))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "organizations": list(self.organizations),
            "allowed_schools": list(self.allowed_schools),
            "starting_benefits": list(self.starting_benefits),
            "advancement_path": list(self.advancement_path),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CareerDefinition":
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            organizations=_string_values(data.get("organizations", [])),
            allowed_schools=_string_values(data.get("allowed_schools", [])),
            starting_benefits=_string_values(data.get("starting_benefits", [])),
            advancement_path=_string_values(data.get("advancement_path", [])),
        )


@dataclass(frozen=True, slots=True)
class OrganizationDefinition:
    id: str
    name: str
    description: str
    career_id: str
    schools: tuple[str, ...] = ()
    trainers: tuple[str, ...] = ()
    reputation_rules: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("OrganizationDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("OrganizationDefinition.name nie może być puste.")
        if not self.career_id.strip():
            raise ValueError("OrganizationDefinition.career_id nie może być puste.")
        object.__setattr__(self, "schools", _normalize_sequence(self.schools))
        object.__setattr__(self, "trainers", _normalize_sequence(self.trainers))
        object.__setattr__(self, "reputation_rules", dict(self.reputation_rules))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "career_id": self.career_id,
            "schools": list(self.schools),
            "trainers": list(self.trainers),
            "reputation_rules": dict(self.reputation_rules),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "OrganizationDefinition":
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            career_id=str(data.get("career_id", "")).strip(),
            schools=_string_values(data.get("schools", [])),
            trainers=_string_values(data.get("trainers", [])),
            reputation_rules=_dict_values(data.get("reputation_rules", {})),
        )


@dataclass(frozen=True, slots=True)
class SchoolDefinition:
    id: str
    name: str
    description: str
    organization: str
    techniques: tuple[str, ...] = ()
    bonuses: dict[str, Any] = field(default_factory=dict)
    masters: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("SchoolDefinition.id nie może być pusty.")
        if not self.name.strip():
            raise ValueError("SchoolDefinition.name nie może być puste.")
        if not self.organization.strip():
            raise ValueError("SchoolDefinition.organization nie może być puste.")
        object.__setattr__(self, "techniques", _normalize_sequence(self.techniques))
        object.__setattr__(self, "bonuses", dict(self.bonuses))
        object.__setattr__(self, "masters", _normalize_sequence(self.masters))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "organization": self.organization,
            "techniques": list(self.techniques),
            "bonuses": dict(self.bonuses),
            "masters": list(self.masters),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "SchoolDefinition":
        return cls(
            id=str(data.get("id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            organization=str(data.get("organization", "")).strip(),
            techniques=_string_values(data.get("techniques", [])),
            bonuses=_dict_values(data.get("bonuses", {})),
            masters=_string_values(data.get("masters", [])),
        )


@dataclass(frozen=True, slots=True)
class CareerUserProfile:
    career_id: str | None = None
    organization_id: str | None = None
    school_id: str | None = None
    organization_rank: int | None = None

    def __post_init__(self) -> None:
        if self.career_id is not None:
            object.__setattr__(self, "career_id", str(self.career_id).strip() or None)
        if self.organization_id is not None:
            object.__setattr__(self, "organization_id", str(self.organization_id).strip() or None)
        if self.school_id is not None:
            object.__setattr__(self, "school_id", str(self.school_id).strip() or None)
        object.__setattr__(self, "organization_rank", _optional_int_value(self.organization_rank))

    def to_dict(self) -> dict[str, Any]:
        return {
            "career_id": self.career_id,
            "organization_id": self.organization_id,
            "school_id": self.school_id,
            "organization_rank": self.organization_rank,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CareerUserProfile":
        return cls(
            career_id=_optional_text_value(data.get("career_id")),
            organization_id=_optional_text_value(data.get("organization_id")),
            school_id=_optional_text_value(data.get("school_id")),
            organization_rank=_optional_int_value(data.get("organization_rank", data.get("awans"))),
        )


@dataclass(frozen=True, slots=True)
class CareerJoinResult:
    allowed: bool
    reason_code: str
    message: str


@dataclass(frozen=True, slots=True)
class CareerIntegrityResult:
    valid: bool
    reason_code: str
    message: str


CAREERS: tuple[CareerDefinition, ...] = (
    CareerDefinition(
        id="zolnierz",
        name="Żołnierz",
        description="Służy w szyku, w marszu i w miejscach, gdzie obowiązuje porządek narzucony siłą.",
        organizations=("legion", "straz_miejska", "kompania_najemna"),
        allowed_schools=("szkola_legionu", "szkola_strazy", "szkola_najemna"),
        starting_benefits=("dyscyplina", "wytrzymałość"),
        advancement_path=("szeregowy", "weteran", "oficer"),
    ),
    CareerDefinition(
        id="lowca",
        name="Łowca",
        description="Żyje z tropu, cierpliwości i umiejętności czytania terenu zanim zrobi to zwierzyna.",
        organizations=("bractwo_tropicieli",),
        allowed_schools=("szkola_tropicieli",),
        starting_benefits=("tropienie", "orientacja"),
        advancement_path=("praktykant", "tropiciel", "mistrz_pola"),
    ),
    CareerDefinition(
        id="kupiec",
        name="Kupiec",
        description="Handluje towarem, czasem i zaufaniem, a jego przewagą jest sieć kontaktów.",
        organizations=("gildia_kupcow",),
        allowed_schools=("szkola_gildii",),
        starting_benefits=("targowanie", "orientacja"),
        advancement_path=("pomocnik", "czeladnik", "partner_handlowy"),
    ),
    CareerDefinition(
        id="rzemieslnik",
        name="Rzemieślnik",
        description="Buduje, naprawia i doprowadza przedmioty do stanu, w którym znowu da się ich używać.",
        organizations=("cech_kowali",),
        allowed_schools=("szkola_kuzni",),
        starting_benefits=("kowalstwo", "garbarstwo"),
        advancement_path=("uczen", "czeladnik", "mistrz"),
    ),
    CareerDefinition(
        id="rzezimieszek",
        name="Rzezimieszek",
        description="Trzyma się cieniu, wybiera łatwiejsze drogi i unika uwagi, dopóki nie nadejdzie właściwa chwila.",
        organizations=("cienie",),
        allowed_schools=("szkola_cieni",),
        starting_benefits=("skradanie", "otwieranie_zamkow"),
        advancement_path=("pomocnik", "wylacznik", "cien"),
    ),
)

ORGANIZATIONS: tuple[OrganizationDefinition, ...] = (
    OrganizationDefinition(
        id="legion",
        name="Legion",
        description="Trzyma żołnierzy w jednym porządku i uczy walki w szeregu.",
        career_id="zolnierz",
        schools=("szkola_legionu",),
        trainers=("master_sword", "master_halberd"),
        reputation_rules={},
    ),
    OrganizationDefinition(
        id="straz_miejska",
        name="Straż Miejska",
        description="Pilnuje porządku w mieście i szkoli ludzi do pracy przy bramach, patrolach i zatrzymaniach.",
        career_id="zolnierz",
        schools=("szkola_strazy",),
        trainers=("master_sword",),
        reputation_rules={},
    ),
    OrganizationDefinition(
        id="kompania_najemna",
        name="Kompania Najemna",
        description="Sprzedaje miecz i dyscyplinę tam, gdzie ktoś płaci lepiej niż reszta.",
        career_id="zolnierz",
        schools=("szkola_najemna",),
        trainers=("master_halberd",),
        reputation_rules={},
    ),
    OrganizationDefinition(
        id="bractwo_tropicieli",
        name="Bractwo Tropicieli",
        description="Zbiera łowców, przewodników i tropicieli pracujących w terenie.",
        career_id="lowca",
        schools=("szkola_tropicieli",),
        trainers=(),
        reputation_rules={},
    ),
    OrganizationDefinition(
        id="gildia_kupcow",
        name="Gildia Kupców",
        description="Łączy handel, składy i ludzi, którzy pilnują przepływu towaru.",
        career_id="kupiec",
        schools=("szkola_gildii",),
        trainers=(),
        reputation_rules={},
    ),
    OrganizationDefinition(
        id="cech_kowali",
        name="Cech Kowali",
        description="Porządkuje pracę przy ogniu, metalu i narzędziach.",
        career_id="rzemieslnik",
        schools=("szkola_kuzni",),
        trainers=("master_hammer",),
        reputation_rules={},
    ),
    OrganizationDefinition(
        id="cienie",
        name="Cienie",
        description="Luźna sieć ludzi, którzy wolą nie zostawiać po sobie wyraźnych śladów.",
        career_id="rzezimieszek",
        schools=("szkola_cieni",),
        trainers=(),
        reputation_rules={},
    ),
)

SCHOOLS: tuple[SchoolDefinition, ...] = (
    SchoolDefinition(
        id="szkola_legionu",
        name="Szkoła Legionu",
        description="Uczy walki w szyku i współpracy z linią towarzyszy.",
        organization="legion",
        techniques=("counterattack",),
        bonuses={},
        masters=("master_sword",),
    ),
    SchoolDefinition(
        id="szkola_strazy",
        name="Szkoła Straży",
        description="Skupia się na patrolu, kontroli przejść i technikach porządkowych.",
        organization="straz_miejska",
        techniques=("riposte", "disarm"),
        bonuses={},
        masters=("master_sword",),
    ),
    SchoolDefinition(
        id="szkola_najemna",
        name="Szkoła Kompanii",
        description="Przygotowuje do pracy w ruchu i do broni drzewcowej używanej w polu.",
        organization="kompania_najemna",
        techniques=("guard_break", "armor_pierce"),
        bonuses={},
        masters=("master_halberd",),
    ),
    SchoolDefinition(
        id="szkola_tropicieli",
        name="Szkoła Tropicieli",
        description="Uczy czytania śladów, podejścia i pracy w terenie otwartym.",
        organization="bractwo_tropicieli",
        techniques=(),
        bonuses={},
        masters=(),
    ),
    SchoolDefinition(
        id="szkola_gildii",
        name="Szkoła Gildii",
        description="Przygotowuje do negocjacji, liczenia i pracy przy wymianie towaru.",
        organization="gildia_kupcow",
        techniques=(),
        bonuses={},
        masters=(),
    ),
    SchoolDefinition(
        id="szkola_kuzni",
        name="Szkoła Kuźni",
        description="Łączy pracę przy ogniu, metalu i ciężkim narzędziu.",
        organization="cech_kowali",
        techniques=("stun",),
        bonuses={},
        masters=("master_hammer",),
    ),
    SchoolDefinition(
        id="szkola_cieni",
        name="Szkoła Cieni",
        description="Uczy cichego poruszania się, wyboru wejścia i pracy bez świadków.",
        organization="cienie",
        techniques=(),
        bonuses={},
        masters=(),
    ),
)


_CAREER_BY_ID = {_fold(value): entry for entry in CAREERS for value in (entry.id, entry.name)}
_ORGANIZATION_BY_ID = {_fold(value): entry for entry in ORGANIZATIONS for value in (entry.id, entry.name)}
_SCHOOL_BY_ID = {_fold(value): entry for entry in SCHOOLS for value in (entry.id, entry.name)}


def all_careers() -> list[CareerDefinition]:
    return list(CAREERS)


def all_organizations() -> list[OrganizationDefinition]:
    return list(ORGANIZATIONS)


def all_schools() -> list[SchoolDefinition]:
    return list(SCHOOLS)


def resolve_career(value: str) -> CareerDefinition:
    definition = _CAREER_BY_ID.get(_fold(value))
    if isinstance(definition, CareerDefinition):
        return definition
    raise CareerLookupError(f"Nieznane powołanie: {value}")


def resolve_organization(value: str) -> OrganizationDefinition:
    definition = _ORGANIZATION_BY_ID.get(_fold(value))
    if isinstance(definition, OrganizationDefinition):
        return definition
    raise CareerLookupError(f"Nieznana organizacja: {value}")


def resolve_school(value: str) -> SchoolDefinition:
    definition = _SCHOOL_BY_ID.get(_fold(value))
    if isinstance(definition, SchoolDefinition):
        return definition
    raise CareerLookupError(f"Nieznana szkoła: {value}")


def _profile_matches(profile: CareerUserProfile, value: str | None) -> bool:
    if value is None:
        return False
    return _fold(value) == _fold(profile.career_id or "")


def validate_career_integrity(profile: CareerUserProfile) -> CareerIntegrityResult:
    if profile.career_id is None:
        if profile.organization_id is not None:
            return CareerIntegrityResult(False, "ORGANIZATION_WITHOUT_CAREER", "Nie można należeć do organizacji bez powołania.")
        if profile.school_id is not None:
            return CareerIntegrityResult(False, "SCHOOL_WITHOUT_CAREER", "Nie można należeć do szkoły bez powołania.")
        if profile.organization_rank is not None:
            return CareerIntegrityResult(False, "RANK_WITHOUT_CAREER", "Nie można mieć rangi bez powołania.")
        return CareerIntegrityResult(True, "OK", "Stan kariery jest poprawny.")

    try:
        career = resolve_career(profile.career_id)
    except CareerLookupError as exc:
        return CareerIntegrityResult(False, "UNKNOWN_CAREER", str(exc))

    if profile.organization_id is not None:
        try:
            organization = resolve_organization(profile.organization_id)
        except CareerLookupError as exc:
            return CareerIntegrityResult(False, "UNKNOWN_ORGANIZATION", str(exc))
        if _fold(organization.career_id) != _fold(career.id):
            return CareerIntegrityResult(False, "CAREER_MISMATCH", "Organizacja nie należy do wybranego powołania.")
        if profile.school_id is not None:
            try:
                school = resolve_school(profile.school_id)
            except CareerLookupError as exc:
                return CareerIntegrityResult(False, "UNKNOWN_SCHOOL", str(exc))
            if _fold(school.organization) != _fold(organization.id):
                return CareerIntegrityResult(False, "SCHOOL_MISMATCH", "Szkoła nie należy do wybranej organizacji.")
    elif profile.school_id is not None:
        return CareerIntegrityResult(False, "SCHOOL_WITHOUT_ORGANIZATION", "Nie można należeć do szkoły bez organizacji.")

    if profile.organization_rank is not None and profile.organization_id is None:
        return CareerIntegrityResult(False, "RANK_WITHOUT_ORGANIZATION", "Nie można mieć rangi bez organizacji.")

    return CareerIntegrityResult(True, "OK", "Stan kariery jest poprawny.")


def can_join_career(profile: CareerUserProfile, career_id: str) -> CareerJoinResult:
    integrity = validate_career_integrity(profile)
    if not integrity.valid:
        return CareerJoinResult(False, integrity.reason_code, integrity.message)
    try:
        career = resolve_career(career_id)
    except CareerLookupError as exc:
        return CareerJoinResult(False, "CAREER_NOT_FOUND", str(exc))
    if _profile_matches(profile, career.id):
        return CareerJoinResult(False, "ALREADY_IN_CAREER", "Postać już ma to powołanie.")
    if profile.career_id:
        return CareerJoinResult(False, "CAREER_ALREADY_SELECTED", "Postać ma już wybrane powołanie.")
    return CareerJoinResult(True, "OK", "Powołanie może zostać wybrane.")


def can_join_organization(profile: CareerUserProfile, organization_id: str) -> CareerJoinResult:
    integrity = validate_career_integrity(profile)
    if not integrity.valid:
        return CareerJoinResult(False, integrity.reason_code, integrity.message)
    try:
        organization = resolve_organization(organization_id)
    except CareerLookupError as exc:
        return CareerJoinResult(False, "ORGANIZATION_NOT_FOUND", str(exc))
    if not profile.career_id:
        return CareerJoinResult(False, "REQUIRES_CAREER_FIRST", "Najpierw trzeba wybrać powołanie.")
    if _fold(profile.career_id) != _fold(organization.career_id):
        return CareerJoinResult(False, "CAREER_MISMATCH", "Ta organizacja nie należy do wybranego powołania.")
    if _profile_matches(profile, organization.id):
        return CareerJoinResult(False, "ALREADY_IN_ORGANIZATION", "Postać już należy do tej organizacji.")
    return CareerJoinResult(True, "OK", "Organizacja może zostać wybrana.")


def can_join_school(profile: CareerUserProfile, school_id: str) -> CareerJoinResult:
    integrity = validate_career_integrity(profile)
    if not integrity.valid:
        return CareerJoinResult(False, integrity.reason_code, integrity.message)
    try:
        school = resolve_school(school_id)
    except CareerLookupError as exc:
        return CareerJoinResult(False, "SCHOOL_NOT_FOUND", str(exc))
    if not profile.career_id:
        return CareerJoinResult(False, "REQUIRES_CAREER_FIRST", "Najpierw trzeba wybrać powołanie.")
    if not profile.organization_id:
        return CareerJoinResult(False, "REQUIRES_ORGANIZATION_FIRST", "Najpierw trzeba wybrać organizację.")
    organization = resolve_organization(profile.organization_id)
    if _fold(organization.id) != _fold(school.organization):
        return CareerJoinResult(False, "ORGANIZATION_MISMATCH", "Ta szkoła nie należy do wybranej organizacji.")
    if _profile_matches(profile, school.id):
        return CareerJoinResult(False, "ALREADY_IN_SCHOOL", "Postać już należy do tej szkoły.")
    return CareerJoinResult(True, "OK", "Szkoła może zostać wybrana.")


def career_profile_from_character(character: "Character") -> CareerUserProfile:
    return CareerUserProfile(
        career_id=character.career_id or None,
        organization_id=character.organization_id or None,
        school_id=character.school_id or None,
        organization_rank=character.organization_rank,
    )


def join_career(character: "Character", career_id: str) -> CareerJoinResult:
    result = can_join_career(career_profile_from_character(character), career_id)
    if not result.allowed:
        return result
    character.career_id = resolve_career(career_id).id
    character.organization_id = None
    character.school_id = None
    character.organization_rank = None
    return result


def leave_career(character: "Character") -> CareerJoinResult:
    character.career_id = None
    character.organization_id = None
    character.school_id = None
    character.organization_rank = None
    return CareerJoinResult(True, "OK", "Powołanie zostało opuszczone.")


def join_organization(character: "Character", organization_id: str) -> CareerJoinResult:
    result = can_join_organization(career_profile_from_character(character), organization_id)
    if not result.allowed:
        return result
    organization = resolve_organization(organization_id)
    previous_organization = character.organization_id
    character.organization_id = organization.id
    if previous_organization is not None and _fold(previous_organization) != _fold(organization.id):
        character.school_id = None
        character.organization_rank = None
    elif character.school_id is not None:
        try:
            school = resolve_school(character.school_id)
        except CareerLookupError:
            character.school_id = None
        else:
            if _fold(school.organization) != _fold(organization.id):
                character.school_id = None
                character.organization_rank = None
    return result


def leave_organization(character: "Character") -> CareerJoinResult:
    character.organization_id = None
    character.school_id = None
    character.organization_rank = None
    return CareerJoinResult(True, "OK", "Organizacja została opuszczona.")


def join_school(character: "Character", school_id: str) -> CareerJoinResult:
    result = can_join_school(career_profile_from_character(character), school_id)
    if not result.allowed:
        return result
    character.school_id = resolve_school(school_id).id
    return result


def leave_school(character: "Character") -> CareerJoinResult:
    character.school_id = None
    return CareerJoinResult(True, "OK", "Szkoła została opuszczona.")
