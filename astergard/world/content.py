from __future__ import annotations

from dataclasses import dataclass, field

from astergard.items.models import Item
from astergard.world.models import Location


@dataclass(frozen=True)
class LocationContent:
    """Hand-authored content overlay for procedural rooms.

    The generator still creates the full 500-room graph. Content overlays turn
    selected rooms into memorable places with inspectable details, ground
    objects, hidden items and stronger atmospheric identity.
    """

    room_id: int
    name: str | None = None
    description: str | None = None
    inspectables: dict[str, str] = field(default_factory=dict)
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()


START_CONTENT: tuple[LocationContent, ...] = (
    LocationContent(
        room_id=0,
        name="Brama Dymnych Chorągwi",
        description=(
            "Wąska brama wciska trakt między kamienny mur i czarne belki strażnicy. "
            "Na hakach wiszą mokre płaszcze wartowników, a w koleinach stoi brunatna woda. "
            "Miasto zaczyna się tu nie od rynku, lecz od kontroli, chłodu i zapachu starego żelaza."
        ),
        inspectables={
            "brama": "Brama jest okuta żelazem. W rysach drewna zebrał się pył drogi i sadza z pochodni.",
            "mur": "Mur nie jest wysoki, ale gruby; miejscami widać świeżą zaprawę po zimowych pęknięciach.",
            "warta wartownicy zolnierz zolnierze": "Wartownicy patrzą raczej na ręce podróżnych niż na ich twarze.",
            "koleiny blotnista droga droga": "Koleiny zdradzają, że najcięższe wozy wjeżdżają tędy przed świtem.",
        },
        items=(Item("żelazny klucz", "Prosty klucz do bocznej furty; na uchwycie ma wybity znak straży.", 0.1, 5, "iron_key"),),
    ),
    LocationContent(
        room_id=1,
        name="Plac Przed Wartownią",
        description=(
            "Plac jest bardziej ubity niż wybrukowany. Pod ścianą wartowni leżą polana, skrzynki z grotami "
            "i tarcze odstawione do naprawy. Z komina idzie niski dym, który nie chce podnieść się nad dach."
        ),
        inspectables={
            "wartownia": "Za uchylonymi drzwiami słychać kaszel, stuk kubka i krótki śmiech człowieka po nocnej służbie.",
            "tarcze tarcza": "Tarcze są obdarte na krawędziach. Jedna ma świeży ślad po toporze.",
            "skrzynki groty": "W skrzynkach leżą groty włóczni i krótkie żelazne kolce do naprawy palisady.",
            "komin dym": "Dym pachnie mokrym drewnem, tanią kaszą i czymś przypalonym na dnie garnka.",
        },
        hidden_items=((Item("srebrny pierścień", "Zmatowiały pierścień wciśnięty między deski pod ścianą wartowni.", 0.05, 50, "silver_ring"), 12),),
    ),
    LocationContent(
        room_id=20,
        name="Trakt Przy Murze",
        description=(
            "Trakt biegnie wzdłuż muru tak blisko, że idący mimowolnie ściszają głos. "
            "Kamienie są tu wyszlifowane przez buty patroli i obręcze wozów."
        ),
        inspectables={
            "mur": "W murze widać wąskie szczeliny obserwacyjne, ciemne jak zamknięte oczy.",
            "slady ślady tropy": "Ślady żołnierskich butów przykrywają drobniejsze odciski bosych stóp.",
            "wozy koleiny": "Koleiny są głębokie; ostatni wóz musiał wieźć kamień albo mokre drewno.",
        },
    ),
    LocationContent(
        room_id=21,
        name="Dziedziniec Suchych Studni",
        description=(
            "Na dziedzińcu stoją dwie studnie, obie zakryte ciężkimi kratami. "
            "Dzieci nie bawią się tu nigdy, a dorośli przechodzą szybciej, niż wymaga droga."
        ),
        inspectables={
            "studnia studnie kraty krata": "Krata jest zamknięta na stary łańcuch. Z dołu nie dochodzi plusk wody, tylko zimny przeciąg.",
            "dzieci": "Nie ma tu dzieci. To właśnie jest najbardziej zauważalne.",
            "lancuch łańcuch": "Ogniwa są grube i świeżo natłuszczone, jakby ktoś regularnie sprawdzał zamknięcie.",
        },
    ),
    LocationContent(
        room_id=22,
        name="Zaułek Garbarzy",
        description=(
            "Między niskimi szopami wisi kwaśny smród skór, popiołu i zgniłej wody. "
            "Deski pod ścianami są ciemne od lat pracy, której nikt nie chce oglądać z bliska."
        ),
        inspectables={
            "skory skóry": "Skóry wiszą na hakach. Niektóre są świeże, inne sztywne jak deski.",
            "szopy": "Szopy wyglądają, jakby trzymały się tylko na smołowanym sznurze i uporze właścicieli.",
            "woda rynsztok": "W rynsztoku płynie szara woda z tłustymi plamami na powierzchni.",
        },
        items=(Item("skórzany worek", "Poplamiony worek po garbnikach. Nadal nadaje się jako prosty pojemnik.", 0.6, 3, "leather_sack", is_container=True, capacity=8),),
    ),
    LocationContent(
        room_id=23,
        name="Ulica Przy Składach",
        description=(
            "Długie składy zamykają ulicę z obu stron. Na drzwiach wiszą znaki kupieckie, a pod progami "
            "leży słoma, piasek i kawałki sznura."
        ),
        inspectables={
            "sklady składy drzwi": "Drzwi składów są mocne, okute i poznaczone pieczęciami kilku kupieckich rodzin.",
            "znaki szyldy": "Znaki są proste: zboże, sól, skóry, żelazo. Każdy mówi więcej kupcowi niż podróżnemu.",
            "sznur sloma słoma": "W słomie można znaleźć urwane wiązania paczek i ślady drobnych gryzoni.",
        },
    ),
    LocationContent(
        room_id=24,
        name="Cichy Przesmyk",
        description=(
            "Przesmyk jest tak wąski, że dwie osoby muszą minąć się bokiem. Powyżej, między dachami, "
            "widać tylko cienką kreskę nieba."
        ),
        inspectables={
            "dachy niebo": "Dachy prawie się stykają. W deszczu woda musi spadać tu zwartą zasłoną.",
            "sciany ściany": "Ściany noszą ślady dłoni, sadzy i ostrzy przeciągniętych po tynku.",
            "przesmyk zaulek zaułek": "To dobre miejsce, żeby zgubić ogon. Albo przekonać się, że samemu jest się czyimś ogonem.",
        },
    ),
)


_DISTRICT_NAMES = (
    "Targ Północny", "Kramy Płócienników", "Podcienia Kupieckie", "Zaułek za Kramami", "Chata Drwala",
    "Zagroda Koźlarza", "Kładka nad Rynsztokiem", "Schody do Cystern", "Dom Snycerza", "Stary Spichlerz",
    "Kuźnia przy Murze", "Szeroka Brukowana", "Karczma pod Żurawiem", "Tyły Karczmy", "Mała Stajnia",
    "Róg Bednarzy", "Ulica Popielarzy", "Pod Bramą Solną", "Plac Wozów", "Studnia Żołnierska",
    "Próg Lazaretu", "Izba Cyrulika", "Dziedziniec Magazynów", "Przejście pod Łukiem", "Warsztat Łuczarza",
    "Plac Musztry", "Cień Wieży Zachodniej", "Zbrojownia Zewnętrzna", "Pralnia przy Kanale", "Kamienny Przepust",
    "Ogród Ziół", "Szopa Rybaków", "Mały Mostek", "Skwer Dłużników", "Ulica Cieśli",
    "Boczna Furta", "Przy Słupie Ogłoszeń", "Dom Pisarza", "Schody Wartowników", "Kram Świecarza",
    "Rynek Żelazny", "Przejście Rymarzy", "Plac Popasowy", "Ciemna Sień", "Górka Strażnicza",
    "Kantor Wagowy", "Zaułek Farbiarzy", "Skład Soli", "Niska Brama", "Koniec Bruku",
    "Droga pod Palisadą", "Stary Cmentarzyk", "Kapliczka Podróżnych", "Kamień Przysiąg", "Błotny Rozjazd",
    "Wylot na Trakt", "Młynny Rów", "Podmokłe Łąki", "Gaj Strażniczy", "Ostatni Posterunek",
)

_FEATURES = (
    ("bruki bruk kamienie", "Bruk jest nierówny i popękany; w szczelinach leży czarny piasek oraz resztki słomy."),
    ("rynna rynsztok woda", "Rynsztok niesie wodę leniwie, zbierając po drodze sadzę, łuski cebuli i drobny żwir."),
    ("okna shutters okiennice", "Okiennice są przymknięte. Ludzie patrzą przez szpary, ale szybko cofają twarze."),
    ("slady ślady tropy", "Ślady nachodzą na siebie warstwami: żołnierskie buty, koła wozów i drobne stopy dzieci."),
    ("szyld znak", "Szyld jest wyblakły, lecz nadal czytelny dla miejscowych; obcy musi zgadywać znaczenie symbolu."),
    ("drzwi prog próg", "Próg jest wytarty, jakby przez lata przechodzono tędy ciężko i bez radości."),
    ("sciana ściana mur", "Na ścianie widać ślady sadzy, uderzeń i starych ogłoszeń zdartych nożem."),
    ("latarnia pochodnia", "Latarnia nawet za dnia pachnie łojem i dymem. Ktoś niedawno wymienił knot."),
)

_ATMOSPHERE = (
    "Pachnie mokrym drewnem, dymem i skórą suszoną zbyt blisko ognia.",
    "Gdzieś za ścianą ktoś kłóci się półgłosem, ale milknie, gdy kroki zbliżają się do rogu.",
    "Wiatr nie ma tu miejsca, więc wciska się w szczeliny i porusza tylko kurzem przy ziemi.",
    "Kamień trzyma chłód nawet wtedy, gdy niebo jest jasne.",
    "Nad głową wiszą sznury, płótna i cudze sprawy, których lepiej nie dotykać.",
    "Wszystko wygląda zwyczajnie, lecz każdy przedmiot ma tu właściciela albo kogoś, kto nim się interesuje.",
)

_DETAILS = (
    "Pod ścianą leży pęknięta deska, używana najwyraźniej jako ławka przez straż albo handlarzy.",
    "W kącie zebrano stare beczki, tak suche, że przy dotknięciu mogłyby rozsypać się jak kora.",
    "Na ziemi widać kilka świeżych plam błota, jakby ktoś przyszedł tu z drogi spoza murów.",
    "Jedna z dachówek jest obluzowana i stuka przy mocniejszym podmuchu.",
    "Na wysokości pasa ciągnie się rysa po ostrzu, długa i zbyt równa, by była przypadkowa.",
)


def _district_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _FEATURES[index % len(_FEATURES)]
    feature_b = _FEATURES[(index + 3) % len(_FEATURES)]
    description = (
        f"{name} należy do gęstego, roboczego serca twierdzy. {_ATMOSPHERE[index % len(_ATMOSPHERE)]} "
        f"{_DETAILS[index % len(_DETAILS)]}"
    )
    inspectables = {
        feature_a[0]: feature_a[1],
        feature_b[0]: feature_b[1],
        "ludzie przechodnie mieszkancy mieszkańcy": "Miejscowi patrzą krótko i rzeczowo; nie szukają zaczepki, ale pamiętają twarze.",
    }
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if index in {4, 13, 31, 52}:
        items = (Item("połamana latarnia", "Stara latarnia z pękniętym szkłem. Ma niewielką wartość, ale nadal można ją naprawić.", 1.1, 4, f"broken_lantern_{room_id}"),)
    if index in {8, 27, 34, 46, 55}:
        hidden_items = ((Item("miedziana moneta", "Pojedyncza miedziana moneta, prawie czarna od brudu.", 0.01, 1, f"copper_coin_{room_id}"), 11),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_district_content() -> tuple[LocationContent, ...]:
    # D35.1A narrows Astergard to exactly 60 city rooms: 0-59.
    # Rooms 0, 1 and 20-24 are hand-authored landmarks; the remaining city
    # rooms receive coherent district content here.
    room_ids = tuple(range(2, 20)) + tuple(range(25, 60))
    return tuple(_district_content(room_id, idx, _DISTRICT_NAMES[idx]) for idx, room_id in enumerate(room_ids))



_D351B_ZONE_DATA: dict[str, tuple[range, tuple[str, ...], str, str, tuple[str, str], tuple[str, str], tuple[str, str]]] = {
    "Podgrodzie": (
        range(60, 80),
        (
            "Błotna Brama", "Szopa Tragarzy", "Zajazd Pod Mokrym Kołem", "Plac Bydlęcy", "Rów Garbarski",
            "Chata Kołodzieja", "Podmurze Przy Palisadzie", "Klepisko Najemników", "Targ Drzewny", "Studnia Przedmieścia",
            "Ulica Popiołów", "Warsztat Garncarza", "Zagroda Gęsi", "Skład Siana", "Przeprawa przez Rynsztok",
            "Błotny Rozjazd", "Stary Kamień Mytny", "Droga do Pól", "Niska Łąka", "Ostatnia Chata",
        ),
        "Podgrodzie Astergardu",
        "podgrodzie",
        ("bloto błoto koleiny", "Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych."),
        ("palisada mur podmurze", "Palisada wygląda gorzej niż mur miasta, ale miejscowi naprawiają ją z uporem po każdej zimie."),
        ("ludzie tragarze mieszczanie", "Ludzie pracują szybko, z głowami spuszczonymi nisko; podgrodzie nie nagradza bezczynności."),
    ),
    "Haldun": (
        range(80, 95),
        (
            "Droga do Haldun", "Krzyżowy Kamień", "Pierwsze Zagony", "Studnia Haldun", "Plac przy Spichrzu",
            "Chata Sołtysa", "Obora pod Wierzbami", "Stodoły Zachodnie", "Młynny Rów", "Mostek nad Strugą",
            "Pola Jęczmienia", "Sad Kwaśnych Jabłek", "Pastwisko Koni", "Kapliczka Żniwiarzy", "Droga ku Fortecy",
        ),
        "Haldun",
        "wieś rolnicza",
        ("pola zagony zboze zboże", "Zagony są długie i równe. Ziemia jest ciężka, lecz wyraźnie dobrze obrabiana od pokoleń."),
        ("studnia struga woda", "Woda jest chłodna i twarda od kamienia. Przy cembrowinie leżą wiadra z wyślizganymi uchwytami."),
        ("chlopi chłopi gospodarze", "Gospodarze są małomówni. Patrzą na niebo, drogę i obce ręce, właśnie w tej kolejności."),
    ),
    "Osada_Mysliwych": (
        range(95, 110),
        (
            "Wschodnia Furta Łowców", "Suszarnia Skór", "Dymne Szałasy", "Plac Tropicieli", "Chata Starszego Łowcy",
            "Stojaki na Łuki", "Garaż dla Sań", "Rów na Odpadki", "Leśna Kapliczka", "Polana Psów",
            "Schron przy Dębie", "Wędzarnia Mięsa", "Skład Wnyków", "Ścieżka Ku Puszczy", "Ostatni Znak Toporem",
        ),
        "Osada Myśliwych",
        "osada łowiecka",
        ("skory skóry futra", "Skóry wiszą na żerdziach. Jedne pachną dymem, inne krwią i mokrym psem."),
        ("slady ślady tropy", "W ziemi mieszają się ślady ludzi, psów, jeleni i czegoś większego, co przeciągnięto tędy nocą."),
        ("lowcy łowcy mysliwi myśliwi", "Łowcy mówią mało, ale każdy z nich odruchowo siada plecami do ściany i twarzą do wejścia."),
    ),
    "Forteca_Dungrim": (
        range(110, 125),
        (
            "Brama Dungrim", "Przedbramie z Wilczymi Hakami", "Dziedziniec Garnizonu", "Studnia Forteczna", "Koszary Zachodnie",
            "Stajnie Patroli", "Skład Bełtów", "Zbrojownia Dungrim", "Wieża Sygnałowa", "Mur Nad Traktem",
            "Izba Dowódcy", "Kaplica Przysiąg", "Cela Dezerterów", "Kuchnia Garnizonowa", "Wyjazd na Zachodni Trakt",
        ),
        "Forteca Dungrim",
        "forteca graniczna",
        ("mur blanki kamien", "Mur jest niski, ale gruby. Kamienie noszą ciemne ślady po dawnych pożarach i smołowanych naprawach."),
        ("zolnierze żołnierze garnizon", "Żołnierze poruszają się oszczędnie. To garnizon drogi, nie paradny oddział stolicy."),
        ("trakt brama przejazd", "Przejazd jest wąski, celowo niewygodny dla wozów. Forteca uczy pokory każdego kupca."),
    ),
    "Trakty": (
        range(135, 180),
        (
            "Kapliczka Podróżnych za Murem", "Pierwszy Kamień Milowy", "Mokra Koleina", "Rozstaje Trzech Wozów", "Stary Słup Mytny",
            "Droga przy Łanach", "Mostek Kupiecki", "Karczemne Popasowisko", "Zakręt pod Topolami", "Miejsce po Starym Ognisku",
            "Trakt Haldunski", "Kopiec Graniczny", "Bród na Zimnej Strudze", "Kładka Przewoźników", "Wójtowski Kamień",
            "Skręt ku Dungrim", "Wysoka Grobla", "Szlak Solnych Wozów", "Czarna Koleina", "Zawiany Przepust",
            "Długi Prostak", "Rozdroże Straży", "Północny Nasyp", "Brzezina przy Drodze", "Krzywy Mostek",
            "Przejazd pod Skałką", "Czerwony Kamień", "Dolina Wozów", "Stary Popas", "Miejsce po Szubienicy",
            "Droga Myśliwych", "Zakole przy Stawie", "Sypki Nawrót", "Kamienny Znak", "Zajazd bez Szyldu",
            "Wąski Przejazd", "Pola Ostatnich Chat", "Brodnica", "Granica Puszczy", "Torfowa Krawędź",
            "Południowy Trakt", "Głaz z Nacięciem", "Puste Rozstaje", "Zejście ku Bagnom", "Zachodni Odcinek Karawan",
        ),
        "Trakty Północnego Pogranicza",
        "trakt handlowy",
        ("droga trakt koleiny", "Droga nie idzie prosto dłużej niż trzeba. Omija mokradła, stare groby i miejsca, gdzie wozy kiedyś grzęzły na dobre."),
        ("kamien kamień znak milowy", "Kamień milowy jest obity deszczem i wozami. Znaki wydrapano głęboko, żeby przetrwały więcej niż jedną władzę."),
        ("wozy kupcy patrole", "Ruch na trakcie nigdy nie cichnie zupełnie: nawet pusta droga ma zapach koni, dymu i taniego smaru."),
    ),
    "Boczne_Drogi": (
        range(180, 210),
        (
            "Stara Droga za Furtą", "Zarośnięty Dukt", "Rów Przemytników", "Ścieżka przez Leszczyny", "Zapadły Mostek",
            "Miejsce po Obozie", "Droga bez Kamieni", "Wąwóz Węglarzy", "Krzywe Brzozy", "Cichy Bród",
            "Leśny Objazd", "Mokra Górka", "Próg Starej Grobli", "Zakryte Rozstaje", "Piaszczysty Skręt",
            "Dukt do Puszczy", "Rozbita Kapliczka", "Wyschnięte Koryto", "Cień Czarnych Sosen", "Kamienie Węglarzy",
            "Ślepa Miedza", "Lisza Ścieżka", "Niski Przesmyk", "Dawna Droga Drwali", "Stary Pień z Nacięciem",
            "Przepust pod Korzeniami", "Zejście ku Kniei", "Sucha Polana", "Rów Graniczny", "Zanikający Dukt",
        ),
        "Boczne drogi i rozstaje",
        "boczny trakt",
        ("sciezka ścieżka dukt droga", "Ścieżka jest wąska i kapryśna; miejscami znika pod trawą, żeby wrócić kilka kroków dalej."),
        ("krzaki leszczyny korzenie", "Krzaki łapią za nogawki, a korzenie wystają z ziemi jak stare, zaciśnięte palce."),
        ("slady ślady oboz tropy", "Ślady są nieliczne, ale świeże. Ktoś używa tej drogi właśnie dlatego, że nie wygląda na używaną."),
    ),
}

_D351B_ATMOSPHERE = (
    "Nie ma tu nic przypadkowego: droga, zabudowania i ludzie istnieją dzięki twierdzy, ale nie są jej częścią.",
    "Powietrze niesie pył, dym i ciężki zapach pracy, której nie widać z murów miasta.",
    "To miejsce jest zbyt zwyczajne, by lekceważyć jego znaczenie; tędy przechodzą towary, plotki i strach.",
    "Dalej od bram Astergardu cisza robi się szersza, a każdy skręt drogi zaczyna mieć własną cenę.",
    "Lokalni znają skróty, lecz obcy szybko rozumie, że mapa nie zastąpi pamięci nóg.",
)


def _d351b_content(room_id: int, index: int, name: str, label: str, terrain: str, feature_a: tuple[str, str], feature_b: tuple[str, str], feature_c: tuple[str, str]) -> LocationContent:
    description = (
        f"{name} leży w strefie: {label}. To {terrain}, ukształtowany przez codzienny ruch ludzi, wozów i patroli. "
        f"{_D351B_ATMOSPHERE[index % len(_D351B_ATMOSPHERE)]}"
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], feature_c[0]: feature_c[1]}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {63, 82, 99, 113, 143, 156, 183, 196}:
        items = (Item("porzucony rzemień", "Krótki, zużyty rzemień. Może posłużyć do prostych napraw albo wiązania pakunków.", 0.05, 1, f"strap_{room_id}"),)
    if room_id in {69, 91, 107, 121, 151, 176, 188, 205}:
        hidden_items = ((Item("miedziana moneta", "Brudna miedziana moneta zgubiona przy drodze.", 0.01, 1, f"road_copper_{room_id}"), 10),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351b_content() -> tuple[LocationContent, ...]:
    contents: list[LocationContent] = []
    for _zone, (room_range, names, label, terrain, feature_a, feature_b, feature_c) in _D351B_ZONE_DATA.items():
        for index, room_id in enumerate(room_range):
            contents.append(_d351b_content(room_id, index, names[index], label, terrain, feature_a, feature_b, feature_c))
    return tuple(contents)


_D351C_NAMES = (
            "Skraj Cichej Puszczy",
            "Strażniczy Dąb",
            "Ścieżka Pod Smołowaną Sosną",
            "Korzenie przy Dukcie",
            "Zwisłe Leszczyny",
            "Polana Drwali",
            "Popiół po Ognisku",
            "Czarne Jagodniki",
            "Mostek z Rozłupanej Sosny",
            "Mokry Zakręt",
            "Rów Węglarzy",
            "Stare Znaki na Korze",
            "Dukt pod Wronim Gniazdem",
            "Kamień z Rysą",
            "Wysoka Paproć",
            "Przejście Jeleni",
            "Złamany Buk",
            "Sucha Kładka",
            "Cisowy Przesmyk",
            "Zasypany Wykrot",
            "Mrowisko przy Drodze",
            "Łan Ciemnych Traw",
            "Strumień Cichego Mchu",
            "Brodzik pod Korzeniami",
            "Garb Starego Lasu",
            "Krąg Białych Brzóz",
            "Zielona Kotlina",
            "Wąska Ścieżka Łowców",
            "Sosny bez Igieł",
            "Głucha Polana",
            "Wilcze Drapania",
            "Ślad Ciągniętego Wozu",
            "Wyschnięty Jar",
            "Dwie Powalone Sosny",
            "Zarośnięty Kamień Milowy",
            "Niska Gęstwina",
            "Obozowisko Smolarzy",
            "Czarny Pień",
            "Przesmyk pod Jałowcami",
            "Skręt ku Starej Kniei",
            "Słony Zdrój",
            "Wypłowiała Kapliczka",
            "Dół po Wykrocie",
            "Kryjówka pod Korzeniami",
            "Świerki Zbite Cieniem",
            "Polana Trzech Pni",
            "Martwy Dukt",
            "Zielony Parów",
            "Tropy przy Strudze",
            "Sosnowa Brama",
            "Głaz Myśliwych",
            "Pochylona Olcha",
            "Ścieżka z Wilczą Sierścią",
            "Rozszarpany Krzew",
            "Twardy Grzbiet Ziemi",
            "Kładka Mytników",
            "Ciemna Wilgoć",
            "Miejsce Cichego Strzału",
            "Róg Starego Ostępu",
            "Wschodni Skraj Puszczy",
            "Grzęda Borówek",
            "Skręt pod Szarym Dębem",
            "Ślad Niedźwiedziej Łapy",
            "Zatarty Obóz Banitów",
            "Stara Miedza Leśna",
            "Wąwóz Pokrzyw",
            "Bród na Leśnym Potoku",
            "Ostatnia Sosna przy Dukcie",
            "Cienista Granica Kniei",
            "Przejście ku Głębi",
        )

_D351C_ATMOSPHERE = (
    "Korony drzew tłumią dźwięk tak skutecznie, że nawet własny oddech brzmi obco.",
    "Ziemia ugina się miękko pod butem; mech przykrywa stare koleiny i świeże tropy.",
    "Między pniami widać krótkie, mylące prześwity, lecz żaden nie obiecuje prostej drogi.",
    "Powietrze pachnie żywicą, mokrą korą i dymem tak starym, że mógł zostać po wczoraj albo po wojnie.",
    "Las nie jest pusty; po prostu wszystko, co tu żyje, nauczyło się milczeć pierwsze.",
)

_D351C_FEATURES = (
    ("drzewa sosny dab dąb pnie", "Pnie stoją gęsto i nierówno. Na kilku widać nacięcia pozostawione przez drwali, patrol albo kogoś, kto znaczył drogę bez zgody straży."),
    ("mech ziemia poszycie", "Mech przykrywa kamienie i stare korzenie. W miejscach, gdzie został zdarty, widać ciemną, tłustą ziemię."),
    ("tropy slady ślady", "Tropy przecinają się warstwami: jeleń, człowiek, pies albo wilk. Najświeższe prowadzą dalej niż rozsądnie byłoby iść samotnie."),
    ("korzenie wykrot", "Korzenie wystają z ziemi jak żebra czegoś dawno pogrzebanego. Pod niektórymi można ukryć sakwę, sidła albo ciało."),
    ("krzaki paprocie gestwina gęstwina", "Gęstwina nie tworzy ściany, tylko sieć. Da się przez nią przejść, ale ona zapamięta ubranie i skórę."),
    ("strumien strumień woda", "Woda płynie płytko, prawie bez dźwięku. Na piasku przy brzegu zostały drobne odciski łap."),
    ("kamien kamień glaz głaz", "Kamień jest obrośnięty porostami. Ktoś kiedyś wyciął na nim znak, teraz bardziej wyczuwalny palcami niż widoczny."),
    ("ptaki wrony cisza", "Ptaków prawie nie słychać. Gdy odzywa się wrona, jej krzyk brzmi jak ostrzeżenie, nie jak przypadek."),
)


def _d351c_forest_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351C_FEATURES[index % len(_D351C_FEATURES)]
    feature_b = _D351C_FEATURES[(index + 3) % len(_D351C_FEATURES)]
    feature_c = _D351C_FEATURES[(index + 5) % len(_D351C_FEATURES)]
    description = (
        f"{name} należy do Puszczy Ciszy, pierwszego wielkiego lasu poza bezpiecznym ruchem traktów. "
        f"{_D351C_ATMOSPHERE[index % len(_D351C_ATMOSPHERE)]} "
        "Ścieżka istnieje tu tylko dlatego, że wiele stóp powtarzało ten sam błąd przez lata."
    )
    inspectables = {
        feature_a[0]: feature_a[1],
        feature_b[0]: feature_b[1],
        feature_c[0]: feature_c[1],
    }
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {216, 223, 241, 252, 267}:
        items = (Item("wiązka suchego chrustu", "Lekka wiązka chrustu, dobra na ognisko albo do prostych prac obozowych.", 0.4, 1, f"dry_brushwood_{room_id}"),)
    if room_id in {230, 246, 258, 272}:
        hidden_items = ((Item("garść leśnych ziół", "Gorzko pachnące zioła zebrane z miejsc, których nie widać z duktu.", 0.05, 3, f"forest_herbs_{room_id}"), 11),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351c_content() -> tuple[LocationContent, ...]:
    return tuple(_d351c_forest_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(210, 280), _D351C_NAMES)))



_D351D_NAMES = (
    "Cienista Granica Kniei", "Stare Rozstaje bez Znaków", "Korytarz Cichych Leszczyn", "Zatarta Ścieżka Straży", "Kamień Trzech Nacięć",
    "Wykrot pod Czarnym Grabem", "Suchy Parów", "Mostek z Zardzewiałym Ćwiekiem", "Głuchy Zakręt", "Łuk Pochylonych Buków",
    "Wilgotne Dno Kniei", "Mchowe Stopnie", "Ślad Dawnego Traktu", "Zarwany Przepust", "Kotlina Milczących Pni",
    "Stara Smolarnia", "Piec Węglarzy", "Leśne Popielisko", "Oczko Czarnej Wody", "Skręt pod Kruczym Gniazdem",
    "Słup Graniczny bez Herbu", "Zielona Ściana Jałowców", "Cień nad Strugą", "Bród pod Wykrotem", "Ścieżka Przemytników",
    "Niski Tunel w Krzakach", "Opuszczony Szałas", "Kości przy Palenisku", "Polana bez Śpiewu", "Głaz Łowców z Dungrim",
    "Wąwóz Suchych Liści", "Cisowy Jar", "Korzeń jak Most", "Złamana Żerdź", "Trop pod Mokrą Korą",
    "Stary Gaj Graniczny", "Krąg Milczących Kamieni", "Przejście pod Martwym Dębem", "Dukt Wysokich Paproci", "Ukryty Zakos",
    "Ślepa Ścieżka Banitów", "Mokre Siodło Terenu", "Zielony Próg Gór", "Kamienista Gardziel", "Skręt ku Mekharze",
    "Ciemny Spływ do Bagien", "Torfowa Miedza", "Zimna Struga Kniei", "Kładka nad Czarnym Błotem", "Szeptane Rozlewisko",
    "Powalony Słup Myśliwych", "Ostatnie Brzozy", "Długi Cień Starej Kniei", "Zagubiony Kamień Milowy", "Głęboka Granica Ostępu",
)

_D351D_ATMOSPHERE = (
    "Knieja nie tłumi dźwięków jak puszcza; ona je połyka, a potem oddaje w niewłaściwym miejscu.",
    "Dawny trakt istnieje tu już tylko jako różnica w gęstości mchu i kierunku, w którym rosną młode pnie.",
    "Powietrze jest cięższe, chłodniejsze i wyraźnie starsze niż przy zwykłych leśnych drogach.",
    "Każde przejście wygląda możliwie, ale tylko niektóre prowadzą dalej niż do mokrego dołu albo ściany jałowców.",
    "To miejsce nie straszy krzykiem. Straszy tym, że nic nie musi krzyczeć, żeby człowiek zaczął iść szybciej.",
)

_D351D_FEATURES = (
    ("dukt trakt sciezka ścieżka", "Dukt jest prawie zatarty. Widać go tylko tam, gdzie mech rośnie niżej, a korzenie układają się zbyt równo jak na przypadek."),
    ("drzewa buki graby cisy", "Drzewa stoją ciasno i ukośnie, jakby przez lata cofały się przed wiatrem, który nigdy tutaj nie dochodzi."),
    ("kamien kamień znaki naciecia nacięcia", "Na kamieniu lub korze widać stare nacięcia. Nie są ozdobą; ktoś znaczył nimi drogę albo granicę, której dziś nikt nie pilnuje jawnie."),
    ("mech liscie liście ziemia", "Mech i liście maskują nierówności. Jeden nieuważny krok wystarczy, by kostka zapadła się między korzenie."),
    ("woda struga blotnisko błotnisko", "Woda stoi w ciemnych zagłębieniach albo sączy się bez plusku. Jej powierzchnia drży, choć nie widać wiatru."),
    ("slady ślady tropy", "Ślady są nieliczne, urywane i często celowo zatarte. Ktoś zna knieje lepiej niż zwykły myśliwy."),
    ("krzaki jalowce jałowce paprocie", "Jałowce i paprocie tworzą zieloną zasłonę. Można przez nią przejść, lecz nie da się zrobić tego cicho."),
    ("cisza ptaki kruki", "Ptaki milkną tu wcześniej niż powinny. Kiedy kruk odezwie się z góry, brzmi to jak komentarz, nie odgłos lasu."),
)


def _d351d_deep_forest_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351D_FEATURES[index % len(_D351D_FEATURES)]
    feature_b = _D351D_FEATURES[(index + 2) % len(_D351D_FEATURES)]
    feature_c = _D351D_FEATURES[(index + 5) % len(_D351D_FEATURES)]
    description = (
        f"{name} leży w Kniei Cichych Ścieżek, głębszej i mniej uczęszczanej niż Puszcza Ciszy. "
        f"{_D351D_ATMOSPHERE[index % len(_D351D_ATMOSPHERE)]} "
        "Drogę wyznaczają tu nie tablice, lecz pamięć, nacięcia w korze i ostrożność ludzi, którzy wrócili."
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], feature_c[0]: feature_c[1]}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {295, 304, 318, 327}:
        items = (Item("kawał smolnego drewna", "Ciemny kawał drewna przesycony żywicą. Dobrze łapie ogień i pachnie starą smolarnią.", 0.35, 2, f"pitchwood_{room_id}"),)
    if room_id in {287, 301, 316, 331}:
        hidden_items = ((Item("ciemne zioła z knieii", "Wiotkie, gorzkie zioła rosnące w miejscach, gdzie słońce prawie nie dotyka ziemi.", 0.04, 4, f"deep_forest_herbs_{room_id}"), 12),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351d_content() -> tuple[LocationContent, ...]:
    return tuple(_d351d_deep_forest_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(280, 335), _D351D_NAMES)))



_D351E_PASS_NAMES = (
    "Droga pod Strażnicą Przełęczy", "Przedbramie Kamiennych Strażników", "Dziedziniec Północnej Warty", "Studnia pod Skarpą", "Barak Zimowych Wart",
    "Skład Siana i Soli", "Wieża Sygnałowa Mekhary", "Mur nad Gardzielą", "Brama Wąskiego Gardła", "Ostatni Kamień Graniczny",
)

_D351E_MOUNTAIN_NAMES = (
    "Podnóże Mekhary", "Kamienny Zakręt", "Półka nad Ciemnym Lasem", "Ścieżka Kozich Racic", "Suchy Żleb",
    "Złamany Drogowskaz", "Stara Droga Straży", "Piargi pod Sosnami", "Wąskie Siodło", "Głaz z Żelaznym Klinem",
    "Urwisko Kruków", "Zawalony Szałas Tragarzy", "Skręt ku Srebrnej Skale", "Źródło pod Łupkiem", "Północna Ściana Jarów",
    "Niski Próg Skalny", "Dawna Ambona Łuczników", "Kamienie po Ognisku", "Przejście pod Wiszącą Skałą", "Czerwony Osyp",
    "Ślad Starej Lawiny", "Koryto Suchego Potoku", "Wysoka Półka Wartownicza", "Cień Poszarpanej Grani", "Miejsce po Mostku Linowym",
    "Skały Dymnych Ptaków", "Skręt nad Bezdennym Parowem", "Jama Niedźwiedzia", "Rozpadlina Trzech Głosów", "Kamienny Grzbiet",
    "Ścieżka pod Gołą Granią", "Zimna Nisza", "Czarny Balkon nad Doliną", "Stary Punkt Sygnałowy", "Osypisko z Rdzą",
    "Wrota do Głębokich Sztolni", "Ślepa Półka Górników", "Zielony Nalot na Skale", "Gwizd Wiatru w Szczelinie", "Próg Przed Burzą",
    "Kruchy Trawers", "Skała Dwóch Strażników", "Zimowy Zakos", "Kozia Drabina", "Rozdroże nad Kopalnią",
    "Stary Słup Kopalniany", "Zejście do Rudych Skał", "Wietrzna Gardziel", "Ostatni Widok na Astergard", "Półka Martwych Jałowców",
    "Przysypana Ścieżka", "Głęboki Cień Grani", "Brama Kamiennego Wiatru", "Krawędź Starej Mekhary", "Zejście ku Kopalni Żelaza",
)

_D351E_PASS_ATMOSPHERE = (
    "Strażnica nie broni miasta przed armią; broni drogi przed zimą, głodem i ludźmi, którzy przyszli za późno.",
    "Kamień jest tu pocięty śladami kół, racic i żelaza, a każdy dźwięk odbija się od ścian przełęczy.",
    "Warta patrzy na północ dłużej niż na podróżnych, jakby sama gardziel mogła pewnego ranka zejść niżej.",
)

_D351E_MOUNTAIN_ATMOSPHERE = (
    "Im wyżej, tym mniej tu lasu, a więcej ostrego kamienia i wiatru, który nie pyta o zgodę.",
    "Ścieżka nie prowadzi prosto; wybiera to, co dało się przeżyć ostatniej zimy.",
    "Dolina pod stopami wygląda spokojnie, ale każdy krok przypomina, że spokój bywa tylko odległością.",
    "Kamienie osuwają się cicho, dopiero po chwili zdradzając, jak blisko jest urwisko.",
    "To nie jest miejsce dla kolumny wojska. To kraj zwiadowców, tragarzy, pasterzy i ludzi, którzy wiedzą, kiedy zawrócić.",
)

_D351E_PASS_FEATURES = (
    ("brama przejazd gardziel", "Przejazd jest celowo wąski. Dwóch ludzi z włóczniami może tu zatrzymać wóz, a dziesięciu - całą karawanę."),
    ("mur blanki kamien kamień", "Mur wyrasta z naturalnej skały i w kilku miejscach trudno rozpoznać, gdzie kończy się praca murarza."),
    ("warta zolnierze żołnierze", "Wartownicy noszą twarze ludzi, którzy widzieli zbyt wiele zawróconych wypraw i zbyt mało cudów."),
    ("wiatr snieg śnieg zimno", "Wiatr niesie drobny pył kamienny i zapowiedź śniegu nawet wtedy, gdy niżej jest jeszcze jesień."),
)

_D351E_MOUNTAIN_FEATURES = (
    ("skaly skały kamien kamień", "Skała jest spękana i ostra. W szczelinach leżą drobne odłamki, które łatwo ruszyć podeszwą."),
    ("sciezka ścieżka trawers", "Ścieżka jest wąska, miejscami wydeptana bardziej przez kozy niż przez ludzi."),
    ("urwisko przepasc przepaść jar", "Urwisko zaczyna się nagle. Mgła na dole sprawia, że głębokość trzeba sobie dopowiedzieć."),
    ("wiatr chmury niebo", "Chmury idą nisko i szybko. Wiatr zmienia kierunek bez ostrzeżenia, jakby odbijał się od niewidzialnych murów."),
    ("slady ślady racice tropy", "W kamiennym pyle widać racice, podkute buty i pojedynczy ślad czegoś cięższego, co zeszło tędy nocą."),
    ("strażnica ruiny wieza wieża", "Pozostałości strażnic są surowe: trochę kamienia, rdza po zawiasach i miejsca, gdzie ogień zostawił czarne języki."),
    ("rdza ruda zelazo żelazo", "Na kilku kamieniach widać rudawe żyły. Góra nie ukrywa żelaza, tylko każe za nie płacić drogą."),
    ("kosodrzewina jalowce jałowce", "Niskie krzewy rosną przy samej ziemi, poskręcane od wiatru i obgryzione przez zwierzęta."),
)


def _d351e_pass_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351E_PASS_FEATURES[index % len(_D351E_PASS_FEATURES)]
    feature_b = _D351E_PASS_FEATURES[(index + 2) % len(_D351E_PASS_FEATURES)]
    description = (
        f"{name} należy do Strażnicy Przełęczy, kamiennego wąskiego gardła między Astergardem a Mekharą. "
        f"{_D351E_PASS_ATMOSPHERE[index % len(_D351E_PASS_ATMOSPHERE)]} "
        "To miejsce ma więcej wspólnego z rygorem niż z chwałą: liczy wozy, ludzi i zapasy, zanim pozwoli im wejść w góry."
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], "znaki rozkazy tablice": "Tablice są krótkie: opłaty, zakazy, ostrzeżenia przed śniegiem i lista tych, którzy nie wrócili."}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {127, 132}:
        items = (Item("zardzewiały grot włóczni", "Stary grot, wciąż ostry pod warstwą rdzy.", 0.25, 2, f"rusty_spearhead_{room_id}"),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _d351e_mountain_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351E_MOUNTAIN_FEATURES[index % len(_D351E_MOUNTAIN_FEATURES)]
    feature_b = _D351E_MOUNTAIN_FEATURES[(index + 3) % len(_D351E_MOUNTAIN_FEATURES)]
    feature_c = _D351E_MOUNTAIN_FEATURES[(index + 5) % len(_D351E_MOUNTAIN_FEATURES)]
    description = (
        f"{name} leży w Górach Mekhara, gdzie droga jest bardziej umową z terenem niż ludzkim dziełem. "
        f"{_D351E_MOUNTAIN_ATMOSPHERE[index % len(_D351E_MOUNTAIN_ATMOSPHERE)]} "
        "Każdy zakos odsłania inną cenę przejścia: czas, ostrożność albo krew."
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], feature_c[0]: feature_c[1]}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {341, 358, 371}:
        items = (Item("odłamek rudy żelaza", "Ciężki, rdzawy odłamek skały z widoczną żyłą żelaza.", 0.7, 3, f"iron_ore_chip_{room_id}"),)
    if room_id in {349, 365, 382}:
        hidden_items = ((Item("górskie zioła", "Twarde, gorzkie zioła rosnące w szczelinach osłoniętych przed wiatrem.", 0.03, 5, f"mountain_herbs_{room_id}"), 13),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351e_content() -> tuple[LocationContent, ...]:
    pass_content = tuple(_d351e_pass_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(125, 135), _D351E_PASS_NAMES)))
    mountain_content = tuple(_d351e_mountain_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(335, 390), _D351E_MOUNTAIN_NAMES)))
    return pass_content + mountain_content


_D351F_MINE_NAMES = (
    "Wrota Kopalni Żelaza", "Plac Przed Szybem", "Szopa Cechu Górników", "Waga Rudy", "Stary Kołowrót",
    "Zjazd do Górnego Chodnika", "Górny Chodnik Północny", "Nisza z Lampami", "Skład Kilofów", "Ślepy Przodek",
    "Rozwidlenie Pod Stemplami", "Mokra Ściana Łupku", "Korytarz Czerwonej Rudy", "Podszybie Pierwszego Poziomu", "Komora Starych Stempli",
    "Zawał pod Sosnową Belką", "Szyb Wentylacyjny", "Schody do Drugiego Poziomu", "Dolny Chodnik Wschodni", "Czarna Kałuża",
    "Magazyn Złamanych Wózków", "Stara Kuźnia Górnicza", "Żyła Rudego Żelaza", "Komora Echa", "Mostek nad Rozpadliną",
    "Przodek Bez Świeżego Powietrza", "Pochylnia do Głębokich Sztolni", "Głębokie Sztolnie", "Podziemny Strumień", "Sala Białego Nacieku",
    "Zardzewiały Tor Wózków", "Jezioro pod Mekharą", "Kamienny Próg Wilgoci", "Stary Szyb Awaryjny", "Przejście ku Wilczym Jamom",
)

_D351F_CAVE_NAMES = (
    "Ciemna Gardziel Wilków", "Niska Jama Wejściowa", "Rozdarte Posłanie", "Korytarz Zimnego Oddechu", "Rozwidlenie Pazurów",
    "Legowisko Młodych", "Kamień Obgryzionych Kości", "Wilgotny Przesmyk", "Jama Starej Watahy", "Szczelina pod Korzeniem",
    "Głucha Komora", "Ostry Zakręt w Skale", "Półka nad Czarną Dziurą", "Ślad Krwawego Tropu", "Wąska Rura Skalna",
    "Cisza po Wyciu", "Sucha Jama Kości", "Ukryty Wylot w Jarze", "Nora Podwójnego Cienia", "Ślepe Serce Jaskiń",
)

_D351F_MINE_ATMOSPHERE = (
    "Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien.",
    "Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny.",
    "Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód.",
    "Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna.",
    "To miejsce nie jest opuszczone; raczej czeka, aż ktoś znów uzna żelazo za warte ryzyka.",
)

_D351F_CAVE_ATMOSPHERE = (
    "Zapach mokrej sierści i starej krwi jest tu mocniejszy niż chłód skały.",
    "Jaskinia nie prowadzi prosto; skręca tak, jak skręca zwierzę uciekające przed ogniem.",
    "Głos ginie szybko, ale szuranie kamyka wraca z kilku stron naraz.",
    "Na ziemi leżą kości zbyt stare, by mówiły o ostatnim posiłku, i zbyt świeże, by je zignorować.",
    "To nie jest kopalniany korytarz. Tu nie ma ludzkiej miary, tylko potrzeba schronienia i zęby.",
)

_D351F_MINE_FEATURES = (
    ("ruda zelazo żelazo zyla żyła", "Ruda wychodzi z kamienia rudymi smugami. Nie jest czysta, ale wystarczy, by utrzymać kuźnie przy pracy."),
    ("stemple belki drewno", "Drewniane stemple są ciemne od wilgoci. Część popękała wzdłuż słojów i została owinięta żelaznymi obręczami."),
    ("tory wozki wózki", "Wąskie tory dla wózków znikają miejscami pod błotem, pyłem i drobnym gruzem."),
    ("lampy swiatlo światło", "Lampy dają żółte, nerwowe światło. Sadza zebrała się nad nimi jak czarne brwi."),
    ("zawal zawał rumowisko", "Rumowisko nie wygląda stabilnie. Małe kamienie co jakiś czas zsuwają się bez dotknięcia."),
    ("woda wilgoc wilgoć strumien strumień", "Woda sączy się po ścianie, chłodna i metaliczna w zapachu."),
    ("kilofy narzedzia narzędzia", "Narzędzia leżą równo, ale nikt rozsądny nie zostawia ich tak bez powodu."),
    ("szyb lina kolowrot kołowrót", "Lina jest szorstka, przetarta i zbyt ważna, by ufać jej bez sprawdzenia."),
)

_D351F_CAVE_FEATURES = (
    ("tropy slady ślady lapy łapy", "W glinie odbiły się wilcze łapy. Jedne są drobne, inne szerokie jak dłoń dorosłego człowieka."),
    ("kosci kości resztki", "Kości są pogryzione i posortowane nie przez człowieka, ale przez cierpliwe zęby."),
    ("sierść siersc futro", "Kępki sierści trzymają się skalnych występów i korzeni wciśniętych przez szczeliny."),
    ("szczelina pekniecie pęknięcie", "Szczelina jest wąska. Przeciąg niesie przez nią zapach lasu i czegoś padłego."),
    ("skala skała sciany ściany", "Ściany są mokre, gładkie od ocierania boków zwierząt i miejscami porysowane pazurami."),
    ("legowisko poslanie posłanie", "Legowisko jest ugniecione, pełne sierści, igliwia i drobnych kości."),
)


def _d351f_mine_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351F_MINE_FEATURES[index % len(_D351F_MINE_FEATURES)]
    feature_b = _D351F_MINE_FEATURES[(index + 3) % len(_D351F_MINE_FEATURES)]
    feature_c = _D351F_MINE_FEATURES[(index + 5) % len(_D351F_MINE_FEATURES)]
    description = (
        f"{name} należy do Kopalni Żelaza pod Mekharą, miejsca, gdzie Astergard płaci za broń ciemnością i pyłem. "
        f"{_D351F_MINE_ATMOSPHERE[index % len(_D351F_MINE_ATMOSPHERE)]} "
        "Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli."
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], feature_c[0]: feature_c[1]}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {390, 398, 412, 422}:
        items = (Item("odłamek rudy żelaza", "Ciężki, rdzawy kawałek rudy wydobyty z żyły Mekhary.", 0.8, 4, f"mine_iron_ore_{room_id}"),)
    if room_id in {404, 416, 421}:
        hidden_items = ((Item("górniczy znacznik", "Mała ołowiana blaszka z wybitym numerem zmiany.", 0.02, 6, f"miner_token_{room_id}"), 12),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _d351f_cave_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351F_CAVE_FEATURES[index % len(_D351F_CAVE_FEATURES)]
    feature_b = _D351F_CAVE_FEATURES[(index + 2) % len(_D351F_CAVE_FEATURES)]
    feature_c = _D351F_CAVE_FEATURES[(index + 4) % len(_D351F_CAVE_FEATURES)]
    description = (
        f"{name} należy do Jaskiń Wilków, naturalnego labiryntu przy starych sztolniach. "
        f"{_D351F_CAVE_ATMOSPHERE[index % len(_D351F_CAVE_ATMOSPHERE)]} "
        "Człowiek jest tu intruzem: zbyt głośnym, zbyt prostym i zbyt wolnym."
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], feature_c[0]: feature_c[1]}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {458, 466, 472}:
        items = (Item("obgryziona kość", "Długa kość, starannie oczyszczona z mięsa przez wilcze zęby.", 0.2, 1, f"gnawed_bone_{room_id}"),)
    if room_id in {462, 470}:
        hidden_items = ((Item("kępa wilczej sierści", "Szorstka kępa ciemnej sierści zaczepiona o ostrą krawędź skały.", 0.01, 2, f"wolf_fur_clump_{room_id}"), 10),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351f_content() -> tuple[LocationContent, ...]:
    mine_content = tuple(_d351f_mine_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(390, 425), _D351F_MINE_NAMES)))
    cave_content = tuple(_d351f_cave_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(455, 475), _D351F_CAVE_NAMES)))
    return mine_content + cave_content

def make_content_pack() -> tuple[LocationContent, ...]:
    return START_CONTENT + _make_district_content() + _make_d351b_content() + _make_d351c_content() + _make_d351d_content() + _make_d351e_content() + _make_d351f_content()


def apply_content_pack(locations: dict[int, Location], content_pack: tuple[LocationContent, ...] | None = None) -> None:
    """Apply hand-authored content without changing the generated graph."""
    for content in content_pack or make_content_pack():
        loc = locations.get(content.room_id)
        if loc is None:
            continue
        if content.name is not None:
            loc.name = content.name
        if content.description is not None:
            loc.description = content.description
        loc.inspectables.update(content.inspectables)
        for item in content.items:
            if item.vnum is None or all(existing.vnum != item.vnum for existing in loc.items):
                loc.items.append(item)
        for item, difficulty in content.hidden_items:
            if all(getattr(hidden.get("data"), "vnum", None) != item.vnum for hidden in loc.hidden_elements):
                loc.hidden_elements.append({"type": "item", "data": item, "difficulty": difficulty})
