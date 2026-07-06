# AUDIT D35.1C — Puszcza Ciszy World Rewrite

## Cel
D35.1C kontynuuje ręczną przebudowę Regionu I na bazie D35.1B. Etap obejmuje Puszczę Ciszy: pierwszy duży obszar leśny, który ma działać jako pełnoprawne expowisko, strefa eksploracji, przyszłe źródło surowców oraz naturalne przejście do głębszej Kniei Cichych Ścieżek.

## Wykonane zmiany

### 1. Ręcznie zaprojektowana Puszcza Ciszy
Zakres lokacji: `210–279`, razem dokładnie 70 lokacji.

Każda lokacja otrzymała:
- unikalną nazwę,
- opis zastępujący placeholder,
- minimum 3 elementy do oglądania,
- spójny leśny klimat,
- miejsce pod przyszłe mechaniki: tropienie, zioła, wilki, bandytów, obozy smolarzy i drwali.

### 2. Organiczny graf przejść
Zastąpiono placeholderowy łańcuch Puszczy Ciszy ręcznie zdefiniowaną topologią:
- główny dukt leśny skręca naturalnie,
- boczne ścieżki tworzą pętle i skróty,
- część przejść diagonalnych modeluje dukty, jary i obejścia,
- nie użyto sztucznej pełnej siatki.

Średnia liczba wyjść w Puszczy pozostaje poniżej 4, aby obszar był nawigowalny, ale nie wyglądał jak plansza.

### 3. Integracja z istniejącą mapą
Puszcza łączy się z:
- Osadą Myśliwych przez lokację `109 -> 210`,
- zachodnim traktem przez `179 -> 210`,
- przyszłą Knieją Cichych Ścieżek przez `279 -> 280`.

### 4. Przedmioty i ukryte elementy
Dodano pierwsze leśne obiekty:
- jawne wiązki suchego chrustu,
- ukryte zioła leśne.

To nie jest jeszcze pełny system surowców, ale przygotowuje lokacje pod D36.

### 5. Testy
Dodano `tests/test_d35_1c_silent_forest_world_rewrite.py`.

Testy sprawdzają:
- kompletność 70 ręcznie opisanych lokacji,
- brak placeholderów w Puszczy Ciszy,
- organiczność grafu,
- przejścia między regionami,
- symetrię wszystkich wyjść w całym świecie.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 153 tests in 2.410s
OK
```

## Krytyczna ocena
D35.1C znacząco poprawia grywalność pierwszego dużego expowiska, ale nadal nie jest to docelowy las produkcyjny. Brakuje jeszcze:
- spawn table wilków, drwali, myśliwych i bandytów,
- mechaniki tropienia,
- realnego zbierania surowców,
- zagrożeń środowiskowych,
- krótkich mikroquestów leśnych,
- powiązania Puszczy z ekonomią skóry, drewna i ziół.

To powinno wejść w D36 po zakończeniu pełnego world rewrite Regionu I.

## Następny etap
D35.1D — Knieja Cichych Ścieżek: głębszy, trudniejszy las z większym ryzykiem, mniej oczywistą nawigacją, miejscami pod elitarnych przeciwników i przejściami ku ruinom oraz bagnom.
