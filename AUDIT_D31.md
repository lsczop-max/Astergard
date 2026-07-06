# AUDIT D31 — Container Interaction Engine

## Cel
D31 rozszerza polski parser interakcji z przedmiotami o realną obsługę pojemników. Po D30 gra umiała wkładać przedmioty do pojemnika, ale brakowało odwrotnej i eksploracyjnej części interakcji: wyjmowania, oglądania zawartości i pobierania wielu obiektów z kontenera.

## Wykonane zmiany

### 1. Parser relacji z pojemnikiem
Rozszerzono `CommandParser.RELATION_COMMANDS`, aby zachowywał składnię relacyjną dla:

- `weź <przedmiot> z <pojemnik>`
- `wyjmij <przedmiot> z <pojemnik>`
- `wyciągnij <przedmiot> z <pojemnik>`
- `obejrzyj w <pojemnik>`
- `obejrzyj <przedmiot> w <pojemnik>`

Jednocześnie zachowano kompatybilność z wcześniejszym zachowaniem `spójrz na żołnierza`, aby przyimek `na` nadal był ignorowany w zwykłym oglądaniu celu.

### 2. Wyjmowanie z pojemników
Dodano w `InventoryService`:

- `take_from_container()`
- `take_all_from_container()`
- `find_container()`
- rekurencyjne wyszukiwanie pojemników w ekwipunku i wyposażeniu.

Obsługiwane przykłady:

```text
weź klucza z plecaka
wyjmij klucz z plecaka
weź wszystko z plecaka
wyjmij wszystko z plecaka
```

### 3. Oglądanie wnętrza pojemnika
Rozszerzono `ExplorationService.look()` o oglądanie pojemników niesionych przez gracza:

```text
obejrzyj w plecaku
obejrzyj klucz w plecaku
```

### 4. Rejestr komend
Dodano kanoniczną komendę:

```text
take_from
```

z aliasami:

```text
wyjmij
wyciągnij
wyciagnij
```

Komenda `weź` zachowała dotychczasowe użycie i kompatybilność, ale potrafi teraz rozpoznać konstrukcję `z <pojemnik>`.

### 5. Testy regresji
Dodano `tests/test_d31_container_interaction_engine.py`:

- parser zachowuje konektor `z` dla `weź klucza z plecaka`,
- `weź klucza z plecaka` przenosi tylko wskazany przedmiot,
- `wyjmij klucz z plecaka` działa przez nowy alias,
- `weź wszystko z plecaka` opróżnia pojemnik,
- `obejrzyj w plecaku` pokazuje zawartość,
- `obejrzyj klucz w plecaku` pokazuje opis przedmiotu,
- brak przedmiotu w pojemniku daje jasny komunikat.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 129 tests in 2.443s
OK
```

## Wynik regresji komend

```text
python3 scripts/run_command_regression.py
Scenario: basic_gameplay
> spojrz
[ Zaułek 0 (Centrum_Twierdza) ]
> cechy
Siła: przeciętny
> ekwipunek
Wyposażenie: brak
> pomoc
Dostępne komendy:
```

## Krytyczna ocena
D31 znacząco poprawia ergonomię przedmiotów i zbliża zachowanie parsera do oczekiwań polskiego MUD-a. To nadal nie jest pełna semantyka Arkadii. Brakuje jeszcze:

1. rozstrzygania wielu pojemników o tej samej nazwie (`drugi plecak`),
2. komend typu `przeszukaj plecak`,
3. operowania na pojemnikach leżących na ziemi,
4. transferu między dwoma pojemnikami bez wyjmowania do ekwipunku,
5. naturalniejszych komunikatów fleksyjnych.

## Następny etap
D32 powinien domknąć interakcje z obiektami w świecie:

- `obejrzyj drugi miecz`,
- `weź drugi klucz z plecaka`,
- `weź wszystko z ziemi`,
- `przeszukaj skrzynię`,
- pojemniki na ziemi,
- transfer `przełóż X z A do B`.
