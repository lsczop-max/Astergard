# AUDIT D17 — korekta parametrów walki po symulacjach

## Cel
D16 ujawnił trzy problemy balansu:

1. `player_defensive_vs_troll`: gracz defensywny wygrywał 99.6% walk, mimo że troll miał być zagrożeniem asymetrycznym.
2. Style `defensywny` i `ostrozny` generowały zbyt dużo remisów i zbyt długie walki.
3. Część NPC nie miała pełnego realnego loadoutu bojowego, więc symulacja testowała bardziej style niż faktyczne archetypy przeciwników.

## Zmiany wykonane

### CombatStyle
W `astergard/combat/manager.py` skorygowano parametry:

- `defensywny`: obrona zmniejszona z `+2` do `+1`, żeby ograniczyć remisy i pasywny stalemate.
- `brutalny`: atak zwiększony do `+3`, kara obrony złagodzona do `-1`, koszt kondycji zmniejszony do `+1`.
- bazowy koszt ataku zmniejszony z `5` do `4`, żeby zwykłe walki rzadziej kończyły się zerową kondycją obu stron.
- próg bloku tarczą podniesiono z `hit_score + 3` do `hit_score + 6`.
- próg parowania podniesiono z `hit_score + 5` do `hit_score + 7`.

### NPC loadout
W `astergard/npcs/models.py` dodano realne wyposażenie bojowe:

- żołnierz: miecz, tarcza, kolczuga,
- kupiec: nóż,
- troll: kamienna maczuga i naturalny pancerz,
- wilk: kły jako naturalna broń.

### Testy
Dodano `tests/test_d17_balance_tuning.py`:

- sprawdza nowe parametry stylów,
- sprawdza loadout trolla,
- sprawdza loadout żołnierza,
- sprawdza, że scenariusze balansu nie mają skrajnych wyników zwycięstw powyżej 86% przy krótszej próbie regresyjnej.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 64 tests
OK
```

## Wynik symulacji D17 — 1000 walk na scenariusz

Zobacz `COMBAT_BALANCE_REPORT_D17.md`.

Kluczowe porównanie:

- `player_defensive_vs_troll`: spadek wygranych gracza z 99.6% do 70.5%; troll wygrywa 29.0%.
- `style_defensywny_vs_balanced`: remisy spadły z 64.6% do 17.6%.
- `style_brutalny_vs_balanced`: brutalny styl przestał być pułapką; wzrost z 8.9% do 57.2% wygranych.

## Krytyczna ocena
D17 poprawia najpoważniejsze anomalie, ale balans nadal nie jest produkcyjny:

- `defensywny` nadal ma średnio 28.6 rund, czyli powyżej progu 25 dla zwykłych walk.
- `ostrozny` faworyzuje atakującego w mirrorze względem zrównoważonego, co wymaga obserwacji.
- Troll jest teraz groźny, ale nadal słabszy niż oczekiwany mini-boss przy defensywnym graczu.

## Następny etap
D18 powinien dodać:

- klasy zagrożenia NPC (`trash`, `standard`, `elite`, `boss`),
- odporności i cechy gatunkowe,
- osobny profil „mini-boss troll”,
- testy balansu progowego dla archetypów NPC.
