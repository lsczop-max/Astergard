# AUDIT_D51_COMBAT_BASELINE

## 1. Aktualna architektura walki

Obecny system walki jest zbudowany wokół jednego głównego resolvera:

- `astergard/combat/manager.py` rozstrzyga inicjatywę, trafienie, obronę, redukcję pancerza, zadawanie ran i śmierć.
- `astergard/application/services/combat_service.py` pełni rolę cienkiej warstwy use-case: wyszukuje cel, wywołuje `CombatManager.attack()`, spawnuje zwłoki, aktualizuje reputację i emituje zdarzenia domenowe.
- `astergard/application/heartbeat.py` uruchamia rundy aktywnych starć w ticku serwera, a także AI NPC, respawn i regenerację.

Mechanika jest dziś scentralizowana i sprzężona z tekstem. `CombatManager.attack()` zwraca `CombatResult`, ale wynik zawiera już gotowe komunikaty dla gracza i obserwatora. To oznacza, że rozstrzygnięcie mechaniczne i narracja nie są rozdzielone.

### Kluczowe elementy obecnego przepływu

- Atak wykorzystuje jedną ścieżkę dla walki wręcz i dystansowej.
- Inicjatywa jest liczona wprost z cech, umiejętności, morale, pancerza i losowości.
- Obrona jest realizowana jako:
  - unik porównywany z wynikiem ataku,
  - blok tarczą,
  - parowanie bronią.
- Miejsce trafienia jest losowane z prostych wag body-partów.
- Pancerz działa jako liniowa redukcja obrażeń.
- Rany są przechowywane jako liczby całkowite na częściach ciała.
- Śmierć jest wyznaczana przez `is_dead(wounds)` po przekroczeniu progu dla głowy lub korpusu.

## 2. Istniejące problemy

### 2.1. Rozstrzygnięcie jest zbyt płaskie

- Jedno wywołanie `attack()` obsługuje zbyt wiele decyzji naraz.
- Brak osobnego modelu zdarzenia bojowego.
- Brak formalnego rozdziału na:
  - wybór akcji,
  - obronę,
  - miejsce kontaktu,
  - rodzaj kontaktu z pancerzem,
  - skutki czasowe,
  - warstwę narracyjną.

### 2.2. Rany zachowują się jak ukryte HP

- `astergard/combat/wounds.py` nadal używa sumy ran jako uproszczonej skali zdrowia.
- Śmierć zależy od progu na `glowa` i `korpus`, bez modelu ciężkości rany, krwawienia, bólu i funkcjonalności.
- W praktyce głębszy model ciała nie istnieje jeszcze mechanicznie.

### 2.3. Pancerz jest zbyt prosty

- Pancerz ma dziś jeden efekt liczbowy: redukcja obrażeń.
- Nie ma rzeczywistej warstwowości, osobnych kontaktów typu:
  - odbicie,
  - ześlizgnięcie,
  - wgniecenie,
  - przebicie,
  - przeniesienie energii bez przebicia.
- Nie ma formalnego rozróżnienia tarczy jako osobnego systemu obrony.

### 2.4. Broń i style są jeszcze zbyt mało rozróżnione

- Rodzina broni wpływa głównie na:
  - zasięg,
  - bazowe obrażenia,
  - inicjatywę,
  - parowanie.
- Nie ma jeszcze pełnej tożsamości rodzin broni w sensie:
  - technik,
  - kosztu kondycji,
  - skuteczności przeciw pancerzom,
  - zachowania przy zwarciu,
  - narracji zależnej od wyszkolenia.

### 2.5. Kondycja i morale są za mało konsekwentne

- Kondycja wpływa na koszt, inicjatywę i skuteczność, ale nie ma pełnego modelu opóźnień, odzyskania równowagi i kolejki zamiarów.
- Morale istnieje jako liczba w obliczeniach, ale nie jest jeszcze pełnym stanem bojowym NPC.

### 2.6. Komunikaty są jeszcze częściowo techniczne

- Część tekstów nadal odpowiada bardziej komunikatowi programu niż opisowi starcia.
- Ta sama struktura bywa wykorzystywana dla wielu sytuacji, co osłabia immersję.
- Brakuje osobnych perspektyw narracyjnych dla:
  - napastnika,
  - obrońcy,
  - obserwatora.

### 2.7. Serializacja i zgodność zapisu niosą ryzyko

- `CharacterStateSerializer` zapisuje:
  - statystyki,
  - umiejętności,
  - rany,
  - wyposażenie,
  - efekty,
  - styl walki,
  - profil kreatora.
- `WorldStateRepository` serializuje NPC wraz z ich stanem wewnętrznym.
- Każda głębsza przebudowa modelu walki musi zachować zgodność z istniejącymi zapisami albo wprowadzić kontrolowaną migrację.

## 3. Ryzyka migracji

- Zmiana struktury ran może unieważnić część zapisów i testów opartych o prostą mapę `body_part -> int`.
- Rozdzielenie resolvera i narracji może ujawnić zależności ukryte w testach regresyjnych.
- Nowy model pancerza może wymagać dopisania pól do `Item` i aktualizacji hydracji z JSON.
- Nowy model zdarzeń bojowych może wymagać zmian w heartbeat, AI NPC, logice śmierci i pościgu.
- Zbyt agresywna migracja może zepsuć kompatybilność z `mud.db`.

## 4. Elementy możliwe do zachowania

- Struktura `Character`, `NPC`, `Item`, `EquipmentSet` i serwisowa architektura use-case.
- Istniejący system:
  - umiejętności,
  - profesji,
  - stylów walki,
  - morale jako punkt wyjścia,
  - obciążenia pancerzem,
  - czasu i pogody,
  - heartbeat.
- Aktualne testy balansu jako baza do nowych porównań po przebudowie.
- Istniejąca serializacja JSON, o ile zostanie rozszerzona w sposób kompatybilny.

## 5. Elementy wymagające przebudowy

- `CombatManager.attack()` jako monolityczna metoda.
- `CombatResult` jako nośnik zarówno mechaniki, jak i narracji.
- `is_dead(wounds)` jako jedyny punkt rozstrzygnięcia życia i śmierci.
- Prosty model redukcji pancerza.
- Jednolity model obrony bez osobnych klas wyników.
- Brak formalnego modelu kolejki zamiarów i opóźnień po ciężkich akcjach.
- Brak biblioteki narracyjnej zależnej od perspektywy i semantyki zdarzenia.

## 6. Proponowana architektura docelowa

### 6.1. Warstwa rozstrzygnięcia mechanicznego

Nowy resolver powinien wyjść z pojedynczego `attack()` i zwracać ustrukturyzowane zdarzenie bojowe.

Powinien liczyć:

- inicjatywę,
- typ akcji,
- trafienie lub pudło,
- rodzaj obrony,
- miejsce trafienia,
- kontakt z pancerzem,
- rodzaj obrażeń,
- głębokość rany,
- koszt kondycji,
- skutki dla postawy,
- skutki dla morale,
- skutki czasowe.

### 6.2. Model zdarzenia bojowego

Zdarzenie powinno przenosić dane semantyczne, a nie gotowy tekst.

### 6.3. Warstwa narracyjna

Tekst powinien być generowany osobno dla:

- napastnika,
- obrońcy,
- obserwatora.

### 6.4. Biblioteka językowa

Powinna dostarczać autorskie warianty dla:

- rodzin broni,
- technik,
- miejsc trafienia,
- obrony,
- pancerzy,
- kondycji,
- morale,
- śmierci,
- ucieczki,
- otoczenia.

### 6.5. Kontrola powtórzeń

Powinna śledzić ostatnio użyte formy i wybierać kolejne warianty bez utraty zgodności mechanicznej.

## 7. Plan migracji etapami

### Etap A

- Wprowadzić model `CombatEvent`.
- Rozdzielić resolver i narrację.
- Zachować kompatybilność publicznego API `CombatManager.attack()`.

### Etap B

- Rozbudować trafienie, obronę, pancerz i tarcze.
- Utrwalić miejsca trafień i ich konsekwencje.

### Etap C

- Przebudować rany i kondycję.
- Zależności od kończyn, korpusu i głowy mają działać konsekwentnie.

### Etap D

- Rozróżnić rodziny broni, techniki i style.
- Dodać koszty, tempo i narrację szkolenia.

### Etap E

- Uzupełnić morale i AI archetypów.
- Dodać kontrolę ucieczki, poddania i reakcji grupowych.

### Etap F

- Podmienić wszystkie komunikaty walki na warstwę narracyjną.
- Dodać kontrolę powtórzeń i perspektywy.

### Etap G

- Przejść pełne testy jednostkowe, integracyjne i balansowe.
- Uruchomić audyt końcowy i przygotować raport z decyzjami.
