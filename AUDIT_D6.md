# AUDIT D6 — Context Ports / ograniczenie GameContext

## Cel
Usunąć szeroki dostęp usług aplikacyjnych i handlerów komend do `GameServer` przez `ctx.server`.

## Problem przed D6
Po D5 `GameContext` zawierał pełny obiekt `GameServer`. To oznaczało, że każda komenda i każda usługa aplikacyjna mogła ominąć warstwy architektury i sięgnąć do dowolnego elementu serwera TCP, repozytorium, NPC, świata albo dispatcherów. Był to ukryty coupling i potencjalny powrót do God Object.

## Wykonane zmiany
- `astergard/server/context.py` definiuje teraz `GameContext` jako kontekst portów aplikacyjnych:
  - `services`,
  - `character`,
  - `players_in_room`,
  - `current_command`.
- Usunięto zależność handlerów i usług od `ctx.server`.
- `GameServer.make_context()` tworzy kontekst przez `GameContext(self.services, character, self.get_players_in_room)`.
- `commands/helpers.py::find_npc()` używa portu `ctx.npcs`, nie `ctx.server.npcs`.
- Komendy i usługi aplikacyjne używają `ctx.services`, `ctx.world`, `ctx.npcs`, `ctx.repo`, `ctx.magic`, `ctx.crafting` oraz `ctx.players_in_room`.
- Testy zostały zaktualizowane do tworzenia kontekstu przez `server.make_context(character)`.

## Dodane testy
`tests/test_d6_context_ports.py`:
- sprawdza, że `GameContext` nie ma atrybutu `server`,
- skanuje warstwy `commands/` oraz `application/services/` pod kątem zakazanego `ctx.server`,
- sprawdza działanie portu obecności graczy `players_in_room`.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 26 tests in 0.122s
OK
```

## Krytyczna ocena
D6 znacząco ogranicza coupling, ale nie kończy pracy nad architekturą. `GameContext` nadal udostępnia cały kontener `services`, co jest bezpieczniejsze niż `GameServer`, ale nadal szerokie. Docelowo D7 powinien wprowadzić wyspecjalizowane konteksty lub porty per use case, np. `ExplorationContext`, `CombatContext`, `EconomyContext`.

## Następny etap
D7 — pełniejsza separacja domeny od aplikacji: usługi aplikacyjne powinny przyjmować jawne porty w konstruktorach, a nie odczytywać wszystko przez jeden wspólny `GameContext`.
