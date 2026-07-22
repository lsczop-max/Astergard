from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from astergard.characters.appearance import (
    CharacterAppearanceProfile,
    gender_label,
    render_appearance_lines,
    normalize_gender_id,
)
from astergard.characters.models import Character
from astergard.characters.professions import (
    ProfessionSelection,
    build_selection,
    migrate_legacy_profession_selection,
    resolve_profession,
)
from astergard.items.models import Item, starter_items
from astergard.world.manager import STARTING_ROOM_ID


class CharacterCreationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class OriginDefinition:
    key: str
    label: str
    starting_reputation: int
    inventory_factory: Callable[[], list[Item]]


@dataclass(frozen=True, slots=True)
class ChildhoodDefinition:
    key: str
    label: str
    description: str
    skill_bonuses: dict[str, int]


@dataclass(frozen=True, slots=True)
class BirthRegionDefinition:
    key: str
    label: str
    description: str


def _make_item(
    name: str,
    description: str,
    weight: float,
    value: int,
    vnum: str,
    item_type: str = "misc",
    slot: str | None = None,
) -> Item:
    return Item(name, description, weight, value, vnum, item_type, slot)


def _astergard_burgher_items() -> list[Item]:
    return [
        _make_item("mieszczański sygnet", "Niewielki sygnet z herbem miejskiego cechu.", 0.1, 8, "origin_astergard_ring", "tool"),
    ]


def _podgrodzie_peasant_items() -> list[Item]:
    return [
        _make_item("drewniane chodaki", "Proste chodaki do pracy w błocie i kurzu.", 0.8, 3, "origin_podgrodzie_clogs", "tool"),
    ]


def _road_child_items() -> list[Item]:
    return [
        _make_item("gwizdek drogowy", "Porysowany gwizdek do wołania ludzi z traktu.", 0.1, 2, "origin_road_whistle", "tool"),
        _make_item("zawiniątko mapy", "Wysłużony zwój z odręcznymi znakami przy drogach.", 0.2, 3, "origin_road_map", "tool"),
    ]


def _apprentice_items() -> list[Item]:
    return [
        _make_item("skrzynka czeladnicza", "Mała skrzynka na najpotrzebniejsze narzędzia.", 1.0, 12, "origin_apprentice_box", "tool"),
    ]


def _former_guard_items() -> list[Item]:
    return [
        _make_item("znak służby", "Zdarty znak dawnej służby strażniczej.", 0.2, 6, "origin_guard_badge", "tool"),
        _make_item("pas patrolowy", "Stary pas używany podczas patroli.", 0.6, 5, "origin_guard_belt", "tool"),
    ]


def _river_fisher_items() -> list[Item]:
    return [
        _make_item("zestaw haczyków", "Pęk małych haczyków zawiniętych w płótno.", 0.1, 4, "origin_fisher_hooks", "tool"),
        _make_item("sznurek do sieci", "Krótki sznur do naprawy sieci i linek.", 0.2, 3, "origin_fisher_cord", "tool"),
    ]


def _wanderer_items() -> list[Item]:
    return [
        _make_item("łatany tobołek", "Mały tobołek na najpotrzebniejsze drobiazgi.", 0.7, 4, "origin_wanderer_bundle", "tool"),
    ]


ORIGIN_DEFINITIONS: dict[str, OriginDefinition] = {
    "mieszczanin_astergardu": OriginDefinition("mieszczanin_astergardu", "mieszczanin Astergardu", 25, _astergard_burgher_items),
    "chlop_z_podgrodzia": OriginDefinition("chlop_z_podgrodzia", "chłop z Podgrodzia", 5, _podgrodzie_peasant_items),
    "dziecko_traktu": OriginDefinition("dziecko_traktu", "dziecko traktu", -5, _road_child_items),
    "uczen_rzemieslnika": OriginDefinition("uczen_rzemieslnika", "uczeń rzemieślnika", 10, _apprentice_items),
    "byly_straznik": OriginDefinition("byly_straznik", "były strażnik", 20, _former_guard_items),
    "rybak_znad_rzeki": OriginDefinition("rybak_znad_rzeki", "rybak znad rzeki", 8, _river_fisher_items),
    "wloczega": OriginDefinition("wloczega", "włóczęga", -15, _wanderer_items),
}


CHILDHOOD_DEFINITIONS: dict[str, ChildhoodDefinition] = {
    "wies": ChildhoodDefinition(
        "wies",
        "wieś",
        "Prosty rytm pól, zwierząt i pór roku uczy cierpliwości oraz pracy bez świadków.",
        {"gotowanie": 1, "oprawianie": 1},
    ),
    "miasto": ChildhoodDefinition(
        "miasto",
        "miasto",
        "Zgiełk ulic, targów i cudzych spraw uczy szybkiego patrzenia i szybkiego mówienia.",
        {"handel": 1, "obserwacja": 1},
    ),
    "gory": ChildhoodDefinition(
        "gory",
        "góry",
        "Kamień, wiatr i strome ścieżki hartują ciało oraz uczą oszczędzać oddech.",
        {"przetrwanie": 1, "uniki": 1},
    ),
    "wybrzeze": ChildhoodDefinition(
        "wybrzeze",
        "wybrzeże",
        "Sól, mokry wiatr i zmienna woda zostawiają człowieka czujniejszym niż większość podróżnych.",
        {"obserwacja": 1, "handel": 1},
    ),
    "puszcza": ChildhoodDefinition(
        "puszcza",
        "puszcza",
        "Las uczy słuchać, czekać i nie ufać temu, czego nie widać między pniami.",
        {"obserwacja": 1, "oprawianie": 1},
    ),
    "pogranicze": ChildhoodDefinition(
        "pogranicze",
        "pogranicze",
        "Na skraju ziem człowiek wcześniej uczy się, kiedy patrzeć, a kiedy ustąpić miejsca.",
        {"dowodzenie": 1, "parowanie": 1},
    ),
    "swiatynia": ChildhoodDefinition(
        "swiatynia",
        "świątynia",
        "Cisza krużganków i rytm obrzędów zostawiają po sobie spokój oraz dyscyplinę.",
        {"morale": 1, "perswazja": 1},
    ),
    "twierdza": ChildhoodDefinition(
        "twierdza",
        "twierdza",
        "Mur, warta i rozkazy sprawiają, że człowiek wcześniej dojrzewa do odpowiedzialności.",
        {"parowanie": 1, "dowodzenie": 1},
    ),
}

BIRTH_REGION_DEFINITIONS: dict[str, BirthRegionDefinition] = {
    "astergard": BirthRegionDefinition("astergard", "Astergard", "Stare miasto, port i centrum wpływów, gdzie łatwo nauczyć się obcych zwyczajów."),
    "podgrodzie": BirthRegionDefinition("podgrodzie", "Podgrodzie", "Przedmieścia i pola wokół murów, bliżej błota, wozów i codziennej roboty."),
    "trakt": BirthRegionDefinition("trakt", "Trakt", "Droga, karczmy i postoje ludzi w ruchu, gdzie domem bywa następny dzień marszu."),
    "haldun": BirthRegionDefinition("haldun", "Haldun", "Wieś na szlaku, gdzie życie miesza pracę pól z handlem i pogłoską."),
    "dungrim": BirthRegionDefinition("dungrim", "Dungrim", "Forteczna osada na skraju gór i przełęczy, z rytmem służby i karawany."),
    "puszcza": BirthRegionDefinition("puszcza", "Puszcza", "Las, w którym człowiek wcześniej uczy się słuchać niż mówić."),
    "bagna": BirthRegionDefinition("bagna", "Bagna", "Mokradła, torf i ścieżki, które zmieniają się szybciej niż ludzkie plany."),
    "gory": BirthRegionDefinition("gory", "Góry", "Kamień, chłód i wysokie ścieżki, gdzie każdy krok musi mieć sens."),
}

BIRTH_REGION_ALIASES: dict[str, str] = {
    "astergardu": "astergard",
    "w astergardzie": "astergard",
    "miasto": "astergard",
    "miejskie": "astergard",
    "podgrodzia": "podgrodzie",
    "przedmieście": "podgrodzie",
    "przedmiescie": "podgrodzie",
    "traktu": "trakt",
    "droga": "trakt",
    "szlak": "trakt",
    "na trakcie": "trakt",
    "haldunu": "haldun",
    "dungrimu": "dungrim",
    "puszczy": "puszcza",
    "bagn": "bagna",
    "bagien": "bagna",
    "gór": "gory",
    "gor": "gory",
}

CHILDHOOD_ALIASES: dict[str, str] = {
    "wies": "wies",
    "na wsi": "wies",
    "wiejskie": "wies",
    "miasto": "miasto",
    "w miescie": "miasto",
    "miejskie": "miasto",
    "gory": "gory",
    "w gorach": "gory",
    "gorskie": "gory",
    "wybrzeze": "wybrzeze",
    "nad morzem": "wybrzeze",
    "port": "wybrzeze",
    "puszcza": "puszcza",
    "w lesie": "puszcza",
    "lesne": "puszcza",
    "pogranicze": "pogranicze",
    "przy granicy": "pogranicze",
    "trakt": "pogranicze",
    "swiatynia": "swiatynia",
    "w swiatyni": "swiatynia",
    "klasztor": "swiatynia",
    "twierdza": "twierdza",
    "forteca": "twierdza",
    "garnizon": "twierdza",
}


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def origin_labels() -> list[str]:
    return [definition.label for definition in ORIGIN_DEFINITIONS.values()]


def _choice_prompt_text(title: str, question: str, definitions: Mapping[str, object]) -> str:
    lines = [f"{title}:"]
    for index, definition in enumerate(definitions.values(), start=1):
        label = getattr(definition, "label")
        description = getattr(definition, "description", "")
        if description:
            lines.append(f"{index}. {label} - {description}")
            continue
        starting_reputation = getattr(definition, "starting_reputation", None)
        if starting_reputation is not None:
            lines.append(f"{index}. {label} - startowa reputacja {starting_reputation}")
            continue
        lines.append(f"{index}. {label}")
    lines.append("")
    lines.append(f"{question} Wpisz numer albo nazwę.")
    return "\n".join(lines)


def birth_region_prompt_text() -> str:
    return _choice_prompt_text(
        "Region urodzenia",
        "Kronikarz przesuwa palcem po mapie.\n— Gdzie stawiałeś pierwsze kroki?",
        BIRTH_REGION_DEFINITIONS,
    )


def resolve_birth_region(value: str) -> BirthRegionDefinition:
    normalized = normalize_text(value).lower()
    if not normalized:
        raise CharacterCreationError("Region urodzenia nie może być pusty.")
    if normalized.isdigit():
        index = int(normalized) - 1
        definitions = list(BIRTH_REGION_DEFINITIONS.values())
        if 0 <= index < len(definitions):
            return definitions[index]
    alias = BIRTH_REGION_ALIASES.get(normalized)
    if alias is not None:
        return BIRTH_REGION_DEFINITIONS[alias]
    if normalized in BIRTH_REGION_DEFINITIONS:
        return BIRTH_REGION_DEFINITIONS[normalized]
    for definition in BIRTH_REGION_DEFINITIONS.values():
        if normalized == normalize_text(definition.label).lower():
            return definition
    raise CharacterCreationError("Nieznany region urodzenia.")


def origin_prompt_text() -> str:
    return _choice_prompt_text(
        "Pochodzenie",
        "Karczmarz opiera łokcie o stół.\n— Skąd przychodzisz?",
        ORIGIN_DEFINITIONS,
    )


def resolve_origin(value: str) -> OriginDefinition:
    normalized = normalize_text(value).lower()
    if not normalized:
        raise CharacterCreationError("Pochodzenie nie może być puste.")
    if normalized.isdigit():
        index = int(normalized) - 1
        definitions = list(ORIGIN_DEFINITIONS.values())
        if 0 <= index < len(definitions):
            return definitions[index]
    if normalized in ORIGIN_DEFINITIONS:
        return ORIGIN_DEFINITIONS[normalized]
    for definition in ORIGIN_DEFINITIONS.values():
        if normalized == normalize_text(definition.label).lower():
            return definition
    raise CharacterCreationError("Nieznane pochodzenie.")


def childhood_prompt_text() -> str:
    return _choice_prompt_text(
        "Dzieciństwo",
        "Kronikarz przesuwa palcem po otwartej księdze.\n— Gdzie dorastałeś?",
        CHILDHOOD_DEFINITIONS,
    )


def resolve_childhood(value: str) -> ChildhoodDefinition:
    normalized = normalize_text(value).lower()
    if not normalized:
        raise CharacterCreationError("Dzieciństwo nie może być puste.")
    if normalized.isdigit():
        index = int(normalized) - 1
        definitions = list(CHILDHOOD_DEFINITIONS.values())
        if 0 <= index < len(definitions):
            return definitions[index]
    alias = CHILDHOOD_ALIASES.get(normalized)
    if alias is not None:
        return CHILDHOOD_DEFINITIONS[alias]
    for definition in CHILDHOOD_DEFINITIONS.values():
        if normalized in {definition.key, normalize_text(definition.label).lower()}:
            return definition
    raise CharacterCreationError("Nieznane dzieciństwo.")


def _resolve_or_keep_label(value: str, resolver) -> str:
    try:
        return resolver(value).label
    except CharacterCreationError:
        normalized = normalize_text(value)
        if not normalized:
            raise
        return normalized


def validate_text(label: str, value: str, *, min_length: int = 1, max_length: int = 200) -> str:
    normalized = normalize_text(value)
    if len(normalized) < min_length:
        raise CharacterCreationError(f"{label} nie może być puste.")
    if len(normalized) > max_length:
        raise CharacterCreationError(f"{label} jest zbyt długie.")
    return normalized


def validate_age(value: str | int) -> int:
    normalized = str(value).strip() if isinstance(value, int) else normalize_text(value)
    try:
        age = int(normalized)
    except ValueError as exc:
        raise CharacterCreationError("Wiek musi być liczbą całkowitą.") from exc
    if age < 12 or age > 90:
        raise CharacterCreationError("Wiek musi mieścić się w zakresie 12-90.")
    return age


@dataclass(frozen=True, slots=True)
class CharacterCreationProfile:
    name: str
    gender_id: str
    age: int
    origin: str
    childhood: str
    birth_region: str
    main_profession: str
    secondary_profession: str
    appearance: str
    appearance_profile: CharacterAppearanceProfile | None = None

    @property
    def gender_description(self) -> str:
        return gender_label(self.gender_id)

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "name": self.name,
            "gender_id": self.gender_id,
            "gender_description": self.gender_description,
            "age": self.age,
            "origin": self.origin,
            "childhood": self.childhood,
            "birth_region": self.birth_region,
            "main_profession": self.main_profession,
            "secondary_profession": self.secondary_profession,
            "appearance": self.appearance,
        }
        if self.appearance_profile is not None:
            data["appearance_profile"] = self.appearance_profile.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CharacterCreationProfile":
        raw_age = data.get("age", 0)
        age_value = raw_age if isinstance(raw_age, (str, int)) else 0
        gender_id = normalize_gender_id(data.get("gender_id", data.get("gender_description", "")))
        main_raw = str(data.get("main_profession", "")).strip()
        secondary_raw = str(data.get("secondary_profession", "")).strip()
        migrated_main, migrated_secondary = migrate_legacy_profession_selection(main_raw, secondary_raw or None)
        selection = build_selection(migrated_main, migrated_secondary or None) if migrated_main else ProfessionSelection("", "")
        appearance_profile_raw = data.get("appearance_profile")
        appearance_profile = None
        if isinstance(appearance_profile_raw, Mapping):
            cleaned_profile = dict(appearance_profile_raw)
            cleaned_profile.pop("gender", None)
            try:
                appearance_profile = CharacterAppearanceProfile.from_dict(cleaned_profile)
            except ValueError:
                appearance_profile = None
            else:
                if gender_id == "f" and appearance_profile.beard != "brak":
                    appearance_profile = None
        appearance_text = str(data.get("appearance", "")).strip()
        if not appearance_text and appearance_profile is not None and gender_id in {"m", "f"}:
            appearance_text = "\n".join(render_appearance_lines(appearance_profile, gender_id=gender_id))
        return cls(
            name=validate_text("Imię", str(data.get("name", "")), min_length=2, max_length=32),
            gender_id=gender_id,
            age=validate_age(age_value),
            origin=resolve_origin(str(data.get("origin", ""))).key,
            childhood=resolve_childhood(str(data.get("childhood", ""))).key if str(data.get("childhood", "")).strip() else "",
            birth_region=_resolve_or_keep_label(str(data.get("birth_region", "")), resolve_birth_region),
            main_profession=selection.main_profession,
            secondary_profession=selection.secondary_profession,
            appearance=validate_text("Wygląd", appearance_text, min_length=2, max_length=800),
            appearance_profile=appearance_profile,
        )

    @classmethod
    def build(
        cls,
        *,
        name: str,
        gender_id: str,
        age: str | int,
        origin: str,
        birth_region: str,
        main_profession: str,
        secondary_profession: str | None,
        appearance: str | None = None,
        appearance_profile: CharacterAppearanceProfile | None = None,
        childhood: str = "",
    ) -> "CharacterCreationProfile":
        resolved_origin = resolve_origin(origin)
        selection = build_selection(main_profession, secondary_profession)
        childhood_definition = resolve_childhood(childhood) if normalize_text(childhood) else None
        resolved_gender = normalize_gender_id(gender_id)
        if resolved_gender not in {"m", "f"}:
            raise CharacterCreationError("Płeć nie może być pusta.")
        if appearance_profile is not None:
            rendered_appearance = "\n".join(render_appearance_lines(appearance_profile, gender_id=resolved_gender))
        else:
            rendered_appearance = validate_text("Wygląd", appearance or "", min_length=2, max_length=800)
        return cls(
            name=validate_text("Imię", name, min_length=2, max_length=32),
            gender_id=resolved_gender,
            age=validate_age(age),
            origin=resolved_origin.key,
            childhood=childhood_definition.key if childhood_definition is not None else "",
            birth_region=resolve_birth_region(birth_region).label,
            main_profession=selection.main_profession,
            secondary_profession=selection.secondary_profession,
            appearance=rendered_appearance,
            appearance_profile=appearance_profile,
        )

    def origin_definition(self) -> OriginDefinition:
        return resolve_origin(self.origin)

    def profession_selection(self) -> ProfessionSelection:
        if not self.main_profession:
            return ProfessionSelection("", "")
        return build_selection(self.main_profession, self.secondary_profession or None)

    def childhood_definition(self) -> ChildhoodDefinition | None:
        if not self.childhood:
            return None
        return CHILDHOOD_DEFINITIONS.get(self.childhood)

    def _apply_profession(self, char: Character, selection: ProfessionSelection) -> None:
        for profession_key in [selection.main_profession, selection.secondary_profession or ""]:
            if not profession_key:
                continue
            definition = resolve_profession(profession_key)
            for skill, bonus in definition.skill_bonuses.items():
                char.skills.grant_starting_bonus(skill, bonus)
            for item in definition.inventory_items():
                char.inventory.append(item)
            for slot, item in definition.equipment_items().items():
                matched = next((candidate for candidate in char.inventory if candidate.vnum == item.vnum), None)
                equipped = matched if matched is not None else item
                if matched is not None:
                    char.inventory.remove(matched)
                char.equipment[slot] = equipped
            if definition.combat_style:
                char.combat_style = definition.combat_style
            if char.history:
                char.history = f"{char.history}\n"
            if definition.kind == "main":
                char.history += f"Profesja główna: {definition.label}."
            elif definition.kind == "additional":
                char.history += f"Profesja dodatkowa: {definition.label}."

    def create_character(self, username: str) -> Character:
        origin = self.origin_definition()
        profession_selection = self.profession_selection()
        childhood = self.childhood_definition()
        char = Character(username=username, room_id=STARTING_ROOM_ID)
        char.name = self.name
        char.gender_id = self.gender_id
        char.age = self.age
        char.origin = origin.key
        char.childhood = childhood.key if childhood is not None else ""
        char.birth_region = self.birth_region
        char.main_profession = profession_selection.main_profession
        char.secondary_profession = profession_selection.secondary_profession
        char.appearance = self.appearance
        char.appearance_profile = self.appearance_profile
        char.starting_reputation = origin.starting_reputation
        char.global_reputation = origin.starting_reputation
        char.inventory = starter_items() + origin.inventory_factory()
        if childhood is not None:
            for skill, bonus in childhood.skill_bonuses.items():
                char.skills.grant_starting_bonus(skill, bonus)
        self._apply_profession(char, profession_selection)
        return char


def creation_opening_text() -> str:
    return (
        "Powoli odzyskujesz świadomość.\n"
        "Ciepło kominka wraca do zmarzniętych dłoni.\n"
        "Powietrze pachnie pieczonym mięsem, piwem i dymem.\n"
        "Przy kilku stołach siedzą podróżni.\n"
        "Ktoś śmieje się głośno, ktoś właśnie wygrał partię kości.\n"
        "Karczmarz opiera łokcie o stół i czeka, aż spojrzysz w jego stronę.\n"
        "Przy sąsiednim stole kronikarz unosi pióro.\n"
        "— Najpierw powiedz mi, jak mam cię zapisać."
    )


def creation_closing_text() -> str:
    return (
        "Karczmarz odkłada kufel i kiwa głową.\n"
        "— Wyglądasz na gotowego.\n"
        "— Świat bywa okrutny.\n"
        "— Mam nadzieję, że jeszcze kiedyś usiądziemy przy tym samym stole."
    )


def create_character_from_profile(username: str, profile: CharacterCreationProfile) -> Character:
    return profile.create_character(username)
