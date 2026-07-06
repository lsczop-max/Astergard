# AUDIT D16 — Combat balance simulations and NPC combat profiles

## Cel
D16 rozszerza D15 o mierzalny system symulacji balansu walki. Celem nie było ręczne dopisywanie kolejnych pojedynków, tylko stworzenie narzędzia, które pozwala powtarzalnie uruchamiać minimum 1000 walk na scenariusz i porównywać wynik stylów, NPC oraz typowych spotkań.

## Zmiany w kodzie
- Dodano `astergard/combat/balance.py`.
- Dodano `scripts/combat_balance_report.py`.
- Dodano `astergard/npcs/combat_profiles.py`.
- `NPCFactory` przypisuje profile stylów walki do NPC:
  - `meekhan_soldier` → `defensywny`,
  - `merchant` → `ostrozny`,
  - `mountain_troll` → `brutalny`,
  - `wolf` → `ofensywny`.
- Dodano `COMBAT_BALANCE_REPORT_D16.md` wygenerowany z 1000 iteracji na scenariusz.
- Dodano testy `tests/test_d16_combat_balance_simulation.py`.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 60 tests in 0.559s
OK
```

## Wynik symulacji
Raport wygenerowano poleceniem:

```bash
python3 scripts/combat_balance_report.py --iterations 1000 --output COMBAT_BALANCE_REPORT_D16.md
```

Najważniejsze obserwacje:
- `player_defensive_vs_troll` daje 99.6% zwycięstw gracza. To jest anomalia: troll ma zbyt słabą efektywność mimo stylu `brutalny`.
- `style_defensywny_vs_balanced` i `style_ostrozny_vs_balanced` mają bardzo wysoki draw-rate. Obrona i ostrożność spowalniają walkę za mocno.
- `style_brutalny_vs_balanced` przegrywa zbyt często. Koszt obronny i inicjatywa brutalnego stylu są zbyt karzące przy obecnym modelu uników/parowania.
- `player_offensive_vs_soldier` ma wysoki draw-rate i zbyt niską skuteczność ofensywy.

## Krytyczna ocena
D16 nie zamyka balansu. D16 tworzy narzędzie, które ujawnia problemy balansu. To jest właściwy etap przed zmianą liczb, bo bez symulacji wcześniejsze poprawki byłyby subiektywne.

## Następny etap
D17 powinien wykonać pierwszą korektę parametrów balansu na podstawie `COMBAT_BALANCE_REPORT_D16.md`:
- zwiększyć zagrożenie trolla,
- obniżyć draw-rate defensywy i ostrożności,
- poprawić opłacalność stylu brutalnego,
- skrócić typowe walki zwykłe poniżej 25 rund.
