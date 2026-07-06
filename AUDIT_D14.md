# AUDIT D14 — Combat Balance Core

## Cel
Rozbudować walkę tak, aby aktywne starcia nie były pojedynczym testem trafienia, tylko rundą z inicjatywą, obroną aktywną i wpływem rodzaju broni.

## Wykonane zmiany
- `astergard/combat/manager.py`
  - dodano `CombatTurn` i `CombatRoundResult`,
  - dodano `initiative_score`, `ordered_turns`, `process_pair_round`, `process_active_round`,
  - dodano aktywną obronę: tarcza i parowanie bronią,
  - dodano koszt kondycji zależny od zasięgu broni,
  - dodano mapowanie typu obrażeń na właściwą umiejętność broni,
  - dodano usuwanie walk po śmierci, rozłączeniu encji albo zmianie lokacji.
- `astergard/items/models.py`
  - dodano pola `reach`, `initiative_modifier`, `parry_bonus`, `shield_block`,
  - rozszerzono serializację przedmiotów,
  - doprecyzowano statystyki startowego miecza i tarczy.
- `astergard/characters/models.py`
  - dodano `Character.shield()`.
- `astergard/application/heartbeat.py`
  - heartbeat przetwarza aktywne rundy walki NPC/gracz,
  - martwy NPC generuje zwłoki i trafia do kolejki respawnu.
- `tests/test_d14_combat_balance.py`
  - dodano testy serializacji pól bojowych,
  - dodano testy tarczy,
  - dodano testy parowania,
  - dodano test kolejności inicjatywy,
  - dodano test zakończenia walki po rozdzieleniu lokacji.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 52 tests in 0.488s
OK
```

## Krytyczna ocena
D14 istotnie poprawia rdzeń walki, ale nadal nie jest pełnym systemem balansu produkcyjnego. Brakuje jeszcze:
- raportów symulacyjnych 1000+ walk,
- różnych stylów walki/postaw,
- zaawansowanej tabeli obrażeń zależnej od typu broni,
- reakcji komunikacyjnych do obserwatorów w pokoju,
- pełnej obsługi walki wielu na wielu.

## Następny etap
D15 — testy symulacyjne balansu, style walki, tarczowanie jako decyzja taktyczna oraz komunikaty bojowe dla pokoju.
