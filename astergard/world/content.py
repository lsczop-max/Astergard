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

_DISTRICT_OVERRIDES: dict[int, LocationContent] = {
    2: LocationContent(
        room_id=2,
        name="Główny Plac Astergardu",
        description=(
            "Sercem miasta jest szeroki plac, na którym spotykają się kupcy, żołnierze i ludzie bez stałego zajęcia. "
            "Bruk jest tu lepiej utrzymany niż w bocznych ulicach, lecz wciąż nosi ślady kół i końskich podków. "
            "Nad wszystkim wiszą mokre flagi i dym z pieców, a echo kroków odbija się od fasad jak od wnętrza studni."
        ),
        inspectables={
            "studnia fontanna": "Kamienna studnia ma niski cembrowinowy krąg i żelazny kubeł na łańcuchu. Woda jest zimna i lekko słona od miejskiego pyłu.",
            "ogloszenia tablica słup": "Na słupie wiszą wyblakłe ogłoszenia o targach, straży i zaginionych rzeczach. Dwa z nich są dopisane ręką pisarza, nie urzędnika.",
            "straz żołnierze ludzie": "Plac należy do wszystkich i nikogo. Straż patrzy tu nie na tłum, lecz na kieszenie i dłonie.",
        },
        items=(
            Item("ława targowa", "Niska, ciężka ława z ciemnego drewna. Służyła kupcom i czekającym klientom.", 5.0, 8, "market_bench_02", item_type="furniture"),
            Item("skrzynia targowa", "Porysowana skrzynia po solonych śledziach i płótnie.", 2.4, 4, "market_crate_02", is_container=True, capacity=18),
        ),
    ),
    12: LocationContent(
        room_id=12,
        name="Kuźnia przy Murze",
        description=(
            "Kowalski ogień bije tu przez szczeliny w ścianach i barwi kurz na czerwono. W powietrzu wisi zapach węgla, spalonego smaru i rozgrzanego żelaza. "
            "Każdy dźwięk młota zdaje się krótszy niż w innych częściach miasta, jakby sam mur połykał resztę hałasu."
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
    ),
    14: LocationContent(
        room_id=14,
        name="Karczma pod Żurawiem",
        description=(
            "Karczma stoi ciężko przy ulicy, z niskim dachem i szerokim wejściem od głównego szlaku w mieście. "
            "Przez otwarte okna wypływa zapach warzonego piwa, tłuszczu i mokrych płaszczy. "
            "To miejsce jest głośne tylko wtedy, gdy jeszcze nie zapadła noc albo gdy ktoś właśnie postawił ostatni kubek na stole."
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
            "Świątynia nie błyszczy złotem ani szkłem. Jest zbudowana z ciemnego kamienia i niskich filarów, które znoszą dym z setek świec. "
            "Wewnątrz pachnie popiołem, woskiem i chłodną wodą na kamiennym progu, jakby modlitwy miały tu zawsze najpierw obmyć stopy."
        ),
        inspectables={
            "oltarz ołtarz": "Ołtarz jest prosty, z popękanym blatem i metalową misą na ofiary z oliwy i wosku.",
            "swiece wosk": "Świece palą się nierówno, ale nikt nie gasi ich przed czasem. Wosk spływa grubymi smugami po kamieniu.",
            "kaplani modlitwa": "Kapłani mówią niewiele, lecz ich obecność uspokaja tych, którzy przyszli tu zbyt późno na zwykłe słowa.",
        },
        items=(
            Item("woskowa świeca", "Gruba świeca, jeszcze nieodpalona.", 0.2, 1, "wax_candle_37"),
            Item("drewniana ławka", "Prosta ławka dla modlących się lub czekających.", 4.0, 6, "chapel_bench_37", item_type="furniture"),
        ),
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
        ),
    ),
    39: LocationContent(
        room_id=39,
        name="Most Rzeczny",
        description=(
            "Most łączy oba brzegi niewielkiej rzeki, która wcina się w miasto jak cienki, żywy nóż. "
            "Deski są mokre od mgły i rzeki, a pod spodem słychać tylko szum wody, zbyt cichy, by uspokoić człowieka przyzwyczajonego do kamiennych murów. "
            "To miejsce wygląda skromnie, ale bez niego port i targ oddzieliłaby długa droga wokół bagiennych brzegów."
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
            "Na rynku handluje się wszystkim, co można zważyć, zwinąć albo wycenić bez patrzenia w oczy. "
            "Wózki z żelazem stoją obok skrzyń z tkaniną, a przekupki wybijają rytm targu głosami ostrzejszymi niż noże rzeźników. "
            "Tu Astergard pokazuje swoją prawdziwą twarz: nie królewską, lecz kupiecką."
        ),
        inspectables={
            "kramy stragany": "Stragany są zasłane płótnem, skórą i odłamkami metalu. Każdy sprzedawca ma inną historię, ale te same obcasy.",
            "wagi odważniki": "Wagi są pilnowane surowiej niż uczciwość. Obok leżą odważniki z wybitymi znakami cechu.",
            "handel kupcy": "Kupcy mówią szybko, lecz milkną, gdy widzą straż. Wtedy wszyscy nagle przypominają sobie o przepisach.",
        },
        items=(
            Item("odważnik targowy", "Mały odważnik z wybitym znakiem rynku.", 0.7, 5, "market_weight_47"),
            Item("skrzynka na przyprawy", "Niska skrzynka po cennych przyprawach i ziołach.", 1.5, 9, "spice_crate_47", is_container=True, capacity=12),
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
    60: LocationContent(
        room_id=60,
        name="Błotna Brama",
        description=(
            "Podgrodzie zaczyna się od błota, kolein i wąskich domów przyklejonych do palisady. "
            "To pierwszy teren poza kamieniem miasta, gdzie ludzie żyją bliżej zwierząt, wozów i deszczu. "
            "Nie ma tu ceremonialnego wejścia w świat pracy - jest tylko nieustanne brudzenie butów."
        ),
        inspectables={
            "brama palisada": "Brama jest prostsza niż miejska, lecz nosi na sobie te same ślady po naprawach i pośpiechu.",
            "błoto koleiny": "Błoto wypełnia koleiny po kostki. Widać, że drogi nikt tu nie oszczędza.",
            "domy chaty": "Domy są niskie, ciasne i ogrzewane tak oszczędnie, jakby drewno było złotem.",
        },
        items=(Item("drewniane wiadro", "Wiadro z grubych klepek, dobre do noszenia wody albo zboża.", 1.1, 3, "bucket_60", item_type="tool"),),
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
        items=(Item("kij mierniczy", "Prosty kij do odmierzania pola i płotu.", 0.8, 2, "measuring_staff_70", item_type="tool"),),
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
            "Na belkach wiszą skóry, łuki i świeżo zdjęte trofea. Mężczyźni i kobiety z osady liczą tutaj zdobycz, dzielą się mięsem i kłócą o ślady."
        ),
        inspectables={
            "skory futra": "Skóry wiszą gęsto, suszone przy dymie. Niektóre są przeznaczone na handel, inne na własne buty i rękawice.",
            "łuki bełty": "Łuki są proste, lecz dobrze dopasowane do zimnego lasu. Bełty i strzały mają różne długości, bo nikt nie poluje tu z jednego powodu.",
            "tropy slady": "W glinie placu widać ślady psów, łasic i ludzi wracających z lasu późnym wieczorem.",
        },
        items=(
            Item("łuk myśliwski", "Lekki łuk z ciemnego drewna.", 1.2, 15, "hunter_bow_100", item_type="weapon", slot="prawa_reka", damage_type="pociskowa", base_damage=4, reach=2),
            Item("kołczan strzał", "Skórzany kołczan z garścią długich strzał.", 1.8, 10, "hunter_quiver_100", item_type="tool"),
        ),
    ),
    110: LocationContent(
        room_id=110,
        name="Brama Dungrim",
        description=(
            "Forteca Dungrim stoi na drodze jak zaciśnięta pięść. Brama jest wąska, wzmocniona żelazem i patrzona przez ludzi, którzy nie zadają pytań dwa razy. "
            "To miejsce żyje rozkazem, zapasem i obawą przed tym, co może przyjść z traktu albo z pustki za nim."
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


def _district_content(room_id: int, index: int, name: str) -> LocationContent:
    override = _DISTRICT_OVERRIDES.get(room_id)
    if override is not None:
        return override
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
        f"{name} należy do Ruin Karshold, dawnej twierdzy granicznej spalonej podczas wojny, "
        f"o której miejscowi mówią tylko wtedy, gdy ogień w palenisku jest już niski. "
        f"{_D351G_RUINS_ATMOSPHERE[index % len(_D351G_RUINS_ATMOSPHERE)]} "
        "To miejsce nie służy już obronie granicy; teraz broni tylko własnych sekretów."
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
        f"{name} należy do Bagien Hookri, rozległego mokradła na skraju starych traktów i zapomnianych ruin. "
        f"{_D351H_SWAMP_ATMOSPHERE[index % len(_D351H_SWAMP_ATMOSPHERE)]} "
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
        for item in content.items:
            if item.vnum is None or all(existing.vnum != item.vnum for existing in loc.items):
                loc.items.append(item)
        for item, difficulty in content.hidden_items:
            if all(getattr(hidden.get("data"), "vnum", None) != item.vnum for hidden in loc.hidden_elements):
                loc.hidden_elements.append({"type": "item", "data": item, "difficulty": difficulty})
