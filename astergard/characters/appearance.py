from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from astergard.combat.weapons import HandRequirement, resolve_weapon_profile
from astergard.combat.wounds import overall_health_desc
from astergard.items.models import EQUIPMENT_SLOTS, Item


@dataclass(frozen=True, slots=True)
class AppearanceOption:
    key: str
    label: str
    description: str
    forms: dict[str, str] = field(default_factory=dict)

    def label_for_gender(self, gender_id: str | None) -> str:
        if gender_id is None:
            return self.label
        gendered = self.forms.get(f"label:{gender_id}")
        return gendered if gendered is not None else self.label


@dataclass(frozen=True, slots=True)
class AppearanceCreatorStep:
    step_id: str
    title: str
    prompt: str
    options: tuple[AppearanceOption, ...]
    resolver: Callable[[str], AppearanceOption]


@dataclass(frozen=True, slots=True)
class VisibleEquipmentItem:
    slot: str
    item: object
    visible_areas: frozenset[str]
    partial_occluders: tuple[object, ...] = ()
    full_occluders: tuple[object, ...] = ()


@dataclass(frozen=True, slots=True)
class CharacterAppearanceProfile:
    build: str
    height: str
    eyes: str
    hair_color: str
    hair_style: str
    beard: str
    special_feature: str

    def to_dict(self) -> dict[str, str]:
        return {
            "build": self.build,
            "height": self.height,
            "eyes": self.eyes,
            "hair_color": self.hair_color,
            "hair_style": self.hair_style,
            "beard": self.beard,
            "special_feature": self.special_feature,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "CharacterAppearanceProfile":
        expected_keys = {
            "build",
            "height",
            "eyes",
            "hair_color",
            "hair_style",
            "beard",
            "special_feature",
        }
        if not isinstance(data, Mapping):
            raise ValueError("Profil wyglądu musi być obiektem JSON.")
        data_keys = set(data.keys())
        if data_keys != expected_keys:
            missing = sorted(expected_keys - data_keys)
            extra = sorted(data_keys - expected_keys)
            raise ValueError(f"Nieprawidłowy profil wyglądu: brak={missing!r}, nadmiar={extra!r}.")
        values: dict[str, str] = {}
        for key in expected_keys:
            value = data.get(key)
            if type(value) is not str:
                raise ValueError(f"Profil wyglądu zawiera nieprawidłową wartość pola {key!r}.")
            normalized = value.strip()
            if not normalized:
                raise ValueError(f"Profil wyglądu zawiera puste pole {key!r}.")
            values[key] = normalized
        build = _validate_option_value(values["build"], BUILD_DEFINITIONS, "Nieznana budowa.", aliases=BUILD_ALIASES)
        height = _validate_option_value(values["height"], HEIGHT_DEFINITIONS, "Nieznany wzrost.", aliases=HEIGHT_ALIASES)
        eyes = _validate_option_value(values["eyes"], EYE_COLOR_DEFINITIONS, "Nieznany kolor oczu.", aliases=EYE_COLOR_ALIASES)
        hair_color = _validate_option_value(values["hair_color"], HAIR_COLOR_DEFINITIONS, "Nieznany kolor włosów.", aliases=HAIR_COLOR_ALIASES)
        hair_style = _validate_option_value(values["hair_style"], HAIR_STYLE_DEFINITIONS, "Nieznany sposób noszenia włosów.", aliases=HAIR_STYLE_ALIASES)
        beard = _validate_option_value(values["beard"], BEARD_DEFINITIONS, "Nieznany zarost.", aliases=BEARD_ALIASES)
        special_feature = _validate_option_value(values["special_feature"], SPECIAL_FEATURE_DEFINITIONS, "Nieznana cecha szczególna.", aliases=SPECIAL_FEATURE_ALIASES)
        canonical = {
            "build": build.key,
            "height": height.key,
            "eyes": eyes.key,
            "hair_color": hair_color.key,
            "hair_style": hair_style.key,
            "beard": beard.key,
            "special_feature": special_feature.key,
        }
        validate_appearance_profile_values(canonical)
        return cls(**canonical)


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split()).casefold()


def _resolve_choice(
    value: str,
    definitions: Mapping[str, AppearanceOption],
    error_message: str,
    *,
    aliases: Mapping[str, str] | None = None,
) -> AppearanceOption:
    normalized = _normalize_text(value)
    if not normalized:
        raise ValueError(error_message)
    if normalized.isdigit():
        index = int(normalized) - 1
        options = list(definitions.values())
        if 0 <= index < len(options):
            return options[index]
    if aliases is not None and normalized in aliases:
        return definitions[aliases[normalized]]
    if normalized in definitions:
        return definitions[normalized]
    for definition in definitions.values():
        if normalized in {_normalize_text(definition.key), _normalize_text(definition.label)}:
            return definition
    raise ValueError(error_message)


def _step(
    step_id: str,
    title: str,
    prompt: str,
    definitions: Mapping[str, AppearanceOption],
    resolver: Callable[[str], AppearanceOption],
) -> AppearanceCreatorStep:
    return AppearanceCreatorStep(
        step_id=step_id,
        title=title,
        prompt=prompt,
        options=tuple(definitions.values()),
        resolver=resolver,
    )


GENDER_DEFINITIONS: dict[str, AppearanceOption] = {
    "m": AppearanceOption(
        "m",
        "mężczyzna",
        "Męska forma gramatyczna i opis zgodny z mężczyzną.",
        forms={
            "nominative": "mężczyzna",
            "instrumental": "mężczyzną",
            "label:m": "mężczyzna",
            "label:f": "kobieta",
        },
    ),
    "f": AppearanceOption(
        "f",
        "kobieta",
        "Żeńska forma gramatyczna i opis zgodny z kobietą.",
        forms={
            "nominative": "kobieta",
            "instrumental": "kobietą",
            "label:m": "mężczyzna",
            "label:f": "kobieta",
        },
    ),
}

BUILD_DEFINITIONS: dict[str, AppearanceOption] = {
    "szczuply": AppearanceOption(
        "szczuply",
        "szczupła",
        "Smukła sylwetka i oszczędny ruch.",
        forms={
            "label:m": "szczupły",
            "label:f": "szczupła",
            "instrumental:m": "szczupłym",
            "instrumental:f": "szczupłą",
        },
    ),
    "drobny": AppearanceOption(
        "drobny",
        "drobna",
        "Niewielka sylwetka, łatwa do zgubienia w tłumie.",
        forms={
            "label:m": "drobny",
            "label:f": "drobna",
            "instrumental:m": "drobnym",
            "instrumental:f": "drobną",
        },
    ),
    "zylasty": AppearanceOption(
        "zylasty",
        "żylasta",
        "Smukła, sucha budowa i sprężysty ruch.",
        forms={
            "label:m": "żylasty",
            "label:f": "żylasta",
            "instrumental:m": "żylastym",
            "instrumental:f": "żylastą",
        },
    ),
    "krepy": AppearanceOption(
        "krepy",
        "krępa",
        "Niższa, tęższa budowa z mocnym środkiem ciężkości.",
        forms={
            "label:m": "krępy",
            "label:f": "krępa",
            "instrumental:m": "krępym",
            "instrumental:f": "krępą",
        },
    ),
    "barczysty": AppearanceOption(
        "barczysty",
        "barczysta",
        "Szeroka sylwetka, mocne barki i cięższa obecność.",
        forms={
            "label:m": "barczysty",
            "label:f": "barczysta",
            "instrumental:m": "barczystym",
            "instrumental:f": "barczystą",
        },
    ),
    "postawny": AppearanceOption(
        "postawny",
        "postawna",
        "Wyższa, mocniejsza postura i szeroka obecność.",
        forms={
            "label:m": "postawny",
            "label:f": "postawna",
            "instrumental:m": "postawnym",
            "instrumental:f": "postawną",
        },
    ),
}

HEIGHT_DEFINITIONS: dict[str, AppearanceOption] = {
    "bardzo_niski": AppearanceOption(
        "bardzo_niski",
        "bardzo niska",
        "Znacznie niższy wzrost niż u większości ludzi.",
        forms={
            "phrase": "bardzo niskiego wzrostu",
            "label:m": "bardzo niski",
            "label:f": "bardzo niska",
            "instrumental:m": "bardzo niskim",
            "instrumental:f": "bardzo niską",
        },
    ),
    "niski": AppearanceOption(
        "niski",
        "niska",
        "Niższy wzrost niż większość ludzi.",
        forms={
            "phrase": "niskiego wzrostu",
            "label:m": "niski",
            "label:f": "niska",
            "instrumental:m": "niskim",
            "instrumental:f": "niską",
        },
    ),
    "sredni": AppearanceOption(
        "sredni",
        "średnia",
        "Wzrost niewyróżniający się w tłumie.",
        forms={
            "phrase": "średniego wzrostu",
            "label:m": "średni",
            "label:f": "średnia",
            "instrumental:m": "średnim",
            "instrumental:f": "średnią",
        },
    ),
    "wysoki": AppearanceOption(
        "wysoki",
        "wysoka",
        "Wyraźnie wysoka sylwetka.",
        forms={
            "phrase": "wysokiego wzrostu",
            "label:m": "wysoki",
            "label:f": "wysoka",
            "instrumental:m": "wysokim",
            "instrumental:f": "wysoką",
        },
    ),
    "bardzo_wysoki": AppearanceOption(
        "bardzo_wysoki",
        "bardzo wysoka",
        "Ponadprzeciętnie wysoka postać.",
        forms={
            "phrase": "bardzo wysokiego wzrostu",
            "label:m": "bardzo wysoki",
            "label:f": "bardzo wysoka",
            "instrumental:m": "bardzo wysokim",
            "instrumental:f": "bardzo wysoką",
        },
    ),
}

EYE_COLOR_DEFINITIONS: dict[str, AppearanceOption] = {
    "szare": AppearanceOption("szare", "szare", "Szare oczy.", forms={"locative_plural": "szarych oczach"}),
    "piwne": AppearanceOption("piwne", "piwne", "Piwne oczy o ciepłym odcieniu.", forms={"locative_plural": "piwnych oczach"}),
    "zielone": AppearanceOption("zielone", "zielone", "Zielone oczy.", forms={"locative_plural": "zielonych oczach"}),
    "niebieskie": AppearanceOption("niebieskie", "niebieskie", "Niebieskie oczy.", forms={"locative_plural": "niebieskich oczach"}),
    "czarne": AppearanceOption("czarne", "czarne", "Bardzo ciemne oczy.", forms={"locative_plural": "czarnych oczach"}),
    "jasnobursztynowe": AppearanceOption(
        "jasnobursztynowe",
        "jasnobursztynowe",
        "Jasne oczy w bursztynowym odcieniu.",
        forms={"locative_plural": "jasnobursztynowych oczach"},
    ),
}

HAIR_COLOR_DEFINITIONS: dict[str, AppearanceOption] = {
    "ciemne": AppearanceOption("ciemne", "ciemne", "Ciemne włosy.", forms={"adjective": "ciemne"}),
    "jasne": AppearanceOption("jasne", "jasne", "Jasne włosy.", forms={"adjective": "jasne"}),
    "rude": AppearanceOption("rude", "rude", "Rude włosy.", forms={"adjective": "rude"}),
    "siwe": AppearanceOption("siwe", "siwe", "Siwe włosy.", forms={"adjective": "siwe"}),
    "kasztanowe": AppearanceOption("kasztanowe", "kasztanowe", "Kasztanowe włosy.", forms={"adjective": "kasztanowe"}),
}

HAIR_STYLE_DEFINITIONS: dict[str, AppearanceOption] = {
    "krotkie": AppearanceOption("krotkie", "krótkie", "Włosy przycięte krótko."),
    "dlugie": AppearanceOption("dlugie", "długie", "Włosy noszone długo."),
    "spiete": AppearanceOption("spiete", "spięte", "Włosy noszone spięte."),
    "rozpuszczone": AppearanceOption("rozpuszczone", "rozpuszczone", "Włosy noszone swobodnie."),
    "warkocze": AppearanceOption("warkocze", "warkocze", "Włosy zaplecione w warkocze."),
    "ogolone": AppearanceOption("ogolone", "ogolone", "Włosy ogolone lub bardzo krótko ścięte."),
}

BEARD_DEFINITIONS: dict[str, AppearanceOption] = {
    "brak": AppearanceOption("brak", "brak", "Gładko ogolona twarz."),
    "kilkudniowy_zarost": AppearanceOption("kilkudniowy_zarost", "kilkudniowy zarost", "Krótki, codzienny zarost."),
    "broda": AppearanceOption("broda", "broda", "Pełna broda."),
    "wasy": AppearanceOption("wasy", "wąsy", "Same wąsy."),
}

SPECIAL_FEATURE_DEFINITIONS: dict[str, AppearanceOption] = {
    "brak": AppearanceOption("brak", "brak", "Brak wyraźnych znaków szczególnych."),
    "blizna_policzek": AppearanceOption("blizna_policzek", "wąska blizna na policzku", "Wąska blizna biegnąca przez policzek.", forms={"sentence": "Wąska blizna przecina policzek."}),
    "blizna_dlon": AppearanceOption("blizna_dlon", "blizna na dłoni", "Blizna na dłoni po pracy albo ostrzu.", forms={"sentence": "Na grzbiecie dłoni widnieje wąska blizna."}),
    "slad_po_oparzeniu": AppearanceOption("slad_po_oparzeniu", "ślad po oparzeniu", "Ślad po ogniu albo gorącym metalu.", forms={"sentence": "Na skórze widać ślad po oparzeniu."}),
    "krzywy_nos": AppearanceOption("krzywy_nos", "krzywy nos", "Nos po starym uderzeniu.", forms={"sentence": "Masz krzywy nos."}),
}

GENDER_ALIASES = {
    "mezczyzna": "m",
    "mężczyzna": "m",
    "m": "m",
    "kobieta": "f",
    "k": "f",
}

BUILD_ALIASES = {
    "szczupła": "szczuply",
    "szczupły": "szczuply",
    "chudy": "szczuply",
    "krępa": "krepy",
    "krępy": "krepy",
    "żylasta": "zylasty",
    "żylasty": "zylasty",
    "".join(["wys", "portowany"]): "zylasty",
    "".join(["atle", "tyczny"]): "barczysty",
    "postawna": "postawny",
    "postawny": "postawny",
    "drobna": "drobny",
    "drobny": "drobny",
    "barczysta": "barczysty",
    "barczysty": "barczysty",
}

HEIGHT_ALIASES = {
    "bardzo niska": "bardzo_niski",
    "bardzo niski": "bardzo_niski",
    "niska": "niski",
    "niski": "niski",
    "średnia": "sredni",
    "srednia": "sredni",
    "wysoka": "wysoki",
    "wysoki": "wysoki",
    "bardzo wysoka": "bardzo_wysoki",
    "bardzo wysoki": "bardzo_wysoki",
}

EYE_COLOR_ALIASES = {
    "szare": "szare",
    "szary": "szare",
    "piwne": "piwne",
    "zielone": "zielone",
    "niebieskie": "niebieskie",
    "czarne": "czarne",
    "bursztynowe": "jasnobursztynowe",
}

HAIR_COLOR_ALIASES = {
    "ciemne": "ciemne",
    "jasne": "jasne",
    "rude": "rude",
    "siwe": "siwe",
    "kasztanowe": "kasztanowe",
}

HAIR_STYLE_ALIASES = {
    "krótkie": "krotkie",
    "krotkie": "krotkie",
    "długie": "dlugie",
    "dlugie": "dlugie",
    "spięte": "spiete",
    "spiete": "spiete",
    "rozpuszczone": "rozpuszczone",
    "warkocze": "warkocze",
    "ogolone": "ogolone",
}

BEARD_ALIASES = {
    "brak": "brak",
    "zarost": "kilkudniowy_zarost",
    "krótki zarost": "kilkudniowy_zarost",
    "krotki zarost": "kilkudniowy_zarost",
    "kilkudniowy zarost": "kilkudniowy_zarost",
    "broda": "broda",
    "wąsy": "wasy",
    "wasy": "wasy",
}

SPECIAL_FEATURE_ALIASES = {
    "brak": "brak",
    "blizna na policzku": "blizna_policzek",
    "blizna na dłoni": "blizna_dlon",
    "blizna na dloni": "blizna_dlon",
    "oparzenie": "slad_po_oparzeniu",
    "krzywy nos": "krzywy_nos",
}


def _gender_option(gender_id: str) -> AppearanceOption:
    option = GENDER_DEFINITIONS.get(gender_id)
    if option is None:
        raise ValueError("Nieznana płeć.")
    return option


def normalize_gender_id(value: object) -> str:
    if value is None or type(value) is bool:
        return ""
    text = _normalize_text(str(value))
    if not text:
        return ""
    if text in GENDER_ALIASES:
        return GENDER_ALIASES[text]
    if text in GENDER_DEFINITIONS:
        return text
    return ""


def gender_label(gender_id: str | None) -> str:
    if gender_id not in GENDER_DEFINITIONS:
        return "osoba"
    return GENDER_DEFINITIONS[gender_id].forms.get("nominative", GENDER_DEFINITIONS[gender_id].label)


def gender_instrumental(gender_id: str | None) -> str:
    if gender_id not in GENDER_DEFINITIONS:
        return "osobą"
    return GENDER_DEFINITIONS[gender_id].forms.get("instrumental", "osobą")


def _option_label(options: Mapping[str, AppearanceOption], key: str, gender_id: str | None = None) -> str:
    option = options.get(key)
    if option is None:
        return key
    return option.label_for_gender(gender_id)


def _option_form(options: Mapping[str, AppearanceOption], key: str, form: str, fallback: str | None = None) -> str:
    option = options.get(key)
    if option is None:
        return fallback if fallback is not None else key
    return option.forms.get(form) or (fallback if fallback is not None else option.label)


def _instrumental_phrase(label: str, gender_id: str | None) -> str:
    if gender_id == "m":
        return {
            "szczupła": "szczupłym",
            "drobna": "drobnym",
            "żylasta": "żylastym",
            "krępa": "krępym",
            "barczysta": "barczystym",
            "postawna": "postawnym",
            "bardzo niska": "bardzo niskim",
            "niska": "niskim",
            "wysoka": "wysokim",
            "bardzo wysoka": "bardzo wysokim",
        }.get(label, label)
    if gender_id == "f":
        return {
            "szczupła": "szczupłą",
            "drobna": "drobną",
            "żylasta": "żylastą",
            "krępa": "krępą",
            "barczysta": "barczystą",
            "postawna": "postawną",
            "bardzo niska": "bardzo niską",
            "niska": "niską",
            "wysoka": "wysoką",
            "bardzo wysoka": "bardzo wysoką",
        }.get(label, label)
    return label


def _validate_option_value(
    value: str,
    definitions: Mapping[str, AppearanceOption],
    error_message: str,
    *,
    aliases: Mapping[str, str] | None = None,
) -> AppearanceOption:
    normalized = _normalize_text(value)
    if not normalized:
        raise ValueError(error_message)
    if normalized.isdigit():
        index = int(normalized) - 1
        options = list(definitions.values())
        if 0 <= index < len(options):
            return options[index]
    if aliases is not None and normalized in aliases:
        return definitions[aliases[normalized]]
    if normalized in definitions:
        return definitions[normalized]
    for definition in definitions.values():
        if normalized in {_normalize_text(definition.key), _normalize_text(definition.label)}:
            return definition
    raise ValueError(error_message)


def validate_appearance_profile_values(profile: Mapping[str, str], *, gender_id: str | None = None) -> None:
    _validate_option_value(profile["build"], BUILD_DEFINITIONS, "Nieznana budowa.", aliases=BUILD_ALIASES)
    _validate_option_value(profile["height"], HEIGHT_DEFINITIONS, "Nieznany wzrost.", aliases=HEIGHT_ALIASES)
    _validate_option_value(profile["eyes"], EYE_COLOR_DEFINITIONS, "Nieznany kolor oczu.", aliases=EYE_COLOR_ALIASES)
    _validate_option_value(profile["hair_color"], HAIR_COLOR_DEFINITIONS, "Nieznany kolor włosów.", aliases=HAIR_COLOR_ALIASES)
    _validate_option_value(profile["hair_style"], HAIR_STYLE_DEFINITIONS, "Nieznany sposób noszenia włosów.", aliases=HAIR_STYLE_ALIASES)
    beard = _validate_option_value(profile["beard"], BEARD_DEFINITIONS, "Nieznany zarost.", aliases=BEARD_ALIASES)
    _validate_option_value(profile["special_feature"], SPECIAL_FEATURE_DEFINITIONS, "Nieznana cecha szczególna.", aliases=SPECIAL_FEATURE_ALIASES)
    if gender_id == "f" and beard.key != "brak":
        raise ValueError("Kobieta nie może wybrać zarostu innego niż brak.")


def gender_step() -> AppearanceCreatorStep:
    return _step(
        "gender_id",
        "Płeć",
        "— Czy mam zapisać cię jako mężczyznę czy kobietę?",
        GENDER_DEFINITIONS,
        lambda value: _validate_option_value(value, GENDER_DEFINITIONS, "Płeć nie może być pusta.", aliases=GENDER_ALIASES),
    )


def build_step() -> AppearanceCreatorStep:
    return _step(
        "build",
        "Budowa",
        "— Jakiej jesteś budowy?",
        BUILD_DEFINITIONS,
        lambda value: _validate_option_value(value, BUILD_DEFINITIONS, "Budowa nie może być pusta.", aliases=BUILD_ALIASES),
    )


def height_step() -> AppearanceCreatorStep:
    return _step(
        "height",
        "Wzrost",
        "— Jakiego jesteś wzrostu?",
        HEIGHT_DEFINITIONS,
        lambda value: _validate_option_value(value, HEIGHT_DEFINITIONS, "Wzrost nie może być pusty.", aliases=HEIGHT_ALIASES),
    )


def eye_color_step() -> AppearanceCreatorStep:
    return _step(
        "eyes",
        "Kolor oczu",
        "— Jakiego koloru są twoje oczy?",
        EYE_COLOR_DEFINITIONS,
        lambda value: _validate_option_value(value, EYE_COLOR_DEFINITIONS, "Kolor oczu nie może być pusty.", aliases=EYE_COLOR_ALIASES),
    )


def hair_color_step() -> AppearanceCreatorStep:
    return _step(
        "hair_color",
        "Kolor włosów",
        "— Jaki mają kolor twoje włosy?",
        HAIR_COLOR_DEFINITIONS,
        lambda value: _validate_option_value(value, HAIR_COLOR_DEFINITIONS, "Kolor włosów nie może być pusty.", aliases=HAIR_COLOR_ALIASES),
    )


def hair_style_step() -> AppearanceCreatorStep:
    return _step(
        "hair_style",
        "Sposób noszenia włosów",
        "— Jak nosisz włosy?",
        HAIR_STYLE_DEFINITIONS,
        lambda value: _validate_option_value(value, HAIR_STYLE_DEFINITIONS, "Sposób noszenia włosów nie może być pusty.", aliases=HAIR_STYLE_ALIASES),
    )


def beard_step() -> AppearanceCreatorStep:
    return _step(
        "beard",
        "Zarost",
        "— Nosisz zarost? Jeśli nie, wybierz brak.",
        BEARD_DEFINITIONS,
        lambda value: _validate_option_value(value, BEARD_DEFINITIONS, "Zarost nie może być pusty.", aliases=BEARD_ALIASES),
    )


def special_feature_step() -> AppearanceCreatorStep:
    return _step(
        "special_feature",
        "Cechy szczególne",
        "— Masz jakąś cechę szczególną? Jeśli nie, wybierz brak.",
        SPECIAL_FEATURE_DEFINITIONS,
        lambda value: _validate_option_value(value, SPECIAL_FEATURE_DEFINITIONS, "Cecha szczególna nie może być pusta.", aliases=SPECIAL_FEATURE_ALIASES),
    )


def appearance_steps_for_gender(gender_id: str) -> tuple[AppearanceCreatorStep, ...]:
    resolved_gender = normalize_gender_id(gender_id)
    if resolved_gender not in {"m", "f"}:
        raise ValueError("Nieznana płeć.")
    steps = [build_step(), height_step(), eye_color_step(), hair_color_step(), hair_style_step()]
    if resolved_gender == "m":
        steps.append(beard_step())
    steps.append(special_feature_step())
    return tuple(steps)


def appearance_creator_steps(gender_id: str | None = None) -> tuple[AppearanceCreatorStep, ...]:
    if gender_id is None:
        return (gender_step(),)
    return appearance_steps_for_gender(gender_id)


def appearance_profile_from_choices(
    *,
    gender_id: str,
    build: str,
    height: str,
    eyes: str,
    hair_color: str,
    hair_style: str,
    beard: str,
    special_feature: str,
) -> CharacterAppearanceProfile:
    resolved_gender = normalize_gender_id(gender_id)
    if resolved_gender not in {"m", "f"}:
        raise ValueError("Płeć nie może być pusta.")
    profile = CharacterAppearanceProfile(
        build=_validate_option_value(build, BUILD_DEFINITIONS, "Budowa nie może być pusta.", aliases=BUILD_ALIASES).key,
        height=_validate_option_value(height, HEIGHT_DEFINITIONS, "Wzrost nie może być pusty.", aliases=HEIGHT_ALIASES).key,
        eyes=_validate_option_value(eyes, EYE_COLOR_DEFINITIONS, "Kolor oczu nie może być pusty.", aliases=EYE_COLOR_ALIASES).key,
        hair_color=_validate_option_value(hair_color, HAIR_COLOR_DEFINITIONS, "Kolor włosów nie może być pusty.", aliases=HAIR_COLOR_ALIASES).key,
        hair_style=_validate_option_value(hair_style, HAIR_STYLE_DEFINITIONS, "Sposób noszenia włosów nie może być pusty.", aliases=HAIR_STYLE_ALIASES).key,
        beard=_validate_option_value(beard, BEARD_DEFINITIONS, "Zarost nie może być pusty.", aliases=BEARD_ALIASES).key,
        special_feature=_validate_option_value(special_feature, SPECIAL_FEATURE_DEFINITIONS, "Cecha szczególna nie może być pusta.", aliases=SPECIAL_FEATURE_ALIASES).key,
    )
    validate_appearance_profile_values(profile.to_dict(), gender_id=resolved_gender)
    return profile


def _appearance_intro(profile: CharacterAppearanceProfile, *, gender_id: str) -> str:
    build_option = _option_label(BUILD_DEFINITIONS, profile.build, gender_id)
    gender_noun = gender_instrumental(gender_id)
    height_phrase = _option_form(HEIGHT_DEFINITIONS, profile.height, "phrase")
    eyes_phrase = _option_form(EYE_COLOR_DEFINITIONS, profile.eyes, "locative_plural")
    build_instrumental = _option_form(BUILD_DEFINITIONS, profile.build, f"instrumental:{gender_id}", build_option)
    if profile.height == "sredni":
        return f"Jesteś {build_instrumental} {gender_noun} {height_phrase} o {eyes_phrase}."
    height_instrumental = _option_form(HEIGHT_DEFINITIONS, profile.height, f"instrumental:{gender_id}", height_phrase)
    return f"Jesteś {height_instrumental}, {build_instrumental} {gender_noun} o {eyes_phrase}."


def render_appearance_lines(profile: CharacterAppearanceProfile | None, *, gender_id: str) -> list[str]:
    if profile is None:
        return []
    lines = [_appearance_intro(profile, gender_id=gender_id)]
    if profile.hair_style == "ogolone":
        lines.append("Masz gładko ogoloną głowę.")
    else:
        hair_color = _option_label(HAIR_COLOR_DEFINITIONS, profile.hair_color, gender_id)
        if profile.hair_style == "warkocze":
            lines.append(f"Masz {hair_color} włosy zaplecione w warkocze.")
        elif profile.hair_style == "dlugie":
            lines.append(f"Masz długie, {hair_color} włosy.")
        elif profile.hair_style == "spiete":
            lines.append(f"Masz {hair_color} włosy spięte z tyłu.")
        elif profile.hair_style == "rozpuszczone":
            lines.append(f"Masz {hair_color} włosy noszone swobodnie.")
        else:
            lines.append(f"Masz krótkie, {hair_color} włosy.")
    if profile.beard != "brak":
        beard_label = _option_label(BEARD_DEFINITIONS, profile.beard, gender_id)
        lines.append(f"Na twarzy nosisz {beard_label}.")
    special_feature = _option_form(SPECIAL_FEATURE_DEFINITIONS, profile.special_feature, "sentence")
    if profile.special_feature != "brak":
        lines.append(special_feature)
    return lines


def render_identity_line(name: str, gender_id: str) -> str:
    noun = gender_label(gender_id)
    return f"{name}, {noun}." if noun != "osoba" else f"{name}."


def render_condition_line(wounds: Mapping[str, int]) -> str:
    description = overall_health_desc(dict(wounds))
    if description == "jest w pełni sił":
        return "Jesteś w pełni sił."
    if description == "jest lekko ranny":
        return "Jesteś lekko ranny."
    if description == "krwawi obficie":
        return "Krwawisz obficie."
    if description == "ledwo trzyma się na nogach":
        return "Ledwo trzymasz się na nogach."
    if description == "jest u progu śmierci":
        return "Jesteś u progu śmierci."
    return f"Jesteś {description}."


def _item_name(item: object) -> str:
    if hasattr(item, "display_nominative_name"):
        value = getattr(item, "display_nominative_name")()
        if isinstance(value, str) and value.strip():
            return value.strip()
    if hasattr(item, "display_nominative"):
        value = getattr(item, "display_nominative")
        if isinstance(value, str) and value.strip():
            return value.strip()
    if hasattr(item, "forms"):
        forms = getattr(item, "forms")
        if isinstance(forms, Mapping):
            nominative = forms.get("nom")
            if isinstance(nominative, str) and nominative.strip():
                return nominative.strip()
    if hasattr(item, "display_name"):
        return getattr(item, "display_name")()
    if hasattr(item, "name"):
        return str(getattr(item, "name"))
    return str(item)


def _item_accusative_name(item: object) -> str | None:
    if hasattr(item, "display_accusative_name"):
        value = getattr(item, "display_accusative_name")()
        if isinstance(value, str) and value.strip():
            return value.strip()
    if hasattr(item, "display_accusative"):
        value = getattr(item, "display_accusative")
        if isinstance(value, str) and value.strip():
            return value.strip()
    if hasattr(item, "forms"):
        forms = getattr(item, "forms")
        if isinstance(forms, Mapping):
            accusative = forms.get("acc")
            if isinstance(accusative, str) and accusative.strip():
                return accusative.strip()
    return None


def _item_identity(item: object) -> str:
    if hasattr(item, "id"):
        identity = getattr(item, "id")
        if isinstance(identity, str) and identity:
            return identity
    return f"object:{id(item)}"


def _slot_item(equipment: Mapping[str, object], slot: str) -> object | None:
    item = equipment.get(slot)
    return item if item is not None else None


def _stack_items(equipment: Mapping[str, object], slot: str) -> tuple[object, ...]:
    if hasattr(equipment, "layers"):
        stack = getattr(equipment, "layers")(slot)
        if isinstance(stack, tuple):
            return stack
        return tuple(stack)
    item = _slot_item(equipment, slot)
    return (item,) if item is not None else ()


def _all_equipment_items(equipment: Mapping[str, object]) -> list[tuple[str, object, int, int]]:
    entries: list[tuple[str, object, int, int]] = []
    slot_index = {slot: idx for idx, slot in enumerate(EQUIPMENT_SLOTS)}
    if hasattr(equipment, "layers"):
        for slot in EQUIPMENT_SLOTS:
            stack = list(_stack_items(equipment, slot))
            for index, item in enumerate(stack):
                entries.append((slot, item, slot_index.get(slot, 999), index))
        return entries
    for slot, item in equipment.items():
        if item is not None:
            entries.append((str(slot), item, slot_index.get(str(slot), 999), 0))
    return entries


def _presentation_layer_rank(item: object) -> int:
    layer = getattr(item, "presentation_layer", None)
    if not isinstance(layer, str):
        return 99
    return {
        "undergarment": 0,
        "clothing": 1,
        "armor": 2,
        "outerwear": 3,
        "accessory": 4,
    }.get(layer, 99)


def _coverage_areas(item: object) -> set[str]:
    if getattr(item, "presentation_layer", None) is None:
        return set()
    if hasattr(item, "coverage_areas"):
        raw = getattr(item, "coverage_areas")
        if isinstance(raw, (list, tuple, set)):
            return {str(area) for area in raw if isinstance(area, str) and area.strip()}
    return set()


def _coverage_mode(item: object) -> str:
    mode = getattr(item, "coverage_mode", None)
    if mode in {"partial", "full"}:
        return mode
    return "full"


def visible_equipped_items(equipment: Mapping[str, object]) -> list[VisibleEquipmentItem]:
    entries = _all_equipment_items(equipment)
    ordered_entries = sorted(
        entries,
        key=lambda entry: (_presentation_layer_rank(entry[1]), entry[2], entry[3], _item_identity(entry[1])),
    )
    visible: list[VisibleEquipmentItem] = []
    rendered_ids: set[str] = set()
    for index, (slot, item, _, _) in enumerate(ordered_entries):
        item_id = _item_identity(item)
        if item_id in rendered_ids:
            continue
        coverage = _coverage_areas(item)
        higher_items = [candidate for _, candidate, _, _ in ordered_entries[index + 1:]]
        covered_areas: set[str] = set()
        partial_occluders: list[object] = []
        full_occluders: list[object] = []
        for higher in higher_items:
            higher_coverage = _coverage_areas(higher)
            if not higher_coverage:
                continue
            overlap = coverage & higher_coverage
            if not overlap:
                continue
            if _coverage_mode(higher) == "partial":
                partial_occluders.append(higher)
            else:
                full_occluders.append(higher)
            covered_areas.update(overlap)
        visible_areas = frozenset(coverage - covered_areas) if coverage else frozenset()
        visible.append(
            VisibleEquipmentItem(
                slot=slot,
                item=item,
                visible_areas=visible_areas,
                partial_occluders=tuple(partial_occluders),
                full_occluders=tuple(full_occluders),
            )
        )
        rendered_ids.add(item_id)
    return visible


def _render_worn_item_line(
    slot: str,
    item: object,
    *,
    visible_areas: frozenset[str] = frozenset(),
    partial_occluders: tuple[object, ...] = (),
) -> str | None:
    accusative = _item_accusative_name(item)
    nominative = _item_name(item)
    neutral_fallback = f"Widoczne wyposażenie: {nominative}."
    if slot == "plecy":
        return f"Na plecach niesiesz {accusative or nominative}." if accusative is not None else neutral_fallback
    if slot == "pas":
        if getattr(item, "item_type", None) in {"clothing", "armor"} or getattr(item, "presentation_layer", None) in {"clothing", "armor"}:
            return f"Biodra opasuje {nominative}."
        return f"U pasa wisi {nominative}."
    if slot == "glowa":
        return f"Głowę osłania {nominative}."
    if slot == "szyja":
        return f"Na szyi nosisz {nominative}."
    if slot == "korpus":
        if getattr(item, "presentation_layer", None) == "outerwear" and getattr(item, "coverage_mode", None) == "partial":
            return f"Ramiona okrywa {nominative}."
        if partial_occluders and any(getattr(occluder, "presentation_layer", None) == "outerwear" for occluder in partial_occluders):
            return f"Spod rozpiętego płaszcza widać {accusative or nominative}."
        return f"Masz na sobie {accusative}." if accusative is not None else neutral_fallback
    if slot == "rece":
        return f"Ramiona okrywa {nominative}."
    if slot == "dlonie":
        return f"Na dłoniach nosisz {nominative}."
    if slot == "nogi":
        return f"Na nogach nosisz {accusative or nominative}." if accusative is not None else neutral_fallback
    if slot == "stopy":
        return f"Stopy chronią {nominative}."
    if slot == "amulet":
        return f"Na piersi nosisz {nominative}."
    if slot in {"pierscien_1", "pierscien_2"}:
        return f"Na palcach nosisz {nominative}."
    return neutral_fallback


def _weapon_line(slot: str, item: object, *, other_item_id: str | None = None) -> str | None:
    weapon = item if isinstance(item, Item) and item.item_type == "weapon" else None
    weapon_profile_id = weapon.weapon_profile_id if weapon is not None else None
    profile = resolve_weapon_profile(weapon) if weapon is not None else None
    name = _item_accusative_name(item) or _item_name(item)
    if weapon_profile_id not in {None, ""} and profile is not None and not profile.legacy:
        if profile.hand_requirement == HandRequirement.TWO_HANDED and slot == "bron_glowna":
            return f"Oburącz dzierżysz {name}."
        if profile.hand_requirement == HandRequirement.TWO_HANDED:
            return None
        if slot == "bron_glowna":
            return f"W prawej ręce trzymasz {name}."
        if slot == "bron_pomocnicza":
            if other_item_id is not None and _item_identity(item) == other_item_id:
                return None
            return f"W lewej ręce trzymasz {name}."
    if slot == "bron_glowna":
        return f"Twoją prawą rękę zajmuje: {_item_name(item)}."
    if slot == "bron_pomocnicza":
        if other_item_id is not None and _item_identity(item) == other_item_id:
            return None
        return f"Twoją lewą rękę zajmuje: {_item_name(item)}."
    return None


def _shield_line(item: object) -> str:
    phrase = _item_accusative_name(item) or _item_name(item)
    return f"W lewej ręce trzymasz {phrase}."


def render_equipment_lines(equipment: Mapping[str, object]) -> list[str]:
    lines: list[str] = []
    for visible_item in visible_equipped_items(equipment):
        slot = visible_item.slot
        item = visible_item.item
        if slot in {"bron_glowna", "bron_pomocnicza", "tarcza"}:
            continue
        if not visible_item.visible_areas and getattr(item, "coverage_areas", None):
            continue
        line = _render_worn_item_line(
            slot,
            item,
            visible_areas=visible_item.visible_areas,
            partial_occluders=visible_item.partial_occluders,
        )
        if line is not None:
            lines.append(line)

    main_weapon = _slot_item(equipment, "bron_glowna")
    off_weapon = _slot_item(equipment, "bron_pomocnicza")
    main_two_handed = False
    if isinstance(main_weapon, Item) and main_weapon.item_type == "weapon":
        main_profile = resolve_weapon_profile(main_weapon)
        main_two_handed = bool(main_profile is not None and not main_profile.legacy and main_profile.hand_requirement == HandRequirement.TWO_HANDED)
    if main_weapon is not None:
        main_line = _weapon_line("bron_glowna", main_weapon, other_item_id=_item_identity(off_weapon) if off_weapon is not None else None)
        if main_line is not None:
            lines.append(main_line)
    if off_weapon is not None and not main_two_handed:
        off_line = _weapon_line("bron_pomocnicza", off_weapon, other_item_id=_item_identity(main_weapon) if main_weapon is not None else None)
        if off_line is not None:
            lines.append(off_line)

    shield = _slot_item(equipment, "tarcza")
    if shield is not None and not main_two_handed:
        lines.append(_shield_line(shield))

    return lines


def render_self_observation(
    *,
    name: str,
    gender_id: str,
    wounds: Mapping[str, int],
    equipment: Mapping[str, object],
    appearance_profile: CharacterAppearanceProfile | None,
    legacy_appearance: str = "",
) -> str:
    blocks: list[str] = []
    if appearance_profile is not None and gender_id in {"m", "f"}:
        blocks.append("\n".join(render_appearance_lines(appearance_profile, gender_id=gender_id)))
    identity_line = render_identity_line(name, gender_id)
    if identity_line:
        blocks.append(identity_line)
    tail_lines = [render_condition_line(wounds), *render_equipment_lines(equipment)]
    if tail_lines:
        blocks.append("\n".join(tail_lines))
    return "\n\n".join(blocks).strip()
