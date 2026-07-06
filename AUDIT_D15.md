# AUDIT D15 — Combat simulation, styles and observer output

## Cel
D15 rozszerza walkę z D14 o mechanikę stylów walki, jawne komunikaty dla obserwatorów oraz testy regresyjne balansu.

## Zmiany wykonane
- Dodano `CombatStyle`, `COMBAT_STYLES`, `normalize_combat_style()` i `get_combat_style()` w `astergard/combat/manager.py`.
- Dodano style: `zrownowazony`, `ofensywny`, `defensywny`, `ostrozny`, `brutalny`.
- Styl wpływa na:
  - test trafienia,
  - aktywną obronę,
  - inicjatywę,
  - koszt kondycji,
  - efektywne obrażenia.
- `CombatResult` posiada teraz `observer_message` i `style_used`.
- `CombatRoundResult` posiada `observer_message` agregujący komunikaty rundy.
- Dodano trwały zapis `Character.combat_style` przez migrację `006_combat_style.sql`.
- Dodano komendę `styl` / `postawa`.
- `cechy` pokazują obecny styl walki.
- Dodano testy D15 dla aliasów stylu, wpływu na kondycję, komunikatów obserwatorów i persistence.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 56 tests in 0.473s
OK
```

## Krytyczna ocena
D15 poprawia głębię walki, ale nadal nie jest pełnym systemem balansu produkcyjnego. Brakuje jeszcze:
- długich symulacji statystycznych 1000+ walk na scenariusz,
- raportu CSV/Markdown z rozkładem zwycięstw,
- pełnego rozgłaszania komunikatów heartbeat do rzeczywistych połączeń Telnet,
- ustawiania stylów NPC per archetyp.

## Następny etap
D16 — symulacje balansu 1000 walk/scenariusz, raporty automatyczne i profile stylów NPC.
