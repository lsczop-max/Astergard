# Astergard — pakiet mapy Regionu I

Stan pakietu: materiał projektowy gotowy do analizy i kontrolowanego wdrożenia.

## Zawartość

- `mapa_astergard_region_I.json` — źródłowa mapa: 170 lokacji i 219 połączeń.
- `mapa_astergard_region_I.svg` — wizualizacja mapy.
- `mapa_karty_lokacji.json` — karty funkcji wszystkich 170 lokacji.
- `mapa_plan_rozgrywki.json` — plan aktywności, progresji i sekretów.
- `mapa_balans_expowisk.json` — projekt balansu lasu i mokradeł.
- `mapa_opisy_pilot.json` — 15 poprawionych opisów pilotażowych.
- `Astergard_Map_Studio.html` — lokalny edytor mapy działający w przeglądarce.

## Ważne

Nie kopiuj tych plików bezpośrednio nad istniejące moduły Pythona. Mapa i materiały
projektowe muszą najpierw zostać dopasowane do aktualnego modelu świata w
repozytorium Astergardu. Identyfikatory lokacji, kierunki wyjść i istniejące
źródło prawdy wymagają sprawdzenia przed importem.

Plik SVG służy do oglądania mapy, a nie do importowania świata do serwera.
Opisy pilotażowe obejmują tylko 15 lokacji i nie są kompletem opisów Regionu I.

## Zalecana kolejność wdrożenia

1. Skopiować cały pakiet do osobnego katalogu importowego w repozytorium.
2. Porównać identyfikatory oraz wyjścia z bieżącym źródłem świata.
3. Zintegrować mapę bez tworzenia drugiego źródła prawdy.
4. Wdrożyć 15 opisów pilotażowych jako mały, odwracalny etap.
5. Dodać testy topologii, osiągalności, wyjść i opisów.
6. Uruchomić `ruff check .`, `mypy .` i `pytest`.
7. Dopiero potem przeprowadzić próbę w Mudlecie.
