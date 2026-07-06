# AUDIT D2 — modularizacja rdzenia

## Cel
Usunąć centralizację logiki komend w `astergard/server/game.py` bez zmiany zachowania gry.

## Zmiany wykonane
- Dodano `astergard/server/context.py` jako jawny kontekst wykonania komend.
- Przeniesiono logikę komend z `server/game.py` do modułów domenowych:
  - `astergard/commands/exploration.py`
  - `astergard/commands/communication.py`
  - `astergard/commands/character_sheet.py`
  - `astergard/commands/inventory.py`
  - `astergard/commands/combat.py`
  - `astergard/commands/social_systems.py`
  - `astergard/commands/economy.py`
  - `astergard/commands/magic_crafting.py`
  - `astergard/commands/system.py`
  - `astergard/commands/helpers.py`
  - `astergard/commands/registration.py`
- `GameServer` pełni teraz rolę orkiestratora: inicjalizuje repozytoria, menedżery, serwer TCP i heartbeat.
- Zachowano kompatybilność testów przez aliasy `server.cmd_*`, ale implementacje znajdują się w modułach komend.
- Dodano testy regresji modularności: sprawdzenie modułu handlera, aliasów kompatybilności i limitu długości `server/game.py`.

## Metryki
- `astergard/server/game.py`: 336 linii przed D2 → 177 linii po D2.
- Liczba testów: 7 → 10.
- Wynik: `Ran 10 tests in 0.034s OK`.

## Co nadal jest niedopracowane
- `GameServer` nadal tworzy wszystkie menedżery bez osobnego bootstrappera lub dependency container.
- Komendy są rozdzielone, ale część logiki aplikacyjnej nadal znajduje się bezpośrednio w handlerach komend zamiast w usługach application-layer.
- Brakuje pełnego testu manualnego przez socket/Telnet w automacie.
- Brakuje statycznej kontroli importów/cykli zależności.

## Decyzja następnego etapu
D3 powinien wprowadzić `GameBootstrapper` i warstwę usług aplikacyjnych dla eksploracji, ekwipunku, walki i ekonomii. Dopiero wtedy handler komendy będzie tylko adapterem wejścia/wyjścia.
