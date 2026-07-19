from __future__ import annotations

from dataclasses import dataclass, field
import random
from uuid import uuid4
from typing import TypedDict, cast

from astergard.characters.models import Character, CharacterStats
from astergard.items.models import (
    Item,
    baker_shop_inventory,
    blacksmith_shop_inventory,
    karczmarz_shop_inventory,
    karczmarka_shop_inventory,
    dungrim_armory_inventory,
    dungrim_kitchen_inventory,
    dungrim_quartermaster_inventory,
    dungrim_stable_inventory,
    haldun_forge_inventory,
    haldun_market_inventory,
    haldun_mill_inventory,
    fisher_shop_inventory,
    innkeeper_shop_inventory,
    merchant_shop_inventory,
    butcher_shop_inventory,
    skin_trader_shop_inventory,
    tanner_shop_inventory,
    bagna_herbal_inventory,
    bagna_hermit_inventory,
    puszcza_herbal_inventory,
    puszcza_hermit_inventory,
    puszcza_hunter_inventory,
    straznica_caravan_inventory,
    straznica_hunter_inventory,
    straznica_supply_inventory,
    trakty_caravan_inventory,
    trakty_courier_inventory,
    trakty_hunter_inventory,
    trakty_lumber_inventory,
    trakty_route_inventory,
    vendor_shop_inventory,
)
from astergard.npcs.combat_profiles import combat_style_for_vnum
from astergard.npcs.threat import apply_threat_profile, threat_for_vnum
from astergard.state import NPC_STATE_MACHINE, NPCState, parse_npc_state


def _phase_from_hour(hour: int | None) -> str:
    if hour is None:
        return "dzień"
    hour = hour % 24
    if 4 <= hour < 7:
        return "świt"
    if 7 <= hour < 11:
        return "poranek"
    if 11 <= hour < 16:
        return "dzień"
    if 16 <= hour < 20:
        return "wieczór"
    return "noc"


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def _pick_fragment(options: tuple[str, ...], key: str) -> str:
    if not options:
        return ""
    return random.choice(options)


def _is_compound_activity(text: str) -> bool:
    lowered = text.lower()
    return " i " in lowered or ", " in lowered or " oraz " in lowered


def _single_activity_clause(text: str, *, prefer_last: bool = False) -> str:
    clause = text.strip().rstrip(".")
    for separator in (" oraz ", " i ", ","):
        if separator in clause:
            clause = clause.split(separator, 1)[-1 if prefer_last else 0].strip()
    return clause


_SCENE_FRAGMENTS: dict[str, dict[str, tuple[str, ...]]] = {
    "świt": {
        "default": (
            "otwiera okiennice",
            "zamiata próg",
            "sprawdza zamki",
        ),
        "deszcz": (
            "strząsa wodę z kaptura",
            "przykrywa towary płótnem",
            "domyka okiennice",
        ),
        "wiatr": (
            "przytrzymuje płaszcz przed podmuchem",
            "poprawia chorągiewkę",
            "dociska skrzynię do ściany",
        ),
        "mróz": (
            "trze dłonie i dmucha w palce",
            "rozbija cienki lód na kałuży",
            "sprawdza, czy woda w wiadrze nie zamarzła",
        ),
        "upał": (
            "otwiera szerzej drzwi",
            "szuka cienia pod okapem",
            "zwalnia krok, zanim słońce dobrze wejdzie na bruk",
        ),
    },
    "dzień": {
        "default": (
            "układa towary",
            "przelicza monety",
            "wyciera blat",
            "sprawdza zapasy",
            "nawołuje klientów",
            "obchodzi plac",
            "naprawia uprząż",
        ),
        "deszcz": (
            "ściąga kaptur nisko na czoło",
            "przykrywa skrzynki płótnem",
            "zbiera towar spod okapu",
        ),
        "wiatr": (
            "przytrzymuje drzwi",
            "prostuje szyld",
            "dociska płachtę do lady",
        ),
        "mróz": (
            "rozgrzewa dłonie nad kubkiem",
            "dmucha w palce",
            "otrząsa szron z płaszcza",
        ),
        "upał": (
            "przenosi pracę w cień",
            "otwiera szerzej okno",
            "zwalnia tempo i ociera pot z czoła",
        ),
    },
    "wieczór": {
        "default": (
            "przykrywa towary płótnem",
            "zamyka okiennice",
            "zapala pochodnię",
            "zlicza zapasy",
            "odprowadza gości",
        ),
        "deszcz": (
            "osłania wejście przed deszczem",
            "otrząsa wodę z ramion",
            "przesuwa skrzynki pod dach",
        ),
        "wiatr": (
            "sprawdza zasuwę przy drzwiach",
            "podnosi kołnierz",
            "przywiązuje luźną płachtę",
        ),
        "mróz": (
            "dokłada drewna do paleniska",
            "zamyka szczelniej wejście",
            "ustawia świecę bliżej okna",
        ),
        "upał": (
            "zostawia otwarte okno",
            "przesiada się bliżej chłodniejszej ściany",
            "powoli porządkuje ladę, zanim zrobi się duszno",
        ),
    },
    "noc": {
        "default": (
            "patroluje przejście",
            "nasłuchuje kroków",
            "dogląda ognia",
            "zamyka drzwi po ostatnich gościach",
            "siedzi przy ścianie i czeka na zmianę",
        ),
        "deszcz": (
            "patrzy przez mokrą szybę",
            "nasłuchuje deszczu na dachu",
            "trzyma się bliżej ognia",
        ),
        "wiatr": (
            "sprawdza zasuwę i zasłony",
            "przytrzymuje płonącą latarnię",
            "zamyka okiennice, nim podmuch je wyrwie",
        ),
        "mróz": (
            "rozgrzewa dłonie przy ogniu",
            "dmucha na palce",
            "zaciąga płaszcz ciaśniej pod szyję",
        ),
        "upał": (
            "stoi przy otwartym oknie",
            "szuka chłodu przy progu",
            "odsuwa krzesło od dusznej ściany",
        ),
    },
}


def _weather_hint(weather: str | None) -> str:
    if weather == "deszcz":
        return "deszcz"
    if weather == "burza":
        return "wiatr"
    if weather == "mgla":
        return "noc"
    if weather == "sniezyca":
        return "mróz"
    if weather == "slonecznie":
        return "upał"
    return "default"


@dataclass(slots=True)
class NPC:
    vnum: str
    name: str
    short_desc: str
    long_desc: str
    zone: str
    faction: str
    ai_state: str = "IDLE"
    room_id: int = 0
    character: Character = field(default_factory=lambda: Character("npc"))
    is_merchant: bool = False
    shop_inventory: list[Item] = field(default_factory=list)
    merchant_gold: int = 100
    id: str = field(default_factory=lambda: uuid4().hex)
    dialogue_tree: dict[str, list[str]] = field(default_factory=dict)
    home_room_id: int = 0
    respawn_delay_seconds: int = 300
    threat_tier: str = "standard"
    threat_label: str = "standardowy przeciwnik"
    daily_schedule: dict[str, str] = field(default_factory=dict)
    daily_activity: str = ""
    daily_target_room_id: int | None = None
    daily_phase: str = ""
    presentation_category: str = "npc"
    scene_position: str | None = None
    forms: dict[str, str] = field(default_factory=dict)

    def transition_ai_state(self, target: str | NPCState) -> None:
        current = parse_npc_state(self.ai_state)
        next_state = parse_npc_state(target)
        self.ai_state = NPC_STATE_MACHINE.validate(current, next_state).value

    def dialogue(self, topic: str = "default", reputation: int = 0) -> str:
        lines = self.dialogue_tree.get(topic) or self.dialogue_tree.get("default") or ["Milczy."]
        if reputation < 0 and len(lines) > 1:
            return lines[1]
        if reputation > 4 and len(lines) > 2:
            return lines[2]
        return lines[0]

    def scene_line(self, time_of_day: int | None = None, weather: str | None = None, zone: str | None = None) -> str:
        base = self.short_desc.strip().rstrip(".")
        phase = self.daily_phase or _phase_from_hour(time_of_day)
        raw_activity = self.daily_activity
        prefer_last = phase in {"wieczór", "noc"}
        _ = _weather_hint(weather)
        _ = zone or self.zone
        activity = _single_activity_clause(raw_activity, prefer_last=prefer_last)
        if not activity:
            activity = _single_activity_clause(self.daily_schedule.get(phase, self.daily_schedule.get("dzień", "")), prefer_last=prefer_last)
        if self.vnum == "podgrodzie_kowal" and phase == "noc" and raw_activity:
            return f"Kowal {_lower_first(_single_activity_clause(raw_activity, prefer_last=False))}."
        if self.vnum == "traveler" and (zone == "Centrum_Twierdza" or self.zone == "Centrum_Twierdza"):
            chapel_activity = {
                "świt": "kładzie monetę w niszy",
                "dzień": "zapala świecę przy kapliczce",
                "wieczór": "składa dłonie przy kapliczce",
                "noc": "stoi w ciszy przy niszy",
            }.get(phase, "kładzie monetę w niszy")
            return f"{base}, {chapel_activity}."
        if activity:
            return f"{base}, {_lower_first(activity)}."
        return base


class NPCFactory:
    def _finalize(self, npc: NPC) -> NPC:
        profile = threat_for_vnum(npc.vnum)
        npc.threat_tier = profile.tier
        npc.threat_label = profile.label
        npc.respawn_delay_seconds = max(30, int(npc.respawn_delay_seconds * profile.respawn_multiplier))
        if not npc.daily_schedule:
            npc.daily_schedule = self._daily_schedule_for(npc.vnum)
        if not npc.dialogue_tree:
            npc.dialogue_tree = {
                "default": [
                    f"{npc.name.capitalize()} mierzy cię spojrzeniem i wraca do swoich spraw.",
                    f"{npc.name.capitalize()} odpowiada niechętnie, jak ktoś przyzwyczajony do nieproszonych pytań.",
                    f"{npc.name.capitalize()} po chwili mięknie i zdradza odrobinę więcej, niż planował.",
                ],
                "praca": [
                    f"{npc.name.capitalize()} mówi o robocie bez ozdób, jak ktoś, kto wie, ile kosztuje dzień spóźnienia.",
                    f"{npc.name.capitalize()} dodaje kilka szczegółów o codziennym trudzie i narzędziach.",
                    f"{npc.name.capitalize()} opowiada o pracy tak, jakby była częścią pogody w tym miejscu.",
                ],
                "miejsce": [
                    f"{npc.name.capitalize()} zna te przejścia lepiej niż własne buty.",
                    f"{npc.name.capitalize()} wskazuje skróty, zdradliwe przejścia i rzeczy, których lepiej nie dotykać.",
                    f"{npc.name.capitalize()} wspomina historię miejsca tak, jakby sam ją tu przechowywał.",
                ],
                "plotki": [
                    f"{npc.name.capitalize()} nie ufa plotkom, ale coś jednak słyszał.",
                    f"{npc.name.capitalize()} podaje jedną świeżą wieść i jedną, której woli nie powtarzać głośno.",
                    f"{npc.name.capitalize()} dorzuca jeszcze nazwisko, miejsce i połowę prawdy.",
                ],
            }
        apply_threat_profile(npc.character, profile)
        return npc

    def _social_dialogue(
        self,
        default: str,
        praca: str,
        miejsce: str,
        plotki: str,
        **extra: str,
    ) -> dict[str, list[str]]:
        tree = {
            "default": [default],
            "praca": [praca],
            "miejsce": [miejsce],
            "plotki": [plotki],
        }
        for topic, line in extra.items():
            tree[topic] = [line]
        return tree

    def _daily_schedule_for(self, vnum: str) -> dict[str, str]:
        specific_schedules: dict[str, dict[str, str]] = {
            "astergard_guard": {
                "świt": "Obchodzi bramę i sprawdza, czy bruk jest czysty po nocy.",
                "dzień": "Patroluje plac i zagląda w boczne przejścia.",
                "wieczór": "Wraca pod bramę i zamyka ruch na szlaku.",
                "noc": "Siedzi przy wartowni i nasłuchuje kroków za murem.",
            },
            "watch_sergeant": {
                "świt": "Liczy zmianę i idzie od placu do koszar.",
                "dzień": "Sprawdza posterunki i wraca po meldunki.",
                "wieczór": "Przechodzi przez dziedziniec i zamyka odprawę.",
                "noc": "Wraca do wartowni i pilnuje ciszy w koszarach.",
            },
            "innkeeper": {
                "świt": "Otwiera karczmę i ustawia stoły przy wejściu.",
                "dzień": "Obsługuje gości, dogląda sali i wraca po beczki.",
                "wieczór": "Siedzi przy ladzie i liczy kufle przed zamknięciem.",
                "noc": "Wraca na zaplecze i gasi światło w sali.",
            },
            "merchant": {
                "świt": "Rozstawia kram przy bramie i sprawdza ceny.",
                "dzień": "Przechodzi między placem a kramem, szukając kupujących.",
                "wieczór": "Zamyka stoisko i wraca z towarem do składu.",
                "noc": "Liczy monety i siedzi przy zamkniętym kramie.",
            },
            "customs_clerk": {
                "świt": "Idzie od bramy do kancelarii i układa księgi.",
                "dzień": "Przyjmuje listy i wraca po kolejne wpisy.",
                "wieczór": "Obchodzi magazyn i zamyka rachunki.",
                "noc": "Wraca do izby przy kantorze i odkłada pieczęcie.",
            },
            "dockhand": {
                "świt": "Idzie nad nabrzeże i rozplątuje liny przy łodziach.",
                "dzień": "Nosi skrzynie między pomostem a składami.",
                "wieczór": "Wraca z portu ciężkim krokiem i czyści dłonie z soli.",
                "noc": "Siedzi przy nabrzeżu i pilnuje cum przed snem.",
            },
            "fishmonger": {
                "świt": "Wystawia ryby na targu i idzie po świeży połów.",
                "dzień": "Krąży między targiem a szopą rybaków.",
                "wieczór": "Zawija towar i wraca do chłodni przy wodzie.",
                "noc": "Zamyka stragan i liczy, ile ryb wróci jutro.",
            },
            "fisherman": {
                "świt": "Schodzi nad wodę z sieciami i wraca na pomost.",
                "dzień": "Sprzedaje część połowu i znika po kolejne ryby.",
                "wieczór": "Wraca do szopy nad rzeką i naprawia sieci.",
                "noc": "Siedzi przy nabrzeżu i suszy liny po pracy.",
            },
            "beggar": {
                "świt": "Przenosi się spod muru pod lepszy kąt przy rynku.",
                "dzień": "Siedzi przy placu i wraca tam, gdzie ludzie częściej rzucają drobne.",
                "wieczór": "Idzie pod osłonę bramy i szuka suchego kąta.",
                "noc": "Wraca pod mur i zwija lichy koc do snu.",
            },
            "traveler": {
                "świt": "Rusza od bramy do karczmy i sprawdza, czy droga jest bezpieczna.",
                "dzień": "Krąży między targiem a przystankiem, szukając wieści o szlaku.",
                "wieczór": "Wraca pod karczmę i szuka noclegu przed zmrokiem.",
                "noc": "Śpi przy zajeździe i szykuje sakwy na rano.",
            },
            "child": {
                "świt": "Wybiega na podwórko i wraca przed pierwszym tłokiem na placu.",
                "dzień": "Biega między straganami i wraca do domu po południu.",
                "wieczór": "Siedzi przy progu i wraca na podwórko, gdy zaczyna się ściemniać.",
                "noc": "Wraca pod dach i zasypia blisko pieca.",
            },
            "urchin": {
                "świt": "Wysuwa się z zaułka i sprawdza, co zostało na targu.",
                "dzień": "Kręci się przy kramach i wraca po chwili do bezpieczniejszej uliczki.",
                "wieczór": "Znika przy murze i wraca do kryjówki przed nocą.",
                "noc": "Śpi tam, gdzie nie dosięga wiatr z bramy.",
            },
            "priest_aide": {
                "świt": "Idzie do kapliczki i wraca z wodą oraz świecami.",
                "dzień": "Dogląda porządku przy świątyni i odwiedza cmentarzyk.",
                "wieczór": "Wraca po zapasy do zakrystii i zamyka drzwi.",
                "noc": "Zasypia przy kaplicy i pilnuje ciszy.",
            },
            "carpenter": {
                "świt": "Otwiera warsztat i idzie po drewno z placu składowego.",
                "dzień": "Pracuje przy ławie i wraca po nowe deski.",
                "wieczór": "Odkłada narzędzia i wraca do domu z trocinami na rękawach.",
                "noc": "Siedzi przy warsztacie i liczy zlecenia na jutro.",
            },
            "tanner": {
                "świt": "Sprawdza skóry na podwórzu i wraca po sól do składu.",
                "dzień": "Pracuje przy beczkach i idzie na plac po kolejne skóry.",
                "wieczór": "Chowa skóry do zadaszenia i wraca do domu.",
                "noc": "Myje ręce i siedzi przy zamkniętej garbarni.",
            },
            "armorer": {
                "świt": "Idzie do magazynu po hełmy i wraca do stołu naprawczego.",
                "dzień": "Dopasowuje pancerze i kontroluje stan zbroi.",
                "wieczór": "Wraca do warsztatu i zamyka stojaki z ochroną.",
                "noc": "Liczy klamry i odkłada skórzane pasy pod dach.",
            },
            "woodcutter": {
                "świt": "Idzie po drewno do składu i wraca z wiązką na barku.",
                "dzień": "Pracuje przy pile i nosi drewno na plac.",
                "wieczór": "Zamyka robotę i wraca z ostrzem pod pachą.",
                "noc": "Siedzi przy stercie pni i ostrzy topór.",
            },
            "puszcza_szczur": {
                "świt": "Przemyka przy korzeniach i wraca do ściółki.",
                "dzień": "Szuka resztek przy obozach i wraca pod zwalone gałęzie.",
                "wieczór": "Krąży przy kamieniach i wraca do kryjówki przed zmrokiem.",
                "noc": "Siedzi cicho pod korzeniem i czeka na ciszę.",
            },
            "puszcza_kruk": {
                "świt": "Zrywa się z gałęzi i wraca na wyższy konar.",
                "dzień": "Obserwuje polanę i wraca tam, gdzie widać więcej niż ludziom.",
                "wieczór": "Kracze nad ścieżką i wraca do gniazda.",
                "noc": "Kuli pióra i drzemiąc czeka na świt.",
            },
            "puszcza_lis": {
                "świt": "Obchodzi skraj polany i wraca do nory.",
                "dzień": "Poluje na drobne zwierzęta i wraca do gęstwiny.",
                "wieczór": "Krąży przy śladach ludzi i wraca przed nocą.",
                "noc": "Leży w bezpiecznej jamie i słucha lasu.",
            },
            "puszcza_pies_dziki": {
                "świt": "Obwąchuje ścieżkę i wraca do pniaka.",
                "dzień": "Węszy przy obozie i wraca na krótki postój.",
                "wieczór": "Warczy na obcych i wraca pod osłonę drzew.",
                "noc": "Krąży niespokojnie i szuka słabszego zapachu.",
            },
            "puszcza_wilk_mlody": {
                "świt": "Wychodzi ostrożnie na ślad i wraca do stada.",
                "dzień": "Próbuje podchodzić bliżej zwierzyny i wraca pod osłonę krzewów.",
                "wieczór": "Krąży po znanym kręgu i wraca przed nocą.",
                "noc": "Słucha odgłosów lasu i czeka na ruch starszych wilków.",
            },
            "puszcza_wilk": {
                "świt": "Sprawdza granice terenu i wraca do swojej drogi.",
                "dzień": "Poluje, obwąchuje tropy i wraca bliżej starych śladów.",
                "wieczór": "Przechodzi przez cień polany i wraca w las.",
                "noc": "Krąży bezszelestnie i poluje wtedy, gdy inni śpią.",
            },
            "podgrodzie_woznica": {
                "świt": "Sprawdza wóz na skraju Podgrodzia i wraca do szopy z uprzężą.",
                "dzień": "Jedzie do rynku i wraca z towarem przy osi.",
                "wieczór": "Odprowadza zaprzęg do stajni i zamyka podwórze.",
                "noc": "Wraca do domu i przykrywa wóz płachtą.",
            },
            "podgrodzie_karczmarz": {
                "świt": "Otwiera karczmę i idzie po drewno do kuchni.",
                "dzień": "Siedzi przy ladzie i dogląda gości między salą a zapleczem.",
                "wieczór": "Wraca do stołu z rachunkami i zamyka wejście.",
                "noc": "Pilnuje ciszy na zapleczu i wraca do kwatery.",
            },
            "podgrodzie_karczmarka": {
                "świt": "Przygotowuje tace i wraca po wodę dla gości.",
                "dzień": "Krąży między kuchnią a salą, podając jadło przy stołach.",
                "wieczór": "Wraca do sali po puste misy i liczy zamówienia.",
                "noc": "Siedzi przy pustej karczmie i wraca na piętro.",
            },
            "podgrodzie_pielgrzym": {
                "świt": "Idzie do kapliczki i wraca z modlitwy na skraj drogi.",
                "dzień": "Odwiedza targ, by zostawić drobną ofiarę i wraca do rozstajów.",
                "wieczór": "Zatrzymuje się przy karczmie i wraca przed nocą do miejsca spoczynku.",
                "noc": "Wraca pod osłonę kapliczki i siedzi cicho do rana.",
            },
            "podgrodzie_piekarz": {
                "świt": "Rozpala piec i idzie po mąkę do składu.",
                "dzień": "Wypieka chleb i wraca po kolejne porcje ciasta.",
                "wieczór": "Zamyka piekarnię i wraca z ostatnimi bochenkami.",
                "noc": "Śpi przy wygasającym piecu i czeka na świt.",
            },
            "podgrodzie_handlarz": {
                "świt": "Rozstawia kram przy targu i wraca po wagę.",
                "dzień": "Handluje między placem a bramą i wraca po drobny towar.",
                "wieczór": "Zamyka stoisko i wraca z zarobkiem do domu.",
                "noc": "Liczy monety i siedzi przy zamkniętym kramie.",
            },
            "podgrodzie_przekupka": {
                "świt": "Idzie na targ z koszem i wraca po świeży drobiazg.",
                "dzień": "Krąży między straganami i wraca po kolejną dostawę.",
                "wieczór": "Sprząta kram i wraca do domu przez boczne uliczki.",
                "noc": "Odkłada kosze i siedzi przy kuchni po dniu handlu.",
            },
            "podgrodzie_kowal": {
                "świt": "Rozpala palenisko i wraca po węgiel do kuźni.",
                "dzień": "Kuje przy placu i wraca po podkowy oraz szczypce.",
                "wieczór": "Gasi żar i wraca z narzędziami pod dach.",
                "noc": "Liczy zamówienia i siedzi przy osmolonym stole.",
            },
            "podgrodzie_pomocnik_kowala": {
                "świt": "Nosi węgiel do paleniska i wraca po wodę.",
                "dzień": "Pomaga przy kowadle i wraca po szczypce do kuźni.",
                "wieczór": "Sprząta żużel i wraca do izby z brudnym fartuchem.",
                "noc": "Siedzi przy wygaszonym ogniu i pakuje narzędzia.",
            },
            "podgrodzie_straznik_miejski": {
                "świt": "Obchodzi bramę Podgrodzia i wraca na posterunek.",
                "dzień": "Patroluje skrzyżowania i wraca po meldunek.",
                "wieczór": "Zamyka przejście i wraca do wartowni.",
                "noc": "Siedzi przy bramie i nasłuchuje, czy ktoś wraca spóźniony.",
            },
            "podgrodzie_rybak": {
                "świt": "Schodzi nad rzekę z sieciami i wraca na targ z pierwszym połowem.",
                "dzień": "Sprzedaje ryby i wraca po kolejne skrzynki przy wodzie.",
                "wieczór": "Naprawia sieci i wraca do pomostu przed nocą.",
                "noc": "Siedzi przy wodzie i suszy liny po pracy.",
            },
            "podgrodzie_dziecko": {
                "świt": "Wybiega na podwórze i wraca przed ruchem na targu.",
                "dzień": "Biega między uliczkami i wraca do domu po południu.",
                "wieczór": "Wraca z placu do domu, zanim zrobi się ciemno.",
                "noc": "Śpi przy piecu i nie wychodzi na pusty bruk.",
            },
            "podgrodzie_zebrak": {
                "świt": "Przenosi się spod ściany do cieplejszego zakątka przy rynku.",
                "dzień": "Siedzi przy bramie i wraca pod mur, gdy robi się tłoczno.",
                "wieczór": "Szuka schronienia przy karczmie i wraca pod osłonę dachu.",
                "noc": "Leży pod murem i zasypia tam, gdzie wiatr słabnie.",
            },
            "podgrodzie_chlop": {
                "świt": "Przynosi sprzęt z pola i wraca po kolejne worki.",
                "dzień": "Sprzedaje plony na placu i wraca do obejścia.",
                "wieczór": "Zamyka robotę i wraca do domu z błotem na butach.",
                "noc": "Siedzi przy gospodarstwie i ostrzy narzędzia na rano.",
            },
            "podgrodzie_chlopka": {
                "świt": "Roznosi kosze z jajami i wraca po mleko do obejścia.",
                "dzień": "Handluje na targu i wraca do domu z zakupami.",
                "wieczór": "Zamyka kosze i wraca do kuchni przed nocą.",
                "noc": "Siedzi przy domowym ogniu i układa zapasy na jutro.",
            },
        }
        if vnum in specific_schedules:
            return specific_schedules[vnum]
        if vnum in {"astergard_guard", "watch_sergeant", "podgrodzie_straznik_miejski", "haldun_wartownik", "dungrim_guard", "dungrim_patrol_guard", "dungrim_sergeant", "dungrim_lieutenant", "dungrim_commander"}:
            return {
                "świt": "Zmienia wartę i obchodzi drogę.",
                "dzień": "Patroluje obejście i wypatruje cudzych błędów.",
                "wieczór": "Obchodzi posterunek przed nocą.",
                "noc": "Pilnuje przejścia i nasłuchuje poza murem.",
            }
        if vnum in {"straznica_dowodca", "straznica_wartownik", "straznica_zwiadowca"}:
            return {
                "świt": "Sprawdza meldunki i zlicza ludzi przed zmianą.",
                "dzień": "Dogląda traktu i wyznacza kolejne patrole.",
                "wieczór": "Porządkuje raporty i zamyka przejazd.",
                "noc": "Nasłuchuje wiatru i liczy ogniska na szlaku.",
            }
        if vnum in {"innkeeper", "podgrodzie_karczmarz", "podgrodzie_karczmarka"}:
            return {
                "świt": "Sprząta salę i otrzepuje stoły.",
                "dzień": "Obsługuje gości przy ladzie.",
                "wieczór": "Wyciera drewniane stoły i liczy kufle.",
                "noc": "Zamyka karczmę i pilnuje ciszy.",
            }
        if vnum in {"merchant", "customs_clerk", "fishmonger", "podgrodzie_handlarz", "podgrodzie_przekupka", "haldun_merchant", "haldun_wellkeeper", "dungrim_quartermaster", "dungrim_storekeeper"}:
            return {
                "świt": "Rozstawia towar i sprawdza wagę.",
                "dzień": "Handluje i liczy monety.",
                "wieczór": "Pakuje skrzynki i zwija płótno.",
                "noc": "Zamyka stoisko i odkłada klucze.",
            }
        if vnum in {"straznica_przewodnik", "straznica_karawanowy"}:
            return {
                "świt": "Układa ładunek i sprawdza, czy towar przetrwa drogę.",
                "dzień": "Obsługuje drogę, gości albo towar według potrzeby.",
                "wieczór": "Zamyka interes i liczy straty po przełęczy.",
                "noc": "Chroni to, co jeszcze nie ruszyło w drogę.",
            }
        if vnum in {"blacksmith", "carpenter", "tanner", "armorer", "podgrodzie_kowal", "podgrodzie_pomocnik_kowala", "haldun_blacksmith", "dungrim_armorer", "dungrim_military_blacksmith"}:
            return {
                "świt": "Otwiera warsztat.",
                "dzień": "Uderza młotem w żelazo.",
                "wieczór": "Czyści stanowisko.",
                "noc": "Wraca do domu.",
            }
        if vnum in {"straznica_woznica", "straznica_podrozny", "straznica_pielgrzym"}:
            return {
                "świt": "Spina sakwy i przygniata płaszcz przed wiatrem.",
                "dzień": "Idzie albo jedzie powoli, pilnując stopy i oddechu.",
                "wieczór": "Szuka postoju bliżej ognia i dalej od krawędzi.",
                "noc": "Odpoczywa, jeśli przełęcz pozwala mu zasnąć.",
            }
        if vnum in {"trakty_przewodnik", "trakty_karawaniarz", "trakty_woznica", "trakty_kurier", "trakty_podrozny", "trakty_pielgrzym", "trakty_zebrak", "trakty_mysliwy", "trakty_drwal", "trakty_handlarz"}:
            return {
                "świt": "Sprawdza drogę, sakwy i to, czy dzień nie zaczyna się od błota.",
                "dzień": "Pilnuje traktu, ludzi i ładunków według własnego rytmu.",
                "wieczór": "Szuka bezpiecznego postoju albo kończy handel przy ogniu.",
                "noc": "Odpoczywa przy drodze, jeśli droga na to pozwala.",
            }
        if vnum in {"puszcza_mysliwy", "puszcza_zielarz", "puszcza_pustelnik", "puszcza_drwal", "bagna_zielarz", "bagna_pustelnik", "bagna_mysliwy"}:
            return {
                "świt": "Sprawdza ślady, zbiory albo miejsce noclegu po chłodnej nocy.",
                "dzień": "Pilnuje lasu lub mokradeł i zbiera to, co akurat daje ziemia.",
                "wieczór": "Wraca do ognia albo kapliczki, zanim zapadnie pełna ciemność.",
                "noc": "Słucha lasu, bagna i tego, czego w ciemności nie warto nazywać.",
            }
        if vnum in {"puszcza_szczur", "puszcza_kruk", "puszcza_lis", "puszcza_pies_dziki", "puszcza_wilk_mlody", "puszcza_wilk", "puszcza_jelen", "puszcza_dzik", "puszcza_pajak", "puszcza_pajak_lesny", "puszcza_pajak_duzy", "puszcza_wilk_stary", "puszcza_wataha_wilkow", "puszcza_niedzwiedz", "puszcza_niedzwiedzica", "puszcza_bandyta", "puszcza_bandyta_zwiadowca", "puszcza_lowca", "puszcza_lowczy", "puszcza_bandycki_naczelnik", "puszcza_niedzwiedzi_olbrzym", "puszcza_troll", "bagna_zaba"}:
            return {
                "świt": "Wychodzi z ukrycia i szuka spokojnego miejsca.",
                "dzień": "Przemieszcza się ostrożnie po własnym terenie.",
                "wieczór": "Wraca bliżej kryjówki albo wody.",
                "noc": "Kryje się w cieniu i czeka na ciszę.",
            }
        if vnum in {"fisherman", "podgrodzie_rybak", "dockhand"}:
            return {
                "świt": "Idzie nad wodę z sieciami i liną.",
                "dzień": "Niesie świeżo złowione ryby.",
                "wieczór": "Wraca z połowu ciężkim krokiem.",
                "noc": "Odpoczywa od soli i wilgoci.",
            }
        if vnum in {"podgrodzie_woznica", "haldun_farmhand"}:
            return {
                "świt": "Sprawdza uprząż i koła wozu.",
                "dzień": "Prowadzi wóz po błotnej drodze.",
                "wieczór": "Odprowadza zaprzęg do stajni.",
                "noc": "Pilnuje sprzętu pod płachtą.",
            }
        if vnum in {"podgrodzie_piekarz", "haldun_farmerka"}:
            return {
                "świt": "Przygotowuje piec albo przynosi karmę dla zwierząt.",
                "dzień": "Dba o domowe obowiązki i zapasy.",
                "wieczór": "Odkłada narzędzia i porządkuje izbę.",
                "noc": "Odpoczywa po długim dniu pracy.",
            }
        if vnum in {"child", "urchin", "podgrodzie_dziecko"}:
            return {
                "świt": "Wysuwa się na podwórko, zanim dorośli skończą poranki.",
                "dzień": "Biega między zaułkami i zagląda do cudzych spraw.",
                "wieczór": "Wraca do domu przed zmrokiem.",
                "noc": "Śpi w bezpiecznym kącie.",
            }
        if vnum in {"beggar", "vagrant", "podgrodzie_zebrak"}:
            return {
                "świt": "Szuka suchego miejsca przy ścianie.",
                "dzień": "Prosi o jałmużnę i wypatruje dobrych twarzy.",
                "wieczór": "Szuka schronienia przed nocą.",
                "noc": "Drzemie pod murem.",
            }
        if vnum in {"traveler", "podgrodzie_pielgrzym"}:
            return {
                "świt": "Kładzie monetę w niszy.",
                "dzień": "Zapala świecę przy kapliczce.",
                "wieczór": "Składa dłonie przy kapliczce.",
                "noc": "Stoi w ciszy przy niszy.",
            }
        if vnum in {"farmer", "woodcutter", "miller", "priest_aide", "podgrodzie_chlop", "podgrodzie_chlopka", "haldun_farmer", "haldun_pasterz", "haldun_solt", "dungrim_stablemaster"}:
            return {
                "świt": "Przygotowuje narzędzia i zaczyna dzień pracy.",
                "dzień": "Zajmuje się codziennym obowiązkiem.",
                "wieczór": "Zamyka robotę i wraca do domu.",
                "noc": "Odpoczywa po pracy.",
            }
        if vnum == "dungrim_cook":
            return {
                "świt": "Rozpala kuchenny ogień i sprawdza garnki.",
                "dzień": "Karmi garnizon i miesza gulasz.",
                "wieczór": "Czyści kotły i odkłada racje.",
                "noc": "Pilnuje ognia, żeby śniadanie nie przyszło za późno.",
            }
        if vnum == "straznica_mysliwy":
            return {
                "świt": "Sprawdza sidła i ślady przy kamieniach.",
                "dzień": "Wypatruje zwierzyny i osłania szlak przed drobną kradzieżą.",
                "wieczór": "Skraca drogę z łupem i liczy, ile zostało zapasów.",
                "noc": "Suszy skórę i porządkuje ekwipunek przed kolejnym wyjściem.",
            }
        return {
            "świt": "Rozpoczyna zwykły dzień.",
            "dzień": "Zajmuje się swoimi sprawami.",
            "wieczór": "Powoli kończy dzień.",
            "noc": "Odpoczywa w ciszy.",
        }

    def _haldun_dialogue(self, role: str) -> dict[str, list[str]]:
        dialogues = {
            "haldun_solt": self._social_dialogue(
                "Jeśli chcesz coś załatwić, mów krótko i rzeczowo.",
                "Moja praca to liczyć zboże, ludzi i problemy, zanim urosną.",
                "Stoję między domem, stodołą i drogą, bo tam wszystko się przecina.",
                "Plotki o wozach, cenach i wilkach rozchodzą się tu szybciej niż dym z pieca.",
                studnia="Studnia jest sercem wsi. Gdy wyschnie, wszyscy to poczują.",
            ),
            "haldun_wellkeeper": self._social_dialogue(
                "Woda jest dla wszystkich, ale wiadro już nie zawsze.",
                "Pilnuję studni, łapię wiadra i pamiętam, komu co obiecałem.",
                "Stoję przy studni, bo ktoś musi pilnować łańcucha i cembrowiny.",
                "Plotki? Najczęściej słyszę je przy wiadrze, bo ludzie przy wodzie mówią prawdę częściej.",
                woda="Jeśli chcesz wody, nie rozlewaj jej więcej niż trzeba.",
            ),
            "haldun_blacksmith": self._social_dialogue(
                "Żelazo nie czeka, ale możesz chwilę postać w progu.",
                "Praca kowala zaczyna się od ognia, a kończy na odciskach.",
                "Kuźnia stoi przy rowie, żeby iskry nie poszły na siano.",
                "Plotki? Słyszę je przez młot, ale i tak rozpoznaję, kto przyszedł z pustymi rękami.",
                kuznia="W kuźni nie ma miejsca na gadanie bez celu.",
            ),
            "haldun_miller": self._social_dialogue(
                "Mielimy zboże, nie czas.",
                "Praca młynarza to pył, worki i liczenie uczciwych porcji.",
                "Stoję tam, gdzie rów daje ruch kołu i mące zapach chleba.",
                "Plotki przy młynie mają w sobie sporo pyłu. To dlatego ludzie je rozdmuchują.",
                mly="Młyn nie zatrzyma się sam. Kto przychodzi, ten zwykle coś niesie albo odbiera.",
            ),
            "haldun_merchant": self._social_dialogue(
                "Jeśli masz monety, to kupuj, a jeśli nie, to nie zabieraj mi światła.",
                "Praca handlarza to waga, ceny i dobry wzrok.",
                "Stoję przy moście, bo tędy przechodzą wszyscy, którzy jeszcze wierzą w dobry interes.",
                "Plotki krążą po stoisku szybciej niż monety.",
                targ="Na targu każdy chce coś sprzedać. Ja też.",
            ),
            "haldun_farmer": self._social_dialogue(
                "Jeśli trzeba gadać, to najlepiej przy płocie, nie w polu.",
                "Praca przy ziemi zaczyna się przed świtem i kończy po zachodzie.",
                "Jestem tam, gdzie zagony wymagają najwięcej cierpliwości.",
                "Plotki? W polu słyszy się je z wiatrem i zapamiętuje na czas żniw.",
                pola="Pola nie wybaczają lenistwa.",
            ),
            "haldun_farmerka": self._social_dialogue(
                "Najpierw obowiązki, potem słowa.",
                "Praca w obejściu to karmienie, sprzątanie i pilnowanie zapasów.",
                "Stoję przy oborze albo przy ogrodzie, zależnie od pory dnia.",
                "Plotki przychodzą z sąsiedztwa razem z jajami i mlekiem.",
                zagroda="Zagroda musi być czysta, bo zwierzęta pamiętają brud dłużej niż ludzie.",
            ),
            "haldun_pasterz": self._social_dialogue(
                "Owce słyszą więcej niż ludzie, dlatego mówię spokojnie.",
                "Praca pasterza to liczenie, wołanie i pilnowanie, żeby żadna sztuka nie zniknęła.",
                "Stoję przy pastwisku, kiedy zwierzęta chcą za daleko odejść.",
                "Plotki niosą się po łące tak samo jak gwizd pasterza.",
                pastwisko="Pastwisko daje spokój tylko z daleka.",
            ),
            "haldun_wartownik": self._social_dialogue(
                "Nie rozmawiam długo z obcymi. Taka już służba.",
                "Moja robota to patrzeć na drogę i wiedzieć, kto powinien wrócić przed zmrokiem.",
                "Stoję przy drodze ku fortecy, bo stamtąd najłatwiej o kłopoty.",
                "Plotki przy warcie są jak wiatr: każdy czuje, ale nikt nie złapałby w garść.",
                droga="Na drodze widać, kto pracuje, a kto szuka kłopotów.",
            ),
        }
        return dialogues.get(role, self._social_dialogue(
            "Nie mam teraz wiele do powiedzenia.",
            "Praca trwa od świtu do nocy.",
            "Stoję tam, gdzie trzeba.",
            "Plotki są tanie, ale rzadko dobre.",
        ))

    def _haldun_equipment(self, vnum: str) -> dict[str, Item | None]:
        if vnum == "haldun_solt":
            return {
                "korpus": Item("sołtysi kaftan", "Grubszy kaftan noszony przez sołtysa do codziennych obchodów.", 1.5, 8, "haldun_headman_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("laska sołtysa", "Krótsza laska do wskazywania drogi i porządkowania rozmów.", 0.7, 4, "haldun_headman_staff", "tool", "prawa_reka"),
            }
        if vnum == "haldun_wellkeeper":
            return {
                "korpus": Item("płócienny fartuch", "Mocny fartuch odporny na wodę i błoto.", 1.0, 4, "haldun_wellkeeper_apron", "armor", "korpus", protection=0),
                "prawa_reka": Item("hak do wiadra", "Krótki hak do łańcuchów i wiader.", 0.3, 2, "haldun_bucket_hook", "tool", "prawa_reka"),
            }
        if vnum == "haldun_blacksmith":
            return {
                "korpus": Item("fartuch kowalski", "Skórzany fartuch z osmalonymi brzegami.", 2.5, 12, "haldun_forge_apron", "armor", "korpus", protection=1),
                "prawa_reka": Item("młot kowalski", "Młot do kucia żelaza i odstraszania gapiów.", 2.3, 10, "haldun_forge_hammer", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=1),
            }
        if vnum == "haldun_miller":
            return {
                "korpus": Item("pyłowy kaftan", "Kaftan tak biały od mąki, że nie da się go pomylić z niczym innym.", 1.2, 6, "haldun_miller_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("miernik ziarna", "Mały miernik do worków i porcji mąki.", 0.6, 3, "haldun_mill_measure", "tool", "prawa_reka"),
            }
        if vnum == "haldun_merchant":
            return {
                "korpus": Item("kupiecki płaszcz", "Płaszcz z wieloma kieszeniami na monety i rachunki.", 1.0, 6, "haldun_merchant_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("miarka handlowa", "Krótka miarka i sznur do pilnowania uczciwej wagi.", 0.4, 4, "haldun_merchant_measure", "tool", "prawa_reka"),
            }
        if vnum == "haldun_farmer":
            return {
                "korpus": Item("płócienna koszula", "Koszula dostosowana do pracy w polu i przy sianie.", 1.0, 4, "haldun_farmer_shirt", "armor", "korpus", protection=0),
                "prawa_reka": Item("widły", "Widły do siana i przepędzania ciekawskich psów.", 2.2, 8, "haldun_pitchfork", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=3, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "haldun_farmerka":
            return {
                "korpus": Item("roboczy fartuch", "Fartuch z wieloma łatami i kieszeniami.", 0.9, 4, "haldun_farmer_apron", "armor", "korpus", protection=0),
                "prawa_reka": Item("sierp gospodarski", "Krótki sierp do zboża i ziół.", 0.8, 6, "haldun_farmer_sickle", "weapon", "prawa_reka", damage_type="cieta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "haldun_pasterz":
            return {
                "korpus": Item("wełniany płaszcz", "Płaszcz chroniący przed wiatrem na pastwisku.", 1.3, 5, "haldun_herder_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("pastuszy kij", "Długi kij do prowadzenia stad.", 1.1, 4, "haldun_herder_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "haldun_wartownik":
            return {
                "korpus": Item("płaszcz wartownika", "Służbowy płaszcz do nocnych obchodów.", 1.4, 7, "haldun_watch_cloak", "armor", "korpus", protection=1),
                "prawa_reka": Item("krótka włócznia", "Włócznia do krótkich patroli.", 2.5, 12, "haldun_watch_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        return {}

    class HaldunNPCSpec(TypedDict, total=False):
        name: str
        short_desc: str
        long_desc: str
        room_id: int
        stats: CharacterStats
        merchant: bool
        gold: int
        shop: str
        ai_state: str

    def _create_haldun_npc(self, vnum: str, room_id: int) -> NPC:
        data: dict[str, NPCFactory.HaldunNPCSpec] = {
            "haldun_solt": {
                "name": "sołtys",
                "short_desc": "Sołtys stoi przy domu i mierzy wzrokiem drogę, pole oraz ludzi.",
                "long_desc": "Pilnuje porządku w Haldun, zna sąsiedzkie spory i wie, która stodoła najpierw wymaga naprawy.",
                "room_id": 85,
                "stats": CharacterStats(10, 10, 10, 11, 11, 100),
            },
            "haldun_wellkeeper": {
                "name": "studniarz",
                "short_desc": "Studniarz dogląda wiader i łańcucha przy cembrowinie.",
                "long_desc": "Zna każdy odprysk kamienia przy studni i pamięta, ile wiader wody znosi się tu każdego dnia.",
                "room_id": 83,
                "stats": CharacterStats(9, 10, 10, 10, 10, 90),
                "merchant": True,
                "gold": 34,
                "shop": "haldun_market_inventory",
            },
            "haldun_blacksmith": {
                "name": "kowal",
                "short_desc": "Kowal z Haldun rozgrzewa żelazo i pilnuje, by nikt nie stał za blisko ognia.",
                "long_desc": "Jego kuźnia naprawia pługi, podkowy i cierpliwość całej wsi.",
                "room_id": 88,
                "stats": CharacterStats(12, 9, 12, 10, 10, 110),
                "merchant": True,
                "gold": 62,
                "shop": "haldun_forge_inventory",
            },
            "haldun_miller": {
                "name": "młynarz",
                "short_desc": "Młynarz ma twarz białą od pyłu i ręce od worków z ziarnem.",
                "long_desc": "W Haldun to on decyduje, czy zboże wróci do wsi jako mąka, czy tylko jako narzekanie.",
                "room_id": 87,
                "stats": CharacterStats(9, 9, 10, 10, 10, 95),
                "merchant": True,
                "gold": 48,
                "shop": "haldun_mill_inventory",
            },
            "haldun_merchant": {
                "name": "handlarz",
                "short_desc": "Handlarz liczy worki, jajka i każdą obcą plotkę, która wpada do wsi.",
                "long_desc": "Ma mały kram przy moście i zbyt dobre oko do cen jak na człowieka, który rzekomo sprzedaje tylko proste rzeczy.",
                "room_id": 89,
                "stats": CharacterStats(9, 10, 9, 11, 11, 95),
                "merchant": True,
                "gold": 58,
                "shop": "haldun_market_inventory",
            },
            "haldun_farmer": {
                "name": "rolnik",
                "short_desc": "Rolnik z Haldun wraca z pól, nawet kiedy inni jeszcze nie wyszli z domów.",
                "long_desc": "Żyje rytmem ziemi i zna każde pole po ciężarze ziemi na butach.",
                "room_id": 82,
                "stats": CharacterStats(9, 9, 10, 8, 9, 90),
            },
            "haldun_farmerka": {
                "name": "gospodyni",
                "short_desc": "Gospodyni nadzoruje obejście i pilnuje zapasów lepiej niż księgowy.",
                "long_desc": "Umie wycenić jajko, skrzynię i dobre słowo, a przy tym nikt w wiosce nie wie o niej za mało ani za dużo.",
                "room_id": 84,
                "stats": CharacterStats(9, 10, 9, 10, 10, 90),
                "merchant": True,
                "gold": 28,
                "shop": "haldun_market_inventory",
            },
            "haldun_pasterz": {
                "name": "pasterz",
                "short_desc": "Pasterz trzyma stado blisko pastwiska i patrzy, by żadna sztuka nie poszła za daleko.",
                "long_desc": "Zna owce, konie i ludzi, którzy zbyt często przechodzą obok zagrody bez pytania o zgodę.",
                "room_id": 92,
                "stats": CharacterStats(8, 10, 9, 10, 11, 85),
            },
            "haldun_wartownik": {
                "name": "wartownik",
                "short_desc": "Wartownik stoi przy drodze do fortecy i liczy przechodniów.",
                "long_desc": "To człowiek od krótkich pytań i długiej pamięci. W Haldun widzi wszystko, co jedzie, idzie albo się chowa.",
                "room_id": 94,
                "stats": CharacterStats(11, 11, 11, 11, 11, 110),
                "ai_state": "GUARD",
            },
        }
        spec = data.get(vnum)
        if spec is None:
            raise KeyError(f"Unknown Haldun NPC: {vnum}")
        character = Character(spec["name"].capitalize())
        character.stats = spec["stats"]
        character.inventory.clear()
        shop_factories = {
            "haldun_market_inventory": haldun_market_inventory,
            "haldun_forge_inventory": haldun_forge_inventory,
            "haldun_mill_inventory": haldun_mill_inventory,
        }
        shop_name = cast(str | None, spec.get("shop"))
        ai_state = spec["ai_state"] if "ai_state" in spec else "IDLE"
        merchant_gold = spec["gold"] if "gold" in spec else 100
        npc = NPC(
            vnum=vnum,
            name=spec["name"],
            short_desc=spec["short_desc"],
            long_desc=spec["long_desc"],
            zone="Haldun",
            faction="MEEKHAN",
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=bool(spec.get("merchant", False)),
            shop_inventory=list(shop_factories[shop_name]()) if shop_name is not None else [],
            merchant_gold=merchant_gold,
            home_room_id=int(spec["room_id"]),
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        npc.character.equipment.update(self._haldun_equipment(vnum))
        npc.dialogue_tree = self._haldun_dialogue(vnum)
        return self._finalize(npc)

    class DungrimNPCSpec(TypedDict, total=False):
        name: str
        short_desc: str
        long_desc: str
        room_id: int
        stats: CharacterStats
        merchant: bool
        gold: int
        shop: str
        ai_state: str

    def _dungrim_dialogue(self, role: str) -> dict[str, list[str]]:
        dialogues = {
            "dungrim_commander": self._social_dialogue(
                "Raport krótko. Forteca nie ma czasu na ozdobniki.",
                "Dowodzenie to zapas, dyscyplina i ludzie, którzy wiedzą, gdzie jest ich miejsce.",
                "Stoję tam, gdzie trzeba trzymać całość razem: między bramą, dziedzińcem i murem.",
                "Plotki o trakcie są mniej ważne niż stan zapasów i ludzi w służbie.",
                fort="Fort trzyma się na rozkazie, nie na hałasie.",
            ),
            "dungrim_lieutenant": self._social_dialogue(
                "Jeśli nie masz meldunku, nie masz po co tu stać.",
                "Oficer pilnuje patroli, zmian i tego, by nikt nie zgubił rozkazu po drodze.",
                "Przechodzę między koszarami a dziedzińcem, bo tam wszystko się sprawdza dwa razy.",
                "Plotki? Zwykle zaczynają się od słowa 'widziałem'.",
                patrole="Patrole liczy się jak zapasy: rano, po południu i przed nocą.",
            ),
            "dungrim_sergeant": self._social_dialogue(
                "W szeregu mówimy mało i słuchamy dużo.",
                "Sierżant pilnuje zmiany, porządku i tego, żeby brama nie została sama.",
                "Najczęściej stoję przy koszarach albo przy murze nad traktem.",
                "Plotki noszą młodsi, ale rozkaz musi wykonać każdy.",
                wart="Straż bez warujących ma krótszą pamięć niż zły koń.",
            ),
            "dungrim_guard": self._social_dialogue(
                "Stój, meldunek i dalej już tylko według rozkazu.",
                "Strażnik pilnuje dziedzińca, wieży i magazynów.",
                "Siedzę tam, gdzie trzeba widzieć bramę, ludzi i skrzynie.",
                "Plotki? W fortecy częściej słyszę je przy beczkach niż w koszarach.",
            ),
            "dungrim_patrol_guard": self._social_dialogue(
                "Nie zatrzymuję się bez powodu.",
                "Patrol to marsz, obserwacja i pamięć o każdym rogu muru.",
                "Chodzę po murze i po trakcie, żeby droga nie była zbyt cicha.",
                "Plotki w terenie są jak ślady w błocie: zostają dłużej niż ludzie myślą.",
                mur="Mur trzeba znać krokiem, nie wzrokiem.",
            ),
            "dungrim_armorer": self._social_dialogue(
                "Zbroja ma służyć, nie błyszczeć.",
                "Praca zbrojmistrza to nit, skóra i cierpliwość do wgnieceń.",
                "Stoję przy zbrojowni, bo tam najlepiej słychać, co się psuje.",
                "Plotki? Zbroja pamięta więcej niż ludzie.",
                zbrojownia="Zbrojownia to serce jakości, nie magazyn dla ładnych słów.",
            ),
            "dungrim_military_blacksmith": self._social_dialogue(
                "Jak chcesz narzekać, rób to poza kuźnią.",
                "Kowal wojskowy naprawia ostrza, okucia i wojskową dumę.",
                "Kuźnia stoi obok magazynu, bo tu wszystko ma być blisko ręki.",
                "Plotki? Iskra nie pyta, czy ktoś ją widzi.",
                ogien="Ogień trzyma tempo całej fortecy.",
            ),
            "dungrim_quartermaster": self._social_dialogue(
                "Racja, pieczęć i podpis. Inaczej nie ma rozmowy.",
                "Magazynier pilnuje wydań, spisów i racji.",
                "Stoję przy magazynach, bo tam najłatwiej policzyć, co znika.",
                "Plotki? Każdy z nich to inny sposób na ukrycie braku w tabeli.",
                zapasy="Zapasy nie lubią chaosu.",
            ),
            "dungrim_storekeeper": self._social_dialogue(
                "Do magazynu tylko z listą.",
                "Trzymam wszystko, co armia nosi, je i zgubić nie powinna.",
                "Jestem przy składach, bo ktoś musi wiedzieć, która skrzynia jest czyja.",
                "Plotki? W składzie słychać tylko liczenie i przekleństwa.",
                skrot="Na skróty do zapasów prowadzi tylko cudza odpowiedzialność.",
            ),
            "dungrim_stablemaster": self._social_dialogue(
                "Koń widzi twoje zamiary szybciej niż ty sam.",
                "Stajenny dowodzi końmi patrolowymi i pilnuje sprzętu jeździeckiego.",
                "Stoję przy stajniach, bo tam najlepiej słychać kopyta i złe decyzje.",
                "Plotki? Kiedy koń prycha, wiem, że ktoś skłamał.",
                konie="Konie potrzebują spokoju, nie opowieści.",
            ),
            "dungrim_cook": self._social_dialogue(
                "Jeśli nie jesteś głodny, to masz szczęście i możesz iść dalej.",
                "Kuchnia forteczna karmi wszystkich, którzy wracają z muru.",
                "Stoję przy piecu i kotłach, bo tu smak ma znaczenie większe niż ozdoby.",
                "Plotki? Kuchnia słyszy wszystko, ale zapamiętuje tylko połowę.",
                gulasz="Gulasz wart jest więcej niż kolejna narada.",
            ),
        }
        return dialogues.get(role, self._social_dialogue(
            "Mów z sensem albo wracaj na wartę.",
            "Służba trwa od świtu do nocy.",
            "Stoję tam, gdzie rozkaz tego wymaga.",
            "Plotki w garnizonie żyją krócej niż świeży chleb.",
        ))

    def _dungrim_equipment(self, vnum: str) -> dict[str, Item | None]:
        if vnum == "dungrim_commander":
            return {
                "korpus": Item("płaszcz dowódcy", "Ciężki płaszcz z metalowymi haftami i śladami po deszczu.", 2.2, 18, "dungrim_commander_cloak", "armor", "korpus", protection=2),
                "prawa_reka": Item("miecz dowódczy", "Miecz noszony przez dowódcę fortu.", 2.0, 20, "dungrim_commander_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=5, reach=1, initiative_modifier=1, parry_bonus=1),
            }
        if vnum == "dungrim_lieutenant":
            return {
                "korpus": Item("oficerski kaftan", "Kaftan noszony przez oficera zmiany.", 1.8, 14, "dungrim_officer_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("krótki miecz", "Broń do wydawania krótkich, przekonujących decyzji.", 1.7, 12, "dungrim_officer_blade", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1),
            }
        if vnum == "dungrim_sergeant":
            return {
                "korpus": Item("sierżancki płaszcz", "Płaszcz służbowy używany na posterunku.", 2.0, 12, "dungrim_sergeant_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("halabarda patrolowa", "Halabarda do kontroli bramy i dziedzińca.", 3.8, 16, "dungrim_halberd", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum in {"dungrim_guard", "dungrim_patrol_guard"}:
            return {
                "korpus": Item("płaszcz strażniczy", "Służbowy płaszcz odporny na wiatr.", 1.9, 10, "dungrim_guard_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia forteczna", "Włócznia do kontroli przejść i murów.", 2.6, 14, "dungrim_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "dungrim_armorer":
            return {
                "korpus": Item("fartuch zbrojmistrza", "Ciężki fartuch z łuskami i nitami.", 2.3, 10, "dungrim_armorer_apron", "armor", "korpus", protection=1),
                "prawa_reka": Item("młotek nitujący", "Młotek do naprawy zbroi i tarcz.", 1.1, 5, "dungrim_armorer_hammer", "tool", "prawa_reka"),
            }
        if vnum == "dungrim_military_blacksmith":
            return {
                "korpus": Item("okopcony fartuch", "Fartuch czarny od sadzy i ognia.", 2.6, 12, "dungrim_forge_apron", "armor", "korpus", protection=1),
                "prawa_reka": Item("młot wojskowy", "Młot do podkuwania i napraw służbowych.", 2.4, 11, "dungrim_forge_hammer", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=1),
            }
        if vnum == "dungrim_quartermaster":
            return {
                "korpus": Item("urzędowy płaszcz", "Płaszcz z kieszeniami na pieczęcie i klucze.", 1.6, 8, "dungrim_quartermaster_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("laska magazyniera", "Laska do wskazywania skrzyń i pilnowania porządku.", 0.8, 4, "dungrim_quartermaster_staff", "tool", "prawa_reka"),
            }
        if vnum == "dungrim_storekeeper":
            return {
                "korpus": Item("składowy kaftan", "Roboczy kaftan pełen kurzu i kredy.", 1.4, 6, "dungrim_storekeeper_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("klucz do magazynu", "Pęk kluczy do składów i skrzyń.", 0.2, 3, "dungrim_storekeeper_keys", "tool", "prawa_reka"),
            }
        if vnum == "dungrim_stablemaster":
            return {
                "korpus": Item("stajenny kaftan", "Kaftan odporny na słomę, pot i pył.", 1.3, 6, "dungrim_stable_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("bat stajenny", "Krótki bat używany przy koniach służbowych.", 0.5, 4, "dungrim_stable_whip", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "dungrim_cook":
            return {
                "korpus": Item("fartuch kuchenny", "Fartuch noszony przy wojskowym piecu.", 1.0, 5, "dungrim_cook_apron", "armor", "korpus", protection=0),
                "prawa_reka": Item("łyżka warowna", "Drewniana łyżka wystarczająco twarda, by służyć za kij.", 0.4, 2, "dungrim_cook_spoon", "tool", "prawa_reka"),
            }
        return {}

    def _straznica_dialogue(self, role: str) -> dict[str, list[str]]:
        dialogues = {
            "straznica_dowodca": self._social_dialogue(
                "Przełęcz nie wybacza bałaganu. Mów krótko.",
                "Moja praca to liczyć ludzi, ogień i zapasy, zanim zrobi to śnieg.",
                "Stoję na gardzieli przejazdu, gdzie każdy błąd ma cenę.",
                "Plotki przychodzą z karawanami, ale ja wolę meldunki niż opowieści.",
                karawana="Karawana jest bezpieczna tylko do chwili, gdy minie bramę.",
            ),
            "straznica_wartownik": self._social_dialogue(
                "Stój spokojnie i nie zasłaniaj przejazdu.",
                "Pilnuję muru, schodów i tego, czy ktoś nie niesie za dużo na jedną rękę.",
                "Najczęściej stoję tam, gdzie wiatr pierwszy uderza w twarz.",
                "Plotki? W przełęczy każde echo brzmi jak cudza tajemnica.",
            ),
            "straznica_zwiadowca": self._social_dialogue(
                "Najpierw patrzę na ślady, potem na ludzi.",
                "Zwiad to oczy, nogi i pamięć o tym, co zostaje po śniegu.",
                "Chodzę wyżej niż inni, bo stamtąd lepiej widać problemy.",
                "Plotki w górach wyglądają jak śnieg: dużo ich, ale niewiele ważą.",
                zwiad="Po zwiadzie zawsze trzeba liczyć drogę powrotną.",
            ),
            "straznica_przewodnik": self._social_dialogue(
                "Jeśli chcesz przejść bez kłopotów, słuchaj pierwszej rady.",
                "Prowadzę ludzi i ładunki tak, żeby przełęcz nie zjadła nam dnia.",
                "Stoję przy mapach i znakach, bo każdy skręt wygląda tu podobnie.",
                "Plotki? Najczęściej zaczynają się od pytania, którędy bezpieczniej.",
                szlak="Szlak jest prosty tylko wtedy, gdy ktoś go wcześniej odgarnął.",
            ),
            "straznica_karawanowy": self._social_dialogue(
                "Towar stoi, dopóki ja nie policzę skrzyń.",
                "Handel przez przełęcz to rachunki, cła i cierpliwość do koni.",
                "Mam swoje miejsce przy karawanach, bo ktoś musi patrzeć na ładunek.",
                "Plotki? Kupcy rozpoznają je po tym, ile ważą na końcu drogi.",
                karawana="Karawana lubi płaski teren, a tu dostaje tylko stromiznę.",
            ),
            "straznica_woznica": self._social_dialogue(
                "Koń, oś i klin. Reszta to tylko hałas.",
                "Prowadzę wozy przez zakręty, zanim koło poleci w przepaść.",
                "Siedzę przy zaprzęgu, bo droga sama się nie poprawi.",
                "Plotki? Woźnica słucha stukotu kół bardziej niż ludzi.",
                woz="Wóz mówi wszystko po skrzypieniu osi.",
            ),
            "straznica_podrozny": self._social_dialogue(
                "Nie szukaj tu wygody. Szukaj tylko przejścia.",
                "Podróżny żyje z tego, co uniesie i gdzie zdąży przed zmrokiem.",
                "Stoję przy ogniu albo przy murze, zależnie od wiatru.",
                "Plotki? Każdy trakt niesie je razem z błotem.",
                postoj="Postój bywa najlepszą częścią drogi.",
            ),
            "straznica_pielgrzym": self._social_dialogue(
                "Modlitwa przy przełęczy brzmi ciszej, ale nie mniej szczerze.",
                "Idę tam, gdzie trzeba iść spokojnie, nawet jeśli wiatr nie pomaga.",
                "Staję przy kaplicy i rozstaju, bo tam najczęściej ludzie zwalniają krok.",
                "Plotki nie mają tu wielkiej wartości. Kamień i wiatr i tak pamiętają więcej.",
                kaplica="Kaplica daje chwilę ciszy każdemu, kto jeszcze ją nosi w sobie.",
            ),
            "straznica_mysliwy": self._social_dialogue(
                "Zwierzyna nie czeka na twoją historię.",
                "Moja robota to trop i cierpliwość do kamienia.",
                "Stoję tam, gdzie krawędź szlaku styka się z polowaniem.",
                "Plotki? Na zboczu ważniejsze są ślady niż słowa.",
                tropy="Tropy przy przełęczy mieszają ludzi, kozy i czasem coś większego.",
            ),
        }
        return dialogues.get(role, self._social_dialogue(
            "Mów z sensem albo wracaj na szlak.",
            "Praca trwa tu od świtu do nocy.",
            "Stoję tam, gdzie rozkaz tego wymaga.",
            "Plotki w górach żyją krócej niż świeży śnieg.",
        ))

    def _straznica_equipment(self, vnum: str) -> dict[str, Item | None]:
        if vnum == "straznica_dowodca":
            return {
                "korpus": Item("płaszcz przełęczy", "Gruby, wiatroodporny płaszcz z metalowymi klamrami.", 2.1, 16, "straznica_commander_cloak", "armor", "korpus", protection=2),
                "prawa_reka": Item("miecz przełęczy", "Krótki miecz do krótkich i ostatecznych decyzji.", 1.8, 18, "straznica_commander_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=5, reach=1, initiative_modifier=1, parry_bonus=1),
            }
        if vnum == "straznica_wartownik":
            return {
                "korpus": Item("płaszcz wartowniczy", "Szary płaszcz odporny na deszcz i śnieg.", 1.8, 10, "straznica_guard_cloak", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia strażnicza", "Włócznia do kontroli przejazdu i skraju muru.", 2.5, 14, "straznica_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
                "lewa_reka": Item("mała tarcza", "Lekka tarcza na długie postoje przy wietrze.", 2.2, 11, "straznica_guard_shield", "shield", "lewa_reka", protection=1, shield_block=2),
            }
        if vnum == "straznica_zwiadowca":
            return {
                "glowa": Item("zwiadowczy kaptur", "Kaptur tłumiący wiatr i błysk śniegu.", 1.1, 8, "straznica_scout_hood", "armor", "glowa", protection=0),
                "prawa_reka": Item("krótki nóż zwiadowcy", "Krótki nóż do lin, skór i cichej roboty.", 0.8, 16, "straznica_scout_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=1, parry_bonus=0),
                "lewa_reka": Item("krótki nóż", "Nóż do lin, skór i bliskich problemów.", 0.3, 5, "straznica_scout_knife", "weapon", "lewa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "straznica_przewodnik":
            return {
                "korpus": Item("kurtka przewodnika", "Lekka, ale ciepła kurtka z wieloma kieszeniami.", 1.4, 10, "straznica_guide_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("laska przewodnika", "Laska do wskazywania kamieni, zejść i bezpieczniejszych obejść.", 0.9, 4, "straznica_guide_staff", "tool", "prawa_reka"),
            }
        if vnum == "straznica_karawanowy":
            return {
                "korpus": Item("karawanowy kaftan", "Kaftan z wieloma łatami po linach i sakwach.", 1.5, 9, "straznica_caravan_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("rachmistrzowska pałeczka", "Krótka pałeczka do liczenia skrzyń i worków.", 0.5, 3, "straznica_caravan_tally", "tool", "prawa_reka"),
            }
        if vnum == "straznica_woznica":
            return {
                "korpus": Item("woźnicki płaszcz", "Gruby płaszcz zabezpieczony przed błotem i wiatrem.", 1.9, 11, "straznica_driver_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("bat woźnicy", "Krótki bat do kierowania zaprzęgiem.", 0.6, 5, "straznica_driver_whip", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "straznica_podrozny":
            return {
                "korpus": Item("podróżny płaszcz", "Płaszcz z łatami po wielu drogach.", 1.4, 8, "straznica_travel_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("mały nóż", "Krótki nóż przydatny w drodze.", 0.2, 3, "straznica_travel_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "straznica_pielgrzym":
            return {
                "korpus": Item("pielgrzymi habit", "Ciepły habit odporny na deszcz i śnieg.", 1.6, 9, "straznica_pilgrim_habit", "armor", "korpus", protection=0),
                "prawa_reka": Item("kij pielgrzyma", "Prosty kij do marszu po kamiennym szlaku.", 1.0, 4, "straznica_pilgrim_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "straznica_mysliwy":
            return {
                "korpus": Item("futro myśliwego", "Ciepłe futro wygarbowane na wiatr i śnieg.", 2.0, 12, "straznica_hunter_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia przełęczy", "Włócznia dopasowana do stromych ścieżek i osłony przejazdu.", 2.0, 18, "straznica_hunter_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        return {}

    def _trakty_dialogue(self, role: str) -> dict[str, list[str]]:
        dialogues = {
            "trakty_przewodnik": self._social_dialogue(
                "Na trakcie liczy się kierunek i czas, nie opowieści.",
                "Moja robota to prowadzić ludzi tak, żeby nie zgubiła ich pogoda ani skrót.",
                "Stoję tam, gdzie najłatwiej pomylić szlak z błędną radą.",
                "Plotki? Po drodze każdy ma własną wersję tego samego zakrętu.",
                szlak="Szlak bez przewodnika jest tylko śladem w błocie.",
            ),
            "trakty_karawaniarz": self._social_dialogue(
                "Pokaż manifest, a potem możemy mówić o dalszej drodze.",
                "Liczenie skrzyń i kół to jedyna rzecz, która nie kłamie na trakcie.",
                "Stoję przy karawanie, bo ładunek sam się nie obroni przed błotem.",
                "Plotki kupieckie są jak cło: każdy coś traci, ktoś inny zyskuje.",
                karawana="Karawana jedzie spokojnie tylko wtedy, gdy nikt nie pęka pierwszy.",
            ),
            "trakty_kurier": self._social_dialogue(
                "Jeśli list jest pilny, nie mam czasu na długie pytania.",
                "Praca kuriera to pamięć, nogi i mokry płaszcz.",
                "Stoję tam, gdzie można jeszcze kogoś dogonić przed zmrokiem.",
                "Plotki? Ja wolę wiadomości, które da się dostarczyć zanim ostygną.",
                list="List ma wartość tylko wtedy, gdy trafi do właściwych rąk.",
            ),
            "trakty_woznica": self._social_dialogue(
                "Koło, oś, klin. Reszta to tylko hałas i droga.",
                "Wożę ludzi i towary, a czasem tylko cierpliwość.",
                "Stoję przy wozie, bo drogi nie da się przekonać do litości.",
                "Plotki słyszę po skrzypieniu osi szybciej niż po słowach.",
                woz="Wóz na trakcie nie wybacza byle błędu.",
            ),
            "trakty_podrozny": self._social_dialogue(
                "Dziś idę dalej, ale chwilę mogę postać.",
                "Praca podróżnego to marsz, oszczędność sił i szukanie suchego miejsca.",
                "Stoję tam, gdzie da się jeszcze odpocząć bez walki z wiatrem.",
                "Plotki zbieram tylko wtedy, gdy przydają się do drogi.",
                postoj="Dobry postój jest wart więcej niż szybki krok.",
            ),
            "trakty_pielgrzym": self._social_dialogue(
                "Kaplica i droga wystarczą mi za rozmowę.",
                "Idę spokojnie, bo śpieszenie się przy przełęczy nie pomaga duszy ani nogom.",
                "Stoję przy miejscach modlitwy i na skrzyżowaniach, gdzie każdy zwalnia krok.",
                "Plotki omijam, jeśli nie niosą niczego lepszego niż kurz.",
                modlitwa="Modlitwa przy szlaku ma smak wiatru i zmęczenia.",
            ),
            "trakty_zebrak": self._social_dialogue(
                "Masz drobne? Nie musisz się spieszyć z odpowiedzią.",
                "Praca żebraka to czekać tam, gdzie ludzie jeszcze mają miękkie serca.",
                "Stoję przy rozstajach, bo tam nikt nie wie, czy iść dalej, czy wracać.",
                "Plotki są dobre, jeśli da się za nie dostać zupę.",
                cieplo="Ciepło przy drodze to rzadki luksus.",
            ),
            "trakty_mysliwy": self._social_dialogue(
                "Zwierzyna nie czeka, aż skończysz gadać.",
                "Poluję, patroluję i sprzedaję to, co da się unieść z przełęczy.",
                "Stoję tam, gdzie tropy schodzą z drogi w kamienie albo krzaki.",
                "Plotki o wilkach zwykle kończą się tam, gdzie zaczynają się ślady.",
                tropy="Tropy na trakcie mówią więcej niż cudze obietnice.",
            ),
            "trakty_drwal": self._social_dialogue(
                "Na trakcie drzewo nie pyta, czy chce się je ciąć.",
                "Praca drwala to topór, klin i cierpliwość do drewna, które nie chce współpracować.",
                "Stoję przy składzie drewna albo przy ognisku, zależnie od pory dnia.",
                "Plotki o lasach zawsze wracają do jednego: kto pierwszy ściął zdrowy pień.",
                drewno="Drewno przy drodze ratuje noc, ale kosztuje dzień pracy.",
            ),
            "trakty_handlarz": self._social_dialogue(
                "Jeśli masz monety, to patrz na towar, nie na pogodę.",
                "Handluję tym, co ludzie gubią po drodze i czego potem żałują.",
                "Stoję tam, gdzie ruch jest największy i cisza trwa najkrócej.",
                "Plotki mają cenę, ale zawsze najwyższą płaci ostatni słuchacz.",
                targ="Targ na trakcie jest mniejszy niż w mieście, ale bardziej szczery.",
            ),
        }
        return dialogues.get(role, self._social_dialogue(
            "Nie mam dziś wiele do powiedzenia.",
            "Praca trwa od świtu do nocy.",
            "Stoję tam, gdzie trzeba.",
            "Plotki są tanie, ale rzadko dobre.",
        ))

    def _trakty_equipment(self, vnum: str) -> dict[str, Item | None]:
        if vnum == "trakty_przewodnik":
            return {
                "korpus": Item("kurtka przewodnika", "Lekka, ale ciepła kurtka z wieloma kieszeniami.", 1.4, 10, "trakty_guide_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("laska przewodnika", "Laska do wskazywania kamieni, zejść i bezpieczniejszych obejść.", 0.9, 4, "trakty_guide_staff", "tool", "prawa_reka"),
            }
        if vnum == "trakty_karawaniarz":
            return {
                "korpus": Item("karawanowy kaftan", "Kaftan z wieloma łatami po linach i sakwach.", 1.5, 9, "trakty_caravan_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("rachmistrzowska pałeczka", "Krótka pałeczka do liczenia skrzyń i worków.", 0.5, 3, "trakty_caravan_tally", "tool", "prawa_reka"),
            }
        if vnum == "trakty_kurier":
            return {
                "korpus": Item("kurierki płaszcz", "Płaszcz z krótkim krojem, dobry do biegu i jazdy.", 1.2, 8, "trakty_courier_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("poczta pieczęć", "Krótkie narzędzie do zamykania listów i potwierdzeń.", 0.2, 2, "trakty_courier_seal", "tool", "prawa_reka"),
            }
        if vnum == "trakty_woznica":
            return {
                "korpus": Item("woźnicki płaszcz", "Gruby płaszcz zabezpieczony przed błotem i wiatrem.", 1.9, 11, "trakty_driver_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("bat woźnicy", "Krótki bat do kierowania zaprzęgiem.", 0.6, 5, "trakty_driver_whip", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "trakty_podrozny":
            return {
                "korpus": Item("podróżny płaszcz", "Płaszcz z łatami po wielu drogach.", 1.4, 8, "trakty_travel_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("mały nóż", "Krótki nóż przydatny w drodze.", 0.2, 3, "trakty_travel_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "trakty_pielgrzym":
            return {
                "korpus": Item("pielgrzymi habit", "Ciepły habit odporny na deszcz i pył.", 1.6, 9, "trakty_pilgrim_habit", "armor", "korpus", protection=0),
                "prawa_reka": Item("kij pielgrzyma", "Prosty kij do marszu po kamiennym szlaku.", 1.0, 4, "trakty_pilgrim_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "trakty_zebrak":
            return {
                "korpus": Item("łachman i koc", "Nędzny koc i łachman chronią przed chłodem bardziej niż przed spojrzeniem.", 0.8, 1, "trakty_beggar_rag", "armor", "korpus", protection=0),
                "prawa_reka": Item("kij żebraka", "Krótki kij do podpierania się i odganiania psów.", 0.7, 1, "trakty_beggar_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "trakty_mysliwy":
            return {
                "korpus": Item("futro myśliwego", "Ciepłe futro wygarbowane na wiatr i pył.", 2.0, 12, "trakty_hunter_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia trakty", "Włócznia dopasowana do pracy przy drodze.", 2.0, 18, "trakty_hunter_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "trakty_drwal":
            return {
                "korpus": Item("roboczy kaftan", "Kaftan odporny na żywicę, pył i iskry ogniska.", 1.5, 7, "trakty_lumber_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("topór drwala", "Topór do drewna, wozów i wszystkich rzeczy, które trzeba rozłupać.", 2.9, 11, "trakty_lumber_axe", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "trakty_straznik":
            return {
                "korpus": Item("płaszcz strażniczy", "Służbowy płaszcz odporny na wiatr.", 1.9, 10, "trakty_guard_coat", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia trakty", "Włócznia do kontroli przejść i rozstajów.", 2.6, 14, "trakty_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
                "lewa_reka": Item("mała tarcza", "Lekka tarcza na długie postoje przy wietrze.", 2.2, 11, "trakty_guard_shield", "shield", "lewa_reka", protection=1, shield_block=2),
            }
        if vnum == "trakty_handlarz":
            return {
                "korpus": Item("handlarski płaszcz", "Płaszcz z wieloma kieszeniami i łatami po drogach.", 1.3, 8, "trakty_merchant_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("miarka handlowa", "Krótka miarka i sznur do pilnowania uczciwej wagi.", 0.4, 4, "trakty_merchant_measure", "tool", "prawa_reka"),
            }
        return {}

    class TraktyNPCSpec(TypedDict, total=False):
        name: str
        short_desc: str
        long_desc: str
        room_id: int
        stats: CharacterStats
        merchant: bool
        gold: int
        shop: str
        ai_state: str

    def _create_trakty_npc(self, vnum: str, room_id: int) -> NPC:
        data: dict[str, NPCFactory.TraktyNPCSpec] = {
            "trakty_przewodnik": {
                "name": "przewodnik",
                "short_desc": "Przewodnik zna kamienie milowe i ostrzega przed złą pogodą.",
                "long_desc": "Prowadzi ludzi przez trakty tak, jakby każda koleina była zapisana w pamięci nóg.",
                "room_id": 135,
                "stats": CharacterStats(10, 11, 10, 12, 11, 100),
                "merchant": True,
                "gold": 42,
                "shop": "trakty_route_inventory",
            },
            "trakty_karawaniarz": {
                "name": "karawaniarz",
                "short_desc": "Karawaniarz liczy skrzynie, osie i pieczęcie przewozowe.",
                "long_desc": "Widzi wagę towaru szybciej niż jego cenę i nie wierzy w drogę bez przynajmniej jednego dobrego klinu.",
                "room_id": 138,
                "stats": CharacterStats(10, 10, 10, 11, 11, 95),
                "merchant": True,
                "gold": 55,
                "shop": "trakty_caravan_inventory",
            },
            "trakty_kurier": {
                "name": "kurier",
                "short_desc": "Kurier ma płaszcz ubłocony od biegu między punktami postoju.",
                "long_desc": "Niesie wiadomości szybciej niż plotki i znika, zanim ktoś zdąży zapytać o szczegóły.",
                "room_id": 140,
                "stats": CharacterStats(9, 11, 9, 12, 10, 88),
                "merchant": True,
                "gold": 24,
                "shop": "trakty_courier_inventory",
            },
            "trakty_woznica": {
                "name": "woźnica",
                "short_desc": "Woźnica pilnuje osi i ogląda drogę tak, jakby umiała mówić.",
                "long_desc": "Zna każdy zjazd, w którym wóz może stracić rozum, i każdy kamień, który trzeba obejść.",
                "room_id": 141,
                "stats": CharacterStats(11, 10, 11, 10, 10, 100),
            },
            "trakty_podrozny": {
                "name": "podróżny",
                "short_desc": "Podróżny odpoczywa przy trakcie z sakwą przy nodze.",
                "long_desc": "Na twarzy ma pył z kilku dróg i ostrożność ludzi, którzy nie chcą drugi raz zaczynać od zera.",
                "room_id": 145,
                "stats": CharacterStats(9, 10, 9, 10, 10, 90),
            },
            "trakty_pielgrzym": {
                "name": "pielgrzym",
                "short_desc": "Pielgrzym zwalnia przy kapliczce i poprawia sznur paciorków.",
                "long_desc": "Idzie bez pośpiechu, ale z uporem ludzi, których prowadzi cel silniejszy niż zmęczenie.",
                "room_id": 136,
                "stats": CharacterStats(8, 10, 9, 11, 12, 85),
            },
            "trakty_zebrak": {
                "name": "żebrak",
                "short_desc": "Żebrak siedzi przy rozstajach i udaje, że wiatr go nie dotyczy.",
                "long_desc": "Zna drogi lepiej niż wielu uczciwych ludzi, bo całe życie przesiedział tam, gdzie wszyscy musieli przejść.",
                "room_id": 156,
                "stats": CharacterStats(7, 8, 8, 10, 8, 75),
            },
            "trakty_mysliwy": {
                "name": "myśliwy",
                "short_desc": "Myśliwy sprzedaje sidła i kilka dobrych rad o śladach na kamieniu.",
                "long_desc": "Zna tropy kozy, wilka i człowieka, który za długo stał w jednym miejscu przy drodze.",
                "room_id": 165,
                "stats": CharacterStats(11, 12, 11, 11, 10, 100),
                "merchant": True,
                "gold": 48,
                "shop": "trakty_hunter_inventory",
            },
            "trakty_drwal": {
                "name": "drwal",
                "short_desc": "Drwal niesie topór i wiązkę drewna na suchy ogień.",
                "long_desc": "Przychodzi z lasu przy trakcie z żywicą na rękawach i nie pyta o sprawy, które można rozwiązać jednym cięciem.",
                "room_id": 166,
                "stats": CharacterStats(12, 10, 12, 9, 9, 110),
                "merchant": True,
                "gold": 30,
                "shop": "trakty_lumber_inventory",
            },
            "trakty_straznik": {
                "name": "strażnik traktu",
                "short_desc": "Strażnik traktu patrzy na rozstaje i liczy wozy.",
                "long_desc": "Nosi cierpliwość, włócznię i pamięć do twarzy, które za często wracają po zmroku.",
                "room_id": 172,
                "stats": CharacterStats(11, 11, 12, 11, 10, 108),
                "ai_state": "PATROL",
            },
            "trakty_handlarz": {
                "name": "handlarz",
                "short_desc": "Handlarz trzyma kram przy trakcie i rozstawia towar przed kolejną karawaną.",
                "long_desc": "Ma mały stół, dużą pamięć do cen i cierpliwość tylko do tych, którzy naprawdę chcą kupować.",
                "room_id": 176,
                "stats": CharacterStats(9, 10, 9, 11, 11, 92),
                "merchant": True,
                "gold": 46,
                "shop": "trakty_route_inventory",
            },
        }
        spec = data.get(vnum)
        if spec is None:
            raise KeyError(f"Unknown Trakty NPC: {vnum}")
        character = Character(spec["name"].capitalize())
        character.stats = spec["stats"]
        shop_factories = {
            "trakty_route_inventory": trakty_route_inventory,
            "trakty_caravan_inventory": trakty_caravan_inventory,
            "trakty_courier_inventory": trakty_courier_inventory,
            "trakty_hunter_inventory": trakty_hunter_inventory,
            "trakty_lumber_inventory": trakty_lumber_inventory,
        }
        shop_name = cast(str | None, spec.get("shop"))
        ai_state = spec["ai_state"] if "ai_state" in spec else "IDLE"
        merchant_gold = spec["gold"] if "gold" in spec else 100
        npc = NPC(
            vnum=vnum,
            name=spec["name"],
            short_desc=spec["short_desc"],
            long_desc=spec["long_desc"],
            zone="Trakty",
            faction="MEEKHAN",
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=bool(spec.get("merchant", False)),
            shop_inventory=list(shop_factories[shop_name]()) if shop_name is not None else [],
            merchant_gold=merchant_gold,
            home_room_id=int(spec["room_id"]),
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        npc.character.equipment.update(self._trakty_equipment(vnum))
        npc.dialogue_tree = self._trakty_dialogue(vnum)
        return self._finalize(npc)

    def _wild_dialogue(self, role: str) -> dict[str, list[str]]:
        dialogues = {
            "puszcza_mysliwy": self._social_dialogue(
                "Na leśnej ścieżce nie mówi się głośniej niż trzeba.",
                "Patrzę na tropy, stawiam sidła i znam las z tego, co zostaje po przejściu zwierzyny.",
                "Stoję tam, gdzie droga przechodzi w poszycie, a człowiek musi zwolnić.",
                "Plotki w lesie kończą się szybciej niż ślady po deszczu.",
                tropy="Tropy są uczciwsze niż większość ludzi.",
            ),
            "puszcza_zielarz": self._social_dialogue(
                "Jeśli szukasz ziół, patrz pod nogi, nie w korony drzew.",
                "Zbieram, suszę i mieszam to, co las daje bez pytania.",
                "Stoję przy polanach i strumieniach, gdzie rośliny rosną najtłustsze.",
                "Plotki wolę suszyć razem z ziołami: inaczej spleśnieją.",
                zioła="Dobre zioła rosną tam, gdzie nikt nie depcze zbyt często.",
            ),
            "puszcza_pustelnik": self._social_dialogue(
                "Cisza jest tu uczciwsza od miasta.",
                "Pilnuję kapliczki i wspomnień o tym, co las zabrał, a czego jeszcze nie oddał.",
                "Stoję przy starych kamieniach i zapomnianych ogniskach.",
                "Plotki zostawiam podróżnym. Ja wolę słuchać drzew.",
                kaplica="Kapliczka w lesie bywa lepszym schronieniem niż niejedna chata.",
            ),
            "puszcza_drwal": self._social_dialogue(
                "Jeśli słyszysz topór, to znaczy, że drewno już przegrało.",
                "Ścinam, rąbię i naprawiam obóz, zanim wiatr zrobi to za mnie.",
                "Stoję przy polanie i składzie drewna, bo tam widać pracę najlepiej.",
                "Plotki o lesie są jak suche gałęzie: łatwo je złamać, ale trudno spalić do końca.",
                drewno="Drewno trzeba brać tam, gdzie las pozwala, a nie tam, gdzie człowiek chce.",
            ),
            "puszcza_jelen": self._social_dialogue(
                "Nie zbliżaj się za szybko.",
                "Pasę się, uciekam i wracam tam, gdzie jest najspokojniej.",
                "Stoję przy polanach i wodzie, bo tam trawa jest lepsza.",
                "Plotki? Człowiek mówi za dużo, jeleń za mało.",
            ),
            "puszcza_dzik": self._social_dialogue(
                "Nie oglądam się za ludziami.",
                "Przecinam podszyt i ryję tam, gdzie korzenie są miękkie.",
                "Stoję w gęstwinie, gdzie ślady łatwo znikają.",
                "Plotki? Lepsze są kły i błoto.",
            ),
            "bagna_zielarz": self._social_dialogue(
                "Bagno daje dobre zioła, jeśli nie boisz się ubrudzić rąk.",
                "Zbieram torfowe rośliny, suszę trzcinę i znam leki na wilgoć.",
                "Stoję przy kępach i suchych wyspach, tam gdzie rosną najtwardsze rośliny.",
                "Plotki z mokradła trzeba odsączać dłużej niż napary.",
                zioła="W mokradle zioła rosną gorzkie, ale skuteczne.",
            ),
            "bagna_pustelnik": self._social_dialogue(
                "Tu można zniknąć i nie być znalezionym.",
                "Pilnuję kapliczki i starego ołtarza, bo ktoś musi pamiętać, że bagno też ma święte miejsca.",
                "Stoję przy suchych kępach i kamieniach, które jeszcze nie zapadły się w torf.",
                "Plotki? Bagno połyka je szybciej niż ludzi.",
                kaplica="Stary ołtarz trzyma się lepiej niż połowa świata naokoło.",
            ),
            "bagna_mysliwy": self._social_dialogue(
                "Na mokradle trzeba patrzeć dwa razy: raz pod nogi, raz na ślady.",
                "Poluję, tropię i sprawdzam, co wyszło z wody po zmroku.",
                "Stoję przy groblach i trzcinie, gdzie zwierzyna lubi przechodzić po cichu.",
                "Plotki o bagnach zwykle kończą się w wodzie.",
                tropy="Tropy w błocie są jak podpisy: nie da się ich łatwo skłamać.",
            ),
            "bagna_zaba": self._social_dialogue(
                "Rechot to też odpowiedź.",
                "Skaczę, chowam się i wiem, gdzie jest najmniej suchego błędu.",
                "Stoję przy wodzie i trzcinie, bo to mój dom.",
                "Plotki? Ja słyszę tylko plusk.",
            ),
        }
        return dialogues.get(role, self._social_dialogue(
            "Nie mam dziś wiele do powiedzenia.",
            "Las i bagno wolą czyny od słów.",
            "Stoję tam, gdzie mnie postawiono.",
            "Plotki znikają tu szybciej niż ślad po deszczu.",
        ))

    def _wild_equipment(self, vnum: str) -> dict[str, Item | None]:
        if vnum == "puszcza_mysliwy":
            return {
                "korpus": Item("leśne futro", "Ciężkie futro odporne na wilgoć i mróz.", 2.0, 11, "puszcza_hunter_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("nóż leśny", "Nóż do skórowania, lin i pracy w lesie.", 0.6, 16, "puszcza_hunter_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_zielarz":
            return {
                "korpus": Item("płócienna szata", "Szata odporniejsza na wilgoć i zabrudzenia po ziołach.", 1.0, 6, "puszcza_herbal_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("nożyk ziołowy", "Mały nożyk do obcinania łodyg i korzeni.", 0.2, 3, "puszcza_herbal_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=1, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_pustelnik":
            return {
                "korpus": Item("wytarty płaszcz", "Płaszcz tak stary, jak opowieści o lesie.", 1.3, 5, "puszcza_hermit_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("kij pustelnika", "Kij do marszu i opierania się przy kamieniach.", 0.9, 4, "puszcza_hermit_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "puszcza_drwal":
            return {
                "korpus": Item("roboczy kaftan", "Kaftan odporny na żywicę i pył z kory.", 1.4, 6, "puszcza_lumber_coat", "armor", "korpus", protection=0),
                "prawa_reka": Item("topór drwala", "Ciężki topór do zwalonych pni.", 3.0, 10, "puszcza_lumber_axe", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "puszcza_szczur":
            return {
                "korpus": Item("szara szczecina", "Cienka, matowa osłona zwykłego leśnego szczura.", 0.0, 0, "puszcza_rat_hide", "armor", "korpus", protection=0),
            }
        if vnum == "puszcza_kruk":
            return {
                "korpus": Item("czarne pióra", "Warstwa piór i cienia, która pomaga krukowi wtopić się w konary.", 0.0, 0, "puszcza_raven_feathers", "armor", "korpus", protection=0),
                "prawa_reka": Item("krucze szpony", "Naturalne szpony do wspinaczki i obrony.", 0.0, 0, "puszcza_raven_claws", "weapon", "prawa_reka", damage_type="kluta", base_damage=1, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_lis":
            return {
                "korpus": Item("rudawa skóra", "Miękka skóra lisa, zwinna i ciepła.", 0.0, 0, "puszcza_fox_hide", "armor", "korpus", protection=0),
                "prawa_reka": Item("lisie zęby", "Drobne, lecz ostre kły i zęby lisa.", 0.0, 0, "puszcza_fox_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=1, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_pies_dziki":
            return {
                "korpus": Item("szorstkie futro", "Twarde futro dzikiego psa.", 0.0, 0, "puszcza_wild_dog_fur", "armor", "korpus", protection=0),
                "prawa_reka": Item("dzikie kły", "Kły dzikiego psa. Małe, ale nieprzyjemne.", 0.0, 0, "puszcza_wild_dog_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_wilk_mlody":
            return {
                "korpus": Item("wilcze futro", "Młode futro wilka, jeszcze niezbyt gęste.", 0.0, 0, "puszcza_young_wolf_fur", "armor", "korpus", protection=0),
                "prawa_reka": Item("wilcze kły", "Młode, ale już ostre kły wilka.", 0.0, 0, "puszcza_young_wolf_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_wilk":
            return {
                "korpus": Item("wilcze futro", "Grube futro dorosłego wilka.", 0.0, 0, "puszcza_wolf_fur", "armor", "korpus", protection=0),
                "prawa_reka": Item("wilcze kły", "Twarde kły dorosłego wilka.", 0.0, 0, "puszcza_wolf_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_jelen":
            return {
                "korpus": Item("sierść jelenia", "Naturalna skóra i poroże tworzące zwykłe, leśne ciało.", 0.0, 0, "puszcza_deer_hide", "armor", "korpus", protection=0),
                "prawa_reka": Item("poroże", "Naturalne poroże, bardziej do obrony niż ataku.", 0.0, 0, "puszcza_deer_antlers", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_dzik":
            return {
                "korpus": Item("szorstka szczecina", "Naturalna osłona dzika.", 0.0, 0, "puszcza_boar_hide", "armor", "korpus", protection=0),
                "prawa_reka": Item("kły dzika", "Naturalne kły i ciężki kark.", 0.0, 0, "puszcza_boar_tusks", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=3, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "puszcza_pajak":
            return {
                "korpus": Item("chitynowy pancerz", "Ciemny pancerz pajęczej skorupy.", 0.0, 0, "puszcza_spider_chitin", "armor", "korpus", protection=0),
                "prawa_reka": Item("jadowite szczękoczułki", "Ostre szczękoczułki gotowe do ataku.", 0.0, 0, "puszcza_spider_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=1, reach=1, initiative_modifier=3, parry_bonus=0),
            }
        if vnum == "puszcza_pajak_lesny":
            return {
                "korpus": Item("leśny pancerz", "Szorstka osłona pajęczej skrytości.", 0.0, 0, "puszcza_forest_spider_chitin", "armor", "korpus", protection=0),
                "prawa_reka": Item("leśne szczękoczułki", "Szczękoczułki większego leśnego pająka.", 0.0, 0, "puszcza_forest_spider_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_pajak_duzy":
            return {
                "korpus": Item("gruby pancerz pajęczy", "Cięższy chitynowy pancerz dużego pająka.", 0.0, 0, "puszcza_big_spider_chitin", "armor", "korpus", protection=1),
                "prawa_reka": Item("mocne szczękoczułki", "Szczękoczułki dużego pająka, zdolne przebić lekką skórę.", 0.0, 0, "puszcza_big_spider_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_wilk_stary":
            return {
                "korpus": Item("poszarzałe futro", "Stare, gęste futro wilka, wytarte od walk.", 0.0, 0, "puszcza_old_wolf_fur", "armor", "korpus", protection=0),
                "prawa_reka": Item("stępione kły", "Kły starego wilka, nadal groźne.", 0.0, 0, "puszcza_old_wolf_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_wataha_wilkow":
            return {
                "korpus": Item("zszyte futro stada", "Masywna osłona z futra i blizn watahy.", 0.0, 0, "puszcza_wolf_pack_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("wilcze zębiska stada", "Wataha gryzie jak jedno zwierzę.", 0.0, 0, "puszcza_wolf_pack_fangs", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_niedzwiedz":
            return {
                "korpus": Item("gruba sierść", "Ciężka, gruba sierść niedźwiedzia.", 0.0, 0, "puszcza_bear_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("niedźwiedzie łapy", "Potężne łapy zdolne rozszarpać ofiarę.", 0.0, 0, "puszcza_bear_claws", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=5, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "puszcza_niedzwiedzica":
            return {
                "korpus": Item("matowa sierść", "Gruba sierść niedźwiedzicy chroniąca przed zimnem.", 0.0, 0, "puszcza_bear_mother_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("ostre pazury", "Pazury niedźwiedzicy, groźne przy szarży.", 0.0, 0, "puszcza_bear_mother_claws", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=5, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "puszcza_bandyta":
            return {
                "korpus": Item("skórzana kamizelka", "Porysowana kamizelka bandyty.", 1.2, 8, "puszcza_bandit_vest", "armor", "korpus", protection=1),
                "prawa_reka": Item("krótki miecz", "Niewygodny, ale skuteczny miecz z rabunku.", 1.8, 12, "puszcza_bandit_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_bandyta_zwiadowca":
            return {
                "korpus": Item("płaszcz zwiadowcy", "Szary płaszcz do znikania w leśnym cieniu.", 1.1, 8, "puszcza_bandit_scout_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("sztylet zwiadowcy", "Cichy sztylet do podchodzenia i ucieczki.", 0.5, 10, "puszcza_bandit_dagger", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_lowca":
            return {
                "korpus": Item("łowiecki kaftan", "Wytrzymały kaftan człowieka żyjącego z łowów.", 1.5, 9, "puszcza_hunter_jerkin", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia łowcy", "Długa włócznia do trzymania drapieżników na dystans.", 2.0, 13, "puszcza_hunter_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_lowczy":
            return {
                "korpus": Item("płaszcz tropiciela", "Wysłużony płaszcz pokryty śladami błota i żywicy.", 1.2, 8, "puszcza_tracker_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("sidła i hak", "Sprzęt do łapania i unieruchamiania zwierzyny.", 0.8, 9, "puszcza_tracker_hook", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=3, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        if vnum == "puszcza_bandycki_naczelnik":
            return {
                "korpus": Item("stara kolczuga", "Ciężka kolczuga przejęta po kolejnych ofiarach.", 4.0, 18, "puszcza_bandit_leader_mail", "armor", "korpus", protection=2),
                "prawa_reka": Item("szabla herszta", "Ostra szabla bandyckiego herszta.", 2.0, 20, "puszcza_bandit_leader_sabre", "weapon", "prawa_reka", damage_type="cieta", base_damage=6, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "puszcza_niedzwiedzi_olbrzym":
            return {
                "korpus": Item("potężna sierść", "Potężne futro ogromnego niedźwiedzia.", 0.0, 0, "puszcza_giant_bear_fur", "armor", "korpus", protection=2),
                "prawa_reka": Item("olbrzymie pazury", "Łapy zdolne miażdżyć pancerz i kości.", 0.0, 0, "puszcza_giant_bear_claws", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=7, reach=1, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "puszcza_troll":
            return {
                "korpus": Item("twarda skóra trolla", "Gruba, łupliwa skóra starego trolla.", 3.0, 25, "puszcza_troll_hide", "armor", "korpus", protection=2),
                "prawa_reka": Item("leśna maczuga", "Ciężka gałąź wzmocniona kamieniami i błotem.", 6.0, 18, "puszcza_forest_club", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=8, reach=1, initiative_modifier=-1, parry_bonus=0),
            }
        if vnum == "bagna_zielarz":
            return {
                "korpus": Item("mokry fartuch", "Fartuch chroniący przed wodą i błotem.", 1.0, 5, "bagna_herbal_apron", "armor", "korpus", protection=0),
                "prawa_reka": Item("nożyk torfowy", "Krótki nożyk do cięcia trzcin i ziół.", 0.2, 3, "bagna_herbal_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=1, reach=1, initiative_modifier=1, parry_bonus=0),
            }
        if vnum == "bagna_pustelnik":
            return {
                "korpus": Item("stara opończa", "Opończa przesiąknięta wilgocią i dymem.", 1.2, 5, "bagna_hermit_cloak", "armor", "korpus", protection=0),
                "prawa_reka": Item("kij błotny", "Kij do chodzenia po groblach i kładkach.", 1.0, 4, "bagna_hermit_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "bagna_mysliwy":
            return {
                "korpus": Item("błotne futro", "Futro zabezpieczone przed wodą i pluskiem.", 1.8, 10, "bagna_hunter_fur", "armor", "korpus", protection=1),
                "prawa_reka": Item("włócznia bagienna", "Włócznia odpowiednia do marszu po mokradłach.", 2.0, 16, "bagna_hunter_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=4, reach=2, initiative_modifier=0, parry_bonus=0),
            }
        if vnum == "bagna_zaba":
            return {
                "korpus": Item("śliska skóra", "Naturalna, wilgotna skóra stworzenia z mokradeł.", 0.0, 0, "bagna_frog_skin", "armor", "korpus", protection=0),
                "prawa_reka": Item("długi skok", "Niezwykle szybka, naturalna pogoń.", 0.0, 0, "bagna_frog_jump", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=2, parry_bonus=0),
            }
        return {}

    class WildNPCSpec(TypedDict, total=False):
        name: str
        short_desc: str
        long_desc: str
        room_id: int
        stats: CharacterStats
        merchant: bool
        gold: int
        shop: str
        ai_state: str
        zone: str

    def _create_wild_npc(self, vnum: str, room_id: int) -> NPC:
        data: dict[str, NPCFactory.WildNPCSpec] = {
            "puszcza_mysliwy": {
                "name": "myśliwy",
                "short_desc": "Myśliwy obserwuje tropy przy leśnym skraju.",
                "long_desc": "Zna las, strumienie i miejsca, gdzie zwierzyna wraca po zmroku.",
                "room_id": 216,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(11, 12, 11, 11, 10, 100),
                "merchant": True,
                "gold": 45,
                "shop": "puszcza_hunter_inventory",
            },
            "puszcza_zielarz": {
                "name": "zielarz",
                "short_desc": "Zielarz suszy zioła na sznurku między drzewami.",
                "long_desc": "Zbiera rośliny, które rosną tam, gdzie inni nie chcą stawiać stopy.",
                "room_id": 223,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(9, 11, 9, 12, 11, 90),
                "merchant": True,
                "gold": 34,
                "shop": "puszcza_herbal_inventory",
            },
            "puszcza_pustelnik": {
                "name": "pustelnik",
                "short_desc": "Pustelnik pilnuje kapliczki i słucha lasu.",
                "long_desc": "Mieszka samotnie przy starych kamieniach, żyjąc bardziej z ciszy niż z jedzenia.",
                "room_id": 252,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(8, 10, 9, 11, 12, 80),
            },
            "puszcza_drwal": {
                "name": "drwal",
                "short_desc": "Drwal oznacza pieńki i układa drewno przy polanie.",
                "long_desc": "Pracuje w lesie ostrożnie, bo wie, że las pamięta każdy źle poprowadzony topór.",
                "room_id": 246,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(12, 10, 12, 9, 9, 105),
                "merchant": True,
                "gold": 26,
                "shop": "puszcza_herbal_inventory",
            },
            "puszcza_szczur": {
                "name": "szczur",
                "short_desc": "Szczur przemyka przy korzeniach i znika w ściółce.",
                "long_desc": "Mały leśny gryzoń, który żyje tam, gdzie zostają resztki po obozach i zapomnianych ścieżkach.",
                "room_id": 230,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(5, 11, 6, 12, 6, 35),
                "ai_state": "PATROL",
            },
            "puszcza_pajak": {
                "name": "pająk",
                "short_desc": "Pająk siedzi nieruchomo wśród gałęzi i czeka na ruch ofiary.",
                "long_desc": "Drobny, ale nieprzyjemny mieszkaniec podszytu, który umie zamienić ciszę w pułapkę.",
                "room_id": 216,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(5, 12, 6, 13, 6, 38),
                "ai_state": "PATROL",
            },
            "puszcza_kruk": {
                "name": "kruk",
                "short_desc": "Kruk siedzi nisko na gałęzi i obserwuje okolicę czarnym okiem.",
                "long_desc": "Sprytne ptaszysko, które zna zapach łatwej zdobyczy i od razu rozumie, kiedy trzeba się przenieść.",
                "room_id": 223,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(5, 13, 5, 12, 6, 40),
                "ai_state": "PATROL",
            },
            "puszcza_lis": {
                "name": "lis",
                "short_desc": "Lis przemyka między krzakami i co chwilę zastyga w bezruchu.",
                "long_desc": "Rude zwierzę lasu, ostrożne, szybkie i trudne do zaskoczenia.",
                "room_id": 223,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(7, 14, 7, 12, 8, 50),
                "ai_state": "PATROL",
            },
            "puszcza_pajak_lesny": {
                "name": "leśny pająk",
                "short_desc": "Leśny pająk siedzi w cieniu konarów i pilnuje przejścia.",
                "long_desc": "Większy od zwykłego pająka, cierpliwy i prawie niewidoczny, dopóki nie ruszy się za szybko.",
                "room_id": 229,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(7, 13, 7, 13, 7, 50),
                "ai_state": "PATROL",
            },
            "puszcza_wilk": {
                "name": "wilk",
                "short_desc": "Wilk stoi w półmroku i mierzy wszystko chłodnym spojrzeniem.",
                "long_desc": "Dorosły drapieżnik z puszczy, przyzwyczajony do samotnego polowania i szybkiego ataku.",
                "room_id": 234,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(10, 14, 9, 12, 8, 85),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_wilk_stary": {
                "name": "stary wilk",
                "short_desc": "Stary wilk porusza się wolniej, ale wciąż wygląda groźnie.",
                "long_desc": "Blizny na pysku i zgrubiałe łapy zdradzają zwierzę, które przeżyło zbyt wiele zim, by dać się zlekceważyć.",
                "room_id": 234,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(11, 13, 10, 12, 9, 95),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_wataha_wilkow": {
                "name": "wataha wilków",
                "short_desc": "Wataha wilków trzyma się razem, jakby las był jej własnością.",
                "long_desc": "Kilka wilków porusza się tu niemal jak jedno ciało, zamykając drogę i zmuszając ofiarę do błędu.",
                "room_id": 234,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(11, 14, 10, 13, 9, 105),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_niedzwiedz": {
                "name": "niedźwiedź",
                "short_desc": "Niedźwiedź przechodzi między pniami ciężkim krokiem.",
                "long_desc": "Maszyna z mięśni, sierści i cierpliwości. Jeśli ruszy, lepiej już nie stać na drodze.",
                "room_id": 241,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(13, 11, 14, 9, 9, 120),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_niedzwiedzica": {
                "name": "niedźwiedzica",
                "short_desc": "Niedźwiedzica stoi przy chaszczach i pilnuje swojego terenu.",
                "long_desc": "Nawet z dala widać, że nie zamierza ustępować nikomu, kto wszedł za głęboko w jej las.",
                "room_id": 241,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(13, 12, 13, 10, 10, 115),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_bandyta": {
                "name": "bandyta",
                "short_desc": "Bandyta czai się przy drzewach i obserwuje drogę.",
                "long_desc": "Zwykły leśny opryszek, który woli zasadzić się na słabszego niż walczyć uczciwie.",
                "room_id": 246,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(9, 12, 9, 11, 8, 70),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_bandyta_zwiadowca": {
                "name": "bandycki zwiadowca",
                "short_desc": "Zwiadowca bandytów nasłuchuje lasu i sprawdza ślady przy ziemi.",
                "long_desc": "Porusza się po lesie bezszelestnie i wie, kiedy wezwać resztę bandy.",
                "room_id": 252,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(9, 13, 8, 12, 8, 74),
                "ai_state": "PATROL",
            },
            "puszcza_lowca": {
                "name": "łowca",
                "short_desc": "Łowca chodzi po lesie pewnie, jakby znał każdy jego zakręt.",
                "long_desc": "Nie ufa nikomu, strzela pierwszy i pyta później, przez co sam coraz bardziej przypomina to, na co polował.",
                "room_id": 252,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(10, 12, 10, 11, 9, 80),
                "ai_state": "PATROL",
            },
            "puszcza_lowczy": {
                "name": "lowczy",
                "short_desc": "Lowczy zna sidła, tropy i zwyczaje leśnych dróg.",
                "long_desc": "Węszy za zwierzyną i ludźmi z taką samą uwagą, a jego stary płaszcz znika między drzewami jak cień.",
                "room_id": 258,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(9, 13, 9, 12, 9, 78),
                "ai_state": "PATROL",
            },
            "puszcza_pajak_duzy": {
                "name": "duży pająk",
                "short_desc": "Duży pająk zwisa nad ścieżką jak ciemna, cierpliwa pułapka.",
                "long_desc": "Ma więcej jadu i więcej cierpliwości niż cały kosz leśnych plotek.",
                "room_id": 258,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(8, 13, 8, 13, 8, 60),
                "ai_state": "PATROL",
            },
            "puszcza_bandycki_naczelnik": {
                "name": "bandycki naczelnik",
                "short_desc": "Naczelnik bandy stoi twardo przy ciemnym obozie.",
                "long_desc": "Najbardziej bezwzględny z leśnych zbójów, który trzyma resztę w ryzach tylko strachem i żelazem.",
                "room_id": 267,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(14, 13, 14, 12, 11, 135),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_niedzwiedzi_olbrzym": {
                "name": "ogromny niedźwiedź",
                "short_desc": "Ogromny niedźwiedź ociera się o pnie i blokuje całą ścieżkę.",
                "long_desc": "To już nie zwykły drapieżnik, tylko żywa przeszkoda, która potrafi zmiażdżyć człowieka samym impetem.",
                "room_id": 267,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(15, 11, 16, 9, 10, 150),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_troll": {
                "name": "troll",
                "short_desc": "Rzadki troll chowa się głębiej w lesie i nie lubi światła.",
                "long_desc": "Stary, brutalny stwór, którego obecność w Puszczy Ciszy tłumaczy tylko najgorszy przypadek albo cudzą bezmyślność.",
                "room_id": 274,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(17, 9, 16, 8, 8, 160),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_pies_dziki": {
                "name": "dziki pies",
                "short_desc": "Dziki pies warczy przy pniaku i nie spuszcza z oczu ścieżki.",
                "long_desc": "Zmarniałe zwierzę bez opieki, agresywne i zbyt pewne własnych zębów.",
                "room_id": 246,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(8, 13, 8, 11, 8, 60),
                "ai_state": "AGGRESSIVE",
            },
            "puszcza_wilk_mlody": {
                "name": "młody wilk",
                "short_desc": "Młody wilk krąży niepewnie po swojej ścieżce.",
                "long_desc": "Jeszcze nie dorósł do pełnej zuchwałości, ale już uczy się, jak podchodzić bliżej i uciekać szybciej.",
                "room_id": 229,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(8, 13, 8, 12, 7, 65),
                "ai_state": "PATROL",
            },
            "puszcza_jelen": {
                "name": "jeleń",
                "short_desc": "Jeleń stoi w cieniu drzew i obserwuje każdy ruch.",
                "long_desc": "Zwierzę lasu, czujne i niechętne do bliższego kontaktu.",
                "room_id": 241,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(9, 13, 9, 12, 8, 70),
                "ai_state": "PATROL",
            },
            "puszcza_dzik": {
                "name": "dzik",
                "short_desc": "Dzik ryje przy korzeniach i nie lubi niespodzianek.",
                "long_desc": "Potężne zwierzę z mokrym ryjem i ciężkim karkiem.",
                "room_id": 267,
                "zone": "Puszcza_Ciszy",
                "stats": CharacterStats(12, 11, 13, 9, 11, 100),
                "ai_state": "AGGRESSIVE",
            },
            "bagna_zielarz": {
                "name": "zielarka",
                "short_desc": "Zielarka zbiera torfowe zioła przy skraju mokradeł.",
                "long_desc": "Zna rośliny rosnące tylko tam, gdzie ziemia jest wiecznie mokra i gorzka.",
                "room_id": 478,
                "zone": "Bagna_Hookri",
                "stats": CharacterStats(9, 11, 9, 12, 11, 90),
                "merchant": True,
                "gold": 36,
                "shop": "bagna_herbal_inventory",
            },
            "bagna_pustelnik": {
                "name": "pustelnik",
                "short_desc": "Pustelnik pilnuje starego ołtarza pośrodku bagien.",
                "long_desc": "Mieszka przy suchych kępach i wierzy, że bagno trzeba najpierw zrozumieć, a dopiero potem przejść.",
                "room_id": 493,
                "zone": "Bagna_Hookri",
                "stats": CharacterStats(8, 10, 9, 11, 12, 80),
            },
            "bagna_mysliwy": {
                "name": "myśliwy",
                "short_desc": "Myśliwy śledzi ptactwo i płazy po mokradłach.",
                "long_desc": "Zna groble, kładki i miejsca, gdzie z wody wychodzi zwierzyna.",
                "room_id": 488,
                "zone": "Bagna_Hookri",
                "stats": CharacterStats(10, 12, 10, 11, 10, 95),
                "merchant": True,
                "gold": 38,
                "shop": "puszcza_hunter_inventory",
            },
            "bagna_zaba": {
                "name": "żaba",
                "short_desc": "Żaba przysiada w trzcinach i znika, gdy ktoś rusza się za głośno.",
                "long_desc": "Niewielkie stworzenie mokradeł, szybkie i trudne do złapania.",
                "room_id": 481,
                "zone": "Bagna_Hookri",
                "stats": CharacterStats(6, 14, 6, 12, 8, 50),
                "ai_state": "PATROL",
            },
        }
        spec = data.get(vnum)
        if spec is None:
            raise KeyError(f"Unknown wild NPC: {vnum}")
        character = Character(spec["name"].capitalize())
        character.stats = spec["stats"]
        shop_factories = {
            "puszcza_herbal_inventory": puszcza_herbal_inventory,
            "puszcza_hunter_inventory": puszcza_hunter_inventory,
            "puszcza_hermit_inventory": puszcza_hermit_inventory,
            "bagna_herbal_inventory": bagna_herbal_inventory,
            "bagna_hermit_inventory": bagna_hermit_inventory,
        }
        shop_name = cast(str | None, spec.get("shop"))
        ai_state = spec["ai_state"] if "ai_state" in spec else "IDLE"
        merchant_gold = spec["gold"] if "gold" in spec else 100
        npc = NPC(
            vnum=vnum,
            name=spec["name"],
            short_desc=spec["short_desc"],
            long_desc=spec["long_desc"],
            zone=spec["zone"],
            faction="REBELS",
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=bool(spec.get("merchant", False)),
            shop_inventory=list(shop_factories[shop_name]()) if shop_name is not None else [],
            merchant_gold=merchant_gold,
            home_room_id=int(spec["room_id"]),
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        npc.character.equipment.update(self._wild_equipment(vnum))
        npc.dialogue_tree = self._wild_dialogue(vnum)
        return self._finalize(npc)

    class StraznicaNPCSpec(TypedDict, total=False):
        name: str
        short_desc: str
        long_desc: str
        room_id: int
        stats: CharacterStats
        merchant: bool
        gold: int
        shop: str
        ai_state: str

    def _create_straznica_npc(self, vnum: str, room_id: int) -> NPC:
        data: dict[str, NPCFactory.StraznicaNPCSpec] = {
            "straznica_dowodca": {
                "name": "komendant",
                "short_desc": "Komendant strażnicy porządkuje meldunki i spisuje ruch na przełęczy.",
                "long_desc": "Odpowiada za przejazd, ludzi i zimowe blokady, a każdy jego rozkaz brzmi, jakby już wcześniej został sprawdzony.",
                "room_id": 125,
                "stats": CharacterStats(13, 11, 13, 12, 12, 140),
                "ai_state": "GUARD",
            },
            "straznica_wartownik": {
                "name": "wartownik",
                "short_desc": "Wartownik strzeże wąskiego przejazdu i pilnuje, by nikt nie wchodził bez meldunku.",
                "long_desc": "Zna każdy kamień przy murze, bo spędza tam więcej czasu niż w izbie.",
                "room_id": 126,
                "stats": CharacterStats(12, 11, 12, 11, 11, 120),
                "ai_state": "GUARD",
            },
            "straznica_zwiadowca": {
                "name": "zwiadowca",
                "short_desc": "Zwiadowca wypatruje ruchu na górskiej ścieżce i lubi zniknąć za załamaniem skały.",
                "long_desc": "Wraca z góry z błotem na butach i informacjami, których nikt inny nie zauważyłby na czas.",
                "room_id": 127,
                "stats": CharacterStats(11, 12, 11, 12, 10, 110),
                "ai_state": "PATROL",
            },
            "straznica_przewodnik": {
                "name": "przewodnik",
                "short_desc": "Przewodnik zna bezpieczniejsze obejścia i ostrzega przed zlodowaciałymi płytami.",
                "long_desc": "Prowadzi ludzi przez przełęcz tak, jakby każdy krok miał być później odtworzony z pamięci.",
                "room_id": 128,
                "stats": CharacterStats(10, 11, 10, 12, 11, 100),
                "merchant": True,
                "gold": 40,
                "shop": "straznica_supply_inventory",
            },
            "straznica_karawanowy": {
                "name": "kupiec karawan",
                "short_desc": "Kupiec karawan liczy skrzynie, koła i opłaty za przejazd.",
                "long_desc": "W przełęczy nie pyta o marzenia. Pyta o wagę, pieczęć i to, czy ładunek przetrwa wiatr.",
                "room_id": 129,
                "stats": CharacterStats(10, 10, 10, 11, 11, 95),
                "merchant": True,
                "gold": 55,
                "shop": "straznica_caravan_inventory",
            },
            "straznica_woznica": {
                "name": "woźnica",
                "short_desc": "Woźnica zna rytm kół, skrzyni i hamowania na stromym zboczu.",
                "long_desc": "Kiedy mówi o drodze, mówi jak o żywym stworzeniu, które trzeba szanować albo zostawić w spokoju.",
                "room_id": 130,
                "stats": CharacterStats(11, 10, 11, 10, 10, 105),
            },
            "straznica_podrozny": {
                "name": "podróżny",
                "short_desc": "Podróżny odpoczywa przy przełęczy, zanim ruszy dalej na północ.",
                "long_desc": "Ma błoto na płaszczu i ten rodzaj cierpliwości, który rodzi się tylko na długiej drodze.",
                "room_id": 131,
                "stats": CharacterStats(9, 10, 9, 10, 10, 90),
            },
            "straznica_pielgrzym": {
                "name": "pielgrzym",
                "short_desc": "Pielgrzym zatrzymuje się przy kaplicy i ogrzewa dłonie nad lampą.",
                "long_desc": "Idzie lekko, choć droga jest stroma, i słucha ciszy jak modlitwy.",
                "room_id": 132,
                "stats": CharacterStats(9, 10, 9, 11, 12, 85),
            },
            "straznica_mysliwy": {
                "name": "myśliwy",
                "short_desc": "Myśliwy z przełęczy sprzedaje skórę, futro i kilka dobrych rad o śniegu.",
                "long_desc": "Zna tropy kozy, wilka i człowieka, który za długo stał w jednym miejscu.",
                "room_id": 133,
                "stats": CharacterStats(11, 12, 11, 11, 10, 100),
                "merchant": True,
                "gold": 52,
                "shop": "straznica_hunter_inventory",
            },
        }
        spec = data.get(vnum)
        if spec is None:
            raise KeyError(f"Unknown Straznica NPC: {vnum}")
        character = Character(spec["name"].capitalize())
        character.stats = spec["stats"]
        shop_factories = {
            "straznica_supply_inventory": straznica_supply_inventory,
            "straznica_caravan_inventory": straznica_caravan_inventory,
            "straznica_hunter_inventory": straznica_hunter_inventory,
        }
        shop_name = cast(str | None, spec.get("shop"))
        ai_state = spec["ai_state"] if "ai_state" in spec else "IDLE"
        merchant_gold = spec["gold"] if "gold" in spec else 100
        npc = NPC(
            vnum=vnum,
            name=spec["name"],
            short_desc=spec["short_desc"],
            long_desc=spec["long_desc"],
            zone="Straznica_Przeleczy",
            faction="MEEKHAN",
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=bool(spec.get("merchant", False)),
            shop_inventory=list(shop_factories[shop_name]()) if shop_name is not None else [],
            merchant_gold=merchant_gold,
            home_room_id=int(spec["room_id"]),
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        npc.character.equipment.update(self._straznica_equipment(vnum))
        npc.dialogue_tree = self._straznica_dialogue(vnum)
        return self._finalize(npc)

    def _create_dungrim_npc(self, vnum: str, room_id: int) -> NPC:
        data: dict[str, NPCFactory.DungrimNPCSpec] = {
            "dungrim_commander": {
                "name": "dowódca fortu",
                "short_desc": "Dowódca fortu stoi nad mapą i liczy zarówno ludzi, jak i zapasy.",
                "long_desc": "Pilnuje Dungrim z zimną precyzją człowieka, który wie, że błąd na granicy kończy się szybciej niż dyskusja.",
                "room_id": 120,
                "stats": CharacterStats(14, 11, 14, 12, 12, 150),
                "ai_state": "GUARD",
            },
            "dungrim_lieutenant": {
                "name": "oficer",
                "short_desc": "Oficer prowadzi raporty, zmiany i krótkie odprawy przy mapie.",
                "long_desc": "Mówi mało, a jego głos wystarcza, by koszary zamilkły.",
                "room_id": 118,
                "stats": CharacterStats(12, 11, 12, 11, 11, 120),
                "ai_state": "GUARD",
            },
            "dungrim_sergeant": {
                "name": "sierżant",
                "short_desc": "Sierżant zna każdy korytarz koszar i każdą wymówkę spóźnionego wartownika.",
                "long_desc": "Utrzymuje rytm patroli, bo bez niego forteca rozpadłaby się na krzykliwe nawyki.",
                "room_id": 116,
                "stats": CharacterStats(12, 11, 12, 11, 11, 125),
                "ai_state": "PATROL",
            },
            "dungrim_guard": {
                "name": "strażnik",
                "short_desc": "Strażnik bramy stoi nieruchomo, ale widzi każdy ruch przy przejeździe.",
                "long_desc": "Nosi blizny, hełm i cierpliwość do ludzi, którzy myślą, że wjazd do fortu jest opcjonalny.",
                "room_id": 110,
                "stats": CharacterStats(11, 11, 12, 10, 10, 110),
                "ai_state": "GUARD",
            },
            "dungrim_patrol_guard": {
                "name": "patrolowy",
                "short_desc": "Patrolowy obchodzi mur, zanim zdąży się zrobić cicho.",
                "long_desc": "Widzi drogę, wieżę i dziedziniec, bo od tego zależy, czy noc będzie spokojna.",
                "room_id": 112,
                "stats": CharacterStats(11, 12, 11, 10, 10, 108),
                "ai_state": "PATROL",
            },
            "dungrim_armorer": {
                "name": "zbrojmistrz",
                "short_desc": "Zbrojmistrz siedzi pośród hełmów, nitów i tarcz z wgnieceniami.",
                "long_desc": "Zna wagę dobrego pancerza i nie uznaje połowicznych napraw.",
                "room_id": 121,
                "stats": CharacterStats(12, 10, 12, 10, 10, 110),
                "merchant": True,
                "gold": 64,
                "shop": "dungrim_armory_inventory",
            },
            "dungrim_military_blacksmith": {
                "name": "kowal wojskowy",
                "short_desc": "Kowal wojskowy pilnuje iskier, gwoździ i ostrzy przy kuźni fortecznej.",
                "long_desc": "Naprawia pancerze i broń, a po każdej zmianie zlicza, czy coś nie zniknęło w ogniu.",
                "room_id": 117,
                "stats": CharacterStats(13, 10, 13, 10, 10, 120),
                "merchant": True,
                "gold": 72,
                "shop": "dungrim_armory_inventory",
            },
            "dungrim_quartermaster": {
                "name": "magazynier",
                "short_desc": "Magazynier ma przy pasie klucze, a w głowie dokładny spis skrzyń.",
                "long_desc": "Nikt tak jak on nie wie, które racje znikają, a które tylko zmieniają miejsce.",
                "room_id": 122,
                "stats": CharacterStats(10, 10, 10, 11, 11, 100),
                "merchant": True,
                "gold": 50,
                "shop": "dungrim_quartermaster_inventory",
            },
            "dungrim_storekeeper": {
                "name": "składnik",
                "short_desc": "Składnik pilnuje beczek, skrzyń i worków w fortecznych magazynach.",
                "long_desc": "Zna kolejność rzeczy lepiej niż kolejność przełożonych i nie uważa tego za wadę.",
                "room_id": 123,
                "stats": CharacterStats(10, 10, 10, 10, 10, 95),
                "merchant": True,
                "gold": 36,
                "shop": "dungrim_quartermaster_inventory",
            },
            "dungrim_stablemaster": {
                "name": "stajenny",
                "short_desc": "Stajenny pilnuje koni patrolowych i porządku w stajniach.",
                "long_desc": "Zna każdy stukot kopyt i każdą sztukę, która nie lubi deszczu.",
                "room_id": 114,
                "stats": CharacterStats(10, 10, 10, 10, 11, 95),
                "merchant": True,
                "gold": 40,
                "shop": "dungrim_stable_inventory",
            },
            "dungrim_cook": {
                "name": "kucharz",
                "short_desc": "Kucharz miesza gulasz i liczy, ile racji zostało do wieczora.",
                "long_desc": "Nie pyta o bohaterstwo, tylko o garnki, sól i kolejkę po jedzenie.",
                "room_id": 115,
                "stats": CharacterStats(9, 10, 9, 10, 10, 90),
                "merchant": True,
                "gold": 30,
                "shop": "dungrim_kitchen_inventory",
            },
        }
        spec = data.get(vnum)
        if spec is None:
            raise KeyError(f"Unknown Dungrim NPC: {vnum}")
        character = Character(spec["name"].capitalize())
        character.stats = spec["stats"]
        shop_factories = {
            "dungrim_armory_inventory": dungrim_armory_inventory,
            "dungrim_quartermaster_inventory": dungrim_quartermaster_inventory,
            "dungrim_stable_inventory": dungrim_stable_inventory,
            "dungrim_kitchen_inventory": dungrim_kitchen_inventory,
        }
        shop_name = cast(str | None, spec.get("shop"))
        ai_state = spec["ai_state"] if "ai_state" in spec else "IDLE"
        merchant_gold = spec["gold"] if "gold" in spec else 100
        npc = NPC(
            vnum=vnum,
            name=spec["name"],
            short_desc=spec["short_desc"],
            long_desc=spec["long_desc"],
            zone="Forteca_Dungrim",
            faction="MEEKHAN",
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=bool(spec.get("merchant", False)),
            shop_inventory=list(shop_factories[shop_name]()) if shop_name is not None else [],
            merchant_gold=merchant_gold,
            home_room_id=int(spec["room_id"]),
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        npc.character.equipment.update(self._dungrim_equipment(vnum))
        npc.dialogue_tree = self._dungrim_dialogue(vnum)
        return self._finalize(npc)

    def _basic_npc(
        self,
        *,
        vnum: str,
        name: str,
        short_desc: str,
        long_desc: str,
        zone: str,
        faction: str,
        room_id: int,
        ai_state: str = "IDLE",
        stats: CharacterStats | None = None,
        equipment: dict[str, Item | None] | None = None,
        inventory: list[Item] | None = None,
        dialogue_tree: dict[str, list[str]] | None = None,
        is_merchant: bool = False,
        shop_inventory: list[Item] | None = None,
        merchant_gold: int = 100,
    ) -> NPC:
        character = Character(name.capitalize())
        if stats is not None:
            character.stats = stats
        character.inventory.clear()
        if inventory:
            character.inventory.extend(inventory)
        if equipment:
            character.equipment.update(equipment)
        npc = NPC(
            vnum=vnum,
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            zone=zone,
            faction=faction,
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=is_merchant,
            shop_inventory=list(shop_inventory or []),
            merchant_gold=merchant_gold,
            home_room_id=room_id,
            daily_schedule=self._daily_schedule_for(vnum),
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        if dialogue_tree is not None:
            npc.dialogue_tree = dialogue_tree
        return self._finalize(npc)

    def create(self, vnum: str, room_id: int) -> NPC:
        if vnum == "astergard_guard":
            return self._basic_npc(
                vnum="astergard_guard",
                name="strażnik",
                short_desc="Strażnik miasta opiera włócznię o ramię.",
                long_desc="Nosi płaszcz w barwach Astergardu i ma twarz człowieka, który widział zbyt wiele spóźnionych kłótni.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                ai_state="GUARD",
                stats=CharacterStats(12, 11, 12, 10, 10, 110),
                equipment={
                    "prawa_reka": Item("włócznia strażnicza", "Prosta włócznia do kontroli ulic i bram.", 2.6, 18, "city_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2, initiative_modifier=0, parry_bonus=0),
                    "lewa_reka": Item("mniejsza tarcza", "Tarcza służbowa z wybitym herbem miasta.", 2.7, 14, "city_guard_shield", "shield", "lewa_reka", protection=1, shield_block=2),
                    "korpus": Item("płaszcz straży", "Wzmacniany płaszcz miejskiej straży.", 4.8, 22, "city_guard_cloak", "armor", "korpus", protection=1),
                },
                dialogue_tree=self._social_dialogue(
                    "Pilnuj drogi i nie zawracaj ludziom głowy.",
                    "Służba jest prosta: patrzeć, słuchać i nie mrugać za często.",
                    "Stoję tam, gdzie mi każą. Zwykle przy bramie albo tam, gdzie ruch jest największy.",
                    "Włóczędzy zdradzają się butami, nie słowami. Na to patrzę najpierw.",
                    brama="Przy bramie najłatwiej o kłopoty, więc patrzymy tu podwójnie uważnie.",
                ),
            )
        if vnum == "innkeeper":
            return self._basic_npc(
                vnum="innkeeper",
                name="karczmarz",
                short_desc="Karczmarz ociera dłonie o fartuch.",
                long_desc="Pamięta cudze rachunki lepiej niż cudze twarze, a mimo to rzadko daje się oszukać po raz drugi.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 11, 11, 100),
                is_merchant=True,
                merchant_gold=55,
                shop_inventory=innkeeper_shop_inventory(),
                dialogue_tree=self._social_dialogue(
                    "Siadaj albo idź dalej, ale nie blokuj przejścia.",
                    "Praca przy ladzie nie kończy się nigdy. Kubki same się nie myją.",
                    "Karczma stoi tam, gdzie wszyscy muszą przejść choć raz.",
                    "Plotki przychodzą szybciej niż dostawy. Dwa kufle i już wiem za dużo.",
                    piwo="Piwo jest ciemne, bo ludzie chcą zapomnieć, nie błyszczeć.",
                    gość="Z twarzy widzę, czy ktoś zasługuje na ciepły stół.",
                ),
            )
        if vnum == "podgrodzie_woznica":
            return self._basic_npc(
                vnum="podgrodzie_woznica",
                name="woźnica",
                short_desc="Woźnica stoi przy wozie i sprawdza okucia, jakby od nich zależał porządek świata.",
                long_desc="Zna każdy wybojowy objazd wokół Astergardu i wie, kiedy lepiej czekać na suchą ziemię niż na cud.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 9, 10, 95),
                equipment={
                    "korpus": Item("woźnicki kaftan", "Gruby kaftan odporny na deszcz, kurz i smar od osi.", 2.0, 8, "podgrodzie_driver_coat", "armor", "korpus", protection=1),
                    "prawa_reka": Item("bat woźnicy", "Krótki bat do poganiania koni i porządkowania przestrzeni wokół wozu.", 0.6, 6, "podgrodzie_driver_whip", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
                },
                inventory=[Item("rzemień uprzęży", "Zapasowy rzemień do naprawy uprzęży i plandek.", 0.2, 2, "podgrodzie_driver_strap", item_type="tool")],
            )
        if vnum == "podgrodzie_karczmarz":
            return self._basic_npc(
                vnum="podgrodzie_karczmarz",
                name="karczmarz",
                short_desc="Karczmarz pilnuje lady i nie pozwala, by kufle stały puste zbyt długo.",
                long_desc="Słyszy więcej przy ladzie niż w urzędzie, bo ludzie przy piwie mówią prawdę albo bardzo zbliżoną wersję.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 11, 11, 100),
                is_merchant=True,
                merchant_gold=58,
                shop_inventory=karczmarz_shop_inventory(),
                equipment={
                    "korpus": Item("karczemny fartuch", "Gruby fartuch z kieszeniami na łyżki, klucze i drobne rachunki.", 1.0, 5, "podgrodzie_inn_apron", "armor", "korpus", protection=1),
                },
                inventory=[Item("księga rachunków", "Zeszyt z zapisami należności, poplamiony tłuszczem i winem.", 0.4, 4, "podgrodzie_inn_ledger", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Siadaj, jedz, pij i nie wchodź za ladę.",
                    "Praca jest przy stole, w kuchni i przy rachunkach. Nigdy nie brakuje roboty.",
                    "Karczma stoi przy drodze, więc obcy trafiają tu sami.",
                    "Plotki znam z pierwszej ręki. Goście mówią więcej niż powinni.",
                    gość="Dach nad głową kosztuje mniej niż kłótnia przy drzwiach.",
                ),
            )
        if vnum == "podgrodzie_karczmarka":
            return self._basic_npc(
                vnum="podgrodzie_karczmarka",
                name="karczmarka",
                short_desc="Karczmarka niesie tacę pewniej niż niejeden strażnik tarczę.",
                long_desc="Wie, kto co zamawia, kto co ukradł i kto próbuje zniknąć przed zapłaceniem. W karczmie to wystarczy za talent i broń.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 10, 11, 95),
                is_merchant=True,
                merchant_gold=52,
                shop_inventory=karczmarka_shop_inventory(),
                equipment={
                    "korpus": Item("karczemny gorset", "Roboczy gorset z grubej tkaniny, odporny na kuchenny pośpiech.", 0.9, 5, "podgrodzie_inn_garment", "armor", "korpus", protection=1),
                    "prawa_reka": Item("taca z blachy", "Niewielka taca do noszenia kubków i talerzy.", 0.8, 4, "podgrodzie_inn_tray", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=1, parry_bonus=0),
                },
                inventory=[Item("ściereczka kelnerska", "Ściereczka do ścierania stołów i cudzych śladów.", 0.1, 1, "podgrodzie_inn_cloth", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Jeśli masz chwilę, to powiedz ją szybko. Mam gości do obsłużenia.",
                    "Praca? Tace, kufle i sprzątanie cudzych śladów po nocy.",
                    "Karczma stoi przy drodze, więc zawsze ktoś tu trafia.",
                    "Plotki przychodzą z każdym zamówieniem. Ja tylko udaję, że nie słucham.",
                ),
            )
        if vnum == "podgrodzie_piekarz":
            return self._basic_npc(
                vnum="podgrodzie_piekarz",
                name="piekarz",
                short_desc="Piekarz ma dłonie białe od mąki i spojrzenie człowieka, który wstaje przed resztą miasta.",
                long_desc="Dla niego wszystko mierzy się w cieście, cieple pieca i czasie wyrośnięcia. W Podgrodziu to porządek równie ważny jak straż.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 9, 10, 90),
                is_merchant=True,
                merchant_gold=45,
                shop_inventory=baker_shop_inventory(),
                equipment={
                    "korpus": Item("piekarski fartuch", "Szorstki fartuch z mąką w zagięciach.", 0.8, 4, "podgrodzie_baker_apron", "armor", "korpus", protection=1),
                    "prawa_reka": Item("łopata piekarska", "Krótka łopata do wsuwania bochenków do pieca.", 1.4, 7, "podgrodzie_baker_peel", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("kosz bułek", "Kosz jeszcze ciepłych bułek.", 1.2, 6, "podgrodzie_baker_rolls", item_type="food")],
            )
        if vnum == "podgrodzie_handlarz":
            return self._basic_npc(
                vnum="podgrodzie_handlarz",
                name="handlarz",
                short_desc="Handlarz liczy towar szybciej niż ludzi, chyba że jedno i drugie da się sprzedać.",
                long_desc="Zna wartość wozu, worka i plotki. Na targu potrafi wyczuć, czy lepiej mówić o cenie, czy o pogodzie.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 11, 11, 95),
                is_merchant=True,
                merchant_gold=65,
                shop_inventory=merchant_shop_inventory(),
                equipment={
                    "korpus": Item("handlarski płaszcz", "Płaszcz z wieloma kieszeniami, odpowiedni do targowania się i ukrywania monet.", 1.1, 6, "podgrodzie_merchant_cloak", "armor", "korpus", protection=0),
                    "prawa_reka": Item("kijek do ważenia", "Krótki kij i miarka, które pomagają pilnować uczciwej wagi.", 0.5, 4, "podgrodzie_merchant_staff", "tool", "prawa_reka"),
                },
                inventory=[Item("tabliczka cen", "Tabliczka z kilkoma wyświechtanymi cenami.", 0.2, 2, "podgrodzie_merchant_priceboard", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Handluję, liczę i nie daję się oszukać dwa razy tego samego dnia.",
                    "Praca handlarza to waga, ceny i dobry wzrok.",
                    "Stoję tam, gdzie targ ma najgłośniejszy róg.",
                    "Plotki krążą po stoiskach szybciej niż monety.",
                ),
            )
        if vnum == "podgrodzie_przekupka":
            return self._basic_npc(
                vnum="podgrodzie_przekupka",
                name="przekupka",
                short_desc="Przekupka rozkłada towar tak, żeby każdy myślał, że właśnie znalazł okazję.",
                long_desc="Umie sprzedać jajka, cebulę i zdrowy rozsądek. W Podgrodziu takie umiejętności są równie cenne jak uczciwość rzadkiego dnia targowego.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 8, 11, 10, 85),
                is_merchant=True,
                merchant_gold=42,
                shop_inventory=vendor_shop_inventory(),
                equipment={
                    "korpus": Item("targowy kaftan", "Kaftan wzmocniony łatami i kieszeniami na monety.", 0.9, 4, "podgrodzie_vendor_apron", "armor", "korpus", protection=0),
                },
                inventory=[Item("kosz z towarem", "Kosz z drobnym handlem, gotowy do ustawienia na straganie.", 2.0, 8, "podgrodzie_vendor_basket", is_container=True, capacity=18)],
                dialogue_tree=self._social_dialogue(
                    "Nie gap się, tylko wybieraj. Towar sam się nie sprzeda.",
                    "Praca przy kramie to ciężkie ręce i szybki język.",
                    "Na targu stoję tam, gdzie najlepiej widać klientów i straż.",
                    "Plotki? Jeśli wiem, kto z kim się pokłócił, to znam też cenę cebuli.",
                ),
            )
        if vnum == "blacksmith":
            return self._basic_npc(
                vnum="blacksmith",
                name="kowal",
                short_desc="Kowal ma dłonie zgrubiałe od ognia i młota.",
                long_desc="Jego twarz nosi ślad wiecznego żaru, a ubranie pachnie węglem, olejem i rozgrzanym żelazem.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(13, 9, 12, 10, 10, 110),
                inventory=[Item("młot kowalski", "Praktyczny młot do codziennej pracy.", 2.0, 10, "npc_blacksmith_hammer", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Jak chcesz gadać, to krótko. Mam ogień do pilnowania.",
                    "Praca? Młot, żar i stal. Nic więcej nie trzeba.",
                    "Kuźnia stoi przy murze, bo tam nikt nie marudzi na hałas.",
                    "Plotki? Słyszę je od pomocników, zanim jeszcze ostygnie żelazo.",
                ),
            )
        if vnum == "podgrodzie_kowal":
            return self._basic_npc(
                vnum="podgrodzie_kowal",
                name="kowal",
                short_desc="Kowal z Podgrodzia stoi przy przenośnym palenisku i sprawdza rozgrzane żelazo.",
                long_desc="Nie ma kuźni jak w mieście, ale ma młot, palenisko i klientów, którzy wolą naprawić narzędzie niż kupować nowe.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(13, 9, 12, 10, 10, 110),
                is_merchant=True,
                merchant_gold=75,
                shop_inventory=blacksmith_shop_inventory(),
                equipment={
                    "korpus": Item("okopcony fartuch", "Skórzany fartuch chroniący przed iskrą i żarem.", 2.4, 12, "podgrodzie_smith_apron", "armor", "korpus", protection=1),
                    "prawa_reka": Item("młot kowalski", "Ciężki młot, którym da się zarówno kuć, jak i odstraszyć natrętów.", 2.2, 11, "podgrodzie_smith_hammer", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=1),
                },
                inventory=[Item("szczypce kowalskie", "Długie szczypce do rozgrzanych prętów i podków.", 1.0, 5, "podgrodzie_smith_tongs", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Młot nie robi się lżejszy od gadania, ale mam chwilę.",
                    "Praca kowala zaczyna się od ognia, a kończy na odciskach.",
                    "Stoję tu, gdzie muszę, żeby iskry nie poszły na cudze dachy.",
                    "Plotki przychodzą od pomocnika szybciej niż nowe podkowy.",
                ),
            )
        if vnum == "podgrodzie_pomocnik_kowala":
            return self._basic_npc(
                vnum="podgrodzie_pomocnik_kowala",
                name="pomocnik kowala",
                short_desc="Pomocnik kowala nosi węgiel, czyści żużel i uczy się nie stać za blisko ognia.",
                long_desc="Jeszcze nie bije samodzielnie żelaza, ale zna rytm pracy i wie, kiedy podać narzędzie bez pytania.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 9, 10, 95),
                equipment={
                    "korpus": Item("robocza kamizela", "Ciężka kamizela z łatami i sadzą na ramionach.", 1.4, 6, "podgrodzie_smith_helper_vest", "armor", "korpus", protection=0),
                    "prawa_reka": Item("szczypce pomocnika", "Lżejsze szczypce do trzymania rozgrzanych elementów.", 0.8, 3, "podgrodzie_smith_helper_tongs", "tool", "prawa_reka"),
                },
                inventory=[Item("pudełko gwoździ", "Pudełko z posortowanymi gwoździami i nitami.", 0.9, 4, "podgrodzie_smith_nails", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Jeszcze uczę się, ale i tak wszystko muszę podać zanim mistrz mruknie.",
                    "Praca pomocnika to węgiel, szczypce i pilnowanie żaru.",
                    "Najczęściej jestem przy palenisku albo po drewno biegnę.",
                    "Plotki? W kuźni szybciej lecą iskry niż słowa, ale i tak coś się usłyszy.",
                ),
            )
        if vnum == "podgrodzie_ges":
            return self._basic_npc(
                vnum="podgrodzie_ges",
                name="gęś",
                short_desc="Gęś syczy na każdego, kto podchodzi zbyt blisko podwórza.",
                long_desc="Ptak jest głośny, uparty i zupełnie niechętny do rozmowy. Dziobem potrafi przekonać do zachowania dystansu.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 11, 7, 8, 6, 45),
                ai_state="AGGRESSIVE",
                equipment={
                    "prawa_reka": Item("dziób gęsi", "Twardy dziób do szczypania i odstraszania.", 0.0, 0, "goose_beak", "weapon", "prawa_reka", damage_type="kluta", base_damage=1, reach=1, initiative_modifier=2, parry_bonus=0),
                },
            )
        if vnum == "podgrodzie_straznik_miejski":
            return self._basic_npc(
                vnum="podgrodzie_straznik_miejski",
                name="strażnik miejski",
                short_desc="Strażnik miejski zna wszystkich, którzy próbują wjechać do Podgrodzia bez pytania o zgodę.",
                long_desc="Patroluje bramę i skrzyżowania z praktycznym spokojem człowieka, który woli zapisać nazwisko niż gonić po błocie.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                ai_state="GUARD",
                stats=CharacterStats(12, 11, 12, 11, 11, 115),
                equipment={
                    "prawa_reka": Item("włócznia miejska", "Prosta włócznia do kontroli ruchu i powstrzymywania awantur.", 2.7, 18, "podgrodzie_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2),
                    "lewa_reka": Item("okrągła tarcza", "Tarcza z miejskim znakiem, solidna i już dobrze przeżyta.", 3.0, 16, "podgrodzie_guard_shield", "shield", "lewa_reka", protection=1, shield_block=2),
                    "korpus": Item("płaszcz straży", "Gruby płaszcz na służbę w deszczu i błocie.", 4.5, 20, "podgrodzie_guard_cloak", "armor", "korpus", protection=1),
                },
                dialogue_tree=self._social_dialogue(
                    "Stój spokojnie i nie utrudniaj służby.",
                    "Patrol, wpisy i wypatrywanie błędu. To moja robota.",
                    "Na bramie widzę większość ludzi, którzy wchodzą do Podgrodzia.",
                    "Plotki? Najgorsze są te, które zaczynają się od 'na chwilę tylko'.",
                    brama="Brama to nie targ. Tu się wjeżdża, a nie błądzi.",
                ),
            )
        if vnum == "farmer":
            return self._basic_npc(
                vnum="farmer",
                name="rolnik",
                short_desc="Rolnik ma buty ubłocone od pól i twarz zmęczoną przed świtem.",
                long_desc="Żyje rytmem ziemi, a nie miasta. W jego sakwie prawie zawsze coś szeleści: ziarno, sznurek albo rachunek do spłacenia.",
                zone="Haldun",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 8, 9, 90),
                inventory=[Item("wiązka zboża", "Mały snopek świeżo zebranej słomy.", 0.9, 2, "npc_grain_bundle", item_type="food")],
            )
        if vnum == "podgrodzie_chlop":
            return self._basic_npc(
                vnum="podgrodzie_chlop",
                name="chłop",
                short_desc="Chłop przywiózł z pola brud, słomę i kilka worków, których nie wolno było zgubić po drodze.",
                long_desc="Pracuje jak ziemia każe, a nie jak miasto chce. Na twarzy ma pogodę, na rękach odciski, a przy pasie narzędzie, które zawsze da się użyć do pracy.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 9, 10, 8, 9, 95),
                equipment={
                    "korpus": Item("płócienna koszula", "Płócienna koszula przydatna do ciężkiej roboty w polu.", 1.0, 4, "podgrodzie_farmer_shirt", "armor", "korpus", protection=0),
                    "prawa_reka": Item("widły polne", "Proste widły do siana i obrony przed psami.", 2.2, 8, "podgrodzie_farmer_fork", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=3, reach=2, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("mała motyka", "Narzędzie do ziemi, chwastów i wyciągania się z kłopotów.", 1.0, 3, "podgrodzie_farmer_hoe", item_type="tool")],
            )
        if vnum == "podgrodzie_chlopka":
            return self._basic_npc(
                vnum="podgrodzie_chlopka",
                name="chłopka",
                short_desc="Chłopka niesie kosz, jakby ważył mniej niż jej obowiązki.",
                long_desc="Zna porę karmienia, czas pieczenia i liczenie jaj bez pomyłki. W Podgrodziu to praktyczny rodzaj mądrości.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 9, 10, 90),
                equipment={
                    "korpus": Item("robocza chusta", "Chusta i fartuch chroniące przed kurzem, błotem i mąką.", 0.8, 4, "podgrodzie_farmer_apron", "armor", "korpus", protection=0),
                    "prawa_reka": Item("sierp gospodarski", "Krótki sierp, przydatny do żniw i obrony przed zbyt ciekawą gęsią.", 0.9, 7, "podgrodzie_farmer_sickle", "weapon", "prawa_reka", damage_type="cieta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
                },
                inventory=[Item("kosz jaj", "Kosz z jajami, owiniętymi w słomę.", 1.4, 6, "podgrodzie_farmer_egg_basket", is_container=True, capacity=10)],
            )
        if vnum in {
            "haldun_solt",
            "haldun_wellkeeper",
            "haldun_blacksmith",
            "haldun_miller",
            "haldun_merchant",
            "haldun_farmer",
            "haldun_farmerka",
            "haldun_pasterz",
            "haldun_wartownik",
        }:
            return self._create_haldun_npc(vnum, room_id)
        if vnum in {
            "dungrim_commander",
            "dungrim_lieutenant",
            "dungrim_sergeant",
            "dungrim_guard",
            "dungrim_patrol_guard",
            "dungrim_armorer",
            "dungrim_military_blacksmith",
            "dungrim_quartermaster",
            "dungrim_storekeeper",
            "dungrim_stablemaster",
            "dungrim_cook",
        }:
            return self._create_dungrim_npc(vnum, room_id)
        if vnum in {
            "straznica_dowodca",
            "straznica_wartownik",
            "straznica_zwiadowca",
            "straznica_przewodnik",
            "straznica_karawanowy",
            "straznica_woznica",
            "straznica_podrozny",
            "straznica_pielgrzym",
            "straznica_mysliwy",
        }:
            return self._create_straznica_npc(vnum, room_id)
        if vnum == "fisherman":
            return self._basic_npc(
                vnum="fisherman",
                name="rybak",
                short_desc="Rybak pachnie rzeką, smołą i mokrą liną.",
                long_desc="Przez większość dnia stoi przy nabrzeżu, licząc sieci, a nie słowa. Zna nurt rzeki lepiej niż bruk miasta.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 10, 11, 9, 92),
                inventory=[Item("hak do sieci", "Mały hak do naprawy sieci i lin.", 0.3, 2, "npc_fishhook", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Mam ręce zajęte rybami i liną, ale mogę chwilę pogadać.",
                    "Praca rybaka zaczyna się przed świtem i kończy, gdy zniknie ostatnia łódź.",
                    "Jestem tam, gdzie nurt jest spokojny i sieci nie plączą się o deski.",
                    "Plotki? Na nabrzeżu wszystko niesie woda: i wieści, i kłamstwa.",
                ),
            )
        if vnum == "podgrodzie_rybak":
            return self._basic_npc(
                vnum="podgrodzie_rybak",
                name="rybak",
                short_desc="Rybak z Podgrodzia ma sieć przerzuconą przez ramię i ręce zniszczone od soli.",
                long_desc="Nad rzeką zarabia na życie, a w Podgrodziu sprzedaje to, czego nie zdążył oddać do miasta przed południem.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 10, 11, 9, 92),
                is_merchant=True,
                merchant_gold=60,
                shop_inventory=fisher_shop_inventory(),
                equipment={
                    "korpus": Item("mokry kaftan", "Kaftan impregnowany smołą i rybim tłuszczem.", 1.2, 5, "podgrodzie_fisher_coat", "armor", "korpus", protection=0),
                    "prawa_reka": Item("hak rybacki", "Krótki hak do sieci, lin i nieproszonych palców.", 0.3, 3, "podgrodzie_fisher_hook", "tool", "prawa_reka"),
                },
                inventory=[Item("zwinięta sieć", "Sieć gotowa do rzutu albo naprawy.", 2.0, 10, "podgrodzie_fisher_net", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Sieć sama się nie naprawi, ale mogę odpowiedzieć na jedno pytanie.",
                    "Praca rybaka to mokre buty, zimne dłonie i cierpliwość.",
                    "Stoję przy rzece albo na pomoście, zależnie od pogody.",
                    "Plotki płyną szybciej niż łódź, jeśli ktoś je dobrze rozdmucha.",
                ),
            )
        if vnum == "traveler":
            return self._basic_npc(
                vnum="traveler",
                name="podróżny",
                short_desc="Podróżny stoi z sakwą przy nodze.",
                long_desc="Na płaszczu ma pył z kilku dróg, a na twarzy ostrożność ludzi, którzy widzieli już zbyt wiele granic.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 10, 10, 100),
                inventory=[Item("podróżna sakwa", "Niewielka sakwa z najpotrzebniejszymi rzeczami.", 1.0, 5, "npc_travel_sack", is_container=True, capacity=10)],
                dialogue_tree=self._social_dialogue(
                    "Mam tylko drogę i kilka historii, ale to wystarczy na rozmowę.",
                    "Praca podróżnego to iść, obserwować i nie ufać pierwszej gospodzie.",
                    "Stoję tam, gdzie droga przecina miasto albo gdzie mogę je opuścić.",
                    "Plotki? Na trakcie każdy niesie cudzą opowieść w sakwie.",
                ),
            )
        if vnum == "podgrodzie_pielgrzym":
            return self._basic_npc(
                vnum="podgrodzie_pielgrzym",
                name="pielgrzym",
                short_desc="Pielgrzym idzie bez pośpiechu, ale z uporem ludzi, których prowadzi nie droga, lecz cel.",
                long_desc="Niesie prosty kij, woreczek z drobnymi ofiarami i cierpliwość, którą zwykle mają tylko ludzie przyzwyczajeni do długich dróg.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 9, 11, 12, 85),
                equipment={
                    "korpus": Item("pielgrzymi płaszcz", "Płaszcz odporny na deszcz i pył z traktu.", 1.5, 6, "podgrodzie_pilgrim_cloak", "armor", "korpus", protection=0),
                    "prawa_reka": Item("kij pielgrzyma", "Prosty kij do marszu i podpierania się na długiej drodze.", 1.2, 4, "podgrodzie_pilgrim_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("woreczek ofiarny", "Woreczek z monetami i pamiątkami z modlitw.", 0.2, 2, "podgrodzie_pilgrim_pouch", is_container=True, capacity=6)],
                dialogue_tree=self._social_dialogue(
                    "Idę do świętego miejsca, ale mogę zamienić parę słów.",
                    "Praca pielgrzyma to droga, modlitwa i twarde stopy.",
                    "Stoję tam, gdzie trzeba odpocząć przed kolejnym odcinkiem szlaku.",
                    "Plotki mijają mnie codziennie, ale nie wszystkie warto nosić dalej.",
                ),
            )
        if vnum == "beggar":
            return self._basic_npc(
                vnum="beggar",
                name="żebrak",
                short_desc="Żebrak siedzi przy ścianie i wyciąga dłoń szybciej, niż unosi wzrok.",
                long_desc="Ma płaszcz łatany tak wiele razy, że bardziej przypomina mapę biedy niż ubranie. Nie wygląda groźnie, ale zna ulice lepiej niż niejeden strażnik.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(7, 8, 8, 10, 8, 75),
                inventory=[Item("miska na jałmużnę", "Mała miska na monety i okruchy.", 0.4, 1, "beggar_bowl", item_type="misc")],
                dialogue_tree=self._social_dialogue(
                    "Masz chwilę? To już dużo.",
                    "Praca? Tu się prosi, pamięta twarze i szuka cienia.",
                    "Stoję tam, gdzie nikt nie kopie zbyt mocno.",
                    "Plotki krążą po ulicach szybciej niż ja.",
                ),
            )
        if vnum == "podgrodzie_zebrak":
            return self._basic_npc(
                vnum="podgrodzie_zebrak",
                name="żebrak",
                short_desc="Żebrak przesiaduje tam, gdzie błoto jest najgłębsze i gdzie obcy najchętniej udają, że nie widzą.",
                long_desc="Nie ma nic poza miską, kijem i pamięcią do twarzy ludzi, którzy kiedyś dali mu jałmużnę. Podgrodzie nauczyło go też, gdzie stanąć, by nie przegoniła go pierwsza fala wozów.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(7, 8, 8, 10, 8, 75),
                equipment={
                    "korpus": Item("łachman i koc", "Nędzny koc i łachman chronią przed zimnem bardziej niż przed spojrzeniem.", 0.8, 1, "podgrodzie_beggar_rag", "armor", "korpus", protection=0),
                    "prawa_reka": Item("kij żebraka", "Krótki kij do podpierania się i odganiania psów.", 0.7, 1, "podgrodzie_beggar_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("miska na jałmużnę", "Miska na drobne monety i czasem okruch chleba.", 0.4, 1, "podgrodzie_beggar_bowl", item_type="misc")],
                dialogue_tree=self._social_dialogue(
                    "Nie mam wiele, ale mam czas na słowo.",
                    "Praca? Pilnuję kąta, żeby ktoś nie zajął go przede mną.",
                    "Stoję tu, gdzie błoto jest najgłębsze, a wiatr najmniej wredny.",
                    "Plotki w Podgrodziu są jak błoto: przyczepiają się do butów.",
                ),
            )
        if vnum == "child":
            return self._basic_npc(
                vnum="child",
                name="dziecko",
                short_desc="Dziecko patrzy z ciekawością, której dorośli szybko by się oduczyli.",
                long_desc="Ma startą od zabawy kurtkę i spojrzenie, które widzi więcej, niż powinno w tym wieku.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 10, 7, 10, 8, 70),
            )
        if vnum == "podgrodzie_dziecko":
            return self._basic_npc(
                vnum="podgrodzie_dziecko",
                name="dziecko",
                short_desc="Dziecko biega między zagrodami i co chwilę przystaje, by obejrzeć coś nowego.",
                long_desc="Ma odrapane kolana, błoto na butach i ten rodzaj odwagi, który znika dopiero wraz z pierwszymi obowiązkami.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 10, 7, 10, 8, 70),
                equipment={
                    "prawa_reka": Item("drewniana proca", "Dziecięca proca z kawałka gałęzi i skrawka skóry.", 0.2, 1, "podgrodzie_child_sling", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=2, parry_bonus=0),
                },
                inventory=[Item("gładki kamyk", "Mały kamień zebrany z ziemi dla zabawy albo do procy.", 0.02, 0, "podgrodzie_child_stone", item_type="misc")],
            )
        if vnum == "blacksmith":
            return self._basic_npc(
                vnum="blacksmith",
                name="kowal",
                short_desc="Kowal ma dłonie zgrubiałe od ognia i młota.",
                long_desc="Jego twarz nosi ślad wiecznego żaru, a ubranie pachnie węglem, olejem i rozgrzanym żelazem.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(13, 9, 12, 10, 10, 110),
                inventory=[Item("młot kowalski", "Praktyczny młot do codziennej pracy.", 2.0, 10, "npc_blacksmith_hammer", item_type="tool")],
            )
        if vnum == "farmer":
            return self._basic_npc(
                vnum="farmer",
                name="rolnik",
                short_desc="Rolnik ma buty ubłocone od pól i twarz zmęczoną przed świtem.",
                long_desc="Żyje rytmem ziemi, a nie miasta. W jego sakwie prawie zawsze coś szeleści: ziarno, sznurek albo rachunek do spłacenia.",
                zone="Haldun",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 8, 9, 90),
                inventory=[Item("wiązka zboża", "Mały snopek świeżo zebranej słomy.", 0.9, 2, "npc_grain_bundle", item_type="food")],
            )
        if vnum == "fisherman":
            return self._basic_npc(
                vnum="fisherman",
                name="rybak",
                short_desc="Rybak pachnie rzeką, smołą i mokrą liną.",
                long_desc="Przez większość dnia stoi przy nabrzeżu, licząc sieci, a nie słowa. Zna nurt rzeki lepiej niż bruk miasta.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 10, 11, 9, 92),
                inventory=[Item("hak do sieci", "Mały hak do naprawy sieci i lin.", 0.3, 2, "npc_fishhook", item_type="tool")],
            )
        if vnum == "traveler":
            return self._basic_npc(
                vnum="traveler",
                name="podróżny",
                short_desc="Podróżny stoi z sakwą przy nodze.",
                long_desc="Na płaszczu ma pył z kilku dróg, a na twarzy ostrożność ludzi, którzy widzieli już zbyt wiele granic.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 10, 10, 100),
                inventory=[Item("podróżna sakwa", "Niewielka sakwa z najpotrzebniejszymi rzeczami.", 1.0, 5, "npc_travel_sack", is_container=True, capacity=10)],
            )
        if vnum == "child":
            return self._basic_npc(
                vnum="child",
                name="dziecko",
                short_desc="Dziecko patrzy z ciekawością, której dorośli szybko by się oduczyli.",
                long_desc="Ma startą od zabawy kurtkę i spojrzenie, które widzi więcej, niż powinno w tym wieku.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 10, 7, 10, 8, 70),
            )
        if vnum == "beggar":
            return self._basic_npc(
                vnum="beggar",
                name="żebrak",
                short_desc="Żebrak siedzi przy ścianie i wyciąga dłoń szybciej, niż unosi wzrok.",
                long_desc="Ma płaszcz łatany tak wiele razy, że bardziej przypomina mapę biedy niż ubranie. Nie wygląda groźnie, ale zna ulice lepiej niż niejeden strażnik.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(7, 8, 8, 10, 8, 75),
                inventory=[Item("miska na jałmużnę", "Mała miska na monety i okruchy.", 0.4, 1, "beggar_bowl", item_type="misc")],
            )
        if vnum == "carpenter":
            return self._basic_npc(
                vnum="carpenter",
                name="cieśla",
                short_desc="Cieśla ma dłonie pełne drzazg i pyłu.",
                long_desc="Mierzy belki okiem szybciej niż inni liczą pieniądze, a przy tym zawsze myśli o tym, co da się jeszcze uratować z drewna.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 10, 10, 100),
                inventory=[Item("dłuto", "Robocze dłuto do drewna.", 0.4, 4, "carpenter_chisel_npc", item_type="tool")],
            )
        if vnum == "tanner":
            return self._basic_npc(
                vnum="tanner",
                name="garbarz",
                short_desc="Garbarz pachnie skórą, popiołem i gorzkim płynem z kadzi.",
                long_desc="Pracuje przy skórach bez pośpiechu, bo wie, że twarda robota i tak zrobi z niego człowieka milczącego.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 9, 10, 95),
                is_merchant=True,
                merchant_gold=50,
                shop_inventory=tanner_shop_inventory(),
                inventory=[Item("garbarski skrobak", "Płaski skrobak do skóry.", 0.5, 3, "tanner_scraper_npc", item_type="tool")],
            )
        if vnum == "butcher":
            return self._basic_npc(
                vnum="butcher",
                name="rzeźnik",
                short_desc="Rzeźnik ostrzy narzędzia i zerka na to, co da się jeszcze pociąć na uczciwe porcje.",
                long_desc="Zna wagę mięsa, kości i dobrej soli. Przy ladzie mówi krótko, bo woli pracować niż opowiadać.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 11, 9, 10, 100),
                is_merchant=True,
                merchant_gold=54,
                shop_inventory=butcher_shop_inventory(),
                inventory=[Item("hak rzeźnicki", "Krótki hak do wieszania tusz.", 0.6, 4, "butcher_hook_npc", item_type="tool")],
            )
        if vnum == "skin_trader":
            return self._basic_npc(
                vnum="skin_trader",
                name="handlarz skórami",
                short_desc="Handlarz skórami rozkłada próbki tak, by nawet biedny myślał o dobrym płaszczu.",
                long_desc="Kupuje i sprzedaje to, co zdjęto z lasu, pola albo zbyt pewnej ręki. Wartość widzi w szorstkości, nie w słowach.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 11, 10, 95),
                is_merchant=True,
                merchant_gold=60,
                shop_inventory=skin_trader_shop_inventory(),
                inventory=[Item("worek garbarski", "Worek na próbki skór i maści do ich konserwacji.", 0.7, 4, "skin_trader_bag", is_container=True, capacity=12)],
            )
        if vnum == "armorer":
            return self._basic_npc(
                vnum="armorer",
                name="płatnerz",
                short_desc="Płatnerz ma fartuch okopcony od kuźni i cierpliwość dla krzywych nitów.",
                long_desc="Naprawia pęknięcia, które inni już by wyrzucili. Tego typu ludzie trzymają miasta razem lepiej niż urzędy.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(12, 9, 12, 10, 10, 110),
                inventory=[Item("nitownica", "Ciężkie narzędzie do nitowania zbroi.", 1.0, 5, "armorer_riveter_npc", item_type="tool")],
            )
        if vnum == "dockhand":
            return self._basic_npc(
                vnum="dockhand",
                name="tragarz nabrzeża",
                short_desc="Tragarz nabrzeża ma mokre buty i plecy od worków.",
                long_desc="Przenosi beczki, skrzynie i cudze zyski. Jeśli ma humor, to zwykle dlatego, że dziś jeszcze nic na niego nie spadło.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(11, 10, 11, 9, 9, 100),
                inventory=[Item("hak ładunkowy", "Żelazny hak do przenoszenia ciężkich pakunków.", 0.8, 4, "dockhook_npc", item_type="tool")],
            )
        if vnum == "miller":
            return self._basic_npc(
                vnum="miller",
                name="młynarz",
                short_desc="Młynarz ma twarz białą od pyłu i ręce od worków z ziarnem.",
                long_desc="Wie, ile wart jest zbożowy worek i jak łatwo ludzie kłócą się o mąkę. Jego dzień zaczyna się wcześniej niż dzień miasta.",
                zone="Haldun",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 10, 10, 95),
                inventory=[Item("miernik ziarna", "Mały drewniany miernik do zboża.", 0.5, 3, "miller_measure_npc", item_type="tool")],
            )
        if vnum == "priest_aide":
            return self._basic_npc(
                vnum="priest_aide",
                name="pomocnik kapłana",
                short_desc="Pomocnik kapłana niesie wiadro wody i zwitek płótna.",
                long_desc="Nie ma w nim wielkiej powagi, ale zna porządek świątyni i wie, kiedy lepiej mówić mniej niż trzeba.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 9, 11, 12, 90),
                inventory=[Item("zwitek płótna", "Szorstkie płótno do świątynnych porządków.", 0.3, 2, "priest_aide_linen_npc")],
            )
        if vnum == "watch_sergeant":
            return self._basic_npc(
                vnum="watch_sergeant",
                name="sierżant warty",
                short_desc="Sierżant warty wygląda na człowieka, który nie lubi pytań po zmroku.",
                long_desc="Pilnuje bram i dziedzińców z twarzą kogoś, kto już widział za dużo cudzych wymówek. Inni strażnicy słuchają go szybciej niż radzą się sumienia.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                ai_state="GUARD",
                stats=CharacterStats(13, 11, 13, 11, 11, 125),
                equipment={
                    "prawa_reka": Item("sierżancka włócznia", "Włócznia oznaczona żelaznym pierścieniem.", 2.8, 24, "watch_sergeant_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2),
                    "lewa_reka": Item("sierżancka tarcza", "Cięższa tarcza dla starszego straży.", 3.1, 18, "watch_sergeant_shield", "shield", "lewa_reka", protection=1, shield_block=3),
                },
                dialogue_tree={
                    "default": [
                        "Ruch szybko. Zatrzymasz się, jeśli ja powiem.",
                        "Ruch szybko. Z taką reputacją nie będę udawał gościnności.",
                    ],
                    "brama": [
                        "Bramy pilnuje się przed świtem i po zmroku. W środku dnia też, jeśli trzeba.",
                        "Bramy pilnuje się też przed tobą, bo z taką reputacją nie ma dyskusji.",
                    ],
                },
            )
        if vnum == "customs_clerk":
            return self._basic_npc(
                vnum="customs_clerk",
                name="celnik",
                short_desc="Celnik ma kałamarz przy pasie i twarz człowieka, który liczy wszystko.",
                long_desc="Nie nosi broni ostentacyjnie, ale za to pamięta każdą pieczęć i każdy fałszywy pakunek. To wystarcza, by był niebezpieczny w zupełnie innym sensie.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 9, 11, 12, 90),
                inventory=[Item("księga ceł", "Ciężka księga zapisów celnych.", 1.3, 6, "customs_book_npc", item_type="tool")],
            )
        if vnum == "fishmonger":
            return self._basic_npc(
                vnum="fishmonger",
                name="rybaczka",
                short_desc="Rybaczka sprzedaje ryby szybko, zanim zdążą stracić sens i zapach.",
                long_desc="Ma twardy głos i ręce od soli. W porcie nikt nie pyta, skąd ma najlepszy towar, bo wszyscy to widzą.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 11, 9, 10, 10, 95),
                inventory=[Item("hak do ryb", "Krótki hak do rozcinania i czyszczenia ryb.", 0.2, 2, "fishmonger_hook_npc", item_type="tool")],
            )
        if vnum == "woodcutter":
            return self._basic_npc(
                vnum="woodcutter",
                name="drwal",
                short_desc="Drwal ma topór cięższy niż jego uśmiech.",
                long_desc="Przychodzi z lasu z żywicą na rękawach i nie zadaje pytań, jeśli ktoś nie zadaje ich jego robocie.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(12, 10, 12, 9, 9, 110),
                inventory=[Item("topór drwala", "Użytkowy topór do ścinania drzew.", 2.9, 8, "woodcutter_axe_npc", item_type="weapon", slot="prawa_reka", damage_type="obuchowa", base_damage=4, reach=1)],
            )
        if vnum == "urchin":
            return self._basic_npc(
                vnum="urchin",
                name="dzieciak uliczny",
                short_desc="Dzieciak uliczny ogląda wszystko z ostrożnością i gotowością do biegu.",
                long_desc="Ma za duże oczy jak na swój wiek i wie dokładnie, które kieszenie są lekkie. Na ulicy to cenniejsza wiedza niż alfabet.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 12, 7, 11, 8, 65),
            )
        if vnum == "vagrant":
            return self._basic_npc(
                vnum="vagrant",
                name="włóczęga",
                short_desc="Włóczęga stoi z sakwą przy nodze i wygląda, jakby znał za dużo skrótów.",
                long_desc="Nie trzyma się jednego miejsca dłużej niż trzeba. Tacy ludzie są kłopotem albo świadkami, zależnie od tego, kto pyta.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 8, 10, 9, 85),
                inventory=[Item("wytarta sakwa", "Stara sakwa z jednym paskiem za mało.", 0.8, 2, "vagrant_sack_npc", is_container=True, capacity=8)],
            )
        if vnum == "meekhan_soldier":
            c = Character("Żołnierz")
            c.stats = CharacterStats(12, 10, 12, 10, 10, 120)
            npc = NPC(
                vnum="meekhan_soldier",
                name="żołnierz",
                short_desc="Żołnierz Szóstej Kompanii stoi tutaj.",
                long_desc="Ma kolczugę, zmęczone oczy i rękę blisko miecza.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                ai_state="GUARD",
                room_id=room_id,
                character=c,
                home_room_id=room_id,
            )
            npc.character.combat_style = combat_style_for_vnum(npc.vnum)
            npc.character.equipment["prawa_reka"] = Item("żołnierski miecz", "Miecz piechoty Szóstej Kompanii.", 1.9, 35, "soldier_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1)
            npc.character.equipment["lewa_reka"] = Item("okrągła tarcza", "Tarcza służbowa z obtłuczonym rantem.", 2.8, 25, "soldier_shield", "shield", "lewa_reka", protection=1, shield_block=2)
            npc.character.equipment["korpus"] = Item("kolczuga", "Krótka kolczuga patrolowa.", 8.0, 80, "mail_armor", "armor", "korpus", protection=2)
            npc.dialogue_tree = {
                "default": ["Pilnuj traktu, cywilu."],
                "wojna": ["Wojna nigdy nie kończy się tam, gdzie kończy się mapa."],
            }
            return self._finalize(npc)
        if vnum == "merchant":
            c = Character("Kupiec")
            npc = NPC(
                vnum="merchant",
                name="kupiec",
                short_desc="Kupiec sprawdza sakwy przy pasie.",
                long_desc="Płaszcz ma dobry, ale oczy niespokojne.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                ai_state="IDLE",
                room_id=room_id,
                character=c,
                is_merchant=True,
                home_room_id=room_id,
            )
            npc.character.combat_style = combat_style_for_vnum(npc.vnum)
            npc.character.equipment["prawa_reka"] = Item("nóż kupiecki", "Krótki nóż do cięcia sznurów i odstraszania desperatów.", 0.4, 8, "merchant_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=2, parry_bonus=0)
            npc.shop_inventory = [
                Item(
                    "krzesiwo",
                    "Krzesiwo i krzemień w skórzanym woreczku.",
                    0.2,
                    2,
                    "merchant_flint",
                    "tool",
                ),
                Item("bukłak", "Mały bukłak na wodę.", 0.6, 3, "merchant_waterskin", "tool"),
                Item("latarnia podróżna", "Prosta latarnia z grubym szkłem.", 1.4, 6, "merchant_lantern", "tool"),
                Item("sakwa podróżna", "Sakwa z jedną dużą przegródką i mocnym paskiem.", 1.0, 5, "merchant_travel_sack", is_container=True, capacity=12),
                Item("zwój liny", "Zwój grubej liny, przydatny przy drodze.", 2.8, 4, "merchant_rope", "tool"),
            ]
            npc.merchant_gold = 65
            npc.dialogue_tree = self._social_dialogue(
                "Kupuj szybko albo odejdź od lady.",
                "Praca kupca to ważenie, liczenie i pilnowanie, by nikt nie skrócił mnie o grosz.",
                "Stoję tam, gdzie droga z miasta krzyżuje się z ludzką chciwością.",
                "Plotki? Jeśli są warte grosza, to już są towarem.",
                wilki="Wilki schodzą blisko traktu. Przynieś mi jedną skórę, a zapłacę.",
            )
            return self._finalize(npc)
        if vnum in {
            "trakty_przewodnik",
            "trakty_karawaniarz",
            "trakty_kurier",
            "trakty_woznica",
            "trakty_podrozny",
            "trakty_pielgrzym",
            "trakty_zebrak",
            "trakty_mysliwy",
            "trakty_drwal",
            "trakty_straznik",
            "trakty_handlarz",
        }:
            return self._create_trakty_npc(vnum, room_id)
        if vnum in {
            "puszcza_mysliwy",
            "puszcza_zielarz",
            "puszcza_pustelnik",
            "puszcza_drwal",
            "puszcza_szczur",
            "puszcza_kruk",
            "puszcza_lis",
            "puszcza_pies_dziki",
            "puszcza_wilk_mlody",
            "puszcza_wilk",
            "puszcza_jelen",
            "puszcza_dzik",
            "puszcza_pajak",
            "puszcza_pajak_lesny",
            "puszcza_pajak_duzy",
            "puszcza_wilk_stary",
            "puszcza_wataha_wilkow",
            "puszcza_niedzwiedz",
            "puszcza_niedzwiedzica",
            "puszcza_bandyta",
            "puszcza_bandyta_zwiadowca",
            "puszcza_lowca",
            "puszcza_lowczy",
            "puszcza_bandycki_naczelnik",
            "puszcza_niedzwiedzi_olbrzym",
            "puszcza_troll",
            "bagna_zielarz",
            "bagna_pustelnik",
            "bagna_mysliwy",
            "bagna_zaba",
        }:
            return self._create_wild_npc(vnum, room_id)
        if vnum == "mountain_troll":
            c = Character("Troll")
            c.stats = CharacterStats(17, 9, 16, 8, 8, 160)
            c.inventory.append(Item("twarda skóra trolla", "Gruba i ciężka skóra.", 3.0, 25, "troll_hide"))
            npc = NPC(
                vnum="mountain_troll",
                name="troll",
                short_desc="Troll górski ciężko oddycha w cieniu skał.",
                long_desc="Wysoki, zgarbiony stwór o łapach jak kamienne młoty.",
                zone="Polnoc_Gory",
                faction="REBELS",
                ai_state="AGGRESSIVE",
                room_id=room_id,
                character=c,
                home_room_id=room_id,
            )
            npc.character.combat_style = combat_style_for_vnum(npc.vnum)
            npc.character.equipment["prawa_reka"] = Item("kamienna maczuga", "Ciężki głaz osadzony na pękniętym trzonku.", 7.5, 10, "troll_club", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=8, reach=1, initiative_modifier=-1, parry_bonus=0)
            npc.character.equipment["korpus"] = Item("gruba skóra", "Naturalnie twarda skóra trolla.", 0.0, 0, "troll_hide_armor", "armor", "korpus", protection=1)
            return self._finalize(npc)
        if vnum == "warband_captain":
            c = Character("Kapitan")
            c.stats = CharacterStats(15, 13, 15, 12, 13, 150)
            boss = NPC(
                vnum="warband_captain",
                name="kapitan bandy",
                short_desc="Kapitan bandy stoi tu w zużytej zbroi i mierzy wszystkich wzrokiem.",
                long_desc="To nie jest zwykły rabuś, lecz człowiek przyzwyczajony do wydawania rozkazów i przeżywania zasadzek.",
                zone="Zachod_Las",
                faction="REBELS",
                ai_state="AGGRESSIVE",
                room_id=room_id,
                character=c,
                home_room_id=room_id,
                respawn_delay_seconds=600,
            )
            boss.character.combat_style = combat_style_for_vnum(boss.vnum)
            boss.character.equipment["prawa_reka"] = Item("kapitański topór", "Ciężki topór z karbowanym ostrzem.", 3.8, 90, "captain_axe", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=6, reach=1, initiative_modifier=0, parry_bonus=1)
            boss.character.equipment["lewa_reka"] = Item("wzmocniona tarcza", "Tarcza okuta żelazem.", 4.0, 70, "captain_shield", "shield", "lewa_reka", protection=2, shield_block=3)
            boss.character.equipment["korpus"] = Item("łuskowa zbroja", "Pancerz poskładany z wielu zdobycznych elementów.", 9.5, 120, "scale_armor", "armor", "korpus", protection=3)
            return self._finalize(boss)
        c = Character("Wilk")
        c.stats = CharacterStats(8, 13, 8, 12, 6, 80)
        wolf = NPC(
            vnum="wolf",
            name="wilk",
            short_desc="Wilk warczy nisko przy ziemi.",
            long_desc="Chude zwierzę o żółtych ślepiach.",
            zone="Zachod_Las",
            faction="REBELS",
            ai_state="AGGRESSIVE",
            room_id=room_id,
            character=c,
            home_room_id=room_id,
        )
        wolf.character.inventory.clear()
        wolf.character.combat_style = combat_style_for_vnum(wolf.vnum)
        wolf.character.equipment["prawa_reka"] = Item("kły wilka", "Naturalna broń drapieżnika.", 0.0, 0, "wolf_bite", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=2, parry_bonus=0)
        return self._finalize(wolf)
