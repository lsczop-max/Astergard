# AUDIT D35.1A — Astergard World Rewrite, etap A

## Cel
Pierwszy krok przebudowy Regionu I z proceduralnej mapy 20×25 na ręcznie kontrolowany graf MUD. Etap A obejmuje Twierdzę Astergard jako dokładnie 60 lokacji i przygotowuje szkielet 500-lokacyjnego regionu do dalszych iteracji.

## Zmiany wykonane
- `WorldManager.generate_world()` przestał budować pełną prostokątną siatkę 20×25.
- Dodano stałe zakresy Regionu I: Astergard, podgrodzie, wsie, trakty, puszcze, góry, kopalnię, ruiny, jaskinie i bagna.
- Twierdza Astergard ma teraz dokładnie 60 lokacji: ID `0–59`.
- Miasto otrzymało organiczny graf ulic: trakty skręcają, uliczki stosują także kierunki diagonalne, a przejścia nie są pełną kratownicą.
- Zachowano kompatybilność startu: `0 -> poludnie -> 20`, aby dotychczasowy scenariusz wejścia w miasto nadal działał.
- Usunięto z contentu ryzyko motywu „Wieży Magów”; D35.1A trzyma wcześniejsze założenie świata bez jawnej, grywalnej magii.
- Pozostałe 440 lokacji istnieje jako rzadki, tymczasowy szkielet regionu z nazwami stref i placeholderami. Będą zastępowane ręcznie w kolejnych etapach.

## Testy
Dodano `tests/test_d35_1a_astergard_world_rewrite.py`:
- dokładnie 60 ręcznie autorskich lokacji Astergardu,
- brak Wieży Magów w nazwach i opisach,
- organiczny, niekratowy graf miasta,
- symetria wszystkich kierunków pełnej róży wiatrów.

Wynik:

```text
python3 -m unittest discover tests
Ran 145 tests in 2.693s
OK
```

## Krytyczna ocena
To jest świadomie tylko etap A. Silnik ma teraz lepszy graf bazowy, a Astergard jest właściwie ograniczony do 60 lokacji, ale większość regionu nadal jest szkieletem. Nie należy jeszcze dodawać dużych questów i ekonomii do obszarów z placeholderami. Kolejny sensowny krok to D35.1B: podgrodzie, Haldun, Osada Myśliwych, Forteca Dungrim, trakty i boczne drogi.
