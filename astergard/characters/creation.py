from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from astergard.characters.models import Character
from astergard.characters.professions import (
    ProfessionSelection,
    build_selection,
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


@dataclass(frozen=True, slots=True)
class AppearanceDefinition:
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

BUILD_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "krepy": AppearanceDefinition("krepy", "krępy", "Niższa sylwetka, cięższy środek ciężkości i siła, która bardziej stoi niż biegnie."),
    "szczuply": AppearanceDefinition("szczuply", "szczupła", "Smukła budowa, zwinna i oszczędna w ruchu."),
    "wysportowana": AppearanceDefinition("wysportowana", "wysportowana", "Ciało przyzwyczajone do pracy, marszu i wysiłku."),
    "mocarna": AppearanceDefinition("mocarna", "mocarna", "Szeroka postura, z której trudno zepchnąć kogoś lekkim pchnięciem."),
    "drobna": AppearanceDefinition("drobna", "drobna", "Niewielka sylwetka, łatwa do zgubienia w tłumie albo w cieniu."),
    "atletyczna": AppearanceDefinition("atletyczna", "atletyczna", "Sylwetka z wyraźną siłą i wyćwiczonym ruchem."),
}

HEIGHT_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "niska": AppearanceDefinition("niska", "niska", "Niższy wzrost, bliżej ziemi niż większość ludzi."),
    "srednia": AppearanceDefinition("srednia", "średnia", "Wzrost niewyróżniający się w tłumie."),
    "wysoka": AppearanceDefinition("wysoka", "wysoka", "Wyraźnie wysoka sylwetka."),
    "bardzo_wysoka": AppearanceDefinition("bardzo_wysoka", "bardzo wysoka", "Ponadprzeciętnie wysoka postać, którą widać z daleka."),
    "postawna": AppearanceDefinition("postawna", "postawna", "Wyższa i masywniejsza niż przeciętnie."),
}

HAIR_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "ciemne_spiete": AppearanceDefinition("ciemne_spiete", "ciemne i spięte", "Ciemne włosy związane tak, by nie przeszkadzały w ruchu."),
    "krotkie_jasne": AppearanceDefinition("krotkie_jasne", "krótkie i jasne", "Krótkie, jasne włosy bez większej troski o ozdobę."),
    "dlugie_rude": AppearanceDefinition("dlugie_rude", "długie i rude", "Dłuższe włosy o ciepłym, rudawym odcieniu."),
    "ogolone": AppearanceDefinition("ogolone", "ogolone", "Głowa wygolona lub prawie całkiem pozbawiona włosów."),
    "siwe_rzadkie": AppearanceDefinition("siwe_rzadkie", "siwe i rzadkie", "Siwe, przerzedzone włosy po latach pracy i drogi."),
    "splatane": AppearanceDefinition("splatane", "splątane", "Włosy noszone bez wielkiej troski o porządek."),
}

BEARD_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "brak": AppearanceDefinition("brak", "brak", "Gładko ogolona twarz."),
    "krotka_broda": AppearanceDefinition("krotka_broda", "krótka broda", "Krótko przystrzyżona broda."),
    "dlugi_zarost": AppearanceDefinition("dlugi_zarost", "długi zarost", "Zarost noszony już wyraźnie dłużej niż kilka dni."),
    "wasy": AppearanceDefinition("wasy", "wąsy", "Same wąsy, bardziej z przyzwyczajenia niż z próżności."),
    "pelna_broda": AppearanceDefinition("pelna_broda", "pełna broda", "Gęsta, pełniejsza broda."),
}

SCAR_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "brak": AppearanceDefinition("brak", "brak", "Brak widocznych blizn."),
    "blizna_dlon": AppearanceDefinition("blizna_dlon", "blizna na dłoni", "Blizna na dłoni po pracy albo ostrzu."),
    "blizna_policzek": AppearanceDefinition("blizna_policzek", "stara blizna na policzku", "Widoczna stara blizna na twarzy."),
    "drobne_blizny": AppearanceDefinition("drobne_blizny", "kilka drobnych blizn", "Kilka małych śladów po dawnej robocie i bójce."),
    "oparzenie": AppearanceDefinition("oparzenie", "ślad po oparzeniu", "Ślad po ogniu albo gorącym metalu."),
}

EYE_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "szare": AppearanceDefinition("szare", "szare", "Szare oczy, chłodne i trudne do odczytania."),
    "piwne": AppearanceDefinition("piwne", "piwne", "Piwne oczy o ciepłym, ziemistym odcieniu."),
    "zielone": AppearanceDefinition("zielone", "zielone", "Zielone oczy, wyraźne i rzadsze."),
    "niebieskie": AppearanceDefinition("niebieskie", "niebieskie", "Jasne, niebieskie oczy."),
    "czarne": AppearanceDefinition("czarne", "czarne", "Bardzo ciemne oczy, prawie czarne."),
    "jasnobursztynowe": AppearanceDefinition("jasnobursztynowe", "jasnobursztynowe", "Jasne oczy w bursztynowym odcieniu."),
}

TATTOO_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "brak": AppearanceDefinition("brak", "brak", "Brak tatuaży."),
    "drobne_znaki": AppearanceDefinition("drobne_znaki", "drobne znaki", "Małe znaki lub symbole na skórze."),
    "wojenne_znaki": AppearanceDefinition("wojenne_znaki", "wojenne znaki", "Znaki związane ze służbą, walką albo przysięgą."),
    "plemienne_wzory": AppearanceDefinition("plemienne_wzory", "plemienne wzory", "Tatuaże w stylu rodowym lub plemiennym."),
    "modlitewne_symbole": AppearanceDefinition("modlitewne_symbole", "modlitewne symbole", "Symbole związane z wiarą i modlitwą."),
}

GAIT_DEFINITIONS: dict[str, AppearanceDefinition] = {
    "pewny_spokojny": AppearanceDefinition("pewny_spokojny", "pewnym, spokojnym krokiem", "Porusza się spokojnie i bez pośpiechu."),
    "ciezki": AppearanceDefinition("ciezki", "ciężkim krokiem", "Każdy krok ma w sobie wagę i ostrożność."),
    "lekki": AppearanceDefinition("lekki", "lekko i szybko", "Ruch lekki, szybki i zwinny."),
    "czujny": AppearanceDefinition("czujny", "czujnym krokiem", "Porusza się jak ktoś, kto stale ocenia otoczenie."),
    "powolny": AppearanceDefinition("powolny", "wolno i ostrożnie", "Stawia kroki ostrożnie, bez gwałtownych ruchów."),
}

BUILD_ALIASES: dict[str, str] = {
    "szczupła": "szczuply",
    "szczupły": "szczuply",
    "krępa": "krepy",
    "krępy": "krepy",
    "mocarny": "mocarna",
    "drobny": "drobna",
}

HEIGHT_ALIASES: dict[str, str] = {
    "niski": "niska",
    "średni": "srednia",
    "sredni": "srednia",
    "wysoki": "wysoka",
    "bardzo wysoki": "bardzo_wysoka",
    "postawny": "postawna",
}

HAIR_ALIASES: dict[str, str] = {
    "ciemne i krótkie": "ciemne_spiete",
    "ciemne i krotkie": "ciemne_spiete",
    "krótkie i ciemne": "ciemne_spiete",
    "krotkie i ciemne": "ciemne_spiete",
    "długie i czarne": "dlugie_rude",
}

GAIT_ALIASES: dict[str, str] = {
    "pewnym krokiem": "pewny_spokojny",
    "pewnym, zdecydowanym krokiem": "pewny_spokojny",
    "wolnym krokiem": "powolny",
    "lekko": "lekki",
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


def build_appearance_prompt_text() -> str:
    return _appearance_prompt_text(
        "Budowa",
        "Karczmarz zerka na twoją sylwetkę, nie na twoją historię.\n— Jakiej jesteś budowy?",
        BUILD_DEFINITIONS,
    )


def resolve_build(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, BUILD_DEFINITIONS, "Budowa nie może być pusta.", aliases=BUILD_ALIASES)


def height_prompt_text() -> str:
    return _appearance_prompt_text(
        "Wzrost",
        "Kronikarz unosi wzrok znad pergaminu.\n— Jakiego jesteś wzrostu?",
        HEIGHT_DEFINITIONS,
    )


def resolve_height(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, HEIGHT_DEFINITIONS, "Wzrost nie może być pusty.", aliases=HEIGHT_ALIASES)


def hair_prompt_text() -> str:
    return _appearance_prompt_text(
        "Włosy",
        "Karczmarz kiwa głową na znak, że to ważniejsza rzecz, niż się wydaje.\n— Jak wyglądają twoje włosy?",
        HAIR_DEFINITIONS,
    )


def resolve_hair(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, HAIR_DEFINITIONS, "Włosy nie mogą być puste.", aliases=HAIR_ALIASES)


def beard_prompt_text() -> str:
    return _appearance_prompt_text(
        "Broda",
        "Kronikarz uśmiecha się pod nosem.\n— Nosisz brodę? Jeśli nie, wybierz brak.",
        BEARD_DEFINITIONS,
    )


def resolve_beard(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, BEARD_DEFINITIONS, "Broda nie może być pusta.")


def scars_prompt_text() -> str:
    return _appearance_prompt_text(
        "Blizny",
        "Karczmarz nie naciska.\n— Masz blizny? Jeśli nie, wybierz brak.",
        SCAR_DEFINITIONS,
    )


def resolve_scars(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, SCAR_DEFINITIONS, "Blizny nie mogą być puste.")


def eyes_prompt_text() -> str:
    return _appearance_prompt_text(
        "Oczy",
        "Kronikarz spogląda na ciebie uważniej.\n— Jakiego koloru są twoje oczy?",
        EYE_DEFINITIONS,
    )


def resolve_eyes(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, EYE_DEFINITIONS, "Oczy nie mogą być puste.")


def tattoos_prompt_text() -> str:
    return _appearance_prompt_text(
        "Tatuaże",
        "Karczmarz składa dłonie na blacie.\n— Masz tatuaże? Jeśli nie, wybierz brak.",
        TATTOO_DEFINITIONS,
    )


def resolve_tattoos(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, TATTOO_DEFINITIONS, "Tatuaże nie mogą być puste.")


def gait_prompt_text() -> str:
    return _appearance_prompt_text(
        "Chód",
        "Kronikarz odsuwa pergamin i czeka na ostatni szczegół.\n— Jak się poruszasz?",
        GAIT_DEFINITIONS,
    )


def resolve_gait(value: str) -> AppearanceDefinition:
    return _resolve_choice(value, GAIT_DEFINITIONS, "Chód nie może być pusty.", aliases=GAIT_ALIASES)


def _resolve_or_keep_label(value: str, resolver) -> str:
    try:
        return resolver(value).label
    except CharacterCreationError:
        normalized = normalize_text(value)
        if not normalized:
            raise
        return normalized


def _resolve_choice(
    value: str,
    definitions: dict[str, AppearanceDefinition],
    error_message: str,
    *,
    aliases: dict[str, str] | None = None,
) -> AppearanceDefinition:
    normalized = normalize_text(value).lower()
    if not normalized:
        raise CharacterCreationError(error_message)
    if normalized.isdigit():
        index = int(normalized) - 1
        options = list(definitions.values())
        if 0 <= index < len(options):
            return options[index]
    if aliases is not None:
        alias = aliases.get(normalized)
        if alias is not None:
            return definitions[alias]
    if normalized in definitions:
        return definitions[normalized]
    for definition in definitions.values():
        if normalized in {definition.key, normalize_text(definition.label).lower()}:
            return definition
    raise CharacterCreationError(error_message)


def _appearance_prompt_text(title: str, question: str, definitions: dict[str, AppearanceDefinition]) -> str:
    return _choice_prompt_text(title, question, definitions)


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
    gender_description: str
    age: int
    origin: str
    childhood: str
    birth_region: str
    main_profession: str
    secondary_profession: str
    appearance: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "gender_description": self.gender_description,
            "age": self.age,
            "origin": self.origin,
            "childhood": self.childhood,
            "birth_region": self.birth_region,
            "main_profession": self.main_profession,
            "secondary_profession": self.secondary_profession,
            "appearance": self.appearance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CharacterCreationProfile":
        raw_age = data.get("age", 0)
        age_value = raw_age if isinstance(raw_age, (str, int)) else 0
        main_raw = str(data.get("main_profession", "")).strip()
        secondary_raw = str(data.get("secondary_profession", "")).strip()
        selection = build_selection(main_raw, secondary_raw or None) if main_raw else ProfessionSelection("", "")
        return cls(
            name=validate_text("Imię", str(data.get("name", "")), min_length=2, max_length=32),
            gender_description=validate_text("Opis płci", str(data.get("gender_description", "")), min_length=2, max_length=80),
            age=validate_age(age_value),
            origin=resolve_origin(str(data.get("origin", ""))).key,
            childhood=resolve_childhood(str(data.get("childhood", ""))).key if str(data.get("childhood", "")).strip() else "",
            birth_region=_resolve_or_keep_label(str(data.get("birth_region", "")), resolve_birth_region),
            main_profession=selection.main_profession,
            secondary_profession=selection.secondary_profession,
            appearance=validate_text("Wygląd", str(data.get("appearance", "")), min_length=2, max_length=800),
        )

    @classmethod
    def build(
        cls,
        *,
        name: str,
        gender_description: str,
        age: str | int,
        origin: str,
        birth_region: str,
        main_profession: str,
        secondary_profession: str | None,
        appearance: str,
        childhood: str = "",
    ) -> "CharacterCreationProfile":
        resolved_origin = resolve_origin(origin)
        selection = build_selection(main_profession, secondary_profession)
        childhood_definition = resolve_childhood(childhood) if normalize_text(childhood) else None
        return cls(
            name=validate_text("Imię", name, min_length=2, max_length=32),
            gender_description=validate_text("Opis płci", gender_description, min_length=2, max_length=80),
            age=validate_age(age),
            origin=resolved_origin.key,
            childhood=childhood_definition.key if childhood_definition is not None else "",
            birth_region=resolve_birth_region(birth_region).label,
            main_profession=selection.main_profession,
            secondary_profession=selection.secondary_profession,
            appearance=validate_text("Wygląd", appearance, min_length=2, max_length=800),
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
        char.gender_description = self.gender_description
        char.age = self.age
        char.origin = origin.key
        char.childhood = childhood.key if childhood is not None else ""
        char.birth_region = self.birth_region
        char.main_profession = profession_selection.main_profession
        char.secondary_profession = profession_selection.secondary_profession
        char.appearance = self.appearance
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


def build_appearance_summary(
    *,
    name: str,
    gender_description: str,
    build: str,
    height: str,
    hair: str,
    beard: str,
    scars: str,
    eyes: str,
    tattoos: str,
    gait: str,
) -> str:
    parts = [
        f"Przed tobą stoi {validate_text('Opis płci', gender_description, min_length=2, max_length=80)} o imieniu {validate_text('Imię', name, min_length=2, max_length=32)}.",
        f"Ma {height.strip()} i {build.strip()}.",
        f"Włosy nosi {hair.strip()}.",
    ]
    beard_text = normalize_text(beard).lower()
    if beard_text and beard_text not in {"brak", "bez", "nie", "brak brody", "gładko"}:
        parts.append(f"Brodę opisujesz jako {beard.strip()}.")
    elif beard_text:
        parts.append("Twarz ma gładko ogoloną.")
    if scars.strip() and normalize_text(scars).lower() not in {"brak", "nie", "bez", "żadne", "zadne"}:
        parts.append(f"Na twarzy lub ciele nosi ślady: {scars.strip()}.")
    parts.append(f"Oczy ma {eyes.strip()}.")
    if tattoos.strip() and normalize_text(tattoos).lower() not in {"brak", "nie", "bez", "żadne", "zadne"}:
        parts.append(f"Zwracają też uwagę tatuaże: {tattoos.strip()}.")
    if gait.strip():
        parts.append(f"Porusza się {gait.strip()}.")
    return " ".join(parts)


def create_character_from_profile(username: str, profile: CharacterCreationProfile) -> Character:
    return profile.create_character(username)
