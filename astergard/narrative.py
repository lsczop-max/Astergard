from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

from dataclasses import asdict, dataclass, field
from collections import defaultdict
from typing import Iterable, Mapping, Sequence

from astergard.combat.wounds import overall_health_desc

PHASE_LABELS: dict[str, str] = {
    "swit": "świt",
    "poranek": "poranek",
    "poludnie": "południe",
    "popoludnie": "popołudnie",
    "wieczor": "wieczór",
    "noc": "noc",
}


def polish_direction(direction: str) -> str:
    return {
        "polnoc": "północ",
        "poludnie": "południe",
        "wschod": "wschód",
        "zachod": "zachód",
        "polnocny-wschod": "północny wschód",
        "polnocny-zachod": "północny zachód",
        "poludniowy-wschod": "południowy wschód",
        "poludniowy-zachod": "południowy zachód",
        "gora": "górę",
        "dol": "dół",
    }.get(direction, direction)


def describe_time_of_day(hour: int) -> str:
    hour = hour % 24
    if 4 <= hour < 7:
        return "Na murach i dachach leży chłodny, szary blask."
    if 7 <= hour < 11:
        return "Światło jest jeszcze niskie i ostre."
    if 11 <= hour < 15:
        return "Słońce stoi wysoko, a cienie są krótkie."
    if 15 <= hour < 19:
        return "Cienie wydłużają się przy ścianach i drzewach."
    if 19 <= hour < 23:
        return "Wieczorne światło blednie przy krawędziach zabudowań."
    return "Widać głównie kontury, odbicia i lampy."


def describe_weather(weather: str | None) -> str:
    if weather == "slonecznie":
        return "Na kamieniu i dachach widać równy blask."
    if weather == "deszcz":
        return "Krople zbierają się na bruku, deskach i linach."
    if weather == "burza":
        return "Błyski rozcinają niebo nad okolicą."
    if weather == "mgla":
        return "Mgła skraca widok do najbliższych linii."
    if weather == "sniezyca":
        return "Śnieg zasypuje ślady i krawędzie."
    return ""


def describe_season(season: str | None) -> str:
    if season == "wiosna":
        return "Na gałęziach widać świeże liście."
    if season == "lato":
        return "Powietrze stoi ciężej, a kurz łatwiej osiada na ubraniu."
    if season == "jesien":
        return "Liście zbierają się przy murach i w rowach."
    if season == "zima":
        return "Na kamieniu i drewnie widać chłód i szron."
    return ""


def describe_world_state(state: str | None) -> str:
    if state == "wojna":
        return "Przy bramach stoi więcej straży."
    if state == "najazd":
        return "Na deskach i murach widać świeże naprawy."
    if state == "pozar":
        return "Drewno i kamień trzymają jeszcze zapach dymu."
    if state == "epidemia":
        return "Ludzie trzymają większy odstęp."
    if state == "swieto":
        return "Na belkach wiszą wstęgi i chorągwie."
    return ""


def describe_stat(value: int) -> str:
    if value <= 4:
        return "Jeszcze wiele ci brakuje, nim ta cecha stanie się twoją mocą."
    if value <= 8:
        return "Jesteś przeciętny, ale widać już, że potrafisz się rozwijać."
    if value <= 12:
        return "Jesteś mocny i solidny w tym, co ta cecha opisuje."
    if value <= 16:
        return "Masz w sobie wyraźną przewagę nad zwykłymi ludźmi."
    return "Jesteś naprawdę potężny."


def describe_kondycja(current: int, maximum: int) -> str:
    ratio = 0.0 if maximum <= 0 else current / maximum
    if ratio >= 0.9:
        return "Jesteś w pełni sił."
    if ratio >= 0.7:
        return "Masz w sobie lekkie zmęczenie, ale nadal trzymasz rytm."
    if ratio >= 0.5:
        return "Zmęczenie zaczyna osiadać na ruchach i oddechu."
    if ratio >= 0.25:
        return "Jesteś wyczerpany i potrzebujesz chwili wytchnienia."
    if current > 0:
        return "Ledwie trzymasz się na nogach."
    return "Jesteś na granicy upadku."


def describe_skill_level(level: int) -> str:
    if level <= 1:
        return "ledwo znasz podstawy"
    if level <= 3:
        return "opanowałeś podstawy"
    if level <= 5:
        return "radzisz sobie pewnie"
    if level <= 8:
        return "bardzo dobrze to opanowałeś"
    if level <= 12:
        return "mistrzowsko prowadzisz tę umiejętność"
    return "legendarnie władasz tą umiejętnością"


def describe_load(current_weight: float, max_weight: float) -> str:
    if max_weight <= 0:
        return "nie do określenia. Trudno ocenić, ile jeszcze zdołasz unieść."
    ratio = current_weight / max_weight
    if ratio < 0.25:
        return "niewielkie. Niesiesz niewiele i poruszasz się lekko."
    if ratio < 0.5:
        return "umiarkowane. Ładunek jest rozsądny i nie tłumi ci kroku."
    if ratio < 0.75:
        return "duże. Sprzęt zaczyna już wyraźnie ciążyć."
    if ratio < 1.0:
        return "bardzo duże. Nosisz bardzo dużo i każdy krok wymaga uwagi."
    return "przekroczone. Masz na barkach więcej, niż powinieneś dźwigać."


def join_prose(items: list[str]) -> str:
    cleaned = [item for item in items if item]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} i {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f" oraz {cleaned[-1]}"


@dataclass(slots=True)
class RoomNarrative:
    title: str
    body: list[str]

    def render(self) -> str:
        return "\n".join(part for part in [self.title, *self.body] if part).strip()


def health_report(wounds: dict[str, int]) -> str:
    return overall_health_desc(wounds)


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def _title_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _title_case_phrase(text: str) -> str:
    keep_lower = {"za", "przy", "pod", "nad", "obok", "na", "do", "ku", "w", "u", "od"}
    words = []
    for index, word in enumerate(text.split()):
        if index > 0 and word.lower() in keep_lower:
            words.append(word.lower())
        else:
            words.append(_title_case(word))
    return " ".join(words)


_GENITIVE_EXIT_EXCEPTIONS = {
    "karczma": "karczmy",
    "zaułek": "zaułka",
    "tyły": "tyłów",
    "kapliczka": "kapliczki",
    "szeroka": "szerokiej",
    "brukowana": "brukowanej",
    "przydrożna": "przydrożnej",
}

_LOCATIVE_EXIT_EXCEPTIONS = {
    "karczma": "karczmie",
    "zaułek": "zaułku",
    "kapliczka": "kapliczce",
    "szeroka": "szerokiej",
    "brukowana": "brukowanej",
    "przydrożna": "przydrożnej",
}

_EXACT_EXIT_FORMS = {
    ("szeroka brukowana", "locative"): "Szerokiej Brukowanej",
    ("tyły karczmy", "genitive"): "Tyłów Karczmy",
    ("zaułek za karczmą", "genitive"): "Zaułka za Karczmą",
    ("kapliczka przydrożna", "locative"): "Kapliczce Przydrożnej",
    ("karczma pod żurawiem", "genitive"): "Karczmy pod Żurawiem",
    ("mała stajnia", "genitive"): "Małej Stajni",
    ("kuźnia przy murze", "genitive"): "Kuźni przy Murze",
    ("podcienia kupieckie", "genitive"): "Podcieni Kupieckich",
    ("plac przed wartownią", "genitive"): "Placu Przed Wartownią",
    ("dom snycerza", "genitive"): "Domu Snycerza",
    ("dom snycerzy", "genitive"): "Domu Snycerzy",
    ("stary spichlerz", "genitive"): "Starego Spichlerza",
    ("jatki rzeźników", "genitive"): "Jatek Rzeźników",
    ("boczne uliczki placu", "genitive"): "Bocznych Uliczek Placu",
    ("opuszczona chata", "genitive"): "Opuszczonej Chaty",
    ("wschodnia furta łowców", "genitive"): "Wschodniej Furty Łowców",
    ("skład drewna", "genitive"): "Składu Drewna",
    ("zaułek czeladników", "genitive"): "Zaułka Czeladników",
    ("pastwiska", "genitive"): "Pastwisk",
    ("kapliczka podróżnych", "genitive"): "Kapliczki Podróżnych",
    ("kapliczka podróżnych za murem", "genitive"): "Kapliczki Podróżnych za Murem",
    ("kram świecarzy", "genitive"): "Kramu Świecarzy",
    ("warsztat cieśli", "genitive"): "Warsztatu Cieśli",
}


def _inflect_exit_word(word: str, case: str) -> str:
    lowered = word.lower()
    if case == "genitive":
        if lowered in _GENITIVE_EXIT_EXCEPTIONS:
            form = _GENITIVE_EXIT_EXCEPTIONS[lowered]
        elif lowered.endswith("ły"):
            form = lowered[:-2] + "łów"
        elif lowered.endswith("ek"):
            form = lowered[:-2] + "ka"
        elif lowered.endswith("ka"):
            form = lowered[:-2] + "ki"
        elif lowered.endswith("na"):
            form = lowered[:-1] + "ej"
        elif lowered.endswith("a"):
            form = lowered[:-1] + "y"
        else:
            form = lowered
    elif case == "locative":
        if lowered in _LOCATIVE_EXIT_EXCEPTIONS:
            form = _LOCATIVE_EXIT_EXCEPTIONS[lowered]
        elif lowered.endswith("ka"):
            form = lowered[:-2] + "kiej"
        elif lowered.endswith("na"):
            form = lowered[:-1] + "ej"
        elif lowered.endswith("a"):
            form = lowered[:-1] + "iej"
        elif lowered.endswith("ek"):
            form = lowered[:-2] + "ku"
        else:
            form = lowered
    else:
        form = lowered
    return form


def _has_embedded_relation(tokens: list[str]) -> bool:
    return any(token in {"za", "przy", "pod", "nad", "obok", "między", "miedzy", "na", "w", "u"} for token in tokens[1:])


def _simple_plural(noun: str) -> str:
    if not noun:
        return noun
    lowered = noun.lower()
    if lowered.endswith("a"):
        if lowered.endswith(("ka", "ga")):
            return noun[:-1] + "i"
        if lowered.endswith("ia"):
            return noun[:-2] + "ie"
        return noun[:-1] + "y"
    if lowered.endswith("rz"):
        return noun + "e"
    if lowered.endswith("ch"):
        return noun + "y"
    if lowered.endswith(("k", "g", "t", "d", "n", "m", "p", "b", "s", "z", "ł", "r")):
        return noun + "y"
    return noun + "i"


def _direction_phrase(direction: str) -> str:
    return {
        "polnoc": "na północy",
        "poludnie": "na południu",
        "wschod": "na wschodzie",
        "zachod": "na zachodzie",
        "polnocny-wschod": "na północnym wschodzie",
        "polnocny-zachod": "na północnym zachodzie",
        "poludniowy-wschod": "na południowym wschodzie",
        "poludniowy-zachod": "na południowym zachodzie",
        "gora": "u góry",
        "dol": "niżej",
    }.get(direction, f"na {polish_direction(direction)}")


def _narrative_zone(zone: str) -> str:
    return {
        "centrum": "Centrum_Twierdza",
        "trakt": "Trakty",
        "trakt-gorniczy": "Trakty",
        "trakt-nadrzeczny": "Trakty",
        "polnocny-las": "Puszcza_Ciszy",
        "nadrzeczne-mokradla": "Bagna_Hookri",
    }.get(zone, zone)


def _terrain_for_zone(zone: str) -> str:
    zone = _narrative_zone(zone)
    return {
        "Centrum_Twierdza": "miejska",
        "Podgrodzie": "przedmiejska",
        "Haldun": "wiejska",
        "Osada_Mysliwych": "leśna",
        "Forteca_Dungrim": "forteczna",
        "Straznica_Przeleczy": "górska",
        "Trakty": "drogowa",
        "Boczne_Drogi": "drogowa",
        "Puszcza_Ciszy": "leśna",
        "Knieja_Cichych_Sciezek": "leśna",
        "Gory_Mekhara": "górska",
        "Kopalnia_Zelaza": "podziemna",
        "Ruiny_Karshold": "ruin",
        "Jaskinie_Wilkow": "jaskiniowa",
        "Bagna_Hookri": "bagienna",
    }.get(zone, "miejscowa")


def _space_for_zone(zone: str) -> str:
    zone = _narrative_zone(zone)
    return {
        "Centrum_Twierdza": "otwarta przestrzeń",
        "Podgrodzie": "ulica",
        "Haldun": "zabudowania wiejskie",
        "Osada_Mysliwych": "leśna osada",
        "Forteca_Dungrim": "warownia",
        "Straznica_Przeleczy": "przełęcz",
        "Trakty": "szlak",
        "Boczne_Drogi": "szlak",
        "Puszcza_Ciszy": "las",
        "Knieja_Cichych_Sciezek": "las",
        "Gory_Mekhara": "góry",
        "Kopalnia_Zelaza": "podziemia",
        "Ruiny_Karshold": "ruiny",
        "Jaskinie_Wilkow": "jaskinia",
        "Bagna_Hookri": "bagno",
    }.get(zone, "teren")


def _is_indoors(zone: str) -> bool:
    zone = _narrative_zone(zone)
    return zone in {"Forteca_Dungrim", "Kopalnia_Zelaza", "Jaskinie_Wilkow"}


def _is_central_city_zone(zone: str) -> bool:
    zone = _narrative_zone(zone)
    return zone in {"Centrum_Twierdza", "Podgrodzie"}


def _visibility_label(weather: str | None, time_of_day: int, zone: str) -> str:
    if zone in {"Kopalnia_Zelaza", "Jaskinie_Wilkow"}:
        return "ciemność" if time_of_day >= 20 or time_of_day < 6 else "słabe światło"
    if weather in {"mgla", "sniezyca"}:
        return "słaba widoczność"
    if time_of_day >= 20 or time_of_day < 5:
        return "półmrok"
    if time_of_day >= 5 and time_of_day < 8:
        return "światło świtu"
    return "pełne światło"


def _weather_clause(weather: str | None, zone: str, space: str) -> str:
    if weather == "deszcz":
        if _is_indoors(zone):
            return "Deszcz słychać po dachu."
        if space in {"las", "bagno"}:
            return "Deszcz zamienia grunt w maź."
        return "Deszcz moczy bruk i zbiera się w koleinach."
    if weather == "burza":
        if _is_indoors(zone):
            return "Burza tłucze o dach i okna."
        if space in {"las", "bagno"}:
            return "Burza łamie powietrze nad drzewami i wodą."
        return "Burza zwisa nisko nad drogą."
    if weather == "mgla":
        if space == "bagno":
            return "Mgła gubi granice gruntu i wody."
        return "Mgła ścina dalszy plan."
    if weather == "sniezyca":
        if _is_indoors(zone):
            return "Śnieg słychać głównie na dachu i przy szczelinach."
        return "Śnieżyca zaciera ślady."
    if weather == "slonecznie" and not _is_indoors(zone):
        return "Światło jest równe."
    if weather == "slonecznie":
        return "Na zewnątrz jest jasno."
    return ""


def _time_clause(hour: int, zone: str) -> str:
    hour = hour % 24
    if zone in {"Kopalnia_Zelaza", "Jaskinie_Wilkow"}:
        if hour < 6 or hour >= 20:
            return "Tu porę zdradza cisza."
        return "Światło dociera tylko tam, gdzie ktoś je przyniesie."
    if _is_central_city_zone(zone):
        return ""
    if hour < 7:
        return "Świt rozprasza ciemność."
    if hour < 11:
        return "Poranek jest wyraźny i chłodny."
    if hour < 15:
        return "Najmocniejsze światło wydobywa szczegóły z murów i ziemi."
    if hour < 19:
        return "Popołudnie kładzie dłuższe cienie."
    if hour < 23:
        return "Wieczór przygasa na krawędziach zabudowań."
    return "Noc zostawia przede wszystkim światła, odgłosy i kontury."


def _season_clause(season: str | None, zone: str) -> str:
    if season == "zima":
        if zone in {"Bagna_Hookri", "Kopalnia_Zelaza"}:
            return "Zima ściska teren."
        if _is_indoors(zone):
            return "Zima trzyma chłód przy murach."
        return "Zima usztywnia grunt."
    if season == "lato":
        if _is_indoors(zone):
            return "Lato robi wnętrze dusznym."
        if _is_central_city_zone(zone):
            return ""
        return "Lato trzyma ciepło."
    if season == "wiosna":
        return "Wiosna daje zieleń."
    if season == "jesien":
        return "Jesień daje liście."
    return ""


def _state_clause(state: str | None) -> str:
    if state == "wojna":
        return "Wojna daje się tu odczuć w ruchu straży i napięciu ludzi."
    if state == "najazd":
        return "Najazd zostawił pośpiech i łatane ślady."
    if state == "pozar":
        return "Pożar zostawił dym w drewnie i na murach."
    if state == "epidemia":
        return "Epidemia trzyma ludzi na dystans."
    if state == "swieto":
        return "Święto dodaje temu miejscu ruchu i gwaru."
    return ""


def _infer_item_category(item) -> str:
    if hasattr(item, "scene_category"):
        try:
            return item.scene_category()
        except TypeError:
            pass
    return {
        "weapon": "portable_item",
        "armor": "portable_item",
        "shield": "portable_item",
        "food": "portable_item",
        "tool": "portable_item",
        "furniture": "furniture",
        "resource": "resource",
        "corpse": "corpse",
    }.get(getattr(item, "item_type", "misc"), "portable_item")


def _item_surface(category: str) -> str:
    return {
        "portable_item": "na ziemi",
        "corpse": "na ziemi",
        "furniture": "pod ścianą",
        "container": "pod ścianą",
        "resource": "w otoczeniu",
        "fixture": "w otoczeniu",
        "scenery": "w otoczeniu",
    }.get(category, "na ziemi")


def _pluralize_count(count: int, noun: str) -> str:
    if count == 1:
        return noun
    if count == 2:
        return f"dwa {noun}"
    if count == 3:
        return f"trzy {noun}"
    if count == 4:
        return f"cztery {noun}"
    return f"{count} {noun}"


def _render_item_group(category: str, names: list[str]) -> str:
    if not names:
        return ""
    if category in {"furniture", "container"}:
        if len(names) == 1:
            return f"{_item_surface(category).capitalize()} stoi {names[0]}."
        return f"{_item_surface(category).capitalize()} stoją {join_prose(names)}."
    if category in {"resource", "fixture", "scenery"}:
        if len(names) == 1:
            return f"W otoczeniu widać {names[0]}."
        return f"W otoczeniu widać {join_prose(names)}."
    if len(names) == 1:
        return f"Na ziemi leży {names[0]}."
    return f"Na ziemi leżą {join_prose(names)}."


def _render_items(items: Iterable[object]) -> list[str]:
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for item in items:
        name = getattr(item, "display_name", lambda: getattr(item, "name", "nieznany przedmiot"))()
        category = _infer_item_category(item)
        grouped[(category, _item_surface(category))].append(name)
    lines: list[str] = []
    for (category, _surface), names in grouped.items():
        lines.append(_render_item_group(category, names))
    return lines


_SOUND_BY_ZONE = {
    "Centrum_Twierdza": "Z ulicy słychać wozy, nawoływania i szczekanie psów.",
    "Podgrodzie": "Od błotnych ulic dochodzi skrzypienie kół i krzyk ludzi przepychających wozy.",
    "Haldun": "Z pól dochodzi nawoływanie, stuk wideł i gęganie gęsi przy zagrodach.",
    "Osada_Mysliwych": "W osadzie słychać świst noży, szelest skór i krótkie komendy przy psach.",
    "Forteca_Dungrim": "W murach odzywa się stal, kroki wart i krótkie komendy przy bramie.",
    "Straznica_Przeleczy": "Wiatr świszczy w szczelinach skał i przenosi drobny pył.",
    "Trakty": "Kół nie da się tu pomylić z niczym innym; idą ciężko po kamieniach i błocie.",
    "Boczne_Drogi": "Z bocznych dróg dochodzi pojedyncze trzaśnięcie bata, skrzypienie osi i stłumione rozmowy.",
    "Puszcza_Ciszy": "W koronach odzywają się ptaki, a pod nogami szeleszczą liście.",
    "Knieja_Cichych_Sciezek": "Dźwięk urywa się tu szybko między pniami i krzakami.",
    "Gory_Mekhara": "Wiatr świszczy przez skały, a luźne odłamki obijają się o zbocze.",
    "Kopalnia_Zelaza": "Głos odbija się od skał, a z głębi dochodzi skrzypienie drewna.",
    "Ruiny_Karshold": "Wiatr przechodzi przez puste okna i szczeliny murów, poruszając luźne belki.",
    "Jaskinie_Wilkow": "Głos odbija się od skał, a w ciemności słychać szuranie pazurów i kamyków.",
    "Bagna_Hookri": "Słychać pluski, żaby i bulgotanie wody pod trzciną.",
}

_SMELL_BY_ZONE = {
    "Centrum_Twierdza": "W nos uderza dym z palenisk, mokry bruk i zapach pieczywa.",
    "Podgrodzie": "Czuć błoto, mokre płótno i dym z niskich pieców.",
    "Haldun": "Czuć ziemię po orce, siano i chłód wody ze studni.",
    "Osada_Mysliwych": "W powietrzu unosi się żywica, mokra kora i skóra suszona przy dymie.",
    "Forteca_Dungrim": "Pachnie żelazem, smołą i suchym węglem.",
    "Straznica_Przeleczy": "Czuć zimny kamień i ostre powietrze spływające z przełęczy.",
    "Trakty": "W powietrzu czuć kurz, koński pot i dym z mijanych ognisk.",
    "Boczne_Drogi": "Czuć mokrą trawę, kurz z drogi i tłuszcz z rozgrzanych warsztatów.",
    "Puszcza_Ciszy": "W powietrzu unosi się żywica, mokra kora i ziemia po deszczu.",
    "Knieja_Cichych_Sciezek": "Pachnie wilgotnym mchem, liśćmi i cieniem po deszczu.",
    "Gory_Mekhara": "Czuć zimny kamień, ostre powietrze i pył ze skał.",
    "Kopalnia_Zelaza": "Czuć rozgrzany metal, węgiel i pył ze skały.",
    "Ruiny_Karshold": "Pachnie sadzą, popiołem i wilgotnym kamieniem.",
    "Jaskinie_Wilkow": "Pachnie mokrą sierścią, chłodną skałą i starą krwią.",
    "Bagna_Hookri": "Pachnie torfem, stojącą wodą i gnijącą trzciną.",
}

_WEAR_BY_ZONE = {
    "Centrum_Twierdza": "Bruk jest wygładzony przez koła wozów i wiele par butów.",
    "Podgrodzie": "Bruk znika miejscami pod błotem, a krawędzie desek są starte do drzazg.",
    "Haldun": "Ścieżki są wydeptane między zagonami, a żerdzie płotów mają świeże łatki.",
    "Osada_Mysliwych": "Korzenie przecinają przejście, a deski przy suszarni są spatynowane od dymu.",
    "Forteca_Dungrim": "Kamień jest starty od butów, a poręcze mają chropowate, wygładzone odcinki.",
    "Straznica_Przeleczy": "Kamień ma ślady ciężkich butów, a zawiasy noszą rdzę i świeżą smołę.",
    "Trakty": "Koleiny są głębokie, a pobocza wygniecione przez liczne postoje wozów.",
    "Boczne_Drogi": "Krawędzie drogi są rozjeżdżone, a płoty noszą łaty po zimowych naprawach.",
    "Puszcza_Ciszy": "Korzenie przecinają ścieżkę, a podniesione kępy mchu kryją stare ślady butów.",
    "Knieja_Cichych_Sciezek": "Mech i korzenie przykrywają dawne przejścia, zostawiając tylko wątłe nacięcia w ziemi.",
    "Gory_Mekhara": "Kamień jest starty od butów, a zbocza mają świeże osypiska po każdym deszczu.",
    "Kopalnia_Zelaza": "Krawędzie stołów są okopcone, a ściany noszą ślady sadzy i uderzeń.",
    "Ruiny_Karshold": "Mur jest pęknięty, a zwęglone belki leżą tam, gdzie kiedyś prowadził korytarz.",
    "Jaskinie_Wilkow": "Kamień ma rysy po pazurach, a podłoga jest wyszorowana przez wiele przejść zwierząt.",
    "Bagna_Hookri": "Na kępach leżą zbutwiałe gałęzie, a przy wodzie stoją stare paliki.",
}

_LIFE_BY_ZONE = {
    "Centrum_Twierdza": "Na placu ktoś zamyka skrzynię, ktoś inny przelicza monety, a straż przesuwa się przy murze.",
    "Podgrodzie": "Ludzie poprawiają kaptury, przykrywają towary i przepuszczają wozy bliżej palisady.",
    "Haldun": "Rolnicy przenoszą wiadra, poprawiają płoty i zaganiają zwierzęta do zagród.",
    "Osada_Mysliwych": "Łowcy odbierają skóry, liczą sidła i doglądają psów przy palenisku.",
    "Forteca_Dungrim": "Wartownicy zmieniają pozycję, sprawdzają zapasy i wracają pod bramę.",
    "Straznica_Przeleczy": "Komuś trzeba sprawdzić meldunek, komuś innemu roznieść wodę, a jeszcze ktoś dogląda ognia.",
    "Trakty": "Wozy zwalniają przy postojach, a przewodnicy liczą skrzynie i kliny przed kolejnym odcinkiem.",
    "Boczne_Drogi": "Ktoś znika za zakrętem, ktoś poprawia płachtę nad ładunkiem, a psy obwąchują koleinę.",
    "Puszcza_Ciszy": "Jedni zbierają chrust, inni pilnują tropów, a gdzieś dalej ktoś rozbija nocny obóz.",
    "Knieja_Cichych_Sciezek": "Leśnicy i myśliwi zaglądają pod korzenie, sprawdzają ślady i ostrzą noże.",
    "Gory_Mekhara": "Ludzie stawiają kroki ostrożnie, poprawiają pasy i sprawdzają, czy liny trzymają.",
    "Kopalnia_Zelaza": "Górnicy przesuwają wózki, odstawiają lampy i prostują plecy tylko na chwilę.",
    "Ruiny_Karshold": "Ktoś omiata gruz, ktoś inny przerzuca belki, a strażnik nie spuszcza wzroku z przejścia.",
    "Jaskinie_Wilkow": "Zwierzęta i ludzie trzymają się przy ścianach, jakby każdy ruch miał kosztować za dużo.",
    "Bagna_Hookri": "Ludzie poprawiają buty, przechodzą po kępach i sprawdzają, czy torf jeszcze trzyma.",
}

_SCENE_SOUND_BY_PROFILE = {
    "inn_interior": "W sali dźwięczą kufle, rozmowy i krótki śmiech.",
    "inn_back": "Za kuchenną ścianą stuka drewno i brzęczą kufle odkładane po myciu.",
    "square": "Na placu słychać przesuwane skrzynie, wodę w wiadrze i krótkie komendy straży.",
    "passage": "Między fasadami słychać ostrożne kroki i przyciszone nawoływania.",
    "street": "Na ulicy skrzypią wozy, a spod butów sypie się żwir.",
    "forge": "Metal dźwięczy o metal, a miech syczy przy palenisku.",
    "market": "Kupcy przekrzykują się nad ladami, a skrzynie stukają o bruk.",
    "temple_interior": "W świątyni słychać stłumione kroki i pojedyncze szepty.",
    "crossroads": "Na rozstajach turkoczą koła, a z pobocza dochodzą krótkie nawoływania.",
    "roadside_chapel": "Przy kapliczce słychać wiatr, skrzypienie trawy i pojedyncze kroki.",
}

_SCENE_SMELL_BY_PROFILE = {
    "inn_interior": "Pachnie piwem, pieczonym mięsem i mokrym drewnem.",
    "inn_back": "Pachnie tłuszczem, mokrym drewnem i warzywami z kuchni.",
    "square": "W powietrzu miesza się mokry bruk, pył i dym z pobliskich palenisk.",
    "passage": "Pachnie kurzem znad drogi i mokrym tynkiem.",
    "street": "Pachnie pyłem, mokrym brukiem i sadzą z pobliskich palenisk.",
    "forge": "Czuć rozgrzany metal, węgiel i pył ze skały.",
    "market": "Czuć płótno, żelazo i surowe drewno kramów.",
    "temple_interior": "Pachnie woskiem, dymem świec i kwiatami przy niszy.",
    "crossroads": "Pachnie kurzem traktu, mokrą trawą i dymem z ognisk.",
    "roadside_chapel": "Pachnie mokrym kamieniem, kurzem drogi i woskiem z pojedynczej świecy.",
}

_SCENE_WEAR_BY_PROFILE = {
    "inn_interior": "Ławy są wygładzone od łokci, a próg ma rysy od butów.",
    "inn_back": "Deski są śliskie od tłuszczu, a stół ma nacięcia po nożach.",
    "square": "Bruk jest wyślizgany przy krawędzi i popękany od kół oraz butów.",
    "passage": "Próg jest przetarty, a kamień przy ścianach starty od towarów i butów.",
    "street": "Bruk jest wygładzony i popękany koleinami.",
    "forge": "Krawędzie stołów są okopcone, a ściany noszą ślady sadzy i uderzeń.",
    "market": "Lada jest starta od towaru, a bruk nosi ślady kół i ciężkich skrzyń.",
    "temple_interior": "Kamień przy progu jest gładki od butów i odstawianych świec.",
    "crossroads": "Koleiny rozchodzą się w kilka stron, a pobocza są wygniecione przez postoje.",
    "roadside_chapel": "Próg jest wygładzony przez buty i piasek z drogi.",
}

_SCENE_LIFE_BY_PROFILE = {
    "inn_interior": "Karczmarz liczy kufle, a służba znosi czyste szklanki.",
    "inn_back": "Ktoś odkłada kubeł przy ścianie, a ktoś inny czyści kufle przy stole.",
    "square": "Straż przesuwa się przy murze, a handlarze rozkładają skrzynie.",
    "passage": "Kupcy przymykają okiennice, a przechodnie mijają się bokiem.",
    "street": "Przechodnie mijają się szybko, a ktoś odstawia skrzynię przy ścianie.",
    "forge": "Kowal wyciąga żelazo z ognia i zaraz znowu sięga po młot.",
    "market": "Kupcy ważą towar, a przekupki przesuwają skrzynie bliżej przejścia.",
    "temple_interior": "Ktoś odkłada świecę przy niszy i wychodzi bez słowa.",
    "crossroads": "Wozy zwalniają, a przewodnicy liczą skrzynie przed kolejnym odcinkiem.",
    "roadside_chapel": "Podróżni zostawiają drobne dary i ruszają dalej.",
}

_PROFILE_DROPS_TIME_AND_SEASON = {
    "inn_interior",
    "inn_back",
    "square",
    "passage",
    "street",
    "forge",
    "market",
    "temple_interior",
    "crossroads",
    "roadside_chapel",
}


def _scene_profile(scene: "WorldScene") -> str:
    return scene.scene_profile.strip()


def _scene_sound_clause(scene: "WorldScene") -> str:
    profile = _scene_profile(scene)
    if profile in _SCENE_SOUND_BY_PROFILE:
        return _SCENE_SOUND_BY_PROFILE[profile]
    title = scene.title.lower()
    zone = _narrative_zone(scene.zone)
    if zone in {"Centrum_Twierdza", "Podgrodzie"}:
        if "karcz" in title or "zajazd" in title:
            return "Przez salę idą kufle, rozmowy i krótkie wybuchy śmiechu."
        if "kuź" in title:
            return "Metal dźwięczy o metal, a miech syczy przy palenisku."
        if "rynek" in title or "targ" in title:
            return "Kupcy przekrzykują się nad ladami, a skrzynie stukają o bruk."
        if "kaplic" in title or "świąty" in title:
            return "Przy niszy i ławkach słychać tylko stłumione kroki i pojedyncze szepty."
        if "plac" in title or "studnia" in title:
            return "Na placu słychać przesuwane skrzynie, wodę w wiadrze i krótkie komendy straży."
        return ""
    if "karcz" in title or "zajazd" in title:
        return "Przez salę idą kufle, rozmowy i krótkie wybuchy śmiechu."
    if "kuź" in title or zone in {"Forteca_Dungrim"}:
        return "Metal dźwięczy o metal, a miech syczy przy palenisku."
    if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek", "Osada_Mysliwych"}:
        return "W koronach odzywają się ptaki, a pod nogami szeleszczą liście."
    if zone in {"Bagna_Hookri"}:
        return "Słychać pluski, żaby i bulgotanie wody pod trzciną."
    if zone in {"Gory_Mekhara", "Straznica_Przeleczy"}:
        return "Wiatr świszczy w szczelinach skał i przenosi drobny pył."
    if zone in {"Kopalnia_Zelaza", "Jaskinie_Wilkow"}:
        return "Głos odbija się od skał, a z głębi dochodzi skrzypienie drewna."
    if "port" in title or "most" in title:
        return "Lina skrzypi, woda uderza o pale, a ktoś krótko nawołuje z nabrzeża."
    if "staj" in title or "obora" in title:
        return "Konie parskają, a spod żłobu słychać szelest siana."
    return _SOUND_BY_ZONE.get(scene.zone, "W pobliżu słychać kroki, krótkie rozmowy i pojedyncze odgłosy pracy.")


def _scene_smell_clause(scene: "WorldScene") -> str:
    profile = _scene_profile(scene)
    if profile in _SCENE_SMELL_BY_PROFILE:
        return _SCENE_SMELL_BY_PROFILE[profile]
    title = scene.title.lower()
    zone = _narrative_zone(scene.zone)
    if "karcz" in title or "zajazd" in title:
        return "Pachnie piwem, pieczonym mięsem, dymem i mokrym drewnem."
    if "kuź" in title or zone in {"Kopalnia_Zelaza"}:
        return "Czuć rozgrzany metal, węgiel i pył ze skały."
    if zone in {"Centrum_Twierdza", "Podgrodzie"}:
        if "rynek" in title or "targ" in title:
            return "Czuć płótno, żelazo i surowe drewno kramów."
        if "kaplic" in title or "świąty" in title:
            return "Pachnie woskiem, dymem świec i kwiatami przy niszy."
        if "plac" in title or "studnia" in title:
            return "W powietrzu miesza się mokry bruk, pył i dym z pobliskich palenisk."
        return ""
    if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek", "Osada_Mysliwych"}:
        return "W powietrzu unosi się żywica, mokra kora i ziemia po deszczu."
    if zone in {"Bagna_Hookri"}:
        return "Pachnie torfem, stojącą wodą i gnijącą trzciną."
    if zone in {"Gory_Mekhara", "Straznica_Przeleczy"}:
        return "Czuć zimny kamień i ostre powietrze spływające z przełęczy."
    if "staj" in title or "obora" in title:
        return "Pachnie sianem, końską skórą i mokrą deską."
    if zone in {"Centrum_Twierdza", "Podgrodzie", "Haldun"}:
        return "W nos uderza dym z palenisk, mokry bruk i zapach pieczywa."
    return _SMELL_BY_ZONE.get(zone, "W powietrzu czuć kurz, wilgoć i zapach używanego drewna.")


def _scene_wear_clause(scene: "WorldScene") -> str:
    profile = _scene_profile(scene)
    if profile in _SCENE_WEAR_BY_PROFILE:
        return _SCENE_WEAR_BY_PROFILE[profile]
    title = scene.title.lower()
    zone = _narrative_zone(scene.zone)
    if "karcz" in title or "zajazd" in title:
        return "Ławy są wygładzone od łokci, a próg ma rysy od butów."
    if "kuź" in title or zone in {"Kopalnia_Zelaza"}:
        return "Krawędzie stołów są okopcone, a ściany noszą ślady sadzy i uderzeń."
    if zone in {"Centrum_Twierdza", "Podgrodzie"}:
        if "rynek" in title or "targ" in title:
            return "Lada jest starta od towaru, a bruk nosi ślady kół i ciężkich skrzyń."
        if "kaplic" in title or "świąty" in title:
            return "Kamień przy progu jest gładki od butów i odstawianych świec."
        if "plac" in title or "studnia" in title:
            return "Bruk jest wyślizgany przy krawędzi i pocięty przez częsty ruch wzdłuż ścian."
        return ""
    if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek", "Osada_Mysliwych"}:
        return "Korzenie przecinają ścieżkę, a podniesione kępy mchu kryją stare ślady butów."
    if zone in {"Bagna_Hookri"}:
        return "Na kępach leżą zbutwiałe gałęzie, a przy wodzie stoją stare paliki."
    if zone in {"Gory_Mekhara", "Straznica_Przeleczy"}:
        return "Kamień jest starty od butów, a poręcze mają chropowate, wygładzone odcinki."
    if zone in {"Centrum_Twierdza", "Podgrodzie", "Haldun"}:
        return "Bruk jest wygładzony przez koła wozów i wiele par butów."
    return _WEAR_BY_ZONE.get(zone, "Widać ślady używania: starte krawędzie, szorstkie deski i drobne naprawy.")


def _scene_life_clause(scene: "WorldScene") -> str:
    hour = scene.time_of_day % 24
    profile = _scene_profile(scene)
    if profile in _SCENE_LIFE_BY_PROFILE:
        return _SCENE_LIFE_BY_PROFILE[profile]
    title = scene.title.lower()
    zone = _narrative_zone(scene.zone)
    if zone in {"Centrum_Twierdza", "Podgrodzie"}:
        if "karcz" in title or "zajazd" in title:
            return "Karczmarz liczy kufle, a służba znosi czyste szklanki."
        if "kuź" in title:
            return "Kowal wyciąga żelazo z ognia i zaraz znowu sięga po młot."
        if "rynek" in title or "targ" in title:
            return "Kupcy ważą towar, a przekupki przesuwają skrzynie bliżej przejścia."
        if "kaplic" in title or "świąty" in title:
            return "Ktoś zostawia ofiarę przy niszy i odchodzi bez słowa."
        if "plac" in title or "studnia" in title:
            return "Straż przesuwa się przy murze, a handlarze rozkładają skrzynie."
        return ""
    if hour < 7:
        return "Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień."
    if hour < 11:
        if "staj" in title or "obora" in title:
            return "Widać wyprowadzane zwierzęta i świeżą paszę przy żłobie."
        return "Ludzie ustawiają towary, poprawiają płachty i zaczynają pierwszą pracę dnia."
    if hour < 16:
        return "W środku dnia ruch nie zwalnia: jedni kupują, inni noszą, jeszcze inni pilnują porządku."
    if hour < 20:
        return "Wieczorem ktoś przykrywa towary, zamyka okiennice i zapala pierwsze lampy."
    return _LIFE_BY_ZONE.get(zone, "Po zmroku zostają głównie patrole, zamknięte drzwi i zwierzęta śpiące przy ścianach.")


def _render_npc_line(npc, scene: "WorldScene" | None = None) -> str:
    if scene is not None:
        line = getattr(npc, "scene_line", lambda *_args, **_kwargs: getattr(npc, "short_desc", "ktoś"))(
            scene.time_of_day,
            scene.weather,
            scene.zone,
        )
    else:
        line = getattr(npc, "scene_line", lambda *_args, **_kwargs: getattr(npc, "short_desc", "ktoś"))()
    line = str(line).strip()
    if not line.endswith("."):
        line += "."
    return line


def _render_npcs(npcs: Iterable[object], scene: "WorldScene" | None = None) -> list[str]:
    lines = [_render_npc_line(npc, scene) for npc in npcs]
    return lines


def _clean_target_phrase(target: str, kind: str) -> str:
    lowered = target.lower()
    for prefix in (f"{kind} ", "brama ", "drzwi ", "schody ", "tunel ", "most "):
        if lowered.startswith(prefix):
            lowered = lowered.removeprefix(prefix)
            break
    if lowered.startswith("do "):
        lowered = lowered.removeprefix("do ")
    if lowered.startswith("na "):
        lowered = lowered.removeprefix("na ")
    return lowered


def _inflect_exit_target(target: str, case: str = "locative") -> str:
    cleaned = target.strip()
    if not cleaned:
        return ""
    lowered_cleaned = cleaned.lower()
    exact = _EXACT_EXIT_FORMS.get((lowered_cleaned, case))
    if exact is not None:
        return exact
    tokens = cleaned.split()
    if not tokens:
        return ""
    if _has_embedded_relation([token.lower() for token in tokens]):
        head = _inflect_exit_word(tokens[0], "genitive")
        return _title_case_phrase(" ".join([head, *tokens[1:]]))
    if case == "genitive" and len(tokens) == 1 and tokens[0].lower() in {"astergard", "haldun", "dungrim", "karshold", "mekhara", "hookri", "wilkow", "ciszy"}:
        return _title_case_phrase(tokens[0].lower())
    inflected = " ".join(_inflect_exit_word(token, case) for token in tokens)
    return _title_case_phrase(inflected)


def _infer_exit_kind(zone: str, direction: str, location_name: str) -> str:
    zone = _narrative_zone(zone)
    lowered = f"{zone} {location_name}".lower()
    if any(token in lowered for token in ("karcz", "dom", "izb", "sala", "pokoj", "korytarz", "komnata")):
        return "drzwi"
    if any(token in lowered for token in ("bram", "mur", "fort", "twierd", "strazn")):
        return "brama"
    if any(token in lowered for token in ("schody", "schodami", "schodach", "piętr", "pietr", "wieża", "wieza")):
        return "schody"
    if any(token in lowered for token in ("jaskin", "kopal", "tunel", "szyb")):
        return "tunel"
    if any(token in lowered for token in ("most", "pomost", "kład", "klad")):
        return "most"
    if zone in {"Centrum_Twierdza", "Podgrodzie", "Haldun"}:
        return "ulica"
    if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek", "Osada_Mysliwych"}:
        return "ścieżka"
    if zone in {"Trakty", "Boczne_Drogi"}:
        return "trakt"
    if zone in {"Bagna_Hookri"}:
        return "przesmyk"
    return {
        "gora": "wejście",
        "dol": "zejście",
    }.get(direction, "przejście")


def infer_exit_kind(zone: str, direction: str, location_name: str) -> str:
    return _infer_exit_kind(zone, direction, location_name)


def _render_exit_clause(scene, direction: str, exit_) -> str | None:
    if not getattr(exit_, "visible", True):
        return None
    target = scene.target_names.get(direction)
    kind = getattr(exit_, "kind", "") or _infer_exit_kind(scene.zone, direction, scene.title)
    loc_phrase = _direction_phrase(direction)
    lock_phrase = "zamknięte " if getattr(exit_, "is_locked", False) else ""
    target_text = _clean_target_phrase(target, kind) if target else ""
    target_clause = ""
    if target_text:
        direction_forms = scene.exit_forms.get(direction, {})
        prep = direction_forms.get("prep", "")
        if prep == "w stronę":
            target_clause = f"w stronę {direction_forms.get('genitive') or _inflect_exit_target(target_text, 'genitive')}"
        elif prep == "ku":
            target_clause = f"ku {direction_forms.get('dative') or direction_forms.get('locative') or _inflect_exit_target(target_text, 'locative')}"
        elif prep == "do":
            target_clause = f"do {direction_forms.get('genitive') or _inflect_exit_target(target_text, 'genitive')}"
        else:
            tokens = target_text.split()
            if kind in {"drzwi", "brama", "furta"}:
                if _has_embedded_relation([token.lower() for token in tokens]):
                    target_clause = f"w stronę {_inflect_exit_target(target_text, 'genitive')}"
                else:
                    target_clause = f"do {_inflect_exit_target(target_text, 'genitive')}"
            elif kind == "schody":
                target_clause = f"ku {_inflect_exit_target(target_text, 'locative')}"
            elif kind == "tunel":
                target_clause = f"w stronę {_inflect_exit_target(target_text, 'locative')}"
            elif kind == "most":
                target_clause = f"ku {_inflect_exit_target(target_text, 'locative')}"
            elif kind in {"ulica", "ścieżka", "trakt", "przejście", "wejście", "zejście", "przesmyk"}:
                target_clause = f"ku {_inflect_exit_target(target_text, 'locative')}"
            else:
                target_clause = f"w stronę {_inflect_exit_target(target_text, 'genitive')}"
    if kind == "drzwi":
        if target_clause:
            return f"{loc_phrase.capitalize()} {lock_phrase}drzwi prowadzą {target_clause}."
        return f"{loc_phrase.capitalize()} {lock_phrase}drzwi prowadzą dalej."
    if kind == "brama":
        if target_clause:
            return f"{loc_phrase.capitalize()} {lock_phrase}brama prowadzi {target_clause}."
        return f"{loc_phrase.capitalize()} {lock_phrase}brama prowadzi dalej."
    if kind == "furta":
        if target_clause:
            return f"{loc_phrase.capitalize()} furta prowadzi {target_clause}."
        return f"{loc_phrase.capitalize()} furta prowadzi dalej."
    if kind == "schody":
        if target_clause:
            return f"{loc_phrase.capitalize()} schody prowadzą {target_clause}."
        return f"{loc_phrase.capitalize()} schody prowadzą {('wyżej' if direction == 'gora' else 'niżej') }."
    if kind == "tunel":
        if target_clause:
            return f"{loc_phrase.capitalize()} tunel niknie {target_clause}."
        return f"{loc_phrase.capitalize()} tunel niknie w ciemności."
    if kind == "most":
        if target_clause:
            return f"{loc_phrase.capitalize()} most prowadzi {target_clause}."
        return f"{loc_phrase.capitalize()} most przecina dalszą część terenu."
    if kind == "ulica":
        if target_clause:
            return f"{loc_phrase.capitalize()} ulica prowadzi {target_clause}."
        return f"{loc_phrase.capitalize()} ulica ciągnie się dalej."
    if kind in {"ścieżka", "trakt", "przejście", "wejście", "zejście", "przesmyk"}:
        if target_clause:
            return f"{loc_phrase.capitalize()} {kind} wiedzie {target_clause}."
        return f"{loc_phrase.capitalize()} {kind} ciągnie się dalej."
    if target_clause:
        return f"{loc_phrase.capitalize()} prowadzi przejście {target_clause}."
    return f"{loc_phrase.capitalize()} prowadzi przejście dalej."


@dataclass(slots=True)
class WorldScene:
    title: str
    description: str
    zone: str
    terrain: str
    space: str
    time_of_day: int
    season: str | None
    weather: str | None
    world_state: str | None
    visibility: str
    lighting: str
    perspective: str
    temperature: str
    target_names: Mapping[str, str]
    exit_forms: Mapping[str, Mapping[str, str]]
    exits: Mapping[str, object]
    items: Sequence[object]
    npcs: Sequence[object]
    scene_profile: str = ""
    notable_elements: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScenePlan:
    paragraphs: list[str]


def build_world_scene(
    *,
    title: str,
    description: str,
    zone: str,
    time_of_day: int,
    season: str | None,
    weather: str | None,
    world_state: str | None,
    perspective: str,
    exits: Mapping[str, object],
    items: Sequence[object],
    npcs: Sequence[object],
    target_names: Mapping[str, str],
    exit_forms: Mapping[str, Mapping[str, str]] | None = None,
    scene_profile: str = "",
) -> WorldScene:
    terrain = _terrain_for_zone(zone)
    space = _space_for_zone(zone)
    visibility = _visibility_label(weather, time_of_day, zone)
    lighting = describe_time_of_day(time_of_day)
    temperature = "chłód" if weather in {"mgla", "sniezyca"} or time_of_day < 8 else "umiarkowane"
    return WorldScene(
        title=title,
        description=description,
        zone=zone,
        terrain=terrain,
        space=space,
        time_of_day=time_of_day,
        season=season,
        weather=weather,
        world_state=world_state,
        visibility=visibility,
        lighting=lighting,
        perspective=perspective,
        temperature=temperature,
        target_names=target_names,
        exit_forms=exit_forms or {},
        exits=exits,
        items=items,
        npcs=npcs,
        scene_profile=scene_profile,
    )


def render_world_scene(scene: WorldScene, *, mode: str = "standard") -> str:
    body: list[str] = [scene.title]
    visibility_note = ""
    scene_profile = _scene_profile(scene)
    if scene.visibility == "ciemność":
        visibility_note = "Widzisz głównie najbliższe kontury."
    elif scene.visibility == "słaba widoczność":
        visibility_note = "Dalszy plan ginie w półmroku."
    elif scene.visibility == "półmrok":
        visibility_note = "Mrok skraca widok."
    elif scene.visibility == "światło niesione":
        visibility_note = "Światło trzymasz przy sobie."
    if mode == "short":
        intro_parts = [scene.description.strip().rstrip(".")]
        if scene_profile not in _PROFILE_DROPS_TIME_AND_SEASON:
            intro_parts.append(_time_clause(scene.time_of_day, scene.zone).rstrip("."))
        if visibility_note:
            intro_parts.append(visibility_note.rstrip("."))
        body.append(". ".join(intro_parts) + ".")
        life_parts = [part for part in [_scene_sound_clause(scene), _scene_smell_clause(scene)] if part]
        if life_parts:
            body.append(" ".join(life_parts))
        snippets = _render_items(scene.items)
        if snippets:
            body.append(snippets[0])
        npc_lines = _render_npcs(scene.npcs, scene)
        if npc_lines:
            body.append(" ".join(npc_lines[:2]))
        exit_lines = [line for direction, exit_ in scene.exits.items() if (line := _render_exit_clause(scene, direction, exit_))]
        if exit_lines:
            body.append(" ".join(exit_lines[:2]))
        return "\n".join(part for part in body if part).strip()

    intro_parts = [scene.description.strip().rstrip(".")]
    clauses: list[str] = []
    if scene_profile not in _PROFILE_DROPS_TIME_AND_SEASON:
        clauses.append(_time_clause(scene.time_of_day, scene.zone))
        clauses.append(_season_clause(scene.season, scene.zone))
    clauses.extend([
        _weather_clause(scene.weather, scene.zone, scene.space),
        _state_clause(scene.world_state),
        visibility_note,
    ])
    for clause in clauses:
        if clause:
            intro_parts.append(clause.rstrip("."))
    body.append(". ".join(intro_parts).strip() + ".")
    life_parts = [part for part in [_scene_sound_clause(scene), _scene_smell_clause(scene), _scene_wear_clause(scene), _scene_life_clause(scene)] if part]
    if life_parts:
        body.append(" ".join(life_parts))

    if scene.visibility == "ciemność":
        body.append("Widzisz tylko najbliższe zarysy.")
    else:
        detail_lines = _render_items(scene.items)
        if detail_lines:
            body.extend(detail_lines)

        npc_lines = _render_npcs(scene.npcs, scene)
        if npc_lines:
            body.append(" ".join(npc_lines))

    exit_lines = [line for direction, exit_ in scene.exits.items() if (line := _render_exit_clause(scene, direction, exit_))]
    if exit_lines:
        body.append(" ".join(exit_lines))

    return "\n".join(part for part in body if part).strip()


def _build_narrative_generator():
    from astergard.location_narrative.generator import LocationNarrativeGenerator
    from astergard.world.manager import WorldManager

    world = WorldManager()
    world.generate_world()
    return LocationNarrativeGenerator.default(world), world


def _result_payload(result) -> dict[str, object]:
    payload = asdict(result)
    payload["validation_report"] = asdict(result.validation_report)
    payload["draft_trace"] = [asdict(record) for record in result.draft_trace]
    return payload


def _pilot_location_ids(world) -> tuple[int, ...]:
    buckets = {
        "Centrum_Twierdza": [0, 2, 14, 21, 25],
        "Puszcza_Ciszy": [210, 216, 223, 230, 246],
        "Bagna_Hookri": [475, 480, 485, 490, 495],
        "Gory_Mekhara": [335, 340, 345, 350, 355],
        "Ruiny_Karshold": [425, 430, 435, 440, 445],
        "Kopalnia_Zelaza": [390, 395, 400, 405, 410],
    }
    ids: list[int] = []
    for group in buckets.values():
        ids.extend(group)
    return tuple(id_ for id_ in ids if world.get_location(id_) is not None)[:30]


def _cli_audit_world(output: str | None = None) -> int:
    generator, world = _build_narrative_generator()
    results = [generator.generate(location_id) for location_id in _pilot_location_ids(world)]
    payload = {
        "generator_version": results[0].generator_version if results else "",
        "pilot_size": len(results),
        "average_score": round(sum(result.quality_score for result in results) / len(results), 2) if results else 0,
        "median_score": median([result.quality_score for result in results]) if results else 0,
        "accepted": sum(1 for result in results if result.validation_report.is_accepted),
        "rejected": sum(1 for result in results if not result.validation_report.is_accepted),
        "results": [result.location_id for result in results],
    }
    if output:
        Path(output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _cli_generate_location(location_id: int, output: str | None = None, manual: str | None = None, dry_run: bool = False) -> int:
    generator, _world = _build_narrative_generator()
    result = generator.generate(location_id, manual_description=manual)
    payload = json.dumps(_result_payload(result), ensure_ascii=False, indent=2)
    if output and not dry_run:
        Path(output).write_text(payload, encoding="utf-8")
    print(payload)
    return 0


def _cli_generate_area(area_id: str, output: str | None = None, dry_run: bool = False) -> int:
    generator, world = _build_narrative_generator()
    location_ids = tuple(loc.id for loc in world.locations.values() if loc.zone == area_id)
    results = [generator.generate(location_id) for location_id in location_ids[:30]]
    payload = json.dumps([_result_payload(result) for result in results], ensure_ascii=False, indent=2)
    if output and not dry_run:
        Path(output).write_text(payload, encoding="utf-8")
    print(payload)
    return 0


def _cli_critique_location(location_id: int) -> int:
    generator, _world = _build_narrative_generator()
    result = generator.generate(location_id)
    print(
        json.dumps(
            {
                "location_id": location_id,
                "quality_score": result.quality_score,
                "critical_errors": list(result.validation_report.critical_errors),
                "warnings": list(result.validation_report.warnings),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _cli_compare(loc_a: int, loc_b: int) -> int:
    generator, _world = _build_narrative_generator()
    left = generator.generate(loc_a)
    right = generator.generate(loc_b)
    from astergard.location_narrative.generator import compare_location_results

    print(json.dumps(compare_location_results(left, right), ensure_ascii=False, indent=2))
    return 0


def _cli_similarity_report(area_id: str, output: str | None = None) -> int:
    generator, world = _build_narrative_generator()
    location_ids = [loc.id for loc in world.locations.values() if loc.zone == area_id]
    results = [generator.generate(location_id) for location_id in location_ids]
    scores = []
    for index, left in enumerate(results):
        for right in results[index + 1 :]:
            from astergard.location_narrative.generator import compare_location_results

            scores.append(compare_location_results(left, right)["similarity"])
    payload = {
        "area_id": area_id,
        "count": len(results),
        "average_similarity": round(sum(scores) / len(scores), 3) if scores else 0.0,
        "worst_similarity": round(min(scores), 3) if scores else 0.0,
    }
    if output:
        Path(output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _cli_export_review(area_id: str, output: str | None = None) -> int:
    generator, world = _build_narrative_generator()
    results = [generator.generate(location.id) for location in world.locations.values() if location.zone == area_id]
    from astergard.location_narrative.generator import export_review

    path = export_review(results, output or f"{area_id}_review.json")
    print(str(path))
    return 0


def _cli_apply_approved(review_file: str) -> int:
    from astergard.location_narrative.generator import load_review

    payload = load_review(review_file)
    approved = [entry for entry in payload if entry.get("validation_report", {}).get("critical_errors") in ([], (), None)]
    target = Path(review_file).with_suffix(".approved.json")
    target.write_text(json.dumps(approved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(target))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m astergard.narrative")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit-world")
    audit.add_argument("--output")

    generate_location = subparsers.add_parser("generate-location")
    generate_location.add_argument("location_id", type=int)
    generate_location.add_argument("--output")
    generate_location.add_argument("--manual")
    generate_location.add_argument("--dry-run", action="store_true")

    generate_area = subparsers.add_parser("generate-area")
    generate_area.add_argument("area_id")
    generate_area.add_argument("--output")
    generate_area.add_argument("--dry-run", action="store_true")

    critique = subparsers.add_parser("critique-location")
    critique.add_argument("location_id", type=int)

    compare = subparsers.add_parser("compare")
    compare.add_argument("loc_a", type=int)
    compare.add_argument("loc_b", type=int)

    similarity = subparsers.add_parser("similarity-report")
    similarity.add_argument("area_id")
    similarity.add_argument("--output")

    export = subparsers.add_parser("export-review")
    export.add_argument("area_id")
    export.add_argument("--output")

    apply_review = subparsers.add_parser("apply-approved")
    apply_review.add_argument("review_file")

    args = parser.parse_args(argv)
    if args.command == "audit-world":
        return _cli_audit_world(args.output)
    if args.command == "generate-location":
        return _cli_generate_location(args.location_id, args.output, args.manual, args.dry_run)
    if args.command == "generate-area":
        return _cli_generate_area(args.area_id, args.output, args.dry_run)
    if args.command == "critique-location":
        return _cli_critique_location(args.location_id)
    if args.command == "compare":
        return _cli_compare(args.loc_a, args.loc_b)
    if args.command == "similarity-report":
        return _cli_similarity_report(args.area_id, args.output)
    if args.command == "export-review":
        return _cli_export_review(args.area_id, args.output)
    if args.command == "apply-approved":
        return _cli_apply_approved(args.review_file)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
