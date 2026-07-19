# D58.2 Centrum Twierdzy Pilot

## Verdict
CENTRUM_PILOT_READY_FOR_HUMAN_REVIEW

## Selection
- #14 Karczma pod Żurawiem (start): Punkt startowy nowej postaci i najważniejszy pierwszy interioryzowany punkt miasta.
- #15 Tyły Karczmy (inn_adjacency): Najbliższe zaplecze karczmy, naturalny drugi krok po starcie.
- #2 Główny Plac Astergardu (main_square): Główny plac, czyli centralny węzeł orientacyjny pierwszej godziny.
- #13 Szeroka Brukowana (important_street): Główna ulica spinająca karczmę, kuźnię i ruch pieszy w centrum.
- #4 Podcienia Kupieckie (passage): Wąskie podcienia handlowe, czyli ważne przejście między placem a zapleczem zabudowy.
- #12 Kuźnia przy Murze (workshop): Kuźnia, czyli czytelny warsztat i mocny punkt funkcjonalny miasta.
- #47 Rynek Żelazny (trade_point): Najważniejszy punkt handlowy pilota i właściwy rynek cechowy.
- #37 Świątynia Popiołu (religious_site): Religijny kontrapunkt dla świeckiego centrum oraz czytelny landmark.
- #55 Rozstaje Traktów (city_edge_gate): Skraj miasta i wyjście w stronę obszaru zewnętrznego.
- #59 Kapliczka Przydrożna (trakt_connection): Bezpośrednie połączenie z Traktem, potrzebne do domknięcia pierwszej godziny.

## Manual Review Cards
### #14 Karczma pod Żurawiem
- Slot: `start`
- Removed issues: LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, repetitive_opening, repetitive_closure, UNNATURAL_POLISH, ai_like
- Preserved facts: zachowane wyjścia: polnoc->5, poludnie->15, zachod->13, zachowane przedmioty: beczka piwa, dębowa ława, miska gulaszu, zachowani NPC: karczmarz
- Added inspectables: none
- Neighbor consistency: Karczma pod Żurawiem nadal łączy się z Karczma pod Żurawiem, Szeroka Brukowana
- Risk or dependency: W kolejnym etapie warto wyrównać ton sąsiednich lokacji 5 i 13, żeby wejście do karczmy nie było jedynym mocnym punktem tego pasa.
- Score: 4 -> 8

Before
```text
Karczma pod Żurawiem
Karczma stoi ciężko przy ulicy, z niskim dachem i szerokim wejściem od głównego szlaku w mieście. Przez otwarte okna wypływa zapach warzonego piwa, tłuszczu i mokrych płaszczy. Przy stołach słychać urywane rozmowy, ktoś odstawia kufel z brzękiem, a od paleniska idzie zapach pieczonego mięsa i mokrego drewna. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Pachnie piwem, pieczonym mięsem, dymem i mokrym drewnem. Ławy są wygładzone od łokci, a próg ma rysy od butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Pod ścianą stoi beczka piwa.
Na ziemi leży miska gulaszu.
Pod ścianą stoi dębowa ława.
Karczmarz ociera dłonie o fartuch i patrzy na gości bez zaufania, zamiata próg i otwiera karczmę i ustawia stoły przy wejściu.
Na północy drzwi prowadzą dalej. Na południu drzwi prowadzą dalej. Na zachodzie drzwi prowadzą dalej.
```
After
```text
Karczma pod Żurawiem
Niski dach Karczmy pod Żurawiem schodzi niemal do poziomu ganku, a od zachodu widać szerokie drzwi od Szerokiej Brukowanej. Z izby wypływa zapach piwa, pieczonego mięsa i mokrego drewna, a przy stołach słychać urywane rozmowy i brzęk kufli. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Pachnie piwem, pieczonym mięsem, dymem i mokrym drewnem. Ławy są wygładzone od łokci, a próg ma rysy od butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Pod ścianą stoi beczka piwa.
Na ziemi leży miska gulaszu.
Pod ścianą stoi dębowa ława.
Karczmarz ociera dłonie o fartuch.
Na północy drzwi prowadzą w stronę zaułek za karczmą. Na południu drzwi prowadzą w stronę tyły karczmy. Na zachodzie drzwi prowadzą w stronę szeroka brukowana.
```

### #15 Tyły Karczmy
- Slot: `inn_adjacency`
- Removed issues: LIST_LIKE_DESCRIPTION, NO_LANDMARK, TEMPLATE_ENDING
- Preserved facts: zachowane wyjścia: polnoc->14, wschod->16, zachowane przedmioty: brak, zachowani NPC: brak
- Added inspectables: none
- Neighbor consistency: Tyły Karczmy nadal łączy się z Karczma pod Żurawiem, Mała Stajnia
- Risk or dependency: Brak blokującej zależności; zaplecze karczmy może iść do przeglądu razem z kolejnymi zapleczami centrum.
- Score: 5 -> 8

Before
```text
Tyły Karczmy
Tyły Karczmy należy do wąskiego zaplecza za kuchennym wejściem. Przy ścianie stoją puste beczki, skrzynie po warzywach i poplamiony stół do czyszczenia kufli. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Pachnie piwem, pieczonym mięsem, dymem i mokrym drewnem. Ławy są wygładzone od łokci, a próg ma rysy od butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na północy drzwi prowadzą dalej. Na wschodzie drzwi prowadzą dalej.
```
After
```text
Tyły Karczmy
Wąskie zaplecze za kuchennym wejściem mieści puste beczki, skrzynie po warzywach i stół do czyszczenia kufli. To krótki pas desek między kuchnią a stajnią, gdzie wszystko nosi ślady tłuszczu i mokrych łap. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Pachnie piwem, pieczonym mięsem, dymem i mokrym drewnem. Ławy są wygładzone od łokci, a próg ma rysy od butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na północy drzwi prowadzą w stronę karczma pod żurawiem. Na wschodzie drzwi prowadzą w stronę mała stajnia.
```

### #2 Główny Plac Astergardu
- Slot: `main_square`
- Removed issues: LIST_LIKE_DESCRIPTION, OVERLOADED_RENDER, PLAYER_EMOTION, TEMPLATE_ENDING, UNNATURAL_POLISH, ai_like
- Preserved facts: zachowane wyjścia: poludnie->10, wschod->3, zachod->1, zachowane przedmioty: skrzynia targowa, ława targowa, zachowani NPC: strażnik
- Added inspectables: none
- Neighbor consistency: Główny Plac Astergardu nadal łączy się z Główny Plac Astergardu, Plac Przed Wartownią, Boczne Uliczki Placu
- Risk or dependency: Plac jest kluczowy jako landmark; dalsze wyrównanie narracji powinno objąć placowe sąsiedztwo, ale pilot już trzyma kierunek.
- Score: 4 -> 8

Before
```text
Główny Plac Astergardu
Sercem miasta jest szeroki plac, na którym spotykają się kupcy, żołnierze i ludzie bez stałego zajęcia. Bruk jest tu lepiej utrzymany niż w bocznych ulicach, lecz wciąż nosi ślady kół i końskich podków. Nad wszystkim wiszą mokre flagi i dym z pieców, a echo kroków odbija się od fasad. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Pod ścianą stoi ława targowa.
Pod ścianą stoi skrzynia targowa.
Strażnik miasta opiera włócznię o ramię, zamiata próg i obchodzi bramę i sprawdza, czy bruk jest czysty po nocy.
Na zachodzie brama prowadzi dalej. Na wschodzie brama prowadzi dalej. Na południu brama prowadzi dalej.
```
After
```text
Główny Plac Astergardu
Szeroki plac leży przed strażniczym ramieniem miasta, tam gdzie bruk jest równiejszy niż w bocznych ulicach. Między fasadami stoją flagi, studnia i skrzynie targowe, a od zachodu dochodzi cięższy ruch przy wartowni. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Pod ścianą stoi ława targowa.
Pod ścianą stoi skrzynia targowa.
Strażnik miasta opiera włócznię o ramię, zamiata próg i obchodzi bramę i sprawdza, czy bruk jest czysty po nocy.
Na zachodzie brama prowadzi w stronę plac przed wartownią. Na wschodzie brama prowadzi w stronę boczne uliczki placu. Na południu brama prowadzi w stronę dom snycerza.
```

### #13 Szeroka Brukowana
- Slot: `important_street`
- Removed issues: LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, repetitive_opening, repetitive_closure, ai_like
- Preserved facts: zachowane wyjścia: polnocny-wschod->4, wschod->14, zachod->12, zachowane przedmioty: brak, zachowani NPC: brak
- Added inspectables: beczki
- Neighbor consistency: Szeroka Brukowana nadal łączy się z Karczma pod Żurawiem, Kuźnia przy Murze, Podcienia Kupieckie
- Risk or dependency: Sąsiednia 4 wymagała własnego override, więc dalszy pas ulic trzeba będzie odświeżać w parach.
- Score: 3 -> 8

Before
```text
Szeroka Brukowana
W kącie zebrano stare beczki, tak suche, że przy dotknięciu mogłyby rozsypać się jak kora. W takich miejscach szeroka brukowana zwykle brzmi sucho, ale dziś trzyma się naturalnie. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na zachodzie brama prowadzi dalej. Na wschodzie brama prowadzi dalej. Na północnym wschodzie brama prowadzi dalej.
```
After
```text
Szeroka Brukowana
Szeroka Brukowana łączy karczmę z kuźnią i prowadzi przez środek miejskiego ruchu. Przy ścianach stoją suche beczki, a bruk jest tu gładki od wozów i butów. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na zachodzie brama prowadzi w stronę kuźnia przy murze. Na wschodzie brama prowadzi w stronę karczma pod żurawiem. Na północnym wschodzie brama prowadzi w stronę podcienia kupieckie.
```

### #4 Podcienia Kupieckie
- Slot: `passage`
- Removed issues: ABSTRACT_NARRATOR, LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, cliche_phrase, repetitive_opening, repetitive_closure
- Preserved facts: zachowane wyjścia: poludniowy-wschod->5, poludniowy-zachod->13, zachod->3, zachowane przedmioty: brak, zachowani NPC: brak
- Added inspectables: fasady podcienia, okna okiennice
- Neighbor consistency: Podcienia Kupieckie nadal łączy się z Podcienia Kupieckie, Boczne Uliczki Placu, Zaułek za Karczmą, Szeroka Brukowana
- Risk or dependency: Przejście łączy się z 3 i 13, więc rozszerzenie stylu powinno objąć także placowe odnogi.
- Score: 3 -> 8

Before
```text
Podcienia Kupieckie
Między fasadami podcienia kupieckie okiennice są przymknięte. Ludzie patrzą przez szpary, ale szybko cofają twarze. wiatr nie ma tu miejsca, więc wciska się w szczeliny i porusza tylko kurzem przy ziemi. na ziemi widać kilka świeżych plam błota, jakby ktoś przyszedł tu z drogi spoza murów. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na zachodzie brama prowadzi dalej. Na południowym wschodzie brama prowadzi dalej. Na południowym zachodzie brama prowadzi dalej.
```
After
```text
Podcienia Kupieckie
Podcienia Kupieckie ściskają przejście między fasadami, a kamień zostaje tu na chwilę bez wiatru. Okiennice są przymknięte, pod progiem leży błoto znad drogi, i łatwo stąd wrócić ku placowi albo karczmie. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na zachodzie brama prowadzi w stronę boczne uliczki placu. Na południowym wschodzie brama prowadzi w stronę zaułek za karczmą. Na południowym zachodzie brama prowadzi w stronę szeroka brukowana.
```

### #12 Kuźnia przy Murze
- Slot: `workshop`
- Removed issues: ABSTRACT_NARRATOR, LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, cliche_phrase, repetitive_opening, repetitive_closure
- Preserved facts: zachowane wyjścia: poludniowy-zachod->22, wschod->13, zachod->11, zachowane przedmioty: kowalski młot, pochodnia kuźnicza, szczypce kowalskie, zachowani NPC: kowal
- Added inspectables: none
- Neighbor consistency: Kuźnia przy Murze nadal łączy się z Kuźnia przy Murze, Stary Spichlerz, Szeroka Brukowana, Jatki Rzeźników
- Risk or dependency: Kuźnia jest bezpieczna, ale sąsiedztwo 11 i 22 wciąż będzie wymagać później wyrównania barwy.
- Score: 4 -> 8

Before
```text
Kuźnia przy Murze
Kowalski ogień bije tu przez szczeliny w ścianach i barwi kurz na czerwono. W powietrzu wisi zapach węgla, spalonego smaru i rozgrzanego żelaza. Każdy dźwięk młota zdaje się krótszy niż w innych częściach miasta, jakby sam mur połykał resztę hałasu. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Czuć rozgrzany metal, węgiel i pył ze skały. Krawędzie stołów są okopcone, a ściany noszą ślady sadzy i uderzeń. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na ziemi leżą kowalski młot, szczypce kowalskie oraz pochodnia kuźnicza.
Kowal ma dłonie zgrubiałe od ognia i młota, wyprowadza zwierzęta i otwiera warsztat i rozpala ogień.
Na zachodzie brama prowadzi dalej. Na wschodzie brama prowadzi dalej. Na południowym zachodzie brama prowadzi dalej.
```
After
```text
Kuźnia przy Murze
Kuźnia przy Murze trzyma się nisko przy kamiennym boku ulicy, a na wschodzie zaczyna się Szeroka Brukowana. Ogień bije przez szczeliny, kurz przy wejściu czerwienieje od żaru, a każdy cios młota odbija się krótko od muru. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Czuć rozgrzany metal, węgiel i pył ze skały. Krawędzie stołów są okopcone, a ściany noszą ślady sadzy i uderzeń. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na ziemi leżą kowalski młot, szczypce kowalskie oraz pochodnia kuźnicza.
Kowal ma dłonie zgrubiałe od ognia i młota, zamiata próg i otwiera warsztat i rozpala ogień.
Na zachodzie brama prowadzi w stronę stary spichlerz. Na wschodzie brama prowadzi w stronę szeroka brukowana. Na południowym zachodzie brama prowadzi w stronę jatki rzeźników.
Gdzieś dalej trzaśnie gałąź, a potem wraca zwykły ruch ulicy.
```

### #47 Rynek Żelazny
- Slot: `trade_point`
- Removed issues: LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, repetitive_opening, repetitive_closure, ai_like
- Preserved facts: zachowane wyjścia: polnoc->46, poludniowy-wschod->52, zachod->48, zachowane przedmioty: kosz targowy, odważnik targowy, skrzynka na przyprawy, zachowani NPC: brak
- Added inspectables: none
- Neighbor consistency: Rynek Żelazny nadal łączy się z Rynek Żelazny, Kram Świecarza, Warsztat Cieśli, Skład Drewna
- Risk or dependency: Rynek ma czytelny rdzeń, ale okolica 46/48/52 nadal będzie wymagała dalszego dopasowania w kolejnej turze.
- Score: 4 -> 8

Before
```text
Rynek Żelazny
Na rynku handluje się wszystkim, co można zważyć, zwinąć albo wycenić bez patrzenia w oczy. Wózki z żelazem stoją obok skrzyń z tkaniną, a przekupki wybijają rytm targu głosami ostrzejszymi niż noże rzeźników. Tu Astergard pokazuje swoją prawdziwą twarz: nie królewską, lecz kupiecką. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na ziemi leży odważnik targowy.
Pod ścianą stoją skrzynka na przyprawy i kosz targowy.
Na północy brama prowadzi dalej. Na zachodzie brama prowadzi dalej. Na południowym wschodzie brama prowadzi dalej.
```
After
```text
Rynek Żelazny
Rynek Żelazny rozkłada się szeroko między kramami i warsztatami. Wózki z żelazem stoją obok skrzyń z tkaniną, a przekupki pilnują wag ostrzej niż własnych sakiew. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na ziemi leży odważnik targowy.
Pod ścianą stoją skrzynka na przyprawy i kosz targowy.
Na północy brama prowadzi w stronę kram świecarza. Na zachodzie brama prowadzi w stronę warsztat cieśli. Na południowym wschodzie brama prowadzi w stronę skład drewna.
```

### #37 Świątynia Popiołu
- Slot: `religious_site`
- Removed issues: ABSTRACT_NARRATOR, LIST_LIKE_DESCRIPTION, NON_INTERACTIVE_DETAIL, TEMPLATE_ENDING, cliche_phrase, repetitive_opening
- Preserved facts: zachowane wyjścia: polnoc->36, zachod->38, zachowane przedmioty: drewniana ławka, wiązka ziół, woskowa świeca, zachowani NPC: brak
- Added inspectables: none
- Neighbor consistency: Świątynia Popiołu nadal łączy się z Świątynia Popiołu, Przedsionek Świątyni, Port Rzeczny
- Risk or dependency: Świątynia ma własną tożsamość, lecz port i przedsionek zostają zależnością dla osobnego passu.
- Score: 4 -> 8

Before
```text
Świątynia Popiołu
Świątynia nie błyszczy złotem ani szkłem. Jest zbudowana z ciemnego kamienia i niskich filarów, które znoszą dym z setek świec. Wewnątrz pachnie popiołem, woskiem i chłodną wodą na kamiennym progu, jakby modlitwy miały tu zawsze najpierw obmyć stopy. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na ziemi leżą woskowa świeca i wiązka ziół.
Pod ścianą stoi drewniana ławka.
Na północy brama prowadzi dalej. Na zachodzie brama prowadzi dalej.
```
After
```text
Świątynia Popiołu
Świątynia Popiołu stoi z ciemnego kamienia między przedsionkiem a portem. Niskie filary tłumią odgłos kroków, a po progu rozciąga się wosk i chłodna woda. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na ziemi leżą woskowa świeca i wiązka ziół.
Pod ścianą stoi drewniana ławka.
Na północy brama prowadzi w stronę przedsionek świątyni. Na zachodzie brama prowadzi w stronę port rzeczny.
```

### #55 Rozstaje Traktów
- Slot: `city_edge_gate`
- Removed issues: LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, repetitive_opening, repetitive_closure, ai_like
- Preserved facts: zachowane wyjścia: polnoc->54, poludniowy-wschod->59, wschod->95, zachod->56, zachowane przedmioty: brak, zachowani NPC: brak
- Added inspectables: kamień graniczny, słup drogowy
- Neighbor consistency: Rozstaje Traktów nadal łączy się z Rozstaje Traktów, Zaułek Czeladników, Opuszczona Chata, Kapliczka Przydrożna, Wschodnia Furta Łowców
- Risk or dependency: Rozstaje są pierwszym krokiem na zewnątrz, ale pełna sekwencja 56/58/59/95 powinna zostać domknięta w jednym etapie.
- Score: 3 -> 8

Before
```text
Rozstaje Traktów
Rozstaje otwierają się poza miasto jak wybór, który zawsze przychodzi za późno. Tutaj drogi rozchodzą się ku polom, młynowi i mostowi, a każdy skręt ma na sobie ślady kół i decyzji. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Pachnie sianem, końską skórą i mokrą deską. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na północy brama prowadzi dalej. Na zachodzie brama prowadzi dalej. Na południowym wschodzie brama prowadzi dalej. Na wschodzie brama prowadzi dalej.
```
After
```text
Rozstaje Traktów
Na skraju miasta bruk przechodzi w koleiny, a rozstaje zbierają ruch z furty łowców, kapliczki i opuszczonej chaty. Kamień graniczny ma odłupany róg i biały ślad po kredzie, jakby ktoś jeszcze rano sprawdzał kierunek. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. Pachnie sianem, końską skórą i mokrą deską. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Na północy brama prowadzi w stronę zaułek czeladników. Na zachodzie brama prowadzi w stronę opuszczona chata. Na południowym wschodzie brama prowadzi w stronę kapliczka przydrożna. Na wschodzie brama prowadzi w stronę wschodnia furta łowców.
```

### #59 Kapliczka Przydrożna
- Slot: `trakt_connection`
- Removed issues: ABSTRACT_NARRATOR, LIST_LIKE_DESCRIPTION, TEMPLATE_ENDING, cliche_phrase, repetitive_opening
- Preserved facts: zachowane wyjścia: polnocny-zachod->55, poludniowy-wschod->135, zachod->58, zachowane przedmioty: brak, zachowani NPC: podróżny
- Added inspectables: próg bruku
- Neighbor consistency: Kapliczka Przydrożna nadal łączy się z Kapliczka Przydrożna, Rozstaje Traktów, Pastwiska, Kapliczka Podróżnych za Murem
- Risk or dependency: Połączenie z Traktem jest kluczowe, ale dalszy odcinek 135 wymaga osobnego sprawdzenia sąsiednich lokacji.
- Score: 4 -> 8

Before
```text
Kapliczka Przydrożna
Kapliczka stoi przy drodze jak ostatni znak przed dalszą, mniej pewną częścią świata. W niszy z kamienia zostawiono wstążki, monetę i wyblakły kawałek chleba. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Podróżny stoi z sakwą przy nodze i ogląda miasto tak, jakby wciąż szukał wyjścia, sprawdza zamki i rusza od bramy do karczmy i sprawdza, czy droga jest bezpieczna.
Na zachodzie brama prowadzi do pastwisky. Na północnym zachodzie brama prowadzi dalej. Na południowym wschodzie brama prowadzi dalej.
```
After
```text
Kapliczka Przydrożna
Kamienna kapliczka stoi przy samym wylocie bruku, tam gdzie ostatni kamień przechodzi w koleiny traktu. W niszy leżą wstążki, moneta i kawałek chleba, a za plecami zostaje już miasto. Świt rozprasza ciemność. Lato trzyma ciepło.
Z ulicy słychać wozy, nawoływania i szczekanie psów. W nos uderza dym z palenisk, mokry bruk i zapach pieczywa. Bruk jest wygładzony przez koła wozów i wiele par butów. Rano ktoś otwiera drzwi, zamiata próg albo rozpala ogień.
Podróżny stoi z sakwą przy nodze i ogląda miasto tak, jakby wciąż szukał wyjścia, rozpala piec i rusza od bramy do karczmy i sprawdza, czy droga jest bezpieczna.
Na zachodzie brama prowadzi w stronę pastwiska. Na północnym zachodzie brama prowadzi w stronę rozstaje traktów. Na południowym wschodzie brama prowadzi w stronę kapliczka podróżnych za murem.
```

## Files Changed
- `astergard/narrative.py`
- `astergard/npcs/models.py`
- `astergard/world/content.py`
- `tests/test_d34_world_area_expansion.py`
- `tests/test_d58_2_centrum_pilot.py`
- `docs/audits/D58_2_CENTRUM_PILOT.md`
- `docs/audits/D58_2_CENTRUM_PILOT_DATA.json`

## Unresolved Dependencies
- Pilotaż obejmuje tylko 10 lokacji; pozostałe 50 lokacji Centrum Twierdzy pozostają do osobnego passu.
- Sąsiednie lokacje poza pilotem nadal mają starszy ton i będą wymagały kolejnej redakcji, jeśli rozszerzamy styl hurtowo.

## Verification
- `ruff check astergard tests scripts` -> pass
- `mypy astergard tests scripts` -> pass
- `pytest -q` -> pass (`471 passed, 18 subtests passed`)

## Expandability
Pilot style is safe to extend to the remaining 50 Centrum Twierdzy locations, provided adjacent rooms are rebalanced in the same pass where needed.
