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
    forms: dict[str, str] = field(default_factory=dict)
    exit_forms: dict[str, dict[str, str]] = field(default_factory=dict)
    exit_kinds: dict[str, str] = field(default_factory=dict)
    scene_profile: str = ""
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()


START_CONTENT: tuple[LocationContent, ...] = (
    LocationContent(
        room_id=0,
        name="Brama Dymnych Chorągwi",
        description=(
            "Wąska brama wciska trakt między kamienny mur i czarne belki strażnicy. "
            "Na hakach wiszą mokre płaszcze wartowników, a w koleinach stoi brunatna woda. "
            "Od krat, łańcuchów i okutych wrót ciągnie zapach wilgotnego żelaza."
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
        hidden_items=((Item("srebrny pierścień", "Zmatowiały pierścień wciśnięty między deski pod ścianą wartowni.", 0.05, 50, "silver_ring"), 11),),
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
        name="Studnia Miejska",
        description=(
            "Studnia stoi między domami jak obowiązek, z którym nikt nie dyskutuje. "
            "Przychodzą tu wszyscy, od straży po dzieci, a kamień wokół cembrowiny jest wyślizgany do połysku."
        ),
        inspectables={
            "łańcuch wiadro": "Łańcuch jest posmarowany świeżym tłuszczem, żeby nie zjadała go wilgoć.",
            "kamień cembrowina": "Kamień na obrzeżu jest chłodny, twardy i wiecznie mokry od rozchlapywanej wody.",
        },
        items=(
            Item("wiadro studzienne", "Proste wiadro do noszenia wody.", 1.2, 3, "city_well_bucket_21", item_type="tool"),
            Item("zgubione szczypce", "Szczypce pozostawione przy studni przez roztargnienie albo pośpiech.", 1.1, 6, "smith_tongs_lost_21", item_type="tool"),
        ),
    ),
    LocationContent(
        room_id=22,
        name="Jatki Rzeźników",
        description=(
            "Jatki są niskie, czerwone od zachodu i ciemne od krwi niezmywanej do końca. "
            "Podłoga jest tu mokra od wody, tłuszczu i wszystkiego, co spływa do rynsztoka dopiero nocą."
        ),
        inspectables={
            "noze haki": "Noże wiszą równo, a haki są ciężkie od dawnej pracy.",
            "krew podłoga": "Na podłodze widać plamy po krwi, soli i tłuszczu. Nic tu nie pachnie świeżo.",
        },
    ),
    LocationContent(
        room_id=23,
        name="Targ Rybny",
        description=(
            "Ryby leżą tu na lodzie, w beczkach albo bez litości dla nosa. "
            "Handlarze ryczą ceny, rybacy przeklinają wiatr, a mewy krążą nisko nad targiem."
        ),
        inspectables={
            "sieci beczki": "Sieci schną na palach, a obok stoją beczki po śledziach i solankach.",
            "ryby lód": "Lód topnieje w szare kałuże, więc towar trzeba sprzedawać szybko.",
        },
        items=(Item("sakwa śledzi", "Mała sakwa z solonymi śledziami.", 1.6, 6, "fish_market_herring_23", item_type="food"),),
    ),
    LocationContent(
        room_id=24,
        name="Cichy Przesmyk",
        description=(
            "Przesmyk jest tak wąski, że dwie osoby muszą minąć się bokiem. Powyżej, między dachami, "
            "widać tylko cienką kreskę nieba. Z jednej strony wciskają się tu niskie, łatane domy biedoty, "
            "z drugiej - ściana cieńszego niż gdzie indziej spokoju."
        ),
        inspectables={
            "dachy niebo": "Dachy prawie się stykają. W deszczu woda musi spadać tu zwartą zasłoną.",
            "sciany ściany": "Ściany noszą ślady dłoni, sadzy i ostrzy przeciągniętych po tynku.",
            "przesmyk zaulek zaułek": "To dobre miejsce, żeby zgubić ogon. Albo przekonać się, że samemu jest się czyimś ogonem.",
            "chaty bieda": "Niskie domy stoją tu tak blisko, że sąsiedzi słyszą każdy krok i każde westchnienie.",
            "podworka podwórka": "Podwórka są ubite, błotniste i wytarte przez codzienny ruch tych, którzy nie mają gdzie pójść dalej.",
        },
        items=(Item("łatana kurtka", "Stara kurtka połatana tyle razy, że oryginalna tkanina prawie zniknęła.", 1.3, 2, "patched_coat_24"),),
    ),
)


_DISTRICT_NAMES = (
    "Targ Północny", "Kramy Płócienników", "Podcienia Kupieckie", "Zaułek za Kramami", "Chata Drwala",
    "Zagroda Koźlarza", "Kładka nad Rynsztokiem", "Schody do Cystern", "Dom Snycerza", "Stary Spichlerz",
    "Kuźnia przy Murze", "Szeroka Brukowana", "Karczma pod Żurawiem", "Tyły Karczmy", "Mała Stajnia",
    "Róg Bednarzy", "Ulica Popielarzy", "Pod Bramą Solną", "Plac Wozów", "Studnia Żołnierska",
    "Próg Lazaretu", "Izba Cyrulika", "Dziedziniec Magazynów", "Przejście pod Sklepieniem", "Warsztat Stolarski",
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

_CITY_OPENERS = (
    lambda name, a, b, detail, atmosphere: f"{a} {atmosphere} {detail}",
    lambda name, a, b, detail, atmosphere: f"{b} {atmosphere} {detail}",
    lambda name, a, b, detail, atmosphere: f"Między fasadami {name.lower()} {a[:1].lower() + a[1:]} {atmosphere.lower()} {detail.lower()}",
    lambda name, a, b, detail, atmosphere: f"Przy {name.lower()} {b[:1].lower() + b[1:]} {atmosphere.lower()} {detail.lower()}",
    lambda name, a, b, detail, atmosphere: f"W {name.lower()} {a[:1].lower() + a[1:]} i {b[:1].lower() + b[1:]} {atmosphere.lower()} {detail.lower()}",
    lambda name, a, b, detail, atmosphere: f"{detail} W takich miejscach {name.lower()} zwykle brzmi sucho, ale dziś trzyma się naturalnie.",
)

_DISTRICT_OVERRIDES: dict[int, LocationContent] = {
    2: LocationContent(
        room_id=2,
        name="Główny Plac Astergardu",
        description=(
            "Szeroki plac leży przed miejską wartownią, tam gdzie bruk jest równiejszy niż w bocznych ulicach. "
            "Na środku stoi studnia, a przy fasadach leżą skrzynie targowe; od zachodu dochodzi cięższy ruch przy ścianach wartowni."
        ),
        inspectables={
            "studnia fontanna": "Kamienna studnia ma niski cembrowinowy krąg i żelazny kubeł na łańcuchu. Woda jest zimna i lekko słona od miejskiego pyłu.",
            "ogloszenia tablica słup": "Na słupie wiszą wyblakłe ogłoszenia o targach, straży i zaginionych rzeczach. Dwa z nich są dopisane ręką pisarza, nie urzędnika.",
            "straz żołnierze ludzie": "Przy studni stoją ławy i skrzynie targowe. Straż patrzy raczej na ręce niż na twarze.",
        },
        exit_kinds={"zachod": "ulica", "wschod": "ulica", "poludnie": "drzwi"},
        exit_forms={
            "zachod": {"prep": "ku", "locative": "Placu Przed Wartownią"},
            "wschod": {"prep": "ku", "locative": "Bocznym Uliczkom Placu"},
            "poludnie": {"prep": "do", "genitive": "Domu Snycerza"},
        },
        scene_profile="square",
        items=(
            Item("ława targowa", "Niska, ciężka ława z ciemnego drewna. Służyła kupcom i czekającym klientom.", 5.0, 8, "market_bench_02", item_type="furniture"),
            Item("skrzynia targowa", "Porysowana skrzynia po solonych śledziach i płótnie.", 2.4, 4, "market_crate_02", is_container=True, capacity=18),
        ),
    ),
    12: LocationContent(
        room_id=12,
        name="Kuźnia przy Murze",
        description=(
            "Kuźnia przy Murze przylega do kamiennego muru przy ulicy, a na wschodzie zaczyna się Szeroka Brukowana. "
            "Ogień bije przez szczeliny, kurz przy wejściu czerwienieje od żaru, a każdy cios młota odbija się krótko od muru."
        ),
        inspectables={
            "kowadlo młot": "Kowadło jest spłaszczone od lat pracy. Młoty leżą obok w kolejności, którą rozumie tylko właściciel.",
            "ogien palenisko": "W palenisku tlą się jeszcze ostatnie węgle. Ktoś dorzucił świeżo rozłupaną szczapę, żeby żar nie umarł przed świtem.",
            "narzedzia szczypce": "Szczypce, pilniki i dłuta wiszą na hakach. Są używane tak często, że ich uchwyty wypolerowały się od dłoni.",
        },
        items=(
            Item("kowalski młot", "Ciężki młot o spękanym trzonku, ale nadal zdolny do pracy.", 2.1, 12, "blacksmith_hammer_12", item_type="tool"),
            Item("szczypce kowalskie", "Długie szczypce do wyciągania żelaza z ognia.", 1.0, 6, "smith_tongs_12", item_type="tool"),
            Item("pochodnia kuźnicza", "Pochodnia przesiąknięta smołą i sadzą z kuźni.", 0.5, 2, "forge_torch_12"),
        ),
        exit_kinds={"zachod": "drzwi", "wschod": "ulica", "poludniowy-zachod": "przejście"},
        exit_forms={
            "zachod": {"prep": "do", "genitive": "Starego Spichlerza"},
            "wschod": {"prep": "ku", "locative": "Szerokiej Brukowanej"},
            "poludniowy-zachod": {"prep": "do", "genitive": "Jatek Rzeźników"},
        },
        scene_profile="forge",
    ),
    14: LocationContent(
        room_id=14,
        name="Karczma pod Żurawiem",
        description=(
            "Niski dach Karczmy pod Żurawiem schodzi niemal do poziomu ganku, a od zachodu widać szerokie drzwi od Szerokiej Brukowanej. "
            "Z izby wypływa zapach piwa, pieczonego mięsa i mokrego drewna, a przy stołach słychać urywane rozmowy i brzęk kufli."
        ),
        inspectables={
            "lada karczmarz": "Lada jest gładka od łokci i kubków. Za nią wiszą haczyki na kufle, lecz połowa z nich jest pusta.",
            "kominek ogien": "Ogień w kominku daje więcej dymu niż ciepła. Drewno jest wilgotne, ale karczmarz nie zamierza oszczędzać gościom światła.",
            "lawy stol": "Ławy są ciężkie i odrapane. Na jednej ktoś wyciął znak żeglarskiego węzła, zapewne po pijaku albo z tęsknoty.",
        },
        items=(
            Item("beczka piwa", "Niska beczka z ciemnym, słabym piwem. Dla karczmy to codzienność, nie luksus.", 14.0, 10, "tavern_beer_barrel_14", is_container=True, capacity=60),
            Item("miska gulaszu", "Gliniasta miska z resztką gulaszu. Jeszcze ciepła.", 0.8, 3, "tavern_stew_bowl_14", item_type="food", is_consumable=True, effects_on_consume={"restore_stamina": 16}),
            Item("dębowa ława", "Ława, która pamięta więcej rozmów niż niejeden urzędnik.", 6.0, 9, "tavern_oak_bench_14", item_type="furniture"),
        ),
        exit_kinds={"polnoc": "drzwi", "poludnie": "drzwi", "zachod": "drzwi"},
        exit_forms={
            "polnoc": {"prep": "w stronę", "genitive": "Zaułka za Karczmą"},
            "poludnie": {"prep": "do", "genitive": "Tyłów Karczmy"},
            "zachod": {"prep": "ku", "locative": "Szerokiej Brukowanej"},
        },
        scene_profile="inn_interior",
    ),
    15: LocationContent(
        room_id=15,
        name="Tyły Karczmy",
        description=(
            "Wąskie zaplecze za kuchennym wejściem mieści puste beczki, skrzynie po warzywach i stół do czyszczenia kufli. "
            "To krótki pas desek między kuchnią a stajnią, gdzie wszystko nosi ślady tłuszczu i mokrych łap."
        ),
        inspectables={
            "ludzie przechodnie mieszkancy mieszkańcy": "Najczęściej przewijają się tu ludzie z kuchni, tragarze i ci, którzy wolą wejść od tyłu niż przez salę.",
            "beczki skrzynie": "Beczki są lekkie i suche, a skrzynie noszą ślady po mokrych warzywach i workach z solą.",
            "stol kufle": "Stół ma nacięcia po nożach i ślady po piwie wycieranym byle szmatą.",
        },
        exit_kinds={"polnoc": "drzwi", "wschod": "drzwi"},
        exit_forms={
            "polnoc": {"prep": "do", "genitive": "Karczmy pod Żurawiem"},
            "wschod": {"prep": "ku", "locative": "Małej Stajni"},
        },
        scene_profile="inn_back",
    ),
    25: LocationContent(
        room_id=25,
        name="Koszary Straży",
        description=(
            "Koszary zajmują szeroki plac przy południowym ramieniu miasta. Z otwartych drzwi dochodzą kroki, komendy i dźwięk ostrzonej stali. "
            "W powietrzu miesza się pot, smoła i wilgoć z mokrych płaszczy rozwieszonych przy wejściu."
        ),
        inspectables={
            "lozka prycze": "Prycze są ustawione równo, z zawieszonymi nad nimi tarczami i płaszczami. Każdy przedmiot ma swoje miejsce, choć nikt nie wygląda na zachwyconego porządkiem.",
            "straznicy zbroja": "Strażnicy siedzą cicho, gdy nie ma rozkazu. Ich cisza jest równie ważna jak szkolenie.",
            "stajnia konie": "Przy koszarach trzyma się kilka koni patrolowych. Zwierzęta reagują nerwowo na każdy obcy głos.",
        },
        items=(
            Item("drewniana tarcza patrolowa", "Prosta tarcza strażnicza z wybitym znakiem miasta.", 3.0, 14, "guard_shield_25", item_type="shield", slot="lewa_reka", protection=1, shield_block=2),
            Item("włócznia strażnicza", "Standardowa włócznia miejskiej straży, ciężka w środku i pewna w ręku.", 2.6, 18, "guard_spear_25", item_type="weapon", slot="prawa_reka", damage_type="kluta", base_damage=5, reach=2),
        ),
    ),
    37: LocationContent(
        room_id=37,
        name="Świątynia Popiołu",
        description=(
            "Świątynia Popiołu stoi z ciemnego kamienia między przedsionkiem a portem. "
            "Niskie filary tłumią odgłos kroków, a po progu rozciąga się wosk i chłodna woda."
        ),
        inspectables={
            "oltarz ołtarz": "Ołtarz jest prosty, z popękanym blatem i metalową misą na ofiary z oliwy i wosku.",
            "swiece wosk": "Świece palą się nierówno, ale nikt nie gasi ich przed czasem. Wosk spływa grubymi smugami po kamieniu.",
            "kaplani modlitwa": "Kapłani mówią niewiele, lecz ich obecność uspokaja tych, którzy przyszli tu zbyt późno na zwykłe słowa.",
        },
        items=(
            Item("woskowa świeca", "Gruba świeca, jeszcze nieodpalona.", 0.2, 1, "wax_candle_37"),
            Item("drewniana ławka", "Prosta ławka dla modlących się lub czekających.", 4.0, 6, "chapel_bench_37", item_type="furniture"),
            Item("wiązka ziół", "Świeżo zebrana wiązka ziół leczniczych.", 0.2, 3, "priest_herb_bundle_37"),
        ),
        exit_kinds={"polnoc": "drzwi", "zachod": "przejście"},
        exit_forms={
            "polnoc": {"prep": "do", "genitive": "Przedsionka Świątyni"},
            "zachod": {"prep": "ku", "locative": "Portowi Rzecznemu"},
        },
        scene_profile="temple_interior",
    ),
    38: LocationContent(
        room_id=38,
        name="Port Rzeczny",
        description=(
            "Nabrzeże jest krótkie, ale ruchliwe. Płaskodenne łodzie kołyszą się przy palach, a sieci schną na słupach obok beczek ze śledziami i mokrych lin. "
            "Port nie jest wielki, lecz to przez niego do Astergardu płyną ryby, sól, drewno i wieści z niższych osad."
        ),
        inspectables={
            "lodzie łodzie czolna": "Łodzie są niskie, ciężkie i zbudowane do spokojnej rzeki, nie do chwały. Na burtach widać łaty po dawnych naprawach.",
            "sieci liny": "Sieci wiszą ciężko od wilgoci. Ktoś starannie łatał je igłą i sznurkiem, by nie rozeszły się przy pierwszym rzucie.",
            "beczki ryby sol": "Beczki pachną rybą, solą i smołą. To zapach pracy, która utrzymuje miasto przy życiu.",
        },
        items=(
            Item("sieć rybacka", "Mokra sieć z ciężarkami z ołowiu.", 2.2, 9, "fishing_net_38", item_type="tool"),
            Item("beczka śledzi", "Beczka z solonymi śledziami. Ciężka, ale cenniejsza niż wygląda.", 18.0, 18, "herring_barrel_38", is_container=True, capacity=70),
            Item("skrzynia portowa", "Skrzynia po towarach rzecznych, z popękanym wiekiem.", 4.8, 7, "river_crate_38", is_container=True, capacity=30),
            Item("zwinięta sieć", "Sieć zwinięta w ciasny pakunek, odłożona przy brzegu po nocnym połowie.", 2.0, 8, "podgrodzie_fishing_net_39", item_type="tool"),
        ),
    ),
    39: LocationContent(
        room_id=39,
        name="Most Rzeczny",
        description=(
            "Most łączy oba brzegi niewielkiej rzeki, która wcina się w miasto jak cienki, żywy nóż. "
            "Deski są mokre od mgły i rzeki, a pod spodem słychać tylko szum wody, zbyt cichy, by uspokoić człowieka przyzwyczajonego do kamiennych murów. "
            "Bez niego port i targ oddzieliłaby długa droga wokół bagiennych brzegów."
        ),
        inspectables={
            "rzeka woda": "Rzeka jest wąska, lecz szybka. Niesie patyki, pianę i czasem całe gałęzie z górnego biegu.",
            "deski balustrada": "Balustrada jest nowa tylko w połowie; miejscami widać łaty po zimowych pęknięciach.",
            "prąd nurt": "Prąd poniżej mostu jest zdradliwy. Kto wpadnie do wody, ten najpierw straci buty, potem cierpliwość.",
        },
        items=(
            Item("zwój liny", "Zwój grubej liny, przydatny przy przeprawie albo cumowaniu łodzi.", 3.2, 6, "bridge_rope_39", item_type="tool"),
            Item("pochodnia mostowa", "Pochodnia osmolona od nocnych wart przy brzegu.", 0.6, 2, "bridge_torch_39"),
        ),
    ),
    47: LocationContent(
        room_id=47,
        name="Rynek Żelazny",
        description=(
            "Rynek Żelazny rozkłada się szeroko między kramami i warsztatami. "
            "Wózki z żelazem stoją obok skrzyń z tkaniną, a przekupki pilnują wag ostrzej niż własnych sakiew."
        ),
        inspectables={
            "kramy stragany": "Stragany są zasłane płótnem, skórą i odłamkami metalu. Każdy sprzedawca ma inną historię, ale te same obcasy.",
            "wagi odważniki": "Wagi są pilnowane surowiej niż uczciwość. Obok leżą odważniki z wybitymi znakami cechu.",
            "handel kupcy": "Kupcy mówią szybko, lecz milkną, gdy widzą straż. Wtedy wszyscy nagle przypominają sobie o przepisach.",
        },
        exit_kinds={"polnoc": "przejście", "zachod": "przejście", "poludniowy-wschod": "przejście"},
        exit_forms={
            "polnoc": {"prep": "do", "genitive": "Kramu Świecarza"},
            "zachod": {"prep": "do", "genitive": "Warsztatu Cieśli"},
            "poludniowy-wschod": {"prep": "do", "genitive": "Składu Drewna"},
        },
        scene_profile="market",
        items=(
            Item("odważnik targowy", "Mały odważnik z wybitym znakiem rynku.", 0.7, 5, "market_weight_47"),
            Item("skrzynka na przyprawy", "Niska skrzynka po cennych przyprawach i ziołach.", 1.5, 9, "spice_crate_47", is_container=True, capacity=12),
            Item("kosz targowy", "Kosz pełen warzyw i chleba, przygotowany do dostawy.", 2.0, 9, "market_delivery_basket_47", is_container=True, capacity=12),
        ),
    ),
    54: LocationContent(
        room_id=54,
        name="Skład Soli",
        description=(
            "Sól trzymana jest tu jak skarb, choć wygląda jak zwykły biały pył. Wewnątrz panuje chłód, a podłoga skrzypi od rozlanych kryształków i ciężkich worków. "
            "Robotnicy mówią tu półgłosem, bo nawet kichnięcie potrafi wzniecić chmurę drobnego, gryzącego pyłu."
        ),
        inspectables={
            "worki sol": "Worki są ciasno związane i oznaczone kredowym znakiem cechu. Ktoś już policzył ich zawartość.",
            "beczki skrzynie": "Beczki i skrzynie stoją pod ścianą, gotowe na transport do kuchni, portu albo fortecznych magazynów.",
            "robotnicy nosze": "Robotnicy przenoszą sól ostrożnie, jakby każdy rozsypany garść oznaczał osobistą winę.",
        },
        items=(
            Item("worek soli", "Ciężki worek z grubą, kuchenną solą.", 4.5, 7, "salt_sack_54", is_container=True, capacity=20),
            Item("drewniana beczka", "Zwykła beczka na sól lub mokre towary.", 9.0, 8, "wooden_barrel_54", is_container=True, capacity=40),
        ),
    ),
    59: LocationContent(
        room_id=59,
        name="Kapliczka Podróżnych",
        description=(
            "Kapliczka stoi przy samym wyjściu z bruku, na miejscu, gdzie miasto oddycha już drogą i wiatrem. "
            "Przywieszone do niej wstążki są wyblakłe od deszczu, a kamienna misa na ofiary pełna jest monet, guzików i małych obietnic. "
            "Ludzie zatrzymują się tu nie dlatego, że wierzą więcej, lecz dlatego, że dalej nie warto iść bez chwili ciszy."
        ),
        inspectables={
            "wstazki wstążki": "Wstążki szarzeją od deszczu. Każda ma inny wzór, jakby zostawili je podróżni z różnych krain.",
            "misa ofiary": "W misie leżą drobne monety, kawałki wosku i gładkie kamyki. To skromne ofiary, ale najczęściej szczere.",
            "droga trakt": "Stąd widać już tylko wylot drogi i koleiny prowadzące ku podmiejskim polom.",
        },
        items=(
            Item("kamienna świeczka", "Mała świeczka zostawiona przez podróżnego.", 0.1, 1, "road_candle_59"),
            Item("modlitewny sznur", "Prosty sznur z nawleczonymi paciorkami.", 0.2, 2, "prayer_beads_59"),
        ),
    ),
    61: LocationContent(
        room_id=61,
        items=(
            Item("skrzynia tragarzy", "Ciężka skrzynia po towarze, noszona tu częściej niż zamykana.", 5.0, 10, "podgrodzie_porters_crate_61", is_container=True, capacity=24),
            Item("worek owsa", "Worek z owsem dla koni i wołów.", 6.0, 8, "podgrodzie_oatsack_61", is_container=True, capacity=20),
        ),
    ),
    62: LocationContent(
        room_id=62,
        items=(
            Item("ława karczemna", "Twarda ława ustawiona pod ścianą zajazdu.", 6.0, 7, "podgrodzie_tavern_bench_62", item_type="furniture"),
            Item("ognisko kuchenne", "Zacienione palenisko rozgrzane przez ciągłe gotowanie.", 12.0, 4, "podgrodzie_tavern_fire_62", item_type="furniture"),
        ),
    ),
    63: LocationContent(
        room_id=63,
        items=(
            Item("stragan płócienny", "Prosty stragan z płóciennym daszkiem, wystawiany na targ w kilka chwil.", 8.0, 9, "podgrodzie_canvas_stall_63", item_type="furniture"),
            Item("worek zboża", "Worek z ziarnem, ciężki i dobrze zawiązany.", 7.5, 11, "podgrodzie_grain_sack_63", is_container=True, capacity=24),
        ),
    ),
    64: LocationContent(
        room_id=64,
        items=(
            Item("drewno opałowe", "Porąbane drewno czekające na palenisko albo piec.", 14.0, 6, "podgrodzie_firewood_64"),
            Item("narzędzia kowalskie", "Zestaw szczypiec, pilników i młotków odłożonych po robocie.", 3.0, 12, "podgrodzie_smith_tools_64", item_type="tool"),
        ),
    ),
    65: LocationContent(
        room_id=65,
        items=(
            Item("płot żerdziowy", "Niska bariera z żerdzi, łatana i wielokrotnie poprawiana.", 22.0, 5, "podgrodzie_fence_65", item_type="furniture"),
        ),
    ),
    66: LocationContent(
        room_id=66,
        items=(
            Item("stajnia podwórzowa", "Niewielka stajnia przytwierdzona do skraju zabudowań.", 60.0, 18, "podgrodzie_stable_66", item_type="furniture"),
            Item("żłób", "Kamienny żłób z resztką siana.", 18.0, 6, "podgrodzie_trough_66", item_type="furniture"),
        ),
    ),
    67: LocationContent(
        room_id=67,
        items=(
            Item("beczka wody", "Beczka z wodą dla ludzi i zwierząt pociągowych.", 22.0, 8, "podgrodzie_water_barrel_67", is_container=True, capacity=55),
            Item("kamienne ognisko", "Proste ognisko otoczone polnymi kamieniami.", 10.0, 4, "podgrodzie_campfire_67", item_type="furniture"),
        ),
    ),
    68: LocationContent(
        room_id=68,
        items=(
            Item("stragan targowy", "Stragan ustawiany przy każdym większym ruchu ludzi.", 10.0, 10, "podgrodzie_market_stall_68", item_type="furniture"),
            Item("skrzynia kupiecka", "Skrzynia z grubego drewna, na monety i drobny towar.", 4.5, 12, "podgrodzie_merchant_crate_68", is_container=True, capacity=30),
        ),
    ),
    69: LocationContent(
        room_id=69,
        items=(
            Item("studnia przedmiejska", "Studnia z drewnianą cembrowiną, oblepiona błotem i kredą.", 35.0, 14, "podgrodzie_well_69", item_type="furniture"),
            Item("wiadro studzienne", "Wiadro do wody, zbyt ciężkie jak na swój wygląd.", 1.0, 3, "podgrodzie_bucket_69", item_type="tool"),
        ),
    ),
    70: LocationContent(
        room_id=70,
        name="Droga do Pól",
        description=(
            "Droga odchodzi od miasta szerokim łukiem, wyprowadzając wozy ku otwartym polom i gospodarstwom. "
            "Po bokach ciągną się rowy, niskie płoty i resztki ubitej ziemi, na której jeszcze wczoraj suszyły się snopy. "
            "Kto zna tę okolicę, wie, że to nie jest zwykły trakt - to codzienna obietnica chleba dla Astergardu."
        ),
        inspectables={
            "pola zagony": "Zagony zaczynają się kilka minut marszu dalej. Ziemia jest ciężka, ale uporządkowana z uporem ludzi, którzy nie znają litości wobec pogody.",
            "rowy ploty płoty": "Rowy są czyszczone regularnie, żeby wiosenne wody nie zjadły drogi przed żniwami.",
            "wozy snopy": "Ślady wozów i rozsypane źdźbła pokazują, że droga żyje tu od świtu do zmierzchu.",
        },
        items=(
            Item("kij mierniczy", "Prosty kij do odmierzania pola i płotu.", 0.8, 2, "measuring_staff_70", item_type="tool"),
            Item("wóz dostawczy", "Wóz z szeroką plandeką, zostawiony tu na chwilę albo na zbyt długo.", 50.0, 22, "podgrodzie_delivery_cart_70", item_type="furniture"),
        ),
    ),
    71: LocationContent(
        room_id=71,
        items=(
            Item("narzędzia garncarskie", "Miski, szpatułki i noże do gliny ustawione na jednym stole.", 2.0, 7, "podgrodzie_potter_tools_71", item_type="tool"),
            Item("bryła gliny", "Wilgotna bryła gliny gotowa do lepienia naczyń.", 4.0, 4, "podgrodzie_clay_71"),
        ),
    ),
    72: LocationContent(
        room_id=72,
        items=(
            Item("gęsi gospodarskie", "Kilka gęsi kręci się przy zagrodzie i syczy na obcych.", 35.0, 20, "podgrodzie_geese_72", item_type="misc"),
            Item("koryto karmowe", "Proste koryto na paszę i wodę.", 12.0, 5, "podgrodzie_feed_trough_72", item_type="furniture"),
        ),
    ),
    73: LocationContent(
        room_id=73,
        items=(
            Item("worek zboża", "Worek pełen ziarna, ciężki i dobrze zawiązany.", 7.0, 10, "podgrodzie_grain_sack_73", is_container=True, capacity=24),
            Item("ławka z desek", "Deski zbite w prostą ławę dla ludzi czekających na transport.", 5.5, 4, "podgrodzie_plank_bench_73", item_type="furniture"),
        ),
    ),
    74: LocationContent(
        room_id=74,
        items=(
            Item("woz podróżny", "Mały wóz podróżny z poobijaną plandeką.", 44.0, 18, "podgrodzie_travel_cart_74", item_type="furniture"),
            Item("płot drogowy", "Niski płot z żerdzi, ustawiony po to, by pilnować przejazdu.", 16.0, 6, "podgrodzie_road_fence_74", item_type="furniture"),
        ),
    ),
    75: LocationContent(
        room_id=75,
        items=(
            Item("ognisko podróżnych", "Kiedyś rozpalone ognisko, dziś tylko kamienny ślad i garść popiołu.", 9.0, 3, "podgrodzie_road_fire_75", item_type="furniture"),
            Item("ława przydrożna", "Krótka ława do odpoczynku przed dalszą drogą.", 4.5, 3, "podgrodzie_road_bench_75", item_type="furniture"),
            Item("zwinięta sieć", "Sieć zwinięta w ciasny pakunek, odłożona przy drodze po nocnym połowie.", 2.0, 8, "podgrodzie_fishing_net_75", item_type="tool"),
        ),
    ),
    76: LocationContent(
        room_id=76,
        items=(
            Item("stragan z warzywami", "Stragan z cebulą, marchewką i suchym szczypiorem.", 7.0, 7, "podgrodzie_veg_stall_76", item_type="furniture"),
            Item("skrzynka kupiecka", "Mała skrzynka do codziennego handlu.", 3.2, 5, "podgrodzie_trade_crate_76", is_container=True, capacity=15),
        ),
    ),
    77: LocationContent(
        room_id=77,
        items=(
            Item("drewno opałowe", "Porąbane drewno ułożone przy ogrodzeniu.", 12.0, 5, "podgrodzie_firewood_77"),
            Item("motyka polna", "Motyka do drobnych robót przy polu i płocie.", 1.3, 4, "podgrodzie_hoe_77", item_type="tool"),
        ),
    ),
    78: LocationContent(
        room_id=78,
        items=(
            Item("stajnia polna", "Prosta stajnia przy skraju pastwiska.", 58.0, 16, "podgrodzie_field_stable_78", item_type="furniture"),
            Item("koń pociągowy", "Spokojny koń przyzwyczajony do ciężkich wozów.", 380.0, 40, "podgrodzie_cart_horse_78", item_type="misc"),
        ),
    ),
    79: LocationContent(
        room_id=79,
        items=(
            Item("obora", "Niska obora z ciemnymi deskami i zapachem siana.", 46.0, 14, "podgrodzie_barn_79", item_type="furniture"),
            Item("krowa gospodarska", "Spokojna krowa skubiąca resztki siana przy ścianie.", 420.0, 45, "podgrodzie_cow_79", item_type="misc"),
        ),
    ),
    80: LocationContent(
        room_id=80,
        name="Droga do Haldun",
        description=(
            "Wieś Haldun leży dalej od murów, ale wciąż w zasięgu miejskich wozów i pogłosek. "
            "Droga tuje się między polami, kępami wierzb i zagrodami, które pamiętają więcej zim niż ludzi. "
            "Kto idzie tędy po zmroku, ten słyszy już nie miasto, lecz pracę ziemi."
        ),
        inspectables={
            "chlopi gospodarze": "Gospodarze z Haldun patrzą na obcych jak na możliwy kłopot, który trzeba policzyć, zanim zacznie mówić.",
            "pola zboze zboże": "Pola są równe i wydeptywane codziennie. Żyto i jęczmień trzymają się tu uparcie mimo wiatru.",
            "droga trakty": "Droga jest szeroka na dwa wozy i jedną złą decyzję. Dalej robi się bardziej wiejsko niż bezpiecznie.",
        },
        items=(Item("snop jęczmienia", "Mocno związany snop zboża.", 2.2, 4, "barley_sheaf_80", item_type="food"),),
    ),
    84: LocationContent(
        room_id=84,
        name="Pola Jęczmienia",
        description=(
            "Tutaj ziemia jest tak dobrze obrabiana, jakby każdy skrawek miał własne nazwisko. "
            "Żółte łany falują nisko, a wiatr niesie z nich suchy pył i zapach słomy. "
            "Przy drodze stoją narzędzia, wiadra i gnijące snopy, bo nikt nie ma czasu na porządek, gdy nadchodzi zbiory."
        ),
        inspectables={
            "zboze łany": "Łany są niskie i gęste. Przetrwały wiosenny deszcz, ale jeszcze nie przetrwały ludzi z sierpami.",
            "narzedzia sierpy widły": "Narzędzia leżą byle gdzie, lecz każdy rolnik umiałby wskazać swoje bez chwili wahania.",
            "wiatr pył": "Pył z pól osiada na ubraniu i zostaje tam do wieczora. To znak, że pracowano bez przerwy.",
        },
        items=(
            Item("sierp zbożowy", "Lekki sierp do żniw. Ostrze jest ostre, ale rękojeść wyślizgana.", 0.9, 6, "harvest_sickle_84", item_type="tool", slot="prawa_reka"),
            Item("worek ziarna", "Worek pełen ziarna, ciężki i dobrze zawiązany.", 6.5, 12, "grain_sack_84", is_container=True, capacity=25),
        ),
    ),
    95: LocationContent(
        room_id=95,
        name="Wschodnia Furta Łowców",
        description=(
            "Furtę otwiera się rzadko, bo za nią zaczyna się świat mokrego drewna, sideł i cichego tropienia. "
            "Osada myśliwych jest mała, ale twarda; jej mieszkańcy wiedzą, kiedy wrócić z lasu i kiedy nie wracać wcale. "
            "Dym z ich palenisk ma zapach skóry, tłuszczu i żywicy."
        ),
        inspectables={
            "lowcy myśliwi": "Łowcy noszą noże przy pasie i nie lubią pustych rozmów. Zaczynają od obserwacji, a pytania zostawiają na koniec.",
            "futa palisada": "Furta jest praktyczna, nie ozdobna. Wystarczy do przepuszczenia ludzi, psów i upolowanej zwierzyny.",
            "dym paleniska": "Dym z osady jest ciężki i lepki. To znak suszonych skór i mięsa, które ma przetrwać zimę.",
        },
        items=(Item("wiązka sideł", "Zbiór sideł z powrozem i pętlami.", 1.0, 7, "hunter_traps_95", item_type="tool"),),
    ),
    100: LocationContent(
        room_id=100,
        name="Plac Tropicieli",
        description=(
            "Plac jest tylko ubitym skrawkiem ziemi między szałasami, ale tutaj ważą się ważniejsze rzeczy niż w niejednym urzędzie. "
            "Na belkach wiszą skóry i świeżo zdjęte trofea. Mężczyźni i kobiety z osady liczą tutaj zdobycz, dzielą się mięsem i kłócą o ślady."
        ),
        inspectables={
            "skory futra": "Skóry wiszą gęsto, suszone przy dymie. Niektóre są przeznaczone na handel, inne na własne buty i rękawice.",
            "futra skory": "Skóry są proste, lecz dobrze dopasowane do zimnego lasu. Każdy detal ma tu własny powód.",
            "tropy slady": "W glinie placu widać ślady psów, łasic i ludzi wracających z lasu późnym wieczorem.",
        },
        items=(
        ),
    ),
    110: LocationContent(
        room_id=110,
        name="Brama Dungrim",
        description=(
            "Forteca Dungrim stoi na drodze jak zaciśnięta pięść. Brama jest wąska, wzmocniona żelazem i patrzona przez ludzi, którzy nie zadają pytań dwa razy. "
            "Przy przejeździe stoją beczki, skrzynie i tablice z rozkazami, a nad bramą wiszą ciężkie łańcuchy."
        ),
        inspectables={
            "brama trakt": "Brama została zaprojektowana tak, by zatrzymać wóz, znużyć konia i rozgniewać kupca.",
            "zolnierze żołnierze": "Żołnierze w Dungrim nie wyglądają na paradnych. Ich zadaniem jest trwać i liczyć zapasy.",
            "kamien mur": "Kamień jest tu ciemny od deszczu i smoły, a mur ma więcej łat niż świętości.",
        },
        items=(Item("strażnicza włócznia", "Włócznia fortecznej straży, prosta i dobrze utrzymana.", 2.7, 20, "dungrim_spear_110", item_type="weapon", slot="prawa_reka", damage_type="kluta", base_damage=5, reach=2),),
    ),
    113: LocationContent(
        room_id=113,
        name="Studnia Forteczna",
        description=(
            "Studnia przy garnizonie jest tak głęboka, że jej echo wraca po chwili dłuższej niż rozmowa. "
            "Woda ma smak kamienia i żelaza, a wartownicy traktują ją niemal jak część załogi. "
            "Nad kamienną cembrowiną zwiesza się wiadro, którego nikt nie zostawia bez nadzoru."
        ),
        inspectables={
            "studnia woda": "Woda jest zimna, czysta i ciężka od minerałów. Wystarczy do picia, ale nie do przyjemności.",
            "wiadro lancuch łańcuch": "Łańcuch jest nowy, bo stary pękł tej zimy. W Dungrim rzeczy zużywają się szybciej niż ludzie mówią o tym głośno.",
            "straz garnizon": "Strażnicy są tu bardziej zmęczeni niż dumni. To wystarcza, by byli skuteczni.",
        },
        items=(Item("wiadro forteczne", "Mocne wiadro z metalowym obrzeżem.", 1.6, 4, "fortress_bucket_113", item_type="tool"),),
    ),
}

_DISTRICT_OVERRIDES.update(
    {
        3: LocationContent(
            room_id=3,
            name="Boczne Uliczki Placu",
            description=(
                "Boczne przejścia odchodzą od rynku jak ciemne żyły w kamieniu. "
                "Między fasadami jest tu ciszej, ale też mniej pewnie, bo każde okno widzi trochę za dużo."
            ),
            inspectables={
                "okna okiennice": "Okiennice uchylają się tylko na moment. Mieszkańcy placu wolą widzieć mniej, niż by chcieli inni.",
                "rynsztok": "Rynsztok zbiera wodę, pył i drobne resztki z targu.",
            },
        ),
        4: LocationContent(
            room_id=4,
            name="Podcienia Kupieckie",
            description=(
                "Podcienia Kupieckie ściskają przejście między fasadami, a niskie sklepienia trzymają kurz tuż nad brukiem. "
                "Okiennice są przymknięte, pod progami leży błoto znad drogi, a światło wpada tu tylko wąskim pasem."
            ),
            inspectables={
                "okna okiennice": "Okiennice stoją uchylone tylko na szerokość dłoni. Kupcy wolą widzieć kawałek ulicy niż całe zamieszanie.",
                "drzwi prog próg": "Próg jest przetarty od towarów i butów, a drzwi noszą świeże rysy po hakach.",
                "fasady podcienia": "Fasady są blisko siebie, dlatego słońce wpada tu tylko na chwilę i wąskim pasem.",
            },
            exit_kinds={"zachod": "przejście", "poludniowy-wschod": "przejście", "poludniowy-zachod": "przejście"},
            exit_forms={
                "zachod": {"prep": "ku", "locative": "Bocznym Uliczkom Placu"},
                "poludniowy-wschod": {"prep": "w stronę", "genitive": "Zaułka za Karczmą"},
                "poludniowy-zachod": {"prep": "ku", "locative": "Szerokiej Brukowanej"},
            },
            scene_profile="passage",
        ),
        5: LocationContent(
            room_id=5,
            name="Zaułek za Karczmą",
            description=(
                "Za karczmą zostają popiół, resztki jedzenia i ludzie, którzy nie chcą być pytani o imię. "
                "W nocy czuć tu tłuszcz, mokre drewno i stary dym z kuchennego pieca."
            ),
            inspectables={
                "popiół": "Popiół miesza się z błotem i tworzy ciemną skorupę pod butami.",
                "kufle beczki": "Puste kufle i beczki stoją tu do rana, jeśli wcześniej nie znikną w czyjejś ręce.",
            },
            items=(Item("tłusty fartuch", "Stary fartuch kuchenny z plamami po piwie.", 0.6, 2, "tavern_apron_05"),),
        ),
        13: LocationContent(
            room_id=13,
            name="Szeroka Brukowana",
            description=(
                "Szeroka Brukowana biegnie między karczmą a kuźnią, a jej kamienie tworzą długi, wyślizgany pas. "
                "Przy ścianach stoją suche beczki, a bruk nosi ślad wozów, butów i zsuwanych skrzyń."
            ),
            inspectables={
                "slady ślady tropy": "Ślady kół i butów nakładają się tu na siebie tak gęsto, że dawna nawierzchnia prawie znika.",
                "sciana ściana mur": "Ściany są starta od łokci i sakw, a mur od północy łapie ciepło szybciej niż reszta ulicy.",
                "beczki": "Beczki stoją przy murze, suche i lekkie, gotowe wrócić do karczmy albo do piwnic kupców.",
            },
            exit_kinds={"zachod": "drzwi", "wschod": "drzwi", "polnocny-wschod": "przejście"},
            exit_forms={
                "zachod": {"prep": "do", "genitive": "Kuźni przy Murze"},
                "wschod": {"prep": "do", "genitive": "Karczmy pod Żurawiem"},
                "polnocny-wschod": {"prep": "ku", "locative": "Podcieniom Kupieckim"},
            },
            scene_profile="street",
        ),
        21: LocationContent(
            room_id=21,
            name="Studnia Miejska",
            description=(
                "Studnia stoi między domami jak obowiązek, z którym nikt nie dyskutuje. "
                "Przychodzą tu wszyscy, od straży po dzieci, a kamień wokół cembrowiny jest wyślizgany do połysku."
            ),
            inspectables={
                "łańcuch wiadro": "Łańcuch jest posmarowany świeżym tłuszczem, żeby nie zjadała go wilgoć.",
                "kamień cembrowina": "Kamień na obrzeżu jest chłodny, twardy i wiecznie mokry od rozchlapywanej wody.",
            },
            items=(Item("wiadro studzienne", "Proste wiadro do noszenia wody.", 1.2, 3, "city_well_bucket_21", item_type="tool"),),
        ),
        22: LocationContent(
            room_id=22,
            name="Jatki Rzeźników",
            description=(
                "Jatki są niskie, czerwone od zachodu i ciemne od krwi niezmywanej do końca. "
                "Podłoga jest tu mokra od wody, tłuszczu i wszystkiego, co spływa do rynsztoka dopiero nocą."
            ),
            inspectables={
                "noze haki": "Noże wiszą równo, a haki są ciężkie od dawnej pracy.",
                "krew podłoga": "Na podłodze widać plamy po krwi, soli i tłuszczu. Nic tu nie pachnie świeżo.",
            },
        ),
        23: LocationContent(
            room_id=23,
            name="Targ Rybny",
            description=(
                "Ryby leżą tu na lodzie, w beczkach albo bez litości dla nosa. "
                "Handlarze ryczą ceny, rybacy przeklinają wiatr, a mewy krążą nisko nad targiem."
            ),
            inspectables={
                "sieci beczki": "Sieci schną na palach, a obok stoją beczki po śledziach i solankach.",
                "ryby lód": "Lód topnieje w szare kałuże, więc towar trzeba sprzedawać szybko.",
            },
            items=(Item("sakwa śledzi", "Mała sakwa z solonymi śledziami.", 1.6, 6, "fish_market_herring_23", item_type="food"),),
        ),
        25: LocationContent(
            room_id=25,
            name="Dziedziniec Straży",
            description=(
                "Na dziedzińcu straży stoi stojak na tarcze, kilka żłobów i błoto, które nigdy do końca nie schnie. "
                "To stąd wychodzą patrole, zanim miasto zacznie udawać poranek."
            ),
            inspectables={
                "tarcze": "Tarcze stoją równo, ale każda ma inne rysy po nocnych interwencjach.",
                "żołnierze": "Strażnicy wolą zimną herbatę od bohaterskich historii i zwykle mają rację.",
            },
        ),
        35: LocationContent(
            room_id=35,
            name="Ogród Ziół Kapłanów",
            description=(
                "Za niskim murem kapłani trzymają grządki z gorzkimi ziołami i roślinami na napary. "
                "Zapach jest czysty tylko przez chwilę, po czym miesza się z wilgocią i dymem z miasta."
            ),
            inspectables={
                "grządki zioła": "Rośliny rosną w równych rzędach, jakby nawet leczenie wymagało porządku.",
                "mur": "Mur ogrodu jest niski, ale wystarcza, by oddzielić ciszę od ulicy.",
            },
            items=(Item("wiązka ziół", "Garść świeżo zebranych ziół leczniczych.", 0.2, 3, "priest_herb_bundle_35"),),
        ),
        36: LocationContent(
            room_id=36,
            name="Przedsionek Świątyni",
            description=(
                "Przedsionek oddziela uliczny chłód od ciszy świątyni. "
                "Kamienna posadzka jest tu wygładzona przez mokre buty, a świeczniki noszą ślady sadzy i wosku."
            ),
            inspectables={
                "posadzka": "W kamieniu widać małe pęknięcia, naprawiane więcej niż raz.",
                "świeczniki": "Świeczniki są ciężkie i ciemne od sadzy.",
            },
        ),
        41: LocationContent(
            room_id=41,
            name="Pomosty",
            description=(
                "Pomosty wychodzą nad wodę jak dłonie ludzi, którzy chcą jeszcze coś przytrzymać. "
                "Deski są mokre, śliskie i łatane, ale wciąż wytrzymują beczki, sieci i ludzi."
            ),
            inspectables={
                "deski liny": "Deski są czarne od wilgoci, a liny pachną smołą.",
                "woda": "Woda pod pomostami płynie szybko i niesie śmieci z targu.",
            },
            items=(Item("zwój liny", "Gruba lina do cumowania łodzi.", 2.8, 4, "river_dock_rope_41", item_type="tool"),),
        ),
        42: LocationContent(
            room_id=42,
            name="Przystań Rybacka",
            description=(
                "Przystań rybacka żyje od pierwszego wyładowanego kosza do ostatniej beczki ze śledziami. "
                "W powietrzu czuć rzekę, sól i stary muł."
            ),
            inspectables={
                "lodzie łodzie sieci": "Łodzie są płaskie i mocno obite od brzegu. Sieci schną na palach, a w oczkach widać resztki glonów.",
                "rybacy": "Rybacy mówią krótko, bo mają ręce zajęte pracą.",
            },
        ),
        43: LocationContent(
            room_id=43,
            name="Dom Celników",
            description=(
                "Dom celników stoi przy drodze do mostu i obserwuje każdy wóz tak, jakby każda paczka była podejrzana. "
                "Wnętrze jest skromne, ale pełne list, stempli i pytań o to, co ktoś wiezie."
            ),
            inspectables={
                "stemple listy": "Papier waży tu więcej niż broń.",
                "atrament": "Atrament jest tani, ale używany oszczędnie.",
            },
            items=(Item("stempel celny", "Drewniany stempel z wypalonym znakiem urzędu.", 0.5, 4, "customs_stamp_43"),),
        ),
        44: LocationContent(
            room_id=44,
            name="Magazyn Soli",
            description=(
                "Sól trzyma się tu jak zapas na zimę i wojnę. "
                "W środku jest chłodno, a podłoga skrzypi od ciężkich worków i białego pyłu."
            ),
            inspectables={
                "worki pył": "Worki są ciasno związane i oznaczone kredą.",
                "regały": "Regały trzymają wilgoć, ale nadal wytrzymują ciężar zapasów.",
            },
            items=(Item("worek soli", "Gruby worek z solą kuchenną.", 4.8, 6, "salt_sack_44", is_container=True, capacity=20),),
        ),
        45: LocationContent(
            room_id=45,
            name="Szopa Sieciarzy",
            description=(
                "Szopa sieciarzy jest niska i ciasna, pełna sznurków, haków i mokrego lnu. "
                "Tu łata się dziurawe sieci i przeklina ryby, które uciekły poprzedniej nocy."
            ),
            inspectables={
                "igły sznurek": "Igły do sieci leżą w misce obok ciężkich sznurków.",
                "lny": "Lniane płachty schną na belkach, pachnąc smołą i wodą.",
            },
        ),
        48: LocationContent(
            room_id=48,
            name="Warsztat Cieśli",
            description=(
                "Warsztat cieśli pełen jest wiórów, belek i niedokończonych ram. "
                "Drzewo leży tu w kawałkach, ale każdy element ma swój przyszły sens."
            ),
            inspectables={
                "wióry belki": "Wióry zbierają się w suchych stosach, a belki są oznaczone kredą.",
                "narzędzia": "Narzędzia wiszą na hakach w kolejności znanej tylko właścicielowi.",
            },
        ),
        49: LocationContent(
            room_id=49,
            name="Garbarnia",
            description=(
                "Garbarnia pachnie tak, że człowiek wie od razu, po co tu przyszedł i jak bardzo chciałby już wyjść. "
                "Skóry wiszą na ramach, a podłoga jest wiecznie mokra od pracy i odpływu."
            ),
            inspectables={
                "skóry": "Skóry są rozciągnięte na ramach i pracuje się nad nimi powoli.",
                "baryłki": "Baryłki z garbnikiem stoją pod ścianą.",
            },
        ),
        50: LocationContent(
            room_id=50,
            name="Warsztat Stolarski",
            description=(
                "Warsztat stolarski jest pełen giętkiego drewna, kleju i cierpliwości. "
                "Na ścianach wiszą półgotowe deski, a na stole leżą narzędzia bez ostrych deklaracji."
            ),
            inspectables={
                "deski": "Deski wiszą na hakach, od jasnych po ciemne.",
                "klej": "Klej pachnie żywicą i gotowanym kościem.",
            },
        ),
        51: LocationContent(
            room_id=51,
            name="Warsztat Płatnerza",
            description=(
                "Płatnerz pracuje w rytmie młotka, skrobaka i oddechu, bo przy zbroi najmniejszy błąd kosztuje skórę. "
                "Stoją tu połamane hełmy, napierśniki z wgnieceniami i tarcze, które wróciły z bitwy bardziej zniszczone niż właściciele."
            ),
            inspectables={
                "hełmy napierśniki": "Napierśniki wiszą na hakach, częściowo naprawione, częściowo czekające na lepszy dzień.",
                "młot": "Młot leży obok kowadła i ma ciężar, który budzi respekt.",
            },
        ),
        52: LocationContent(
            room_id=52,
            name="Skład Drewna",
            description=(
                "Skład drewna to plac pełen belek, szczap i mokrych stosów, które mają dopiero trafić do pieców, warsztatów albo na łodzie. "
                "W powietrzu czuć żywicę i wilgoć."
            ),
            inspectables={
                "belki szczapy": "Belki są spięte sznurami i oznaczone kredą.",
                "wióry": "Wióry łatwo chwytają ogień, więc nikt nie zostawia tu lamp bez nadzoru.",
            },
            items=(Item("wiązka drewna", "Mała wiązka suchych szczap.", 1.5, 2, "wood_bundle_52"),),
        ),
        53: LocationContent(
            room_id=53,
            name="Palenisko Węglarskie",
            description=(
                "Palenisko węglarskie to czarna, dymiąca dziura w tkance miasta, potrzebna bardziej niż ładna. "
                "Pnie tlą się tu długo, a ludzie pracują w sadzy i półmroku."
            ),
            inspectables={
                "dym sadza": "Dym jest ciężki i tłusty.",
                "węgiel": "Węgiel leży w pryzmach, jeszcze ciepły w środku.",
            },
        ),
        54: LocationContent(
            room_id=54,
            name="Zaułek Czeladników",
            description=(
                "Czeladnicy mieszkają i pracują w zaułku, który nocą brzmi jak zbiór cichych sporów o narzędzia i honor. "
                "Pod ścianami stoją skrzynki, zwoje sznurów i łaty materiału."
            ),
            inspectables={
                "skrzynki": "Skrzynki stoją jedna na drugiej i każda ma swój zbyt mały porządek.",
                "wióry pył": "Wióry i pył tworzą cienką warstwę na bruku.",
            },
        ),
    55: LocationContent(
        room_id=55,
        name="Rozstaje Traktów",
        description=(
            "Na skraju miasta bruk przechodzi w koleiny, a rozstaje zbierają ruch z furty łowców, kapliczki i opuszczonej chaty. "
            "Kamień graniczny ma odłupany róg i biały ślad po kredzie, a słup drogowy wskazuje skręt ku kapliczce i furtce łowców."
        ),
            inspectables={
                "drogi koleiny": "Koleiny rozchodzą się w kilka stron. Najgłębsza jest ta, którą jadą cięższe wozy z zaopatrzeniem.",
                "kamień graniczny": "Kamień graniczny ma odłupany róg i ślad kredy, którym ktoś zaznaczył ostatni objazd.",
                "słup drogowy": "Słup drogowy stoi krzywo, ale wciąż pokazuje drogę ku kapliczce i furtce łowców.",
            },
            exit_kinds={"polnoc": "ulica", "zachod": "trakt", "poludniowy-wschod": "trakt", "wschod": "furta"},
            exit_forms={
                "polnoc": {"prep": "do", "genitive": "Zaułka Czeladników"},
                "zachod": {"prep": "do", "genitive": "Opuszczonej Chaty"},
                "poludniowy-wschod": {"prep": "do", "genitive": "Kapliczki Przydrożnej"},
                "wschod": {"prep": "do", "genitive": "Wschodniej Furty Łowców"},
            },
            scene_profile="crossroads",
        ),
        56: LocationContent(
            room_id=56,
            name="Opuszczona Chata",
            description=(
                "Chata stoi krzywo, ale jeszcze nie upadła, jakby sama nie była pewna, czy zasługuje na zapomnienie. "
                "W środku zalega kurz, stara słoma i kilka śladów po tym, że ktoś kiedyś jednak tu mieszkał."
            ),
            inspectables={
                "słoma kurz": "Słoma jest zbita i zbutwiała.",
                "palenisko": "Palenisko dawno wygasło. Został tylko ciemny krąg i kilka zwęglonych szczap.",
            },
        ),
        57: LocationContent(
            room_id=57,
            name="Gospodarstwo na Skraju",
            description=(
                "Gospodarstwo leży już prawie poza miastem, tam gdzie pole zaczyna wygrywać z brukiem. "
                "Dom, stodoła i mały ogród trzymają się razem przeciwko wiatrowi i podatkom."
            ),
            inspectables={
                "stodoła ogród": "Stodoła ma świeże łaty, a ogród jest mały, lecz uporządkowany.",
                "płoty": "Płoty naprawiono na szybko, bo wiatry nie czekają na sezon po świętach.",
            },
        ),
        58: LocationContent(
            room_id=58,
            name="Pastwiska",
            description=(
                "Pastwiska rozciągają się szeroko, płaskie i wietrzne, z niską trawą i wydeptanymi ścieżkami zwierząt. "
                "To przestrzeń, która wygląda spokojnie tylko z daleka."
            ),
            inspectables={
                "trawa": "Trawa jest niska, szorstka i miejscami już wyjedzona do ziemi.",
                "ślady": "Ślady kopyt nakładają się na siebie warstwami.",
            },
        ),
        59: LocationContent(
            room_id=59,
            name="Kapliczka Przydrożna",
            description=(
                "Kamienna kapliczka stoi przy samym wylocie bruku, tam gdzie ostatni kamień przechodzi w koleiny traktu. "
                "W niszy leżą wstążki, moneta i kawałek chleba, a wiatr łatwo obchodzi niską ścianę."
            ),
            inspectables={
                "wstążki monety": "Wstążki są wyblakłe, monety ciemne od deszczu.",
                "nisza": "Nisza w kamieniu jest płytka, ale wystarcza, by osłonić ofiarę od wiatru.",
                "próg bruku": "Próg kapliczki jest wyślizgany od butów i usiany drobnym piaskiem znoszonym z drogi.",
            },
            exit_kinds={"zachod": "trakt", "polnocny-zachod": "trakt", "poludniowy-wschod": "trakt"},
            exit_forms={
                "zachod": {"prep": "do", "genitive": "Pastwisk"},
                "polnocny-zachod": {"prep": "do", "genitive": "Rozstajów Traktów"},
                "poludniowy-wschod": {"prep": "ku", "locative": "Kapliczce Podróżnych za Murem"},
            },
            scene_profile="roadside_chapel",
        ),
    }
)


def _district_content(room_id: int, index: int, name: str) -> LocationContent:
    override = _DISTRICT_OVERRIDES.get(room_id)
    if override is not None:
        return override
    feature_a = _FEATURES[index % len(_FEATURES)]
    feature_b = _FEATURES[(index + 3) % len(_FEATURES)]
    opener = _CITY_OPENERS[index % len(_CITY_OPENERS)](name, feature_a[1], feature_b[1], _DETAILS[index % len(_DETAILS)], _ATMOSPHERE[index % len(_ATMOSPHERE)])
    description = opener[0].upper() + opener[1:] if opener else name
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
            "Stojaki na Drzewce", "Garaż dla Sań", "Rów na Odpadki", "Leśna Kapliczka", "Polana Psów",
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
            "Stajnie Patroli", "Skład Zaopatrzenia", "Zbrojownia Dungrim", "Wieża Sygnałowa", "Mur Nad Traktem",
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
        "Przedpola Astergardu",
        "boczny trakt",
        ("sciezka ścieżka dukt droga", "Ścieżka jest wąska i kapryśna; miejscami znika pod trawą, żeby wrócić kilka kroków dalej."),
        ("krzaki leszczyny korzenie", "Krzaki łapią za nogawki, a korzenie wystają z ziemi jak stare, zaciśnięte palce."),
        ("slady ślady oboz tropy", "Ślady są nieliczne, ale świeże. Ktoś używa tej drogi właśnie dlatego, że nie wygląda na używaną."),
    ),
}

_D351B_ATMOSPHERE = (
    "Przy bramach stoją beczki, skrzynie i płoty naprawiane po zimie.",
    "Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.",
    "Towary, głosy i biegnące dzieci mijają się tu bez chwili przerwy.",
    "Od bram miasta dalej słychać stuk kół, nawoływania i psy przy płotach.",
    "Skróty znają głównie ci, którzy codziennie mijają ten sam kamień milowy.",
)

_TRACT_ITEM_MAP: dict[int, tuple[Item, ...]] = {
    135: (
        Item("zwój mapy traktu", "Mapa z zaznaczonymi kamieniami milowymi i skrótami.", 0.2, 8, "trakty_route_map_135", "tool"),
        Item("olej do lamp", "Butelka oleju na wieczorne czuwanie.", 0.4, 3, "trakty_lamp_oil_135", "tool"),
    ),
    136: (
        Item("koc podróżny", "Gruby koc na zimny postój przy kapliczce.", 1.8, 5, "trakty_travel_blanket_136", "tool"),
    ),
    138: (
        Item("list przewozowy", "Papier z opisem karawany i ładunku.", 0.1, 4, "trakty_manifest_138", "tool"),
    ),
    140: (
        Item("zapieczętowany list", "Krótkie pismo owinięte woskowym sznurkiem.", 0.1, 2, "trakty_sealed_note_140", "tool"),
    ),
    141: (
        Item("zwój liny", "Mocny zwój liny do wozu i mostu.", 2.6, 4, "trakty_rope_141", "tool"),
    ),
    152: (
        Item("worek soli", "Mały worek soli na drogę i do konserwacji zapasów.", 0.4, 2, "trakty_salt_152", "tool"),
    ),
    165: (
        Item("wiązka sideł", "Zbiór sideł z powrozem i pętlami.", 1.0, 7, "trakty_trap_bundle_165", "tool"),
    ),
    166: (
        Item("topór rozłupujący", "Ciężki topór do rąbania drewna przy drodze.", 3.1, 9, "trakty_lumber_axe_166", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=0),
    ),
    172: (
        Item("raport patrolowy", "Zwijany raport o ruchu na trakcie.", 0.2, 2, "trakty_patrol_report_172", "tool"),
    ),
    176: (
        Item("znacznik targowy", "Drewniany znacznik używany do oznaczania towaru.", 0.1, 1, "trakty_trade_token_176", "tool"),
    ),
    179: (
        Item("pieczęć przejazdu", "Pieczęć uprawniająca do przejazdu poza szlak.", 0.1, 3, "trakty_pass_seal_179", "tool"),
    ),
}


def _tract_profile_for(name: str, _index: int) -> tuple[str, dict[str, str]]:
    lowered = name.lower()
    if any(marker in lowered for marker in ("kapliczka", "modlitw", "święt")):
        return (
            "Przydrożna kapliczka i drobne ofiary tłumią tu hałas traktu.",
            {
                "kamien": "Na kamieniu leżą monety, wosk i ślady butów ludzi, którzy przyszli prosić o bezpieczną drogę.",
                "swiece": "Świece palą się krótko, ale wystarczająco długo, by rozproszyć ciemność przy postoju.",
                "modlitwa": "Kto się tu zatrzyma, zwykle robi to ciszej niż mówi.",
            },
        )
    if any(marker in lowered for marker in ("kamień", "kamien", "słup", "slup", "znak", "milowy", "kopiec", "głaz", "glaz")):
        return (
            "Kamień, słup albo znak przypomina, że na trakcie myli się tylko ten, kto nie patrzy pod nogi.",
            {
                "znaki": "Znaki są porysowane od deszczu i wozów, ale nadal da się z nich czytać kierunek.",
                "koleiny": "Koleiny przy znaku mówią, jak często tędy przejeżdżają wozy i karawany.",
                "wiatr": "Wiatr smaga kamień tak samo jak twarze ludzi, którzy się tu zatrzymują.",
            },
        )
    if any(marker in lowered for marker in ("most", "bród", "kladka", "kładka", "przepust")):
        return (
            "Przejście przez wodę lub nierówny teren wymaga tu cierpliwości i dwóch mocnych lin.",
            {
                "woda": "Woda pod konstrukcją jest chłodna i szybka, a każdy ruch wozu słychać pod deskami.",
                "deski": "Deski i kamienie są wyślizgane przez koła, buty i kopyta.",
                "liny": "Liny trzymają tyle, ile pozwolił ostatni człowiek, który je sprawdzał.",
            },
        )
    if any(marker in lowered for marker in ("popas", "zajazd", "ognisko", "postoj", "postoju")):
        return (
            "Przy ogniu stoją skrzynki, kubki i uprząż zdjęta z wozów.",
            {
                "ognisko": "Kamienie przy ognisku są czarne od wielu drobnych postojów.",
                "sakwa": "Rozłożone sakwy, kubki i garnki wskazują, że ktoś tu nocował dosłownie przed chwilą.",
                "drewno": "W stosie drewna widać, że droga nie daje odpocząć nawet wtedy, gdy człowiek już usiadł.",
            },
        )
    if any(marker in lowered for marker in ("woz", "wozów", "wozow", "karawan", "kupiecki", "przejazd", "rozstaje", "rozdroże", "rozdroze", "zjazd", "skręt", "skret", "zakręt", "zakret", "droga", "trakt", "szlak", "koleina")):
        return (
            "Tu wozy zwalniają, a karawany ustawiają się w kolejkę do kolejnego odcinka drogi.",
            {
                "wozy": "Na ziemi widać ślady skrętu osi, klinów i nerwowego hamowania.",
                "rozstaje": "Rozstaje są szerokie, ale niosą w sobie więcej decyzji niż drogi.",
                "ładunek": "Ładunek przy takich miejscach zawsze wygląda, jakby zaraz miał się rozsunąć.",
            },
        )
    if any(marker in lowered for marker in ("pola", "łan", "lan", "chat", "dolina", "brzezina", "brzezin", "granica", "nasyp", "grobla")):
        return (
            "Szlak ociera się tu o pola, zarośla i ludzkie obejścia, więc ruch robi się gęstszy i bardziej ostrożny.",
            {
                "łany": "Łany i miedze są wydeptane przez ludzi, którzy żyją z drogi i z ziemi jednocześnie.",
                "płoty": "Płoty naprawiane są częściej niż opowiadane o nich historie.",
                "wiatr": "Wiatr niesie pył, słomę i czasem zapach gotującej się strawy z dalszych gospodarstw.",
            },
        )
    if any(marker in lowered for marker in ("bagna", "bagno", "torf", "torfow", "mokra", "mokra", "błot", "blot")):
        return (
            "Krawędź szlaku staje się tu cięższa, mokrzejsza i mniej przyjazna dla każdego, kto nie zna obejścia.",
            {
                "torf": "Torf i błoto połykają ślady szybciej niż ludzie zdążą je obejrzeć.",
                "mokradło": "Na mokradle najważniejsze są buty, kije i cierpliwość.",
                "mgła": "Mgła robi z drogi coś krótszego i bardziej niepewnego niż mapa.",
            },
        )
    return (
        "To odcinek zwykłego traktu, ale nawet zwykłe miejsce ma tu własny ciężar i własne tempo.",
        {
            "droga": "Droga jest wyjeżdżona głęboko, a koleiny pokazują ruch bez przerwy.",
            "pył": "Pył osiada na wszystkim: butach, sakwach i spokojnych twarzach podróżnych.",
            "cisza": "Cisza trwa tu krótko. Zawsze coś jedzie, idzie albo wraca.",
        },
    )

_HALDUN_CONTENT: dict[int, LocationContent] = {
    80: LocationContent(
        room_id=80,
        name="Droga do Haldun",
        description=(
            "Droga do Haldun wychodzi z podmiejskiego błota i przechodzi w udeptany trakt pomiędzy zagonami. "
            "Widać stąd zarówno wieś, jak i wielki ruch wokół niej: wozy, psy, ptaki i ludzi, którzy zawsze gdzieś się spieszą."
        ),
        inspectables={
            "koleiny wozy": "Koleiny są głębokie i świeże. To najpewniejszy znak, że zboże i siano krążą tędy codziennie.",
            "rowy ploty": "Rowy przy drodze czyszczone są tak samo uparcie jak płoty, bo wiosenna woda nie zna litości.",
            "domy zagrody": "Pierwsze zagrody stoją blisko drogi, jakby nie chciały się od niej odrywać zbyt daleko.",
        },
        items=(Item("znak drogowy Haldun", "Drewniana tabliczka z wypalonym kierunkiem do wsi.", 0.6, 3, "haldun_road_sign_80", "tool"),),
    ),
    81: LocationContent(
        room_id=81,
        name="Krzyżowy Kamień",
        description=(
            "Przy rozstaju stoi głaz z naciętym znakiem i śladami kredy po dawnych oznaczeniach. "
            "Miejscowi zostawiają tu informacje, wiązki sznurka i wiadomości, których nie warto wozić dalej niż trzeba."
        ),
        inspectables={
            "kamien znak": "Kamień jest obity deszczem, ale nadal dobrze widać kierunkowe nacięcia.",
            "kreda ogloszenia": "Na skale widać kredowe kreski i stare ślady po ogłoszeniach przybitych do deski.",
            "rozstaje droga": "Tu drogi dzielą się na wieś, pola i obejście przy fortecznej trasie.",
        },
        items=(
            Item("sznurek oznaczeniowy", "Krótki sznurek używany do znakowania zapasów.", 0.1, 1, "haldun_marker_cord_81", "tool"),
            Item("tabliczka pola", "Mała tabliczka z numerem zagonu.", 0.2, 2, "haldun_field_tag_81", "tool"),
        ),
    ),
    82: LocationContent(
        room_id=82,
        name="Pierwsze Zagony",
        description=(
            "Pierwsze zagony są wąskie, ale już dobrze wytyczone. "
            "Tutaj zaczyna się ziemia, która musi wyżywić domy, stodoły i tych, którzy nie chcą pracować ciężej niż trzeba."
        ),
        inspectables={
            "sadzonki ziemia": "Gleba jest ciężka i wilgotna, lecz wyraźnie spulchniana regularnie od wielu sezonów.",
            "strach na wróble": "Strachy na wróble są poprute od wiatru, ale nadal skutecznie odganiają ptaki.",
            "narzedzia sierp": "Narzędzia stoją przy zagonach, gotowe do żniw albo szybkiej naprawy płotu.",
        },
        items=(
            Item("snop jęczmienia", "Mocno związany snop z lokalnych zagonów.", 2.0, 4, "haldun_grain_bundle_82", "food"),
            Item("stary strach na wróble", "Stara kukła ze słomy i szmat. Nie ma dużej wartości, ale robi swoje.", 3.0, 2, "haldun_scarecrow_82", "furniture"),
        ),
    ),
    83: LocationContent(
        room_id=83,
        name="Studnia Haldun",
        description=(
            "Studnia stoi pośrodku wsi jak punkt odniesienia dla wszystkich spraw. "
            "Przy cembrowinie leżą wiadra, sznury i ślady butów tak głębokie, że widać, kto przychodzi tu codziennie, a kto tylko raz."
        ),
        inspectables={
            "cembrowina kamien": "Kamień jest wyślizgany i chłodny. Na krawędzi widać rysy po wiadrach i hakach.",
            "lancuch wiadro": "Łańcuch skrzypi, ale trzyma. To ważniejsze niż wygląd.",
            "woda studnia": "Woda jest zimna, ciężka i dobra do picia nawet po dniu pracy na polu.",
        },
        items=(
            Item("wiadro studzienne", "Wiadro do noszenia wody z lokalnej studni.", 1.0, 3, "haldun_well_bucket", "tool"),
            Item("linowy zwój", "Zwój liny do studni lub płotu.", 0.8, 2, "haldun_well_rope", "tool"),
        ),
    ),
    84: LocationContent(
        room_id=84,
        name="Zagony pod Wierzbami",
        description=(
            "Zagony pod Wierzbami leżą szerzej niż pierwsze pola i widać po nich, że ziemia dostaje tu więcej uwagi niż gdzie indziej. "
            "Wierzby dają cień, ale też zbierają wilgoć, więc rolnicy pracują tu ostrożniej."
        ),
        inspectables={
            "wierzby cień": "Wierzby pochylają się nad rowem i osłaniają część pola przed wiatrem.",
            "zboze łany": "Łany są gęste i równe, gotowe na żniwa albo na kolejną porcję narzekań.",
            "ślad wóz": "Ślady wozów prowadzą do stodoły i z powrotem, tworząc codzienny rytm gospodarstwa.",
        },
        items=(
            Item("zboże do młyna", "Worek z bochenkiem przyszłej mąki.", 6.8, 7, "haldun_grain_delivery", is_container=True, capacity=25),
            Item("żelazny sierp", "Sierp z dobrze naostrzonym ostrzem.", 0.9, 6, "haldun_harvest_sickle_84", "tool"),
        ),
    ),
    85: LocationContent(
        room_id=85,
        name="Chata Sołtysa",
        description=(
            "Chata sołtysa stoi bliżej środka wsi niż większość domów, bo tu przychodzą sprawy, które trzeba liczyć, spisywać i rozstrzygać. "
            "Przy drzwiach wisi deska z ogłoszeniami, a na ławie leży księga zapisów."
        ),
        inspectables={
            "deska ogloszenia": "Na desce wiszą ogłoszenia o zbożu, naprawach i zaginionych narzędziach.",
            "ksiega wpisy": "Księga jest gruba od rachunków, nie od ozdobników.",
            "drzwi próg": "Próg jest mocno wytarty. Tyle ludzi przychodzi tu z prośbą, że drewno już dawno się poddało.",
        },
        items=(
            Item("sołtysia pieczęć", "Drewniana pieczęć do drobnych zapisów.", 0.3, 3, "haldun_headman_seal_85", "tool"),
            Item("lista robót", "Zwinięta lista napraw do wykonania przed żniwami.", 0.2, 2, "haldun_headman_tasks_85", "tool"),
        ),
    ),
    86: LocationContent(
        room_id=86,
        name="Obora pod Wierzbami",
        description=(
            "Obora stoi przy zaroślach i pachnie sianem, mlekiem oraz mokrą deską. "
            "Nie jest duża, ale miejscowi trzymają tu zwierzęta lepiej niż wiele większych gospodarstw."
        ),
        inspectables={
            "krowy żłób": "Krowy leniwie przeżuwają, ale wystarczy jeden obcy ruch, by podnieść całe stado na nogi.",
            "żłób siano": "Siano jest suche i dobrze ułożone, a żłób wciąż nosi ślady świeżej naprawy.",
            "drzwi zagroda": "Drzwi są solidne, bo zwierzęta w Haldun mają talent do nieplanowanych wyjść.",
        },
        items=(
            Item("mleczne wiadro", "Wiadro do dojenia i noszenia mleka.", 1.4, 4, "haldun_milk_pail_86", "tool"),
            Item("wiązka siana", "Sucha wiązka siana dla zwierząt.", 1.2, 2, "haldun_hay_bundle_86"),
        ),
    ),
    87: LocationContent(
        room_id=87,
        name="Stodoły Zachodnie",
        description=(
            "Kilka stodół stoi tu obok siebie jak długi magazyn wsi. "
            "Powietrze pachnie słomą, pyłem i drewnem, a deski szumią przy każdym mocniejszym podmuchu."
        ),
        inspectables={
            "stodoła dach": "Dachy są łatane, ale nadal trzymają zapasy suchsze niż niejeden dom.",
            "wóz siano": "Przez stodoły przejeżdżają wozy z sianem, drewnem i workami zboża.",
            "belka krokiew": "Belki noszą ślady napraw i nowych klinów, bo w Haldun nic nie stoi bez opieki.",
        },
        items=(
            Item("belka stodolna", "Ciężka belka przygotowana do naprawy dachu.", 4.8, 6, "haldun_barn_beam", "furniture"),
            Item("zwój słomy", "Słoma związana w praktyczny zwój.", 1.0, 2, "haldun_straw_roll_87"),
        ),
    ),
    88: LocationContent(
        room_id=88,
        name="Młynny Rów",
        description=(
            "Młynny rów prowadzi wodę do koła i oddaje ją dalej, wzdłuż zabudowań. "
            "Woda szumi tu stale, a pył mączny osiada na kamieniu i deskach jak cienka warstwa śniegu."
        ),
        inspectables={
            "koło woda": "Koło młyna obraca się wolno, ale równo, bez zbędnych kaprysów.",
            "sluz rów": "Sluza kieruje wodę wąskim kanałem, ważniejsza dla wsi niż niejeden urzędnik.",
            "pył mąka": "Pył mączny osiada na wszystkim, co stoi zbyt długo w jednym miejscu.",
        },
        items=(
            Item("węgiel do kuźni", "Worek mocnego węgla, zwykle wynoszony do kuźni.", 3.6, 5, "haldun_forge_coal", is_container=True, capacity=18),
            Item("kamień młyński", "Mały kamień z odłupanym brzegiem.", 5.0, 4, "haldun_millstone_88", "furniture"),
        ),
    ),
    89: LocationContent(
        room_id=89,
        name="Mostek nad Strugą",
        description=(
            "Mostek łączy oba brzegi strugi tak, by wóz nie musiał brnąć przez wodę. "
            "W tym miejscu zbiegają się gospodarstwa, handel i ścieżki, więc zawsze ktoś tu stoi choćby na chwilę."
        ),
        inspectables={
            "deski most": "Deski są wyślizgane od kół i butów, ale nadal trzymają ciężar dnia.",
            "struga nurt": "Struga jest wąska, lecz szybka. Niesie listki, gałązki i plotki z wyższych pól.",
            "handel wóz": "To dobre miejsce na wymianę worka, wiadomości albo cen z sąsiadem.",
        },
        items=(
            Item("zwój liny", "Lina przydatna przy przeprawie albo naprawie mostku.", 2.4, 4, "haldun_bridge_rope_89", "tool"),
            Item("znacznik targowy", "Mały znacznik używany przez handlarzy do oznaczania towaru.", 0.1, 1, "haldun_trade_token_89", "misc"),
        ),
    ),
    90: LocationContent(
        room_id=90,
        name="Pola Jęczmienne",
        description=(
            "Pola jęczmienne ciągną się szeroko i równo, aż po linię drzew przy drodze. "
            "To tutaj widać, czy rok był łaskawy, bo wszystko mierzy się liczbą kłosów i tym, ile zostało po gradzie."
        ),
        inspectables={
            "kłosy zboże": "Kłosy są ciężkie i dobrze wyrośnięte. Właśnie tak ma wyglądać pole, które chce wyżywić wieś.",
            "sierpy widły": "Sierpy i widły stoją przy miedzy, gotowe na żniwa albo na kolejną zmianę pogody.",
            "wiatr pył": "Wiatr niesie pył i suchą słomę, która przyczepia się do butów na cały dzień.",
        },
        items=(
            Item("worek jęczmienia", "Worek pełen jęczmienia, ciężki i dobrze zawiązany.", 7.0, 9, "haldun_barley_sack_90", is_container=True, capacity=24),
            Item("stępiony sierp", "Sierp po całym sezonie żniw.", 0.8, 3, "haldun_worn_sickle_90", "tool"),
        ),
    ),
    91: LocationContent(
        room_id=91,
        name="Sad Kwaśnych Jabłek",
        description=(
            "Sad jest mały, ale zadbany, a jabłka mają wyraźnie kwaśny smak i twardą skórkę. "
            "Drzewa rosną nisko, przez co trzeba schylać się po owoce i uważać na spadające gałęzie."
        ),
        inspectables={
            "jabłka drzewa": "Owoce są gęsto rozsiane po gałęziach. To jeden z nielicznych sadów, który wytrzymuje wiatr.",
            "gałęzie kosze": "Kosze i skrzynki stoją pod drzewami, gotowe do szybkiego zbioru.",
            "trawa wilgoć": "Trawa jest wilgotna od cienia i rano długo nie schnie.",
        },
        items=(
            Item("kosz jabłek", "Kosz kwaśnych jabłek z sadu.", 3.2, 7, "haldun_orchard_crate", is_container=True, capacity=14),
            Item("skrzynka na owoce", "Skrzynka z wytartym dnem, ale nadal użyteczna.", 1.5, 3, "haldun_fruit_crate_91", is_container=True, capacity=10),
        ),
    ),
    92: LocationContent(
        room_id=92,
        name="Pastwisko Koni",
        description=(
            "Pastwisko jest szerokie i wietrzne, a konie trzymają się tu bliżej ogrodzeń niż środka pola. "
            "Widać po nich, że znały już ciężkie wozy i bardziej niż chleb cenią spokój."
        ),
        inspectables={
            "konie ogrodzenie": "Konie obwąchują obcych z wyczuciem tych, którzy nie ufają pierwszemu krokowi.",
            "ogrodzenie słupy": "Ogrodzenie jest świeżo naprawiane; kilka słupów ma jeszcze ślady po nowych klinach.",
            "trawa kopyta": "Trawa jest wydeptana przez kopyta i wraca do siebie tylko w najdalszych rogach pastwiska.",
        },
        items=(
            Item("uzda końska", "Solidna uzda do prowadzenia koni.", 1.0, 5, "haldun_horse_bridle", "tool"),
            Item("sól dla stad", "Mały woreczek soli dla zwierząt.", 0.4, 2, "haldun_salt_pouch_92", "food"),
        ),
    ),
    93: LocationContent(
        room_id=93,
        name="Kapliczka Żniwiarzy",
        description=(
            "Kapliczka stoi przy drodze do fortecy i przypomina, że żniwa też są rodzajem modlitwy. "
            "W niszy palą się świece, a wokół leżą drobne ofiary i sznury paciorków."
        ),
        inspectables={
            "swiece wosk": "Świece są grube, miejscami przypalone do kamienia.",
            "paciorki ofiary": "Paciorki, monety i kawałki chleba leżą w niszy jako proste podziękowanie.",
            "droga forteca": "Z kapliczki widać już kierunek ku fortecy i cięższy ruch na trakcie.",
        },
        items=(
            Item("wiązka wosku", "Wiązka świeżego wosku do świec.", 0.4, 3, "haldun_wax_bundle", is_container=True, capacity=8),
            Item("paciorki modlitewne", "Niewielki sznur z paciorkami do modlitwy.", 0.2, 2, "haldun_prayer_beads_93"),
        ),
    ),
    94: LocationContent(
        room_id=94,
        name="Droga ku Fortecy",
        description=(
            "Droga ku Fortecy wychodzi z Haldun i prowadzi dalej do wojskowego pasa na północy. "
            "Tu kończy się wiejska codzienność, a zaczyna ruch żołnierzy, zapasów i tych, którzy muszą się tłumaczyć z podróży."
        ),
        inspectables={
            "wozy patrole": "Przez drogę przechodzą patrole, wozy z sianem i ludzie, którzy chcą wejść do fortecy bez zbędnych pytań.",
            "słup drogowskaz": "Drogowskaz jest porysowany, ale nadal pokazuje właściwy kierunek.",
            "koleiny błoto": "Koleiny są głębokie i świeże. Nie ma wątpliwości, że tędy ciągle coś jedzie.",
        },
        items=(
            Item("lampa drogowa", "Niewielka lampa przydająca się na nocnym trakcie.", 0.9, 4, "haldun_road_lantern_94", "tool"),
            Item("rozkaz przewozowy", "Zwinięty list przewozowy z pieczęcią.", 0.1, 2, "haldun_route_notice", "tool"),
        ),
    ),
}

_FORTRESS_CONTENT: dict[int, LocationContent] = {
    110: LocationContent(
        room_id=110,
        name="Brama Dungrim",
        description=(
            "Brama Dungrim zamyka fortecę na wąskim przesmyku drogi. Żelazne okucia, hak do łańcucha i zgrana warta mówią jasno, że to nie jest miejsce dla przypadkowych przejazdów."
        ),
        inspectables={
            "brama hak": "Hak i łańcuch są grube, ciężkie i wysmarowane tłuszczem, by wytrzymały deszcz oraz mróz.",
            "warta straż": "Straż przy bramie stoi nieruchomo, ale obserwuje każde dłonie i każdą sakwę.",
            "mur przejazd": "Mur przy przejeździe jest świeżo łatany smołą i kamieniem.",
        },
        items=(Item("bramny klucz", "Ciężki klucz do bocznej furty.", 0.3, 4, "dungrim_gate_key_110", "tool"),),
    ),
    111: LocationContent(
        room_id=111,
        name="Przedbramie Wilczych Haków",
        description=(
            "Przedbramie jest ciasne, niskie i zbudowane tak, by spowolnić każdego, kto nie został tu oczekiwany. Na belkach wiszą stare haki, a pod nogami widać ślady po kołach wozów i butach wartowników."
        ),
        inspectables={
            "haki belki": "Haki są przeznaczone do zatrzymywania ładunków i ludzi, którzy próbują dyskutować z fortem.",
            "ślady koła": "Ślady kół są głębokie od ciężkich dostaw i rannych transportów.",
            "warta drzwi": "Drzwi do przejazdu nie otwierają się bez rozkazu.",
        },
        items=(Item("tabliczka meldunkowa", "Mała tabliczka do meldowania ruchu przy bramie.", 0.2, 2, "dungrim_muster_board_111", "tool"),),
    ),
    112: LocationContent(
        room_id=112,
        name="Dziedziniec Garnizonu",
        description=(
            "Dziedziniec Garnizonu jest sercem codziennego ruchu. Tu ćwiczą oddziały, tu stają skrzynie z zapasami i tu każdy rozkaz robi się głośniejszy, niż chciałby dowódca."
        ),
        inspectables={
            "plac tarcze": "Na placu stoją tarcze treningowe i pachołki do ćwiczeń.",
            "żołnierze ćwiczenia": "Żołnierze ćwiczą krótkimi seriami, bo w Dungrim liczy się oszczędność sił.",
            "błoto koła": "Błoto miesza się tu z piaskiem i odciskami butów w równych pasach.",
        },
        items=(Item("drewniany pachołek", "Pachołek używany do ćwiczeń marszu i ustawiania szyku.", 1.0, 3, "dungrim_training_pole_112", item_type="furniture"),),
    ),
    113: LocationContent(
        room_id=113,
        name="Studnia Forteczna",
        description=(
            "Studnia forteczna stoi na środku dziedzińca i obsługuje nie tylko ludzi, ale i konie, kuchnię oraz magazyny. Woda jest zimna, ciężka i pilnowana prawie jak zapasy w fortecy."
        ),
        inspectables={
            "łańcuch wiadro": "Łańcuch jest nowy i ciężki, a wiadro nosi ślady po zimowej naprawie.",
            "kamien woda": "Kamień wokół studni jest wyślizgany do połysku przez setki butów.",
            "cisza echo": "Echo ze studni wraca krótko i sucho, jakby nawet woda miała tu wojskowy porządek.",
        },
        items=(Item("wiadro forteczne", "Mocne wiadro do wody i zadań służbowych.", 1.4, 4, "dungrim_bucket_113", "tool"),),
    ),
    114: LocationContent(
        room_id=114,
        name="Stajnie Patroli",
        description=(
            "Stajnie są niskie, ciepłe i pełne zapachu słomy oraz mokrej skóry. Konie patrolowe stoją w oddzielnych boksach, gotowe do wyjazdu w każdej chwili."
        ),
        inspectables={
            "boks konie": "Boksy są solidne i świeżo naprawiane, bo konie służbowe nie wybaczają słabych belek.",
            "siano uzda": "Siano leży równo, a uzdy wiszą na hakach obok numerów boksów.",
            "kopyta błoto": "Błoto z kopyt zbiera się przy wejściu, gdzie stajenny zmiata je co kilka godzin.",
        },
        items=(Item("słoma stajenna", "Sucha słoma do boksów i podsypki.", 1.6, 3, "dungrim_stable_straw_114"),),
    ),
    115: LocationContent(
        room_id=115,
        name="Kuchnia Garnizonowa",
        description=(
            "Kuchnia garnizonowa pracuje bez przerwy. Kotły, łopaty do pieca i ciężkie garnki są tu ważniejsze niż ozdoby, bo cała załoga ma jeść na czas."
        ),
        inspectables={
            "kotly ogien": "Kotły stoją w rzędzie, a ogień w palenisku nie gaśnie od świtu.",
            "gulasz racje": "Gulasz i racje są liczone dokładniej niż plotki.",
            "zlew noze": "Noże i łyżki leżą w szeregu, jakby nawet sztućce miały tu musztrę.",
        },
        items=(
            Item("kocioł garnizonowy", "Ciężki kocioł do wojskowego gotowania.", 12.0, 12, "dungrim_garrison_pot_115", item_type="furniture"),
            Item("łyżka polowa", "Drewniana łyżka odpowiednia do zupy i wartowniczej cierpliwości.", 0.2, 1, "dungrim_field_spoon_115", "tool"),
        ),
    ),
    116: LocationContent(
        room_id=116,
        name="Koszary Zachodnie",
        description=(
            "Koszary Zachodnie to długi budynek z pryczami, skrzyniami i tablicą rozkazów. W środku zawsze ktoś śpi, ktoś czyści sprzęt, a ktoś inny udaje, że nie słyszy pobudki."
        ),
        inspectables={
            "prycze skrzynie": "Prycze są ustawione równo, a skrzynie stoją pod ścianą z numerami kompanii.",
            "tablica rozkaz": "Na tablicy wiszą krótkie rozkazy i zmiany wart, zapisane dużymi literami.",
            "buty pasy": "Buty, pasy i mokre płaszcze wiszą przy ścianie obok zbroi i uprzęży.",
        },
        items=(Item("posłanie koszarowe", "Skręcone posłanie i koc odłożony po zmianie.", 1.8, 3, "dungrim_barracks_roll_116"),),
    ),
    117: LocationContent(
        room_id=117,
        name="Kuźnia Wojskowa",
        description=(
            "Kuźnia wojskowa jest gorąca, ciasna i nieustannie pełna dźwięku metalu. Naprawia się tu groty, podkowy, nity i rzeczy, które nie mogą się zepsuć w czasie marszu."
        ),
        inspectables={
            "kowadlo młot": "Kowadło nosi ślady po tysiącach uderzeń, a młoty wiszą na ścianie w porządku rozumianym tylko przez kowala.",
            "iskry ogień": "Iskry lecą nisko, bo kuźnia stoi osłonięta od wiatru.",
            "ostrza nity": "Ostrza i nity czekają na naprawę w osobnych misach i skrzynkach.",
        },
        items=(
            Item("żarownica", "Pojemnik na żar do przenoszenia ognia między paleniskami.", 1.0, 5, "dungrim_brazier_117", item_type="furniture"),
            Item("szczypce wojskowe", "Szczypce do cięższych napraw fortecznych.", 1.2, 6, "dungrim_forge_tongs_117", "tool"),
        ),
    ),
    118: LocationContent(
        room_id=118,
        name="Izba Oficerska",
        description=(
            "Izba Oficerska jest bardziej spokojna niż reszta fortu, ale tylko dlatego, że tu zapadają decyzje. Na stole leżą mapy, pieczęcie i zamknięte raporty."
        ),
        inspectables={
            "mapy pieczęcie": "Mapy są pełne notatek o trakcie, a pieczęcie leżą w jednym, pilnowanym miejscu.",
            "stol raporty": "Stół jest gładki od wielu odpraw i nerwowych palców.",
            "krzesla cisza": "Krzesła są ciężkie, a cisza w izbie zwykle oznacza, że zaraz padnie rozkaz.",
        },
        items=(Item("raport z patrolu", "Zwinięty raport o zmianie patroli.", 0.2, 2, "dungrim_patrol_report_118", "tool"),),
    ),
    119: LocationContent(
        room_id=119,
        name="Mur Nad Traktem",
        description=(
            "Mur Nad Traktem pozwala obserwować drogę w dół i wyłapywać każdy ruch wozów oraz pieszych. Wiatry są tu ostre, a rozmowy krótkie."
        ),
        inspectables={
            "przedmurze droga": "Z muru widać cały zakręt traktu i miejsce, gdzie łatwo urządzić zasadzkę.",
            "straż patrzenie": "Strażnicy na murze patrzą więcej niż mówią.",
            "szczeliny wiatr": "Szczeliny w murze pozwalają oddychać i sprawdzać, czy coś nie idzie od zachodu.",
        },
        items=(Item("lornetka forteczna", "Prosta lornetka do obserwacji traktu.", 0.8, 8, "dungrim_spyglass_119", "tool"),),
    ),
    120: LocationContent(
        room_id=120,
        name="Sala Dowódcy",
        description=(
            "Sala Dowódcy jest najciszej strzeżonym miejscem w fortecy. Mapa działań, pieczęcie i krzesło przy stole mówią, że tu ważą się decyzje o całym garnizonie."
        ),
        inspectables={
            "mapa plany": "Mapa jest ciężko obłożona kamieniami i oznaczona kilkoma trasami patroli.",
            "stol pieczęcie": "Na stole leżą pieczęcie, listy i wosk gotowy do użycia.",
            "okno trakt": "Przez okno widać trakt i ruch przy bramie.",
        },
        items=(Item("rozkaz dowódcy", "Zapieczętowany rozkaz dla zmian fortecznych.", 0.1, 3, "dungrim_commander_order_120", "tool"),),
    ),
    121: LocationContent(
        room_id=121,
        name="Zbrojownia Dungrim",
        description=(
            "Zbrojownia trzyma tarcze, hełmy i części pancerzy na osobnych stojakach. Wszystko tu jest oznaczone i policzone, bo w fortecy brak hełmu jest tak samo ważny jak brak człowieka."
        ),
        inspectables={
            "hełmy tarcze": "Hełmy i tarcze stoją w rzędach według rozmiaru oraz stanu naprawy.",
            "nity skóra": "Nity, skóra i zapięcia leżą osobno, gotowe do wydania zbrojmistrzowi.",
            "broń stojaki": "Broń na stojakach jest czyściutka, ale bez przesadnej ozdoby.",
        },
        items=(Item("pęk nitów", "Zestaw nitów do naprawy zbroi.", 0.5, 4, "dungrim_armor_rivets_121", "tool"),),
    ),
    122: LocationContent(
        room_id=122,
        name="Magazyn Główny",
        description=(
            "Magazyn Główny pęka od skrzyń, beczek i worków. Kto tu wchodzi, musi wiedzieć, że wszystko ma numer, a każdy brak szybko wychodzi na jaw."
        ),
        inspectables={
            "skrzynie beczki": "Skrzynie i beczki są ustawione tak, by dało się je policzyć w kilka chwil.",
            "kreda spisy": "Na podłodze kredą zaznaczono strefy składowania.",
            "klucze magazyn": "Klucze do magazynu wiszą na haku większym niż większość sakiew.",
        },
        items=(Item("lista zapasów", "Spis zapasów fortu z bieżącego tygodnia.", 0.1, 2, "dungrim_stock_list_122", "tool"),),
    ),
    123: LocationContent(
        room_id=123,
        name="Skład Racji",
        description=(
            "Skład Racji trzyma to, co najczęściej znika: chleb, sól, suszone mięso i lampowy tłuszcz. Każda półka ma własny znak, a wszystko pachnie sucho i praktycznie."
        ),
        inspectables={
            "chleb sol": "Chleb i sól stoją razem, bo oba kończą się za szybko.",
            "półki worki": "Półki i worki są podpisane, żeby nikt nie pomylił racji z zapasami warsztatowymi.",
            "pieczęć wydanie": "Pieczęć wydania leży przy małej skrzynce, gotowa na kolejny patrol.",
        },
        items=(Item("racja awaryjna", "Dodatkowa porcja suchych zapasów.", 0.6, 4, "dungrim_emergency_ration_123", "food", is_consumable=True, effects_on_consume={"restore_stamina": 10}),),
    ),
    124: LocationContent(
        room_id=124,
        name="Wyjazd na Zachodni Trakt",
        description=(
            "Wyjazd na Zachodni Trakt jest ostatnim punktem fortecy przed drogą w otwarty teren. Tu kontroluje się wóz, pieczęć i ostatni raz patrzy na zawartość ładunku."
        ),
        inspectables={
            "szlaban trakt": "Szlaban jest szeroki i ciężki, bo ma zatrzymać także najuporczywszy wóz.",
            "pieczęcie warta": "Warta przy wyjeździe sprawdza pieczęcie szybciej niż wymówki.",
            "błoto ślady": "Błoto miesza się z koleinami i pokazuje, jak często tędy coś opuszcza fort.",
        },
        items=(Item("pieczęć przejazdu", "Pieczęć uprawniająca do przejazdu poza fort.", 0.1, 3, "dungrim_pass_seal_124", "tool"),),
    ),
}


def _d351b_content(room_id: int, index: int, name: str, label: str, terrain: str, feature_a: tuple[str, str], feature_b: tuple[str, str], feature_c: tuple[str, str]) -> LocationContent:
    if room_id in _HALDUN_CONTENT:
        return _HALDUN_CONTENT[room_id]
    if room_id in _FORTRESS_CONTENT:
        return _FORTRESS_CONTENT[room_id]
    if room_id == 60:
        return LocationContent(
            room_id=60,
            name="Błotna Brama",
            description=(
                "Błotna Brama trzyma południowy wjazd podgrodzia. "
                "W wysokich odgrodach odcisnęły się koła wozów, a przy zawiasach widać świeżą smołę i naprawiane po zimie deski. "
                "To tutaj ruch zwalnia, bo każdy musi minąć wartę, palenisko i szeroką koleinę pełną brunatnej wody."
            ),
            inspectables={
                "brama wjazd": "Brama jest ciężka, obita żelazem i ciągle obmacana przez dłonie wartowników. Widać na niej ślady po linach, mokrym błocie i uderzeniach kół.",
                "warta wartownicy": "Wartownicy siedzą tu bliżej ognia niż muru. Pilnują nie tyle samej drogi, ile tego, kto wjeżdża i z czym wraca.",
                "koleina błoto woda": "Najgłębsza koleina zbiera wodę z całego przedmieścia. Kto w niej stanie, zostawia po sobie ślad na długo.",
            },
            items=(
                Item("drewniane wiadro", "Wiadro z grubych klepek, dobre do noszenia wody albo zboża.", 1.1, 3, "bucket_60", item_type="tool"),
                Item("wóz furmański", "Zniszczony wóz na szerokich kołach, wciąż gotowy do krótkiego kursu przez błoto.", 48.0, 25, "podgrodzie_cart_60", item_type="furniture"),
                Item("złamane koło wozu", "Pęknięte koło zdjęte z wozu. Da się je jeszcze naprawić u dobrego kowala.", 7.0, 6, "podgrodzie_broken_wheel_60", item_type="tool"),
            ),
        )
    if room_id == 95:
        return LocationContent(
            room_id=95,
            name="Wschodnia Furta Łowców",
            description=(
                "Wschodnia furta otwiera się na wąski przesmyk między palisadą a pierwszymi drzewami. "
                "Z jednej strony stoi suszarnia skór, z drugiej wiszą pęki sidła i świeżo obrane kłody. "
                "To wejście do osady działa bardziej jak punkt wymiany niż prawdziwa brama: tu oddaje się zwierzynę, odbiera narzędzia i liczy, kto wrócił z lasu."
            ),
            inspectables={
                "furta palisada": "Furta jest niska i praktyczna, z szerokimi zawiasami oraz śladami po częstym otwieraniu. Na belce widać nacięcia od noży i haków.",
                "suszarnia skory": "Z suszarni dobiega ostry zapach dymu i tłuszczu. Skóry wiszą tam tak gęsto, że tworzą niemal drugą ścianę.",
                "sidła kłody": "Przy furcie leżą sidła, kołki i kawałki świeżego drewna. Wszystko jest przygotowane do szybkiego wyjścia w las.",
            },
            items=(Item("wiązka sideł", "Zbiór sideł z powrozem i pętlami.", 1.0, 7, "hunter_traps_95", item_type="tool"),),
        )
    if 135 <= room_id <= 179:
        if room_id == 135:
            return LocationContent(
                room_id=135,
                name="Kapliczka Podróżnych za Murem",
                description=(
                    "Kamienna kapliczka stoi przy rozjeździe, trochę cofnięta od traktu, żeby wozy nie rozbijały jej przy każdym mijaniu. "
                    "Nad niszami wiszą woski i drobne dary zostawione przez ludzi, którzy chcą bezpiecznie minąć kolejne mile. "
                    "Miejsce służy odpoczynkowi, modlitwie i sprawdzeniu uprzęży, zanim droga znów zawęzi się między mokrą ziemią a rowem."
                ),
                inspectables={
                    "kamien kapliczka": "Kamień jest wygładzony od dłoni i deszczu. W niszach stoją wypalone świece, kawałki sznurka i kilka monet zostawionych na szczęście.",
                    "ofiary świece wosk": "Ofiary są skromne: garść ziarna, kawałek wstążki, odłamek kości albo świeca dopalona do połowy.",
                    "trakt rozjazd": "Rozjazd rozsuwa drogę na dwa niepewne kierunki. Kapliczka stoi dokładnie tam, gdzie podróżny musi na chwilę zwolnić.",
                },
                items=_TRACT_ITEM_MAP.get(room_id, ()),
                hidden_items=(),
            )
        lead, inspectables = _tract_profile_for(name, index)
        description = (
            f"{name}. {lead} {_D351B_ATMOSPHERE[index % len(_D351B_ATMOSPHERE)]}"
        )
        tract_items = _TRACT_ITEM_MAP.get(room_id, ())
        tract_hidden_items: tuple[tuple[Item, int], ...] = ()
        if room_id in {139, 151, 159, 170, 177}:
            tract_hidden_items = ((Item("miedziana moneta", "Brudna miedziana moneta zgubiona przy drodze.", 0.01, 1, f"road_copper_{room_id}"), 8),)
        return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=tract_items, hidden_items=tract_hidden_items)
    description = (
        f"{name}. {feature_a[1]} {_D351B_ATMOSPHERE[index % len(_D351B_ATMOSPHERE)]}"
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], feature_c[0]: feature_c[1]}
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id == 60:
        items = (
            Item("drewniane wiadro", "Wiadro z grubych klepek, dobre do noszenia wody albo zboża.", 1.1, 3, "bucket_60", item_type="tool"),
            Item("wóz furmański", "Zniszczony wóz na szerokich kołach, wciąż gotowy do krótkiego kursu przez błoto.", 48.0, 25, "podgrodzie_cart_60", item_type="furniture"),
            Item("złamane koło wozu", "Pęknięte koło zdjęte z wozu. Da się je jeszcze naprawić u dobrego kowala.", 7.0, 6, "podgrodzie_broken_wheel_60", item_type="tool"),
        )
    if room_id in {63, 82, 99, 113, 143, 156, 183, 196}:
        items += (Item("porzucony rzemień", "Krótki, zużyty rzemień. Może posłużyć do prostych napraw albo wiązania pakunków.", 0.05, 1, f"strap_{room_id}"),)
    if room_id == 63:
        items += (Item("worek zboża", "Worek z ziarnem, ciężki i dobrze zawiązany.", 7.5, 11, "podgrodzie_grain_sack_63", is_container=True, capacity=24),)
    if room_id == 64:
        items += (Item("drewno opałowe", "Porąbane drewno czekające na palenisko albo piec.", 14.0, 6, "podgrodzie_firewood_64"),)
    if room_id == 185:
        items += (Item("mały obóz myśliwych", "Niski obóz przy starej drodze, z trzema kołkami i zwiniętą płachtą.", 2.1, 5, "boczny_hunter_camp_185", item_type="furniture"),)
    if room_id == 190:
        items += (Item("palenisko przy rozstajach", "Niewielkie palenisko rozstawione tuż przy bocznym obejściu.", 1.4, 4, "boczny_firepit_190", item_type="furniture"),)
    if room_id == 203:
        items += (Item("obóz drwali przy drodze", "Prosty obóz z kłodą do siedzenia, wiązką chrustu i hakami na narzędzia.", 2.6, 5, "boczny_lumber_camp_203", item_type="furniture"),)
    if room_id == 206:
        items += (Item("wygaszone ognisko", "Kamienny krąg po ognisku, które zgasło dawno temu.", 1.0, 2, "boczny_dead_fire_206", item_type="furniture"),)
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
            "Miejsce Cichego Kroku",
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
        f"{name}. {_D351C_ATMOSPHERE[index % len(_D351C_ATMOSPHERE)]} "
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
    if room_id == 216:
        items = (
            Item("wiązka suchego chrustu", "Lekka wiązka chrustu, dobra na ognisko albo do prostych prac obozowych.", 0.4, 1, "dry_brushwood_216"),
            Item("mały obóz myśliwski", "Niski obóz z trzema kołkami, mokrą płachtą i resztką popiołu. Ktoś wraca tu tylko po odpoczynek.", 2.0, 4, "forest_hunter_camp_216", item_type="furniture"),
        )
    if room_id == 223:
        items = (
            Item("wiązka suchego chrustu", "Lekka wiązka chrustu, dobra na ognisko albo do prostych prac obozowych.", 0.4, 1, "dry_brushwood_223"),
            Item("pachnące palenisko", "Niewielkie palenisko dla tych, którzy zatrzymują się na chwilę po zioła i tropy.", 1.4, 3, "forest_firepit_223", item_type="furniture"),
        )
    if room_id == 230:
        items = (
            Item("wygaszone ognisko", "Mały kamienny krąg po ognisku, dziś prawie zimny.", 1.0, 2, "forest_dead_fire_230", item_type="furniture"),
        )
    if room_id in {230, 246, 258, 272}:
        hidden_items = ((Item("garść leśnych ziół", "Gorzko pachnące zioła zebrane z miejsc, których nie widać z duktu.", 0.05, 3, f"forest_herbs_{room_id}"), 11),)
    if room_id == 246:
        items = (
            Item("złamany klin", "Pęknięty klin znaleziony przy obozowisku drwali.", 0.4, 2, "forest_broken_wedge_246", "tool"),
            Item("wiązka suchego chrustu", "Lekka wiązka chrustu, dobra na ognisko albo do prostych prac obozowych.", 0.4, 1, "dry_brushwood_246"),
            Item("małe obozowisko drwali", "Trzy kołki, zawieszony kociołek i mokra płachta. To bardziej postój niż prawdziwy obóz.", 2.2, 5, "forest_lumber_camp_246", item_type="furniture"),
        )
    if room_id == 252:
        items = (
            Item("kamienny medalik", "Mały kamienny medalik pozostawiony przy kapliczce.", 0.1, 4, "forest_chapel_token_252", "tool"),
        )
    if room_id == 258:
        items = (
            Item("bukłak strumienny", "Bukłak napełniony świeżą wodą ze strumienia.", 1.0, 2, "forest_stream_waterskin_258", "food", is_consumable=True, effects_on_consume={"restore_stamina": 4}),
        )
    if room_id == 267:
        items = (
            Item("zardzewiały garnek", "Garnek porzucony przy dawnym obozie.", 1.2, 3, "forest_abandoned_pot_267", "tool"),
            Item("stary rzemień", "Krótki, stary rzemień od sakwy lub pułapki.", 0.1, 1, "forest_old_strap_267", "tool"),
            Item("opuszczony obóz łowców", "Niski obóz przyciśnięty do ziemi, z gałęziami zamiast ścian i starym popiołem w środku.", 2.8, 4, "forest_hunter_camp_267", item_type="furniture"),
        )
    if room_id == 272:
        hidden_items = ((Item("garść leśnych ziół", "Gorzko pachnące zioła zebrane z miejsc, których nie widać z duktu.", 0.05, 3, "forest_herbs_272"), 11),)
    if room_id == 230:
        hidden_items = ((Item("garść leśnych ziół", "Gorzko pachnące zioła zebrane z miejsc, których nie widać z duktu.", 0.05, 3, "forest_herbs_230"), 11),)
    if room_id in {218, 234, 248, 259, 273}:
        hidden_items = (
            (
                Item(
                    "ukryta skrzynka",
                    "Mała skrzynka wciśnięta między korzenie i przykryta mchem. W środku leży drobny łup, który łatwo przeoczyć.",
                    1.4,
                    14,
                    f"forest_hidden_chest_{room_id}",
                    is_container=True,
                    capacity=6.0,
                    contains=[
                        Item(
                            "zawiniątko łupów",
                            "Przewiązany sznurkiem pakiet drobnych rzeczy znalezionych w lesie.",
                            0.2,
                            6,
                            f"forest_hidden_loot_{room_id}",
                        )
                    ],
                ),
                12,
            ),
        )
    if room_id == 274:
        items = (
            Item("zgaszone palenisko", "Kamienny krąg po niedawnym ognisku. Widać, że ktoś odszedł w pośpiechu.", 1.0, 2, "forest_camp_fire_274", item_type="furniture"),
            Item("zgięty kołek namiotu", "Zgięty kołek wbity w ziemię po prowizorycznym szałasie.", 0.4, 1, "forest_camp_stake_274", item_type="tool"),
        )
        hidden_items = ((Item("znacznik obozu", "Zardzewiały znak pozostawiony przez dawne obozowisko banitów.", 0.1, 5, "forest_camp_token_274", "tool"), 13),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351c_content() -> tuple[LocationContent, ...]:
    return tuple(_d351c_forest_content(room_id, index, name) for index, (room_id, name) in enumerate(zip(range(210, 280), _D351C_NAMES)))



_D351D_NAMES = (
    "Cienista Granica Kniei", "Stare Rozstaje bez Znaków", "Korytarz Cichych Leszczyn", "Zatarta Ścieżka Straży", "Kamień Trzech Nacięć",
    "Wykrot pod Czarnym Grabem", "Suchy Parów", "Mostek z Zardzewiałym Ćwiekiem", "Głuchy Zakręt", "Zakos Pochylonych Buków",
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
    "Dźwięk urywa się tu szybko między pniami i krzakami.",
    "Dawny trakt zdradzają tylko ugnieciony mech i równiej rosnące młode pnie.",
    "Powietrze jest cięższe i chłodniejsze niż przy zwykłych leśnych drogach.",
    "Wiele przejść kończy się mokrym dołem albo ścianą jałowców.",
    "Gałęzie, korzenie i ciemne zagłębienia zmuszają do krótszych kroków.",
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
        f"{name}. {_D351D_ATMOSPHERE[index % len(_D351D_ATMOSPHERE)]} "
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
    "Brama Strażnicy Przełęczy", "Dziedziniec Meldunkowy", "Wieża Zwiadowców", "Izba Przewodnika", "Plac Karawan",
    "Stajnie Wozów", "Izba Podróżnych", "Kaplica Przełęczy", "Ambona Myśliwego", "Brama do Dungrim",
)

_D351E_MOUNTAIN_NAMES = (
    "Podnóże Mekhary", "Kamienny Zakręt", "Półka nad Ciemnym Lasem", "Ścieżka Kozich Racic", "Suchy Żleb",
    "Złamany Drogowskaz", "Stara Droga Straży", "Piargi pod Sosnami", "Wąskie Siodło", "Głaz z Żelaznym Klinem",
    "Urwisko Kruków", "Zawalony Szałas Tragarzy", "Skręt ku Srebrnej Skale", "Źródło pod Łupkiem", "Północna Ściana Jarów",
    "Niski Próg Skalny", "Dawna Ambona Strażników", "Kamienie po Ognisku", "Przejście pod Wiszącą Skałą", "Czerwony Osyp",
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
    if room_id == 125:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Brama Strażnicy Przełęczy jest pierwszym miejscem, w którym droga zwalnia przed śniegiem, pieczęciami i pytaniami. "
                "Tu wóz czeka, aż komendant lub wartownik potwierdzi, że przejazd nie przysporzy kłopotów niżej w dolinie."
            ),
            inspectables={
                "brama łańcuch": "Łańcuch bramy jest gruby i świeżo natarty tłuszczem, żeby nie zamarzł podczas nocnej zmiany.",
                "meldunki tablica": "Na tablicy meldunkowej zapisuje się ruch karawan, opóźnienia i to, kto ma wrócić przed zmrokiem.",
                "wiatr szczeliny": "Wiatr wciska się przez szczeliny jak ciekawski urzędnik. Zimą to on pierwszy ogłasza zmianę pogody.",
            },
            items=(Item("mapa przełęczy", "Złożona mapa z zaznaczonymi przejazdami i miejscami, gdzie najczęściej zbiera się śnieg.", 0.2, 6, "straznica_pass_map_125", "tool"),),
        )
    if room_id == 126:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Dziedziniec Meldunkowy zbiera wszystkich, którzy muszą liczyć ludzi, konie i skrzynie. "
                "Ślady kół mieszają się tu z odciskami butów, a każda nowa karawana zostawia po sobie inny układ błota."
            ),
            inspectables={
                "ślady koła": "Koleiny pokazują, że najcięższe wozy muszą skręcać szeroko, żeby nie zaryć bokiem w kamień.",
                "tablica dyżury": "Na tablicy dyżurów wisi rozpiska wart i zmian. Kto czyta ją uważnie, oszczędza sobie krzyków później.",
                "palenisko dym": "W palenisku pali się powoli, bo tu bardziej liczy się ciepło dłoni niż ogień do ozdoby.",
            },
            items=(Item("dzwonek alarmowy", "Żelazny dzwonek do podniesienia straży, gdy w przełęczy dzieje się coś pilnego.", 0.6, 5, "straznica_alarm_bell_126", item_type="tool"),),
        )
    if room_id == 127:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Wieża Zwiadowców stoi wyżej niż reszta przejazdu i patrzy na szlak, zanim ten zdąży skręcić ku śniegu. "
                "Wieża stoi wyżej niż reszta przejazdu. Z jej okien widać skręt szlaku, śnieżne języki między skałami i dalekie ogniska na dole."
            ),
            inspectables={
                "luneta okno": "Przy oknie leży luneta z porysowaną soczewką. Zwiadowcy używają jej do liczenia karawan i śledzenia chmur.",
                "schody drewno": "Schody skrzypią, lecz są dobrze utrzymane. Nikt nie chce, by zwiadowca zsunął się przy pierwszym meldunku.",
                "chorągiew wiatr": "Mała chorągiewka na maszcie pokazuje wiatr lepiej niż większość rozmów w strażnicy.",
            },
            items=(
                Item("luneta strażnicza", "Prosta luneta do obserwacji traktu i górskich zakrętów.", 0.8, 8, "straznica_spyglass_127", "tool"),
                Item("zardzewiały grot włóczni", "Stary grot, wciąż ostry pod warstwą rdzy.", 0.25, 2, "rusty_spearhead_127", "tool"),
            ),
        )
    if room_id == 128:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Izba Przewodnika pachnie mapą, lampowym olejem i suchym sznurkiem. "
                "To tu rozplątuje się drogę dla ludzi, którzy nie chcą zejść z szlaku w złym miejscu."
            ),
            inspectables={
                "mapa stol": "Na stole leży mapa z odręcznymi uwagami o zakrętach, lawinach i miejscach, gdzie koń łamie krok.",
                "olej lampa": "Olej do lamp trzyma się w małych butelkach, bo przy przełęczy nigdy nie ma go za dużo.",
                "sznur notatki": "Notatki są przywiązane sznurkiem, żeby nie porwał ich wiatr wpadający przez uchylone okno.",
            },
            items=(
                Item("olej do lamp", "Mała butelka oleju na nocne czuwanie przy przełęczy.", 0.4, 3, "straznica_lamp_oil", "tool"),
                Item("zwój mapy", "Zwijana mapa przełęczy z zaznaczonymi ścieżkami i punktami widokowymi.", 0.2, 8, "straznica_pass_map", "tool"),
            ),
        )
    if room_id == 129:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Plac Karawan to niewielki, utwardzony skrawek ziemi, gdzie wozy ustawiają się w półkole przed dalszą drogą. "
                "Kupcy sprawdzają plomby, woźnice przeklinają zbocze, a straż liczy skrzynie tak, jakby każda była osobnym problemem."
            ),
            inspectables={
                "skrzynie plomby": "Skrzynie mają nowe plomby, ale na kilku widać już drobne pęknięcia po zimnym transporcie.",
                "wóz koło": "Koła wozów są obwiązane liną, żeby nie zjechały przy nawrocie na stromiznę.",
                "cła rachunki": "Rachunki za przejazd leżą przy skrzyni z pieczęciami. Nikt nie lubi, ale każdy je tu zna.",
            },
            items=(Item("list przewozowy", "Papier z rozpisaną karawaną, ładunkiem i pieczęcią przejazdu.", 0.1, 4, "straznica_manifest_129", "tool"),),
        )
    if room_id == 130:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Stajnie Wozów są niskie i ciasne, zbudowane bardziej pod koła niż pod wygodę ludzi. "
                "Tu naprawia się oś, wiąże uprząż i stawia klin, zanim droga zacznie zbyt mocno ciągnąć w dół."
            ),
            inspectables={
                "koło oś": "Przy ścianie stoją koła z zapasowymi obręczami i świeżym smarem.",
                "uprząż klin": "Uprzęże wiszą na hakach, a kliny są zawsze pod ręką, bo zbocze nie wybacza chwili spóźnienia.",
                "siano słoma": "Siano jest skromne, ale suche. W przełęczy to już brzmi jak luksus.",
            },
            items=(
                Item("zwój liny", "Mocny zwój liny do wozów, noszy i mocowania ładunku.", 2.6, 4, "straznica_rope", "tool"),
                Item("klin pod koło", "Drewniany klin do unieruchamiania wozu na zboczu.", 0.7, 2, "straznica_wheel_wedge", "tool"),
            ),
        )
    if room_id == 131:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Izba Podróżnych jest prostym schronieniem dla tych, którzy nie zdążyli zejść z przełęczy przed nocą. "
                "Ławy, koce i mały piecyk wystarczają, by człowiek przestał marznąć i zaczął myśleć rozsądniej."
            ),
            inspectables={
                "ławy koce": "Ławy są szorstkie, ale koce trzymają ciepło lepiej niż większość obietnic składanych na drodze.",
                "piecyk dym": "Piecyk daje równy żar i trochę dymu. W przełęczy to uczciwa wymiana.",
                "kubki woda": "Przy ścianie stoją kubki i dzban wody, gotowe dla zmęczonych gości.",
            },
            items=(Item("koc podróżny", "Gruby koc chroniący przed wiatrem na nocnym postoju.", 1.8, 5, "straznica_travel_blanket", "tool"),),
        )
    if room_id == 132:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Kaplica Przełęczy jest mała i surowa, ale podróżni zostawiają tu świece, kamyki i krótkie modlitwy. "
                "W kapliczce stoją świece, kamyki i mały dzwonek, a wiatr porusza tylko wstęgami przy wejściu."
            ),
            inspectables={
                "misa świece": "W kamiennej misie stoją świece, skrawki wosku i kilka drobnych monet.",
                "wstęgi dzwonek": "Wstęgi przy wejściu trzepoczą nawet przy słabszym wietrze.",
                "kamień cisza": "Kamień jest tu gładszy od reszty strażnicy, bo ludzie odruchowo ściszają głos.",
            },
            items=(
                Item("świeca pielgrzyma", "Krótka świeca pozostawiona przez podróżnych.", 0.2, 1, "straznica_pilgrim_candle_132", item_type="tool"),
                Item("worek soli", "Mały worek soli na drogę i do prostego posiłku.", 0.4, 2, "straznica_road_salt_132", "tool"),
            ),
        )
    if room_id == 133:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Ambona Myśliwego to wysoka półka skalna z widokiem na boczne zejście i kilka wystających skał, gdzie zwierzyna lubi się kryć. "
                "Kto zna tropy, ten widzi tu więcej niż tylko kamień."
            ),
            inspectables={
                "tropy śnieg": "Na cienkiej warstwie śniegu widać ślady kopyt, łap i podkutych butów.",
                "sidła narzędzia": "Sidła wiszą na haku obok narzędzi. Myśliwy trzyma wszystko blisko ręki.",
                "skóra futro": "Na belce suszą się skóry i futra, przesycone zimnym powietrzem i dymem z ognia.",
            },
            items=(
                Item("futro z kozicy", "Ciepłe futro z górskiej kozicy.", 1.9, 11, "straznica_chamois_fur", "armor", "korpus", protection=1),
            ),
        )
    if room_id == 134:
        return LocationContent(
            room_id=room_id,
            name=name,
            description=(
                "Brama do Dungrim zamyka Strażnicę Przełęczy od strony zachodniego zejścia. "
                "To ostatni punkt, w którym straż liczy pieczęcie, zanim droga spadnie ku wojskowemu fortowi."
            ),
            inspectables={
                "pieczęcie warta": "Pieczęcie leżą tu równo, bo bez nich nikt nie przejdzie dalej w stronę Dungrim.",
                "mur koleiny": "Mur ma tu głębokie koleiny od wozów i sań, które schodziły ze stromej strony przełęczy.",
                "śnieg znak": "Śnieg zbiera się przy murze w małe pasy, pokazując, skąd najczęściej wciska się wiatr.",
            },
            items=(Item("pieczęć przejazdu", "Pieczęć uprawniająca do przejazdu poza strażnicę.", 0.1, 3, "straznica_pass_seal_134", "tool"),),
        )
    feature_a = _D351E_PASS_FEATURES[index % len(_D351E_PASS_FEATURES)]
    feature_b = _D351E_PASS_FEATURES[(index + 2) % len(_D351E_PASS_FEATURES)]
    description = (
        f"{name}. {_D351E_PASS_ATMOSPHERE[index % len(_D351E_PASS_ATMOSPHERE)]} "
        "Przy przejeździe stoją tablice z rozkazami, listy opłat i stosy zapasowych belek."
    )
    inspectables = {feature_a[0]: feature_a[1], feature_b[0]: feature_b[1], "znaki rozkazy tablice": "Tablice są krótkie: opłaty, zakazy, ostrzeżenia przed śniegiem i lista tych, którzy nie wrócili."}
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables)


def _d351e_mountain_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351E_MOUNTAIN_FEATURES[index % len(_D351E_MOUNTAIN_FEATURES)]
    feature_b = _D351E_MOUNTAIN_FEATURES[(index + 3) % len(_D351E_MOUNTAIN_FEATURES)]
    feature_c = _D351E_MOUNTAIN_FEATURES[(index + 5) % len(_D351E_MOUNTAIN_FEATURES)]
    description = (
        f"{name}. {_D351E_MOUNTAIN_ATMOSPHERE[index % len(_D351E_MOUNTAIN_ATMOSPHERE)]} "
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
    "W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę.",
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
        f"{name}. {_D351F_MINE_ATMOSPHERE[index % len(_D351F_MINE_ATMOSPHERE)]} "
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
        f"{name}. {_D351F_CAVE_ATMOSPHERE[index % len(_D351F_CAVE_ATMOSPHERE)]} "
        "Na kamieniach widać ślady łap, otarte krawędzie i resztki sierści zaczepione o ostre odłamy skały."
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


_D351G_RUINS_NAMES = (
    "Zarośnięta Droga do Karshold", "Kamień Dawnej Granicy", "Przewrócony Obelisk", "Przedpole Spalonej Bramy", "Zawalona Brama Karshold",
    "Dziedziniec Popękanych Płyt", "Strażnica Bez Dachu", "Mur Zachodni Ruin", "Mur Wschodni Ruin", "Baszta Kruczych Gniazd",
    "Koszary pod Czarnym Stropem", "Stara Kuźnia Zamkowa", "Studnia Milczącej Wody", "Stajnia Złamanych Żłobów", "Spichlerz Bez Ziarna",
    "Dom Zarządcy Twierdzy", "Plac Broni Karshold", "Kaplica Pękniętego Progu", "Schody do Górnej Sali", "Wielka Sala Bez Chorągwi",
    "Sala Narad Przy Zawalonym Kominie", "Komnaty Wypalonych Belek", "Korytarz Zwęglonych Haków", "Biblioteka Pustych Półek", "Zbrojownia Zakleszczonych Drzwi",
    "Ogród Wewnętrzny pod Popiołem", "Zejście do Krypt", "Piwnice Zimnego Kamienia", "Tunel pod Murem", "Zawalona Komora Ostatniego Wyjścia",
)

_D351G_RUINS_ATMOSPHERE = (
    "Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli.",
    "Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać.",
    "Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem.",
    "Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać.",
    "Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje.",
)

_D351G_RUINS_FEATURES = (
    ("kamien kamień mur mury", "Kamienie są osmalone i popękane. Niektóre noszą ślady narzędzi, inne uderzeń z czasu oblężenia."),
    ("popiol popiół sadza ogien ogień", "Sadza weszła głęboko w szczeliny. Nawet po latach zostawia czarny ślad na palcach."),
    ("znak herb rzezba rzeźba", "Znak Karshold jest prawie starty: tarcza, trzy pionowe nacięcia i ptak o rozpostartych skrzydłach."),
    ("korzenie pnacza pnącza mech", "Korzenie wchodzą między kamienie cierpliwiej niż wojsko. Mur pęka tam, gdzie zieleń znalazła wodę."),
    ("kosci kości szczatki szczątki", "To głównie kości zwierząt, ale kilka fragmentów jest zbyt prostych i białych, by dało się je zignorować."),
    ("drzwi zawiasy belki", "Zawiasy zardzewiały w pozycji otwartej. Drewno pociemniało od wilgoci i dawnych płomieni."),
    ("slady ślady tropy", "Na ziemi mieszają się tropy lisów, wilków i ludzi, którzy najwyraźniej nie chcieli zostawiać wyraźnych śladów."),
    ("studnia woda wilgoc wilgoć", "Z głębi czuć zimną wilgoć. Dźwięk wrzuconego kamienia wróciłby późno, jeśli w ogóle."),
)

def _d351g_ruins_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351G_RUINS_FEATURES[index % len(_D351G_RUINS_FEATURES)]
    feature_b = _D351G_RUINS_FEATURES[(index + 3) % len(_D351G_RUINS_FEATURES)]
    feature_c = _D351G_RUINS_FEATURES[(index + 5) % len(_D351G_RUINS_FEATURES)]
    description = (
        f"{name}. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. "
        f"{_D351G_RUINS_ATMOSPHERE[index % len(_D351G_RUINS_ATMOSPHERE)]} "
        "Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza."
    )
    inspectables = {
        feature_a[0]: feature_a[1],
        feature_b[0]: feature_b[1],
        feature_c[0]: feature_c[1],
    }
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {425, 436, 443, 454}:
        items = (Item("odłamek osmalonego kamienia", "Czarny od sadzy fragment muru z Karshold.", 0.4, 2, f"karshold_burnt_stone_{room_id}"),)
    if room_id in {432, 441, 447, 452}:
        hidden_items = ((Item("zardzewiały znak Karshold", "Mały metalowy znak z niemal startym herbem dawnej twierdzy.", 0.05, 8, f"karshold_rusted_badge_{room_id}"), 13),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351g_content() -> tuple[LocationContent, ...]:
    return tuple(
        _d351g_ruins_content(room_id, index, name)
        for index, (room_id, name) in enumerate(zip(range(425, 455), _D351G_RUINS_NAMES))
    )


_D351H_SWAMP_NAMES = (
    "Błotna Ścieżka Hookri", "Trzcinowy Próg", "Rozlewisko Szarej Wody", "Sucha Kępa pod Wierzbą", "Stara Grobla",
    "Powalone Drzewo nad Topielą", "Grzęzawisko Cichych Bąbli", "Czarna Woda", "Mglista Polana", "Martwy Las",
    "Wyspa Torfowa", "Zarośla Ostrych Trzcin", "Martwe Wierzby", "Kanał Zimnego Mułu", "Chwiejąca się Kładka",
    "Błotny Krąg", "Mokradła Bez Ścieżki", "Zarośnięty Brzeg", "Zapadnięta Chata", "Kamienny Krąg w Mule",
    "Stary Ołtarz Hookri", "Serce Bagien", "Wyspa Mgieł", "Zawalona Grobla", "Wyjście ku Głębokiemu Lasowi",
)

_D351H_SWAMP_ATMOSPHERE = (
    "Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem.",
    "Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but.",
    "Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień.",
    "Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków.",
    "Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody.",
)

_D351H_SWAMP_FEATURES = (
    ("mgla mgła opar opary", "Mgła ogranicza widzenie do kilku kroków. Dalej wszystko rozpływa się w szarych, wilgotnych plamach."),
    ("torf bloto błoto mul muł", "Torf ugina się pod stopą i wypuszcza ciemną wodę o zapachu starego żelaza i zgnilizny."),
    ("trzciny sitowie zielsko", "Trzciny są wysokie, ostre i mokre. Poruszają się nawet wtedy, gdy nie czuć wiatru."),
    ("woda rozlewisko topiel", "Woda wygląda płytko, ale jej ciemny kolor nie pozwala odgadnąć dna."),
    ("groble kladka kładka deski", "Deski i groble są śliskie od porostów. Niektóre trzymają się bardziej pamięcią niż gwoździami."),
    ("wierzby drzewa korzenie", "Wierzby stoją pochylone, z korzeniami odsłoniętymi jak palce wyciągnięte z błota."),
    ("slady ślady tropy", "Ślady urywają się nagle przy wodzie. Nie wiadomo, czy ktoś skręcił, czy po prostu zniknął niżej."),
    ("kamienie krag krąg oltarz ołtarz", "Kamienie są niskie i omszałe. Ustawiono je dawno temu, zanim bagno zabrało resztę znaków."),
)

def _d351h_swamp_content(room_id: int, index: int, name: str) -> LocationContent:
    feature_a = _D351H_SWAMP_FEATURES[index % len(_D351H_SWAMP_FEATURES)]
    feature_b = _D351H_SWAMP_FEATURES[(index + 2) % len(_D351H_SWAMP_FEATURES)]
    feature_c = _D351H_SWAMP_FEATURES[(index + 5) % len(_D351H_SWAMP_FEATURES)]
    description = (
        f"{name}. {_D351H_SWAMP_ATMOSPHERE[index % len(_D351H_SWAMP_ATMOSPHERE)]} "
        "To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej."
    )
    inspectables = {
        feature_a[0]: feature_a[1],
        feature_b[0]: feature_b[1],
        feature_c[0]: feature_c[1],
    }
    items: tuple[Item, ...] = ()
    hidden_items: tuple[tuple[Item, int], ...] = ()
    if room_id in {475, 482, 490, 497}:
        items = (Item("garść torfowego ziela", "Wilgotne, ostro pachnące ziele zebrane na krawędzi mokradła.", 0.05, 3, f"hookri_bog_herb_{room_id}"),)
    if room_id in {481, 488, 495, 499}:
        hidden_items = ((Item("czarny kamyk z bagna", "Gładki, ciemny kamyk zimny nawet w dłoni.", 0.03, 5, f"hookri_black_stone_{room_id}"), 14),)
    if room_id == 475:
        hidden_items = ((Item("zestaw torfowych ziół", "Wiązka mokrych, lecz użytecznych roślin z mokradła.", 0.05, 4, "swamp_herbs_475"), 12),)
    if room_id == 481:
        items = (
            Item("wiązka trzcin", "Wiązka trzcin ściętych na suchszej kępie.", 0.4, 2, "swamp_reeds_481", "tool"),
        )
    if room_id == 495:
        items = (
            Item("kamienny talizman", "Ciężki, ciemny talizman znaleziony przy starym ołtarzu.", 0.2, 5, "swamp_talisman_495", "tool"),
        )
    if room_id == 499:
        hidden_items = ((Item("czarny kamyk bagienny", "Gładki, ciemny kamyk zimny nawet w dłoni.", 0.03, 5, "hookri_black_stone_499"), 14),)
    return LocationContent(room_id=room_id, name=name, description=description, inspectables=inspectables, items=items, hidden_items=hidden_items)


def _make_d351h_content() -> tuple[LocationContent, ...]:
    return tuple(
        _d351h_swamp_content(room_id, index, name)
        for index, (room_id, name) in enumerate(zip(range(475, 500), _D351H_SWAMP_NAMES))
    )

def make_content_pack() -> tuple[LocationContent, ...]:
    return START_CONTENT + _make_district_content() + _make_d351b_content() + _make_d351c_content() + _make_d351d_content() + _make_d351e_content() + _make_d351f_content() + _make_d351g_content() + _make_d351h_content()


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
        if content.forms:
            loc.forms.update(content.forms)
        if content.exit_forms:
            for direction, forms in content.exit_forms.items():
                loc.exit_forms[direction] = dict(forms)
        if content.scene_profile:
            loc.scene_profile = content.scene_profile
        for direction, kind in content.exit_kinds.items():
            if direction in loc.exits:
                loc.exits[direction].kind = kind
        for item in content.items:
            if item.vnum is None or all(existing.vnum != item.vnum for existing in loc.items):
                loc.items.append(item)
        for item, difficulty in content.hidden_items:
            if all(getattr(hidden.get("data"), "vnum", None) != item.vnum for hidden in loc.hidden_elements):
                loc.hidden_elements.append({"type": "item", "data": item, "difficulty": difficulty})
    from astergard.narrative import infer_exit_kind

    for loc in locations.values():
        for exit_ in loc.exits.values():
            if not exit_.kind:
                exit_.kind = infer_exit_kind(loc.zone, next((direction for direction, candidate in loc.exits.items() if candidate is exit_), ""), loc.name)
        for item in loc.items:
            if not item.presentation_category:
                item.presentation_category = item.scene_category()
            if not item.scene_position:
                item.scene_position = {
                    "portable_item": "na ziemi",
                    "corpse": "na ziemi",
                    "furniture": "pod ścianą",
                    "container": "pod ścianą",
                    "resource": "w otoczeniu",
                    "fixture": "w otoczeniu",
                    "scenery": "w otoczeniu",
                }.get(item.presentation_category, "na ziemi")
