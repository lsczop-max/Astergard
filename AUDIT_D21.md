# AUDIT D21 — Rules Engine

## Cel
Domknięcie warstwy reguł silnika przez centralizację parametrów walki, ruchu, ekonomii, reputacji, magii, skilli, wyszukiwania i respawnu.

## Wykonane zmiany
- Dodano pakiet `astergard/rules/`.
- Dodano `RuleSet` jako jawny kontener reguł silnika.
- Dodano reguły domenowe:
  - `rules/combat.py` — wagi trafień, style walki, koszty kondycji, degradacja, parowanie i tarcze.
  - `rules/movement.py` — koszt ruchu, blokada ruchu przez rany nóg, test szukania.
  - `rules/economy.py` — ceny kupna/sprzedaży, reputacyjny rabat, minimalne ceny.
  - `rules/reputation.py` — progi reputacji, reakcja strażników, limity reputacji.
  - `rules/skills.py` — próg rozwoju umiejętności i limit poziomów.
  - `rules/respawn.py` — limit NPC w lokacji, delay respawnu, szansa patrolu.
  - `rules/magic.py` — koszty i parametry czarów.
- `GameBootstrapper` buduje jeden `RuleSet` i wstrzykuje go do usług.
- `CombatManager`, `EconomyService`, `FactionManager`, `MagicService`, `NPCManager`, `ExplorationService` i `CombatApplicationService` korzystają z reguł zamiast lokalnych stałych.
- Dodano testy kontraktowe `tests/test_d21_rules_engine.py`.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 81 tests in 1.364s
OK
```

## Krytyczna ocena
D21 usuwa znaczną część rozproszonych magic numbers, ale nie wszystkie. Część danych pozostaje w content factory NPC oraz item definitions, bo są to parametry zawartości gry, nie reguły silnika. Następny etap powinien wprowadzić `State Machine Layer`, czyli jawne stany sesji, gracza, NPC i walki oraz walidację przejść.

## Następny etap
D22 — State Machine Layer.
