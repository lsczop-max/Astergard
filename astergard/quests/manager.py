from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from astergard.characters.models import Character
from astergard.engine.events import DomainEventType
from astergard.narrative import join_prose


class QuestObjective(TypedDict):
    type: str
    target: str | tuple[str, ...]
    count: int
    current: int


class QuestRewards(TypedDict, total=False):
    gold: int
    rep: int


@dataclass
class Quest:
    id: str
    title: str
    description: str
    start_npc: str
    completion_npc: str
    offer_keywords: tuple[str, ...]
    offer_text: str
    reminder_text: str
    completion_text: str
    objectives: list[QuestObjective]
    rewards: QuestRewards = field(default_factory=QuestRewards)
    auto_complete_on_delivery: bool = False


def _objective_key(index: int) -> str:
    return f"o{index}"


def _target_matches(expected: str | tuple[str, ...], actual: str) -> bool:
    if isinstance(expected, tuple):
        return actual in expected
    return expected == actual


def _format_target(expected: str | tuple[str, ...]) -> str:
    if isinstance(expected, tuple):
        return "jedno z: " + ", ".join(expected)
    return expected


def _objective_label(obj_type: str) -> str:
    return {
        "talk": "rozmowa",
        "give": "oddanie",
        "kill": "pokonanie",
    }.get(obj_type, obj_type)


def _objective_progress(state: dict[str, int], index: int, quest: Quest) -> int:
    key = _objective_key(index)
    if key in state:
        return int(state.get(key, 0))
    if len(quest.objectives) == 1:
        return int(state.get("current", 0))
    return 0


def _refresh_current_total(state: dict[str, int], quest: Quest) -> None:
    state["current"] = sum(_objective_progress(state, index, quest) for index, _ in enumerate(quest.objectives))


QUESTS: dict[str, Quest] = {
    "wolf_pelt": Quest(
        "wolf_pelt",
        "Skóra z traktu",
        "Przynieś kupcowi wilczą skórę.",
        "merchant",
        "merchant",
        ("zadanie", "wilki", "skora", "skóra"),
        "Kupiec: Na traktu jest zbyt dużo wilków. Przynieś mi jedną skórę, a zapłacę.",
        "Kupiec: Nadal czekam na wilczą skórę.",
        "Kupiec: Dobra robota. To wystarczy.",
        [{"type": "kill", "target": "wolf", "count": 1, "current": 0}],
        {"gold": 15, "rep": 5},
    ),
    "market_delivery": Quest(
        "market_delivery",
        "Dostawa z targu",
        "Karczmarz potrzebuje świeżych zapasów z rynku.",
        "innkeeper",
        "innkeeper",
        ("zadanie", "dostawa", "targ", "rynku"),
        "Karczmarz: Potrzebuję kosza z rynku. Przynieś go z targu, zanim wystygnie jedzenie.",
        "Karczmarz: Jeszcze czekam na dostawę z rynku.",
        "Karczmarz: Dziękuję. To uratuje wieczór w karczmie.",
        [{"type": "give", "target": "market_delivery_basket_47", "count": 1, "current": 0}],
        {"gold": 18, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "blacksmith_tools": Quest(
        "blacksmith_tools",
        "Zgubione narzędzia",
        "Kowal szuka swoich zaginionych szczypiec.",
        "blacksmith",
        "blacksmith",
        ("zadanie", "narzedzia", "narzędzia", "szczypce", "kowal"),
        "Kowal: Zgubiłem szczypce przy studni. Przynieś je, a odwdzięczę się.",
        "Kowal: Szczypce nadal gdzieś krążą po mieście.",
        "Kowal: Dobrze. Bez nich nie da się pracować.",
        [{"type": "give", "target": "smith_tongs_lost_21", "count": 1, "current": 0}],
        {"gold": 20, "rep": 4},
        auto_complete_on_delivery=True,
    ),
    "fisher_net": Quest(
        "fisher_net",
        "Zagubiona sieć",
        "Rybak z Podgrodzia chce odzyskać swoją sieć.",
        "podgrodzie_rybak",
        "podgrodzie_rybak",
        ("zadanie", "siec", "sieć", "rybak"),
        "Rybak: Moja sieć gdzieś przepadła przy moście. Przynieś ją, zanim połowu zabraknie.",
        "Rybak: Bez sieci nie ma mowy o połowie.",
        "Rybak: Dobra, wraca do mnie cały zarobek na dziś.",
        [{"type": "give", "target": "podgrodzie_fishing_net_75", "count": 1, "current": 0}],
        {"gold": 16, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "guard_vagrant": Quest(
        "guard_vagrant",
        "Podejrzany włóczęga",
        "Strażnik chce wiedzieć, kim jest włóczęga z placu.",
        "watch_sergeant",
        "watch_sergeant",
        ("zadanie", "wloczega", "włóczęga", "obcy"),
        "Strażnik: Sprawdź, co wie włóczęga. Potem wróć z odpowiedzią.",
        "Strażnik: Najpierw porozmawiaj z włóczęgą.",
        "Strażnik: To wystarczy. Miasto musi wiedzieć, kogo pilnować.",
        [{"type": "talk", "target": "vagrant", "count": 1, "current": 0}],
        {"gold": 8, "rep": 8},
    ),
    "city_ring_search": Quest(
        "city_ring_search",
        "Zaginiony pierścień",
        "Strażnik chce odzyskać pierścień znaleziony w cieniu muru.",
        "watch_sergeant",
        "merchant",
        ("zadanie", "pierscien", "pierścień", "zguba", "znajdz", "znajdź"),
        "Strażnik: Ktoś zgubił pierścień przy murze. Znajdź go, a oddasz komu trzeba.",
        "Strażnik: Pierścień nadal czeka. Przeszukaj okolice placu i wróć z nim.",
        "Kupiec: Dobrze. To była cenna zguba, a nie zwykła błyskotka.",
        [{"type": "give", "target": "silver_ring", "count": 1, "current": 0}],
        {"gold": 18, "rep": 4},
        auto_complete_on_delivery=True,
    ),
    "merchant_price_check": Quest(
        "merchant_price_check",
        "Targowe ceny",
        "Handlarz chce, by ktoś sprawdził ceny u targowych sprzedawców i wrócił z wieściami.",
        "merchant",
        "merchant",
        ("zadanie", "ceny", "handel", "targ", "przekupka", "towar"),
        "Handlarz: Podejdź do przekupki albo rybaczki i sprawdź, ile teraz kosztuje prosty towar. Potem wróć do mnie.",
        "Handlarz: Jeszcze nie wiem, czy ceny na targu poszły w górę.",
        "Handlarz: Dobrze. Teraz wiem, jak ustawić własny kram.",
        [
            {"type": "talk", "target": ("podgrodzie_przekupka", "fishmonger"), "count": 1, "current": 0},
            {"type": "talk", "target": "merchant", "count": 1, "current": 0},
        ],
        {"gold": 10, "rep": 2},
    ),
    "dockside_rumor": Quest(
        "dockside_rumor",
        "Portowa nowina",
        "Pracownik portu chce usłyszeć, co rybak albo tragarz nabrzeża wie o ostatnim połowie.",
        "dockhand",
        "dockhand",
        ("zadanie", "port", "nabrzeze", "nabrzeże", "rybak", "nowina"),
        "Pracownik portu: Porozmawiaj z rybakiem albo tragarzem nabrzeża i sprawdź, co słychać nad wodą.",
        "Pracownik portu: Jeszcze nie mam wieści z nabrzeża.",
        "Pracownik portu: Dobrze. Teraz wiem, co trzeba przenieść i gdzie.",
        [{"type": "talk", "target": ("fisherman", "dockhand"), "count": 1, "current": 0}],
        {"gold": 9, "rep": 2},
    ),
    "pilgrim_escort": Quest(
        "pilgrim_escort",
        "Bezpieczny nocleg",
        "Karczmarz chce, by pielgrzym dotarł do karczmy bez włóczenia się po błocie.",
        "podgrodzie_karczmarz",
        "innkeeper",
        ("zadanie", "eskorta", "pielgrzym", "nocleg", "bezpiecznie"),
        "Karczmarz: Zadbaj, żeby pielgrzym wrócił bezpiecznie pod dach. Potem zamelduj się w karczmie.",
        "Karczmarz: Pielgrzym wciąż potrzebuje opieki.",
        "Karczmarz: Dobrze. Pielgrzym ma już dach nad głową i spokojniejszą noc.",
        [{"type": "talk", "target": "podgrodzie_pielgrzym", "count": 1, "current": 0}],
        {"gold": 11, "rep": 2},
    ),
    "wheel_repair": Quest(
        "wheel_repair",
        "Naprawa koła",
        "Kowal chce naprawić pęknięte koło z wozu woźnicy.",
        "podgrodzie_kowal",
        "podgrodzie_woznica",
        ("zadanie", "naprawa", "koło", "kolo", "wóz", "woz"),
        "Kowal: Przynieś złamane koło. Jeśli jest jeszcze do uratowania, zrobię z niego porządne.",
        "Kowal: Koło nadal czeka na naprawę.",
        "Woźnica: Dobrze. Teraz wóz nie rozpadnie się na pierwszym wyboju.",
        [{"type": "give", "target": "podgrodzie_broken_wheel_60", "count": 1, "current": 0}],
        {"gold": 14, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "shield_repair": Quest(
        "shield_repair",
        "Naprawa tarczy",
        "Zbrojmistrz chce odzyskać miejską tarczę do naprawy.",
        "watch_sergeant",
        "armorer",
        ("zadanie", "naprawa", "tarcza", "zbroja", "straz", "straż"),
        "Zbrojmistrz: Przynieś tarczę patrolową. Z łatwością widać, że trzeba ją podkuć i podbić.",
        "Zbrojmistrz: Tarcza nadal czeka na naprawę.",
        "Zbrojmistrz: Dobrze. Teraz tarcza znowu nadaje się do służby.",
        [{"type": "give", "target": "guard_shield_25", "count": 1, "current": 0}],
        {"gold": 13, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "wolf_watch": Quest(
        "wolf_watch",
        "Wilk pod murami",
        "Strażnik chce, by ktoś odstraszył wilka z okolic miasta.",
        "watch_sergeant",
        "watch_sergeant",
        ("zadanie", "wilk", "wilka", "lasy", "zagrozenie", "zagrożenie"),
        "Strażnik: Na obrzeżach kręci się wilk. Ubierz się i zrób z tym porządek.",
        "Strażnik: Wilk nadal żyje. Miasto potrzebuje spokoju.",
        "Strażnik: Dobrze. Teraz przy murze będzie mniej zębów i wrzasku.",
        [{"type": "kill", "target": "wolf", "count": 1, "current": 0}],
        {"gold": 20, "rep": 5},
    ),
    "fish_delivery": Quest(
        "fish_delivery",
        "Ryby na targ",
        "Rybak chce, by świeży połów trafił do handlarza rybnego.",
        "podgrodzie_rybak",
        "fishmonger",
        ("zadanie", "ryba", "ryby", "połów", "targ", "sprzedaz"),
        "Rybak: Weź świeże śledzie z targu i zanieś je do handlarza, zanim zmiękną.",
        "Rybak: Połów czeka. Ryby nie lubią czekać na brzegu.",
        "Handlarz rybny: Dobrze. Towar pachnie jeszcze rzeką, a nie staniem.",
        [{"type": "give", "target": "fish_market_herring_23", "count": 1, "current": 0}],
        {"gold": 12, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "grain_delivery": Quest(
        "grain_delivery",
        "Worek zboża",
        "Piekarz chce dostarczyć worek zboża do karczmy, zanim skończy się chleb.",
        "podgrodzie_piekarz",
        "podgrodzie_karczmarz",
        ("zadanie", "zboze", "zboże", "maka", "mąka", "chleb", "pieczywo"),
        "Piekarz: Przynieś mi worek zboża z placu. Karczma bez chleba długo nie stoi.",
        "Piekarz: Zboże jeszcze nie wróciło. Bez niego piec będzie głodny.",
        "Karczmarz: Dobrze. Teraz będzie z czego wypiekać wieczorny chleb.",
        [{"type": "give", "target": "podgrodzie_grain_sack_63", "count": 1, "current": 0}],
        {"gold": 11, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "wood_delivery": Quest(
        "wood_delivery",
        "Suchy opał",
        "Cieśla potrzebuje suchego drewna do napraw i pieca warsztatowego.",
        "woodcutter",
        "carpenter",
        ("zadanie", "drewno", "deski", "opał", "stolarz", "ciesla", "cieśla"),
        "Drwal: Zanieś suche drewno cieśli. Bez opału warsztat szybko stygnie.",
        "Drwal: Drewno jeszcze nie wróciło z placu.",
        "Cieśla: Dobrze. Teraz mogę pracować, zanim noc zaciśnie chłód.",
        [{"type": "give", "target": "podgrodzie_firewood_64", "count": 1, "current": 0}],
        {"gold": 10, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "candles_gather": Quest(
        "candles_gather",
        "Świece dla kaplicy",
        "Pomocnik kapłana potrzebuje świecy z kapliczki, żeby domknąć wieczorną modlitwę.",
        "priest_aide",
        "priest_aide",
        ("zadanie", "swieca", "świeca", "kaplica", "modlitwa", "wosk"),
        "Pomocnik kapłana: Przynieś świecę z kapliczki. Bez niej wieczór robi się zbyt ciemny.",
        "Pomocnik kapłana: Świeca jeszcze nie wróciła do kaplicy.",
        "Pomocnik kapłana: Dobrze. Teraz modlitwa będzie miała światło.",
        [{"type": "give", "target": "road_candle_59", "count": 1, "current": 0}],
        {"gold": 8, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "well_water_delivery": Quest(
        "well_water_delivery",
        "Woda ze studni",
        "Przekupka chce czystej wody dla karczmy, zanim ruszy wieczorny handel.",
        "podgrodzie_przekupka",
        "podgrodzie_karczmarz",
        ("zadanie", "woda", "studnia", "wiadro", "karczma", "picie"),
        "Przekupka: Przynieś wiadro wody ze studni i oddaj je karczmarzowi.",
        "Przekupka: Woda jeszcze nie trafiła do karczmy.",
        "Karczmarz: Dobrze. Bez wody nie ma ani piwa, ani zupy.",
        [{"type": "give", "target": "city_well_bucket_21", "count": 1, "current": 0}],
        {"gold": 9, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "priest_herbs": Quest(
        "priest_herbs",
        "Zioła dla kapłana",
        "Pomocnik kapłana potrzebuje świeżych ziół z ogrodu.",
        "priest_aide",
        "priest_aide",
        ("zadanie", "ziola", "zioła", "napary", "kaplan", "kapłan"),
        "Pomocnik kapłana: Potrzebuję świeżej wiązki ziół z ogrodu. Przynieś ją z powrotem.",
        "Pomocnik kapłana: Zioła jeszcze nie wróciły do świątyni.",
        "Pomocnik kapłana: Dobrze. Te zioła trafią tam, gdzie trzeba.",
        [{"type": "give", "target": "priest_herb_bundle_37", "count": 1, "current": 0}],
        {"gold": 12, "rep": 4},
        auto_complete_on_delivery=True,
    ),
    "haldun_well_bucket": Quest(
        "haldun_well_bucket",
        "Wiadro do studni",
        "Sołtys chce, by studniarz dostał nowe wiadro do noszenia wody.",
        "haldun_solt",
        "haldun_wellkeeper",
        ("zadanie", "studnia", "wiadro", "woda"),
        "Sołtys: Studnia jest sercem Haldun. Zanieś nowe wiadro studniarzowi, zanim ktoś się potknie o stare.",
        "Sołtys: Studnia nadal czeka na porządne wiadro.",
        "Studniarz: Dobrze, teraz woda nie ucieknie z połowy wiadra.",
        [{"type": "give", "target": "haldun_well_bucket", "count": 1, "current": 0}],
        {"gold": 12, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "haldun_forge_coal": Quest(
        "haldun_forge_coal",
        "Węgiel do kuźni",
        "Sołtys chce, by kowal dostał świeży węgiel do paleniska.",
        "haldun_solt",
        "haldun_blacksmith",
        ("zadanie", "kuznia", "kuźnia", "węgiel", "kowal"),
        "Sołtys: Kowal bez węgla nie naprawi ani pługa, ani podkowy. Zanieś mu zapas do kuźni.",
        "Sołtys: Kuźnia nadal czeka na węgiel.",
        "Kowal: Dobrze. Żar znowu będzie trzymał temperaturę.",
        [{"type": "give", "target": "haldun_forge_coal", "count": 1, "current": 0}],
        {"gold": 14, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "haldun_grain_delivery": Quest(
        "haldun_grain_delivery",
        "Zboże do młyna",
        "Sołtys chce, by młynarz dostał worek zboża z pól.",
        "haldun_solt",
        "haldun_miller",
        ("zadanie", "zboze", "zboże", "mlyn", "młyn", "maka", "mąka"),
        "Sołtys: Młynarz obrabia zboże dla całej wsi. Zanieś mu worek, zanim zacznie się skarżyć na puste worki.",
        "Sołtys: Młyn nadal czeka na porządne zboże.",
        "Młynarz: Dobrze. Teraz ziarno nie będzie leżało bez sensu.",
        [{"type": "give", "target": "haldun_grain_delivery", "count": 1, "current": 0}],
        {"gold": 16, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "haldun_barn_beam": Quest(
        "haldun_barn_beam",
        "Belka do stodoły",
        "Sołtys potrzebuje belki do naprawy zachodnich stodół.",
        "haldun_solt",
        "haldun_farmerka",
        ("zadanie", "stodoła", "stodola", "belka", "naprawa"),
        "Sołtys: Stodoły trzymają wieś razem. Przynieś belkę gospodyni, zanim dach zacznie przeciekać.",
        "Sołtys: Stodoły wciąż czekają na naprawę.",
        "Gospodyni: Świetnie. Z taką belką dach przetrwa jeszcze jeden sezon.",
        [{"type": "give", "target": "haldun_barn_beam", "count": 1, "current": 0}],
        {"gold": 13, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "haldun_orchard_crate": Quest(
        "haldun_orchard_crate",
        "Kosz jabłek",
        "Sołtys chce, by handlarz dostał jabłka z sadu przed południem.",
        "haldun_solt",
        "haldun_merchant",
        ("zadanie", "jabłka", "jablka", "sad", "kosz"),
        "Sołtys: Handlarz potrzebuje świeżych jabłek. Zanieś mu kosz, zanim owoce zmiękną w słońcu.",
        "Sołtys: Kosz jabłek nadal czeka na dostawę.",
        "Handlarz: Dobrze. Jabłka pójdą na targ, zanim stracą smak.",
        [{"type": "give", "target": "haldun_orchard_crate", "count": 1, "current": 0}],
        {"gold": 15, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "haldun_watch_round": Quest(
        "haldun_watch_round",
        "Obchód drogi",
        "Sołtys chce, by ktoś sprawdził, co wie wartownik o ruchu przy drodze.",
        "haldun_solt",
        "haldun_solt",
        ("zadanie", "obchod", "obchód", "patrol", "droga", "straz", "straż"),
        "Sołtys: Wartownik widzi wszystko przy drodze ku fortecy. Porozmawiaj z nim i wróć z wieściami.",
        "Sołtys: Najpierw sprawdź drogę przy wartowniku.",
        "Sołtys: Dobrze. Teraz wiem, że droga jest pod kontrolą.",
        [{"type": "talk", "target": "haldun_wartownik", "count": 1, "current": 0}],
        {"gold": 10, "rep": 2},
    ),
    "dungrim_patrol_report": Quest(
        "dungrim_patrol_report",
        "Raport z obchodu",
        "Sierżant chce krótkiej relacji od patrolowego o stanie muru i traktu.",
        "dungrim_sergeant",
        "dungrim_sergeant",
        ("zadanie", "raport", "patrol", "obchód", "obchod", "mur"),
        "Sierżant: Patrol ma wrócić z meldunkiem o murze i drodze. Najpierw porozmawiaj z patrolowym.",
        "Sierżant: Czekam na meldunek z obchodu.",
        "Sierżant: Dobrze. Teraz wiem, gdzie trzeba podwoić uwagę.",
        [{"type": "talk", "target": "dungrim_patrol_guard", "count": 1, "current": 0}],
        {"gold": 14, "rep": 3},
    ),
    "dungrim_armory_rivets": Quest(
        "dungrim_armory_rivets",
        "Nity do zbrojowni",
        "Zbrojmistrz potrzebuje nitek do naprawy tarcz i hełmów.",
        "dungrim_commander",
        "dungrim_armorer",
        ("zadanie", "nity", "zbrojownia", "zbroja", "naprawa"),
        "Dowódca: Zbrojownia nie może czekać. Zanieś nity zbrojmistrzowi i wróć z meldunkiem.",
        "Dowódca: Nity nadal są potrzebne w zbrojowni.",
        "Zbrojmistrz: Dobrze. Bez tych nitów naprawy będą się ślimaczyć.",
        [{"type": "give", "target": "dungrim_armor_rivets_121", "count": 1, "current": 0}],
        {"gold": 16, "rep": 4},
        auto_complete_on_delivery=True,
    ),
    "dungrim_kitchen_rations": Quest(
        "dungrim_kitchen_rations",
        "Racje dla kuchni",
        "Kucharz chce ratować obiad dodatkową porcją racji z magazynu.",
        "dungrim_lieutenant",
        "dungrim_cook",
        ("zadanie", "racja", "kuchnia", "gulasz", "jedzenie"),
        "Oficer: Kuchnia pracuje dla całego garnizonu. Zanieś rację kucharzowi.",
        "Oficer: Kuchnia nadal czeka na dodatkową porcję.",
        "Kucharz: Dobrze. Z tym gulaszem nikt nie wyjdzie głodny.",
        [{"type": "give", "target": "dungrim_emergency_ration_123", "count": 1, "current": 0}],
        {"gold": 12, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "dungrim_stable_straw": Quest(
        "dungrim_stable_straw",
        "Słoma do stajni",
        "Stajenny potrzebuje świeżej słomy dla koni patrolowych.",
        "dungrim_lieutenant",
        "dungrim_stablemaster",
        ("zadanie", "słoma", "stajnia", "konie", "patrol"),
        "Oficer: Stajnie muszą być gotowe przed kolejnym wyjazdem. Zanieś słomę stajennemu.",
        "Oficer: Stajnia wciąż czeka na słomę.",
        "Stajenny: Dobrze. Konie będą miały czysto i sucho.",
        [{"type": "give", "target": "dungrim_stable_straw_114", "count": 1, "current": 0}],
        {"gold": 13, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "dungrim_stock_list": Quest(
        "dungrim_stock_list",
        "Spis zapasów",
        "Magazynier chce dostać aktualny spis zapasów, zanim zamknie wydania.",
        "dungrim_commander",
        "dungrim_quartermaster",
        ("zadanie", "spis", "zapas", "magazyn", "lista"),
        "Dowódca: Bez spisu nie ma porządku. Zanieś listę magazynierowi.",
        "Dowódca: Spis zapasów wciąż czeka na przekazanie.",
        "Magazynier: Dobrze. Teraz mogę zamknąć stan bez zgadywania.",
        [{"type": "give", "target": "dungrim_stock_list_122", "count": 1, "current": 0}],
        {"gold": 18, "rep": 4},
        auto_complete_on_delivery=True,
    ),
    "straznica_meldunek": Quest(
        "straznica_meldunek",
        "Meldunek z wieży",
        "Komendant chce potwierdzenia od zwiadowcy, że trasa pod przełęczą jest czysta.",
        "straznica_dowodca",
        "straznica_dowodca",
        ("zadanie", "meldunek", "zwiad", "przełęcz", "przelec", "trasa"),
        "Komendant: Najpierw porozmawiaj ze zwiadowcą i sprawdź, co widać na północnym podejściu.",
        "Komendant: Meldunek nadal czeka. Zwiadowca powinien wiedzieć więcej ode mnie.",
        "Komendant: Dobrze. Teraz wiemy, gdzie trzeba patrzeć dwa razy.",
        [{"type": "talk", "target": "straznica_zwiadowca", "count": 1, "current": 0}],
        {"gold": 14, "rep": 3},
    ),
    "straznica_manifest": Quest(
        "straznica_manifest",
        "Manifest karawany",
        "Kupiec karawan potrzebuje właściwego listu przewozowego, zanim puści wóz dalej.",
        "straznica_karawanowy",
        "straznica_karawanowy",
        ("zadanie", "manifest", "karawana", "lista", "przewoz", "towar"),
        "Kupiec karawan: Najpierw przynieś mi list przewozowy z placu. Bez tego nie puszczę ładunku.",
        "Kupiec karawan: Nadal czekam na manifest. Bez papieru nie ruszamy.",
        "Kupiec karawan: Dobrze. Teraz ładunek ma swoją kolejność i pieczęć.",
        [{"type": "give", "target": "straznica_manifest_129", "count": 1, "current": 0}],
        {"gold": 16, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "straznica_lamp_oil": Quest(
        "straznica_lamp_oil",
        "Olej do lamp",
        "Przewodnik chce uzupełnić lampy, zanim pogoda zasłoni ścieżki.",
        "straznica_przewodnik",
        "straznica_przewodnik",
        ("zadanie", "olej", "lampa", "swiatlo", "światło", "przewodnik"),
        "Przewodnik: Przynieś olej do lamp z izby. Bez światła przełęcz robi się zbyt droga.",
        "Przewodnik: Lampy nadal czekają na olej.",
        "Przewodnik: Dobrze. Nocny patrol będzie widział więcej niż własny nos.",
        [{"type": "give", "target": "straznica_lamp_oil", "count": 1, "current": 0}],
        {"gold": 12, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "straznica_rope": Quest(
        "straznica_rope",
        "Lina do wozów",
        "Woźnica chce mocniejszą linę, zanim zjedzie z ładunkiem po stromym zboczu.",
        "straznica_karawanowy",
        "straznica_woznica",
        ("zadanie", "lina", "woz", "wóz", "woznica", "woźnica"),
        "Kupiec karawan: Woźnica potrzebuje liny ze stajni. Zanieś mu ją, zanim koło poleci za daleko.",
        "Kupiec karawan: Woźnica wciąż czeka na linę. Bez niej ładunek jedzie na ryzyko.",
        "Woźnica: Dobrze. Teraz mogę spinać wóz bez strachu o bok zbocza.",
        [{"type": "give", "target": "straznica_rope", "count": 1, "current": 0}],
        {"gold": 13, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "straznica_blanket": Quest(
        "straznica_blanket",
        "Koc dla podróżnych",
        "Pielgrzym potrzebuje ciepłego koca, zanim zatrzyma się na noc przy kaplicy.",
        "straznica_przewodnik",
        "straznica_pielgrzym",
        ("zadanie", "koc", "koce", "podroz", "podróż", "pielgrzym"),
        "Przewodnik: Weź koc z izby i oddaj go pielgrzymowi przy kaplicy.",
        "Przewodnik: Pielgrzym nadal czeka na koc. Noc bywa tu bezlitosna.",
        "Pielgrzym: Dobrze. To wystarczy, żeby przejść przez zimny postój.",
        [{"type": "give", "target": "straznica_travel_blanket", "count": 1, "current": 0}],
        {"gold": 11, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "straznica_hunter_report": Quest(
        "straznica_hunter_report",
        "Ślad myśliwego",
        "Komendant chce wiedzieć, co myśliwy widział przy bocznym zejściu.",
        "straznica_dowodca",
        "straznica_dowodca",
        ("zadanie", "mysliwy", "myśliwy", "tropy", "zwierzyna", "polowanie"),
        "Komendant: Najpierw porozmawiaj z myśliwym. On widzi więcej niż zwykły patrol.",
        "Komendant: Ślad myśliwego wciąż czeka. Idź do niego i wróć z odpowiedzią.",
        "Komendant: Dobrze. Teraz wiemy, co kręci się przy bocznym zejściu.",
        [{"type": "talk", "target": "straznica_mysliwy", "count": 1, "current": 0}],
        {"gold": 15, "rep": 3},
    ),
    "trakty_kurier_note": Quest(
        "trakty_kurier_note",
        "List kuriera",
        "Kurier chce bezpiecznie dostarczyć zapieczętowany list przewodnikowi.",
        "trakty_kurier",
        "trakty_przewodnik",
        ("zadanie", "kurier", "list", "listem", "pieczec", "pieczęć"),
        "Kurier: Weź list i zanieś go przewodnikowi. Im szybciej, tym lepiej.",
        "Kurier: List wciąż czeka na odbiorcę.",
        "Przewodnik: Dobrze. Teraz wiadomość nie utknie na trakcie.",
        [{"type": "give", "target": "trakty_sealed_note_140", "count": 1, "current": 0}],
        {"gold": 12, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "trakty_manifest": Quest(
        "trakty_manifest",
        "Manifest karawany",
        "Karawaniarz chce własnego manifestu, żeby puścić ładunek dalej.",
        "trakty_karawaniarz",
        "trakty_karawaniarz",
        ("zadanie", "manifest", "karawana", "towar", "przewoz", "przewozowy"),
        "Karawaniarz: Bez manifestu karawana nie rusza. Przynieś papier z traktu.",
        "Karawaniarz: Nadal czekam na manifest.",
        "Karawaniarz: Dobrze. Teraz ładunek ma porządek i pieczęć.",
        [{"type": "give", "target": "trakty_manifest_138", "count": 1, "current": 0}],
        {"gold": 16, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "trakty_lamp_oil": Quest(
        "trakty_lamp_oil",
        "Olej do lamp",
        "Przewodnik potrzebuje oleju, zanim noc zasłoni drogę.",
        "trakty_przewodnik",
        "trakty_przewodnik",
        ("zadanie", "olej", "lampa", "swiatlo", "światło", "przewodnik"),
        "Przewodnik: Przynieś olej do lamp. Na trakcie ciemność kosztuje więcej niż pieniądze.",
        "Przewodnik: Lampy nadal czekają na olej.",
        "Przewodnik: Dobrze. Teraz nocne czuwanie będzie miało czym świecić.",
        [{"type": "give", "target": "trakty_lamp_oil_135", "count": 1, "current": 0}],
        {"gold": 11, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "trakty_rope": Quest(
        "trakty_rope",
        "Zwój liny",
        "Woźnica potrzebuje mocnej liny, zanim zjedzie z ładunkiem po stromym odcinku.",
        "trakty_woznica",
        "trakty_woznica",
        ("zadanie", "lina", "woz", "wóz", "woznica", "woźnica"),
        "Woźnica: Przynieś zwój liny. Bez tego wóz nie przejdzie stromego zjazdu.",
        "Woźnica: Wciąż czekam na linę.",
        "Woźnica: Dobrze. Teraz mogę spinać ładunek bez strachu.",
        [{"type": "give", "target": "trakty_rope_141", "count": 1, "current": 0}],
        {"gold": 13, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "trakty_blanket": Quest(
        "trakty_blanket",
        "Koc dla pielgrzyma",
        "Pielgrzym potrzebuje ciepłego koca na nocny postój.",
        "trakty_pielgrzym",
        "trakty_pielgrzym",
        ("zadanie", "koc", "koce", "podroz", "podróż", "pielgrzym"),
        "Pielgrzym: Zanieś mi koc, zanim wiatr zrobi swoje.",
        "Pielgrzym: Koc jeszcze nie wrócił.",
        "Pielgrzym: Dobrze. To wystarczy, żeby przetrwać zimny postój.",
        [{"type": "give", "target": "trakty_travel_blanket_136", "count": 1, "current": 0}],
        {"gold": 10, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "trakty_hunter_report": Quest(
        "trakty_hunter_report",
        "Ślad myśliwego",
        "Strażnik chce wiedzieć, co myśliwy widział przy bocznym zejściu.",
        "trakty_straznik",
        "trakty_straznik",
        ("zadanie", "mysliwy", "myśliwy", "tropy", "zwierzyna", "polowanie"),
        "Strażnik: Najpierw porozmawiaj z myśliwym. On widzi więcej niż zwykły patrol.",
        "Strażnik: Ślad myśliwego wciąż czeka. Idź do niego i wróć z odpowiedzią.",
        "Strażnik: Dobrze. Teraz wiemy, co kręci się przy bocznym zejściu.",
        [{"type": "talk", "target": "trakty_mysliwy", "count": 1, "current": 0}],
        {"gold": 14, "rep": 3},
    ),
    "puszcza_herbs": Quest(
        "puszcza_herbs",
        "Leśne zioła",
        "Zielarz chce świeżej wiązki ziół z ukrytej polany.",
        "puszcza_zielarz",
        "puszcza_zielarz",
        ("zadanie", "zioła", "ziola", "napar", "las", "zielarz"),
        "Zielarz: Przynieś mi wiązkę ziół z lasu. Najlepsze rosną tam, gdzie nikt nie patrzy za często.",
        "Zielarz: Nadal czekam na leśne zioła.",
        "Zielarz: Dobrze. Teraz rośliny trafią do naparu, nie do błota.",
        [{"type": "give", "target": "forest_herbs_230", "count": 1, "current": 0}],
        {"gold": 12, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "puszcza_camp_token": Quest(
        "puszcza_camp_token",
        "Ślad obozu",
        "Pustelnik chce zobaczyć znak pozostawiony po obozie banitów.",
        "puszcza_pustelnik",
        "puszcza_pustelnik",
        ("zadanie", "oboz", "obóz", "banici", "znak", "camp"),
        "Pustelnik: Zajrzyj do starego obozu i przynieś mi jego znak. Las nie lubi, gdy wszystko zostaje bez śladu.",
        "Pustelnik: Znak obozu jeszcze nie wrócił.",
        "Pustelnik: Dobrze. Teraz wiem, że obóz nie był tylko czyjąś opowieścią.",
        [{"type": "give", "target": "forest_camp_token_274", "count": 1, "current": 0}],
        {"gold": 14, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "puszcza_stream_water": Quest(
        "puszcza_stream_water",
        "Woda ze strumienia",
        "Myśliwy potrzebuje świeżej wody z leśnego strumienia, zanim ruszy dalej.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "woda", "strumien", "strumień"),
        "Myśliwy: Przynieś wodę ze strumienia. W lesie lepsza jest tylko cisza.",
        "Myśliwy: Nadal czekam na wodę ze strumienia.",
        "Myśliwy: Dobrze. Teraz mam co wziąć w drogę.",
        [{"type": "give", "target": "forest_stream_waterskin_258", "count": 1, "current": 0}],
        {"gold": 11, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "puszcza_szczury": Quest(
        "puszcza_szczury",
        "Szczury przy obozie",
        "Myśliwy chce, by ktoś przerzedził szczury kręcące się przy bocznych obozach za miastem.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "szczury", "szczur", "oboz", "obóz", "obozem"),
        "Myśliwy: Szczury obsiadły boczny obóz i ścieżki za Astergardem. Zabij kilka i wróć po zapłatę.",
        "Myśliwy: Szczury nadal kręcą się przy obozie za miastem.",
        "Myśliwy: Dobra. Teraz ogień i zapasy będą bezpieczniejsze.",
        [{"type": "kill", "target": "puszcza_szczur", "count": 3, "current": 0}],
        {"gold": 14, "rep": 3},
    ),
    "puszcza_lisy": Quest(
        "puszcza_lisy",
        "Lisie ścieżki",
        "Myśliwy potrzebuje, by ktoś przepędził lisy z bocznych ścieżek i rozstajów.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "lisy", "lis", "polana", "polany", "młodnik", "mlodnik"),
        "Myśliwy: Lisów jest za dużo przy śladach zwierzyny. Przynieś mi dowód, że droga jest czystsza.",
        "Myśliwy: Lisy jeszcze nie odpuściły rozstajów.",
        "Myśliwy: Dobrze. Teraz zwierzyna powinna wracać spokojniej.",
        [{"type": "kill", "target": "puszcza_lis", "count": 2, "current": 0}],
        {"gold": 16, "rep": 3},
    ),
    "puszcza_wilki_mlode": Quest(
        "puszcza_wilki_mlode",
        "Młode wilki",
        "Myśliwy chce sprawdzić, czy ktoś poradzi sobie z młodymi wilkami krążącymi po drogach za Astergardem.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "wilki", "wilk", "młode", "mlode", "wilkow"),
        "Myśliwy: Młode wilki robią się zbyt śmiałe. Zabij dwa i wróć.",
        "Myśliwy: Młode wilki nadal siedzą na śladach przy drodze.",
        "Myśliwy: Dobrze. To powinno zatrzymać ich zapędy na jakiś czas.",
        [{"type": "kill", "target": "puszcza_wilk_mlody", "count": 2, "current": 0}],
        {"gold": 20, "rep": 4},
    ),
    "puszcza_bandyci": Quest(
        "puszcza_bandyci",
        "Leśni bandyci",
        "Myśliwy chce, by ktoś rozbił zasadzki bandytów w głębi Puszczy Ciszy.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "bandyci", "bandyta", "banda", "zasadzka", "las"),
        "Myśliwy: Bandyci rozstawili się przy ścieżkach i myślą, że nikt ich nie ruszy. Zlikwiduj kilku z nich.",
        "Myśliwy: Bandyci nadal siedzą w lesie.",
        "Myśliwy: Dobrze. Teraz las ma trochę mniej noży w cieniu.",
        [{"type": "kill", "target": "puszcza_bandyta", "count": 3, "current": 0}],
        {"gold": 24, "rep": 5},
    ),
    "puszcza_pajaki": Quest(
        "puszcza_pajaki",
        "Pajęcze zasadzki",
        "Myśliwy prosi o oczyszczenie starych przejść z pajęczyn i gniazd pająków.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "pajaki", "pajak", "pajęczyny", "pajeczyny", "sieci", "las"),
        "Myśliwy: W wilgotnych zagłębieniach wisi za dużo pajęczyn. Przetnij je i przynieś mi spokój.",
        "Myśliwy: Pajęcze gniazda nadal trzymają się ścieżek.",
        "Myśliwy: Dobrze. Teraz łatwiej przejść przez ten kawałek lasu.",
        [{"type": "kill", "target": "puszcza_pajak", "count": 2, "current": 0}],
        {"gold": 22, "rep": 4},
    ),
    "puszcza_niedzwiedzie": Quest(
        "puszcza_niedzwiedzie",
        "Ślad niedźwiedzi",
        "Myśliwy chce sprawdzić, czy wielkie drapieżniki nie wróciły do starych legowisk.",
        "puszcza_mysliwy",
        "puszcza_mysliwy",
        ("zadanie", "niedzwiedzie", "niedzwiedz", "niedźwiedź", "niedźwiedzie", "legowisko"),
        "Myśliwy: Niedźwiedzie zbliżyły się za bardzo do ludzkich ścieżek. Zajmij się nimi, zanim ktoś zginie.",
        "Myśliwy: Niedźwiedzie nadal pilnują swoich przejść.",
        "Myśliwy: Dobrze. Teraz można oddychać w tej części lasu spokojniej.",
        [{"type": "kill", "target": "puszcza_niedzwiedz", "count": 1, "current": 0}],
        {"gold": 32, "rep": 6},
    ),
    "bagna_herbs": Quest(
        "bagna_herbs",
        "Torfowe zioła",
        "Zielarka chce wiązkę torfowych ziół z mokradła.",
        "bagna_zielarz",
        "bagna_zielarz",
        ("zadanie", "zioła", "ziola", "bagno", "torf", "zielarka"),
        "Zielarka: Przynieś torfowe zioła z bagna. Rosną tam, gdzie inne rośliny gniją.",
        "Zielarka: Torfowe zioła jeszcze nie wróciły.",
        "Zielarka: Dobrze. Teraz napar będzie miał sens.",
        [{"type": "give", "target": "swamp_herbs_475", "count": 1, "current": 0}],
        {"gold": 13, "rep": 2},
        auto_complete_on_delivery=True,
    ),
    "bagna_stone": Quest(
        "bagna_stone",
        "Kamień z ołtarza",
        "Pustelnik chce odzyskać ciemny kamień ze starego ołtarza.",
        "bagna_pustelnik",
        "bagna_pustelnik",
        ("zadanie", "kamien", "kamień", "ołtarz", "altarz", "bagno"),
        "Pustelnik: Przynieś kamień z ołtarza. To stary znak, nie zwykły kamyk.",
        "Pustelnik: Kamień nadal tkwi w mokradle.",
        "Pustelnik: Dobrze. Ten kamień powinien wrócić na swoje miejsce.",
        [{"type": "give", "target": "hookri_black_stone_499", "count": 1, "current": 0}],
        {"gold": 15, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "bagna_tracks": Quest(
        "bagna_tracks",
        "Bagienne tropy",
        "Myśliwy chce wiedzieć, co porusza się nocą po mokradłach.",
        "bagna_pustelnik",
        "bagna_pustelnik",
        ("zadanie", "tropy", "ślady", "slady", "bagna", "mokradlo", "mokradło"),
        "Pustelnik: Najpierw porozmawiaj z myśliwym i sprawdź, co widzi po zmroku.",
        "Pustelnik: Tropy z mokradeł nadal czekają na relację.",
        "Pustelnik: Dobrze. Teraz wiem, co krąży po bagnach.",
        [{"type": "talk", "target": "bagna_mysliwy", "count": 1, "current": 0}],
        {"gold": 10, "rep": 2},
    ),
}


class QuestManager:
    def add(self, char: Character, quest_id: str) -> bool:
        if quest_id in char.active_quests or quest_id in char.completed_quests:
            return False
        char.active_quests[quest_id] = {"current": 0}
        return True

    def is_ready(self, char: Character, quest_id: str) -> bool:
        quest = QUESTS.get(quest_id)
        if quest is None or quest_id not in char.active_quests:
            return False
        if not quest.objectives:
            return False
        state = char.active_quests[quest_id]
        return all(_objective_progress(state, index, quest) >= objective["count"] for index, objective in enumerate(quest.objectives))

    def progress(self, char: Character, obj_type: str, target: str, amount: int = 1) -> list[str]:
        messages: list[str] = []
        for qid, state in char.active_quests.items():
            quest = QUESTS.get(qid)
            if quest is None:
                continue
            for index, obj in enumerate(quest.objectives):
                if obj["type"] != obj_type or not _target_matches(obj["target"], target):
                    continue
                key = _objective_key(index)
                current = _objective_progress(state, index, quest)
                new_value = min(obj["count"], current + amount)
                state[key] = new_value
                _refresh_current_total(state, quest)
                if current < obj["count"] and new_value >= obj["count"]:
                    messages.append(f"<green>[Zadanie: {quest.title}] Cel osiągnięty!</green>")
        return messages

    def complete_if_ready(self, char: Character, quest_id: str, event_bus=None) -> str:
        if quest_id not in char.active_quests:
            return "Nie masz takiego zadania."
        quest = QUESTS.get(quest_id)
        if quest is None:
            return "Nie znam takiego zadania."
        if not self.is_ready(char, quest_id):
            return "Jeszcze nie ukończyłeś celu zadania."
        reward_gold = quest.rewards.get("gold", 0)
        reward_rep = quest.rewards.get("rep", 0)
        char.gold += reward_gold
        del char.active_quests[quest_id]
        char.completed_quests.append(quest_id)
        if event_bus is not None:
            event_bus.emit(DomainEventType.QUEST_COMPLETED, username=char.username, character=char, quest_id=quest_id, rep=reward_rep)
        reward_text = f"{reward_gold} monet"
        if reward_rep:
            reward_text += f" i {reward_rep} reputacji"
        return f"<green>Kończysz zadanie: {quest.title}. Otrzymujesz {reward_text}.</green>"

    def render(self, char: Character) -> str:
        if not char.active_quests and not char.completed_quests:
            return "Nie masz aktywnych zadań. Nie nosisz teraz żadnej obietnicy do spełnienia."

        lines: list[str] = []
        if char.active_quests:
            lines.append("W dzienniku wciąż są sprawy, które czekają na domknięcie.")
            for qid, state in sorted(char.active_quests.items()):
                quest = QUESTS.get(qid)
                if quest is None:
                    lines.append(f"{qid}: wspomnienie zadania, którego nie umiesz już nazwać.")
                    continue
                total_current = int(state.get("current", 0))
                total_count = sum(objective["count"] for objective in quest.objectives)
                progress = total_current / total_count if total_count else 0
                reward = quest.rewards
                reward_text: list[str] = []
                if "gold" in reward:
                    reward_text.append(f"{reward['gold']} monet")
                if "rep" in reward:
                    reward_text.append(f"{reward['rep']} reputacji")
                reward_clause = f" W nagrodę czeka {join_prose(reward_text)}." if reward_text else ""
                if progress < 0.33:
                    mood = "Ledwie zaczęte, ale już zapisane w pamięci."
                elif progress < 0.66:
                    mood = "Sprawa jest w toku i widać, że zmierza ku końcowi."
                elif progress < 1.0:
                    mood = "Został ostatni krok, zanim opowieść się domknie."
                else:
                    mood = "Zadanie wygląda na gotowe do oddania."
                lines.append(f"{quest.title}. {quest.description} {mood}{reward_clause}")
                objective_lines = [
                    f"{_objective_label(objective['type'])}: {_format_target(objective['target'])}"
                    for objective in quest.objectives
                ]
                lines.append("Cele: " + join_prose(objective_lines) + ".")

        if char.completed_quests:
            lines.append("To, co już domknąłeś, zostaje za tobą jak cicha blizna.")
            for qid in char.completed_quests:
                quest = QUESTS.get(qid)
                lines.append(quest.title if quest else qid)

        return "\n".join(lines)
