# AUDIT D24 — Command Engine

## Cel etapu
Domknięcie warstwy wejścia gracza przez wprowadzenie jawnego silnika komend: metadane, aliasy, walidacja argumentów, cooldowny, uprawnienia i pomoc generowana z rejestru.

## Wykonane zmiany
- Dodano `astergard/commands/engine.py`.
- Dodano `CommandMetadata`, `CommandArgumentSpec`, `CommandSpec`, `CommandRegistry`, `CooldownTracker` i `PermissionLevel`.
- Rozszerzono `CommandDispatcher`:
  - zachowuje kompatybilne `commands: dict[str, CommandFunc]`,
  - ma jawny `registry`,
  - waliduje wymagane argumenty przed wejściem do handlera,
  - egzekwuje cooldowny per postać i komenda,
  - egzekwuje poziomy uprawnień,
  - generuje `pomoc` / `help` z rejestru.
- Rozszerzono `CommandBus` o `CommandDefinition`.
- `commands/registration.py` definiuje teraz komendy jako katalog metadanych, a nie tylko mapę aliasów.
- Zachowano kompatybilność z testami D8: `CommandBus.handlers`, `CommandBus.aliases` i `dispatcher.commands` nadal istnieją.

## Nowe testy
Dodano `tests/test_d24_command_engine.py`:
- metadane komend są przechowywane w rejestrze,
- pomoc jest generowana z rejestru,
- walidacja wymaganych argumentów działa przed handlerem,
- cooldown blokuje natychmiastowe ponowne użycie,
- uprawnienia admina są egzekwowane przez dispatcher.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 96 tests in 1.654s
OK
```

## Ocena krytyczna
D24 domyka podstawowy Command Engine, ale nie jest jeszcze pełnym systemem składniowym klasy produkcyjnej. Nadal brakuje:
- typowanych parserów argumentów per komenda,
- walidatorów domenowych per komenda,
- cooldownów zapisywanych w trwałym stanie,
- rozbudowanych ról administracyjnych zamiast prostego `admin`/`player`,
- automatycznego eksportu dokumentacji komend do pliku.

## Następny etap
D25 — Testing Engine: fake clients, fake world, regression harness dla komend i testy scenariuszowe bez prawdziwego socketu.
