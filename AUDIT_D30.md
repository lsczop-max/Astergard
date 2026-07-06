# AUDIT D30 — Object Interaction Parser

## Cel
D30 rozbudowuje polski parser interakcji z obiektami, tak aby obsługiwał typowe komendy MUD-owe w stylu Arkadii: działania na wielu przedmiotach, relacje `przedmiot -> pojemnik`, przekazywanie przedmiotów NPC oraz odmianę/synonimy w podstawowych przypadkach.

## Wykonane zmiany

### Parser i normalizacja
- Rozszerzono `astergard/commands/polish.py` o:
  - `is_all_phrase()` dla fraz `wszystko` / `wszystkie`,
  - `split_relation()` do rozbijania komend relacyjnych, np. `włóż klucza do plecaka`, `daj skórę kupcowi`,
  - nowe lematy: `plecaka`, `plecakiem`, `plecaku`.
- Zmieniono `CommandParser`, aby dla komend relacyjnych (`wloz`, `daj`, `oddaj`, `przekaz`) zachowywał spójniki/relatory potrzebne do interpretacji obiektu docelowego.
- Dodano obsługę odmienionych liczebników porządkowych, np. `drugiego`, `trzeciego`, `czwartego`, `piatego`.

### Ekwipunek i obiekty
- Rozszerzono `InventoryService` o:
  - `get_all_items()` — `weź wszystko`,
  - `drop_all_items()` — `upuść wszystko`,
  - `put_item()` — `włóż <przedmiot> do <pojemnik>`,
  - `give_item()` — `daj <przedmiot> <NPC>`.
- Ekwipunek pokazuje zawartość pojemników, np. `plecak (w środku: żelazny klucz)`.
- Zabezpieczono wkładanie pojemnika w samego siebie i przekroczenie pojemności.

### Komendy
Dodano komendy i aliasy:
- `wloz`, `włóż`, `wsadz`, `wsadź`,
- `daj`, `oddaj`, `przekaz`, `przekaż`.

### Testy
Dodano `tests/test_d30_object_interaction_parser.py`:
- parser zachowuje relację `do` dla `włóż miecz do plecaka`,
- `weź wszystko` przenosi wszystkie pasujące przedmioty z lokacji,
- `włóż klucza do plecaka` działa z odmianą,
- `daj skórę kupcowi` działa z celownikiem i aktualizuje quest `wolf_pelt`,
- `upuść wszystko` przenosi cały plecak na ziemię.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 123 tests in 2.340s
OK
```

## Krytyczna ocena
D30 znacząco poprawia ergonomię interakcji z obiektami, ale nadal nie jest pełnym parserem Arkadii. Brakuje jeszcze:
- pełnej odmiany rzeczowników i przymiotników,
- rozstrzygania niejednoznaczności przez pytanie doprecyzowujące,
- obsługi `weź wszystko z pojemnika`,
- obsługi `daj wszystko kupcowi`,
- kompletnego parsera wieloobiektowego typu `weź miecz i tarczę`,
- mapy synonimów dla setek nazw przedmiotów i NPC.

## Następny etap
D31 powinien wprowadzić `Container Interaction Engine`:
- `obejrzyj w plecaku`,
- `weź X z Y`,
- `wyjmij X z Y`,
- `weź wszystko z Y`,
- rekurencyjne przeszukiwanie pojemników,
- jawne komunikaty przy wielu podobnych obiektach.
