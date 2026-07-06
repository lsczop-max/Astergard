# AUDIT D22 — State Machine Layer

## Cel
Domknąć warstwę maszyn stanów dla krytycznych encji silnika: sesji, postaci, NPC i walki. Celem było ograniczenie niekontrolowanych stringów stanu oraz dodanie walidacji przejść.

## Wykonane zmiany
- Dodano pakiet `astergard/state/`.
- Dodano `StateMachine` i `StateTransitionError`.
- Dodano enumy:
  - `SessionState`,
  - `CharacterState`,
  - `NPCState`,
  - `CombatState`.
- Dodano jawne maszyny przejść:
  - `SESSION_STATE_MACHINE`,
  - `CHARACTER_STATE_MACHINE`,
  - `NPC_STATE_MACHINE`,
  - `COMBAT_STATE_MACHINE`.
- `ClientConnection` ma teraz `transition_state()` i używa `SessionState`.
- `Character` ma teraz pole `state` oraz metody:
  - `sync_flags_from_state()`,
  - `sync_state_from_flags()`,
  - `transition_state()`,
  - `enter_combat()`,
  - `leave_combat()`,
  - `die()`.
- `NPC` ma teraz `transition_ai_state()`.
- Walka ustawia śmierć przez `Character.die()` zamiast bezpośrednio zmieniać `is_alive`.
- Agresja NPC ustawia walkę przez `enter_combat()` zamiast bezpośrednio zmieniać `in_combat`.
- Snapshot NPC zapisuje i odtwarza `character.state`.

## Testy dodane w D22
- `tests/test_d22_state_machines.py`

Pokrycie testowe obejmuje:
- poprawne przejście sesji `CONNECTED -> IN_GAME -> DISCONNECTED`,
- blokadę nielegalnego przejścia z `DISCONNECTED` do `IN_GAME`,
- synchronizację stanu postaci z flagami legacy `is_alive` i `in_combat`,
- blokadę niejawnego wskrzeszenia martwej postaci,
- walidację przejść AI NPC,
- blokadę przejścia `DEAD -> AGGRESSIVE`,
- użycie maszyny stanu przy śmierci w walce.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 88 tests in 1.431s
OK
```

## Krytyczna ocena
D22 wprowadza formalny State Machine Layer, ale zachowuje kompatybilność z dotychczasowymi flagami `is_alive` i `in_combat`. To celowe przejście pośrednie. Pełne usunięcie flag legacy wymaga osobnego etapu, ponieważ są używane szeroko w repozytoriach, testach i usługach.

## Ryzyka pozostałe
- `Character.is_alive` i `Character.in_combat` nadal istnieją jako flagi kompatybilności.
- `NPC.ai_state` nadal jest przechowywany jako string, choć walidowany przez maszynę przy użyciu nowej metody.
- Nie ma jeszcze kompletnej maszyny stanów dla całego cyklu życia walki jako osobnej encji walki; `CombatState` jest przygotowany, ale wymaga D23/D24 przy refaktoryzacji aktywnych walk.

## Rekomendowany następny etap
D23 — Save/Load Engine albo D23a — usunięcie flag legacy i pełne przeniesienie stanu na enumy/maszyny stanów.
