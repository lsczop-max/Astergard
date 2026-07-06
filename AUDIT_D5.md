# AUDIT D5 — application services for exploration, communication, magic/crafting and system commands

## Cel
D5 usuwa kolejną warstwę logiki z handlerów komend. Po D4 aplikacyjne use-case'y obejmowały ekwipunek, walkę, questy i ekonomię. D5 rozszerza ten wzorzec na eksplorację, komunikację, magię/crafting oraz komendy systemowe.

## Wykonane zmiany
- Dodano `astergard/application/services/exploration_service.py`.
- Dodano `astergard/application/services/communication_service.py`.
- Dodano `astergard/application/services/magic_crafting_service.py`.
- Dodano `astergard/application/services/system_service.py`.
- Rozszerzono `GameServices` o nowe usługi aplikacyjne.
- Odchudzono handlery:
  - `commands/exploration.py`,
  - `commands/communication.py`,
  - `commands/magic_crafting.py`,
  - `commands/system.py`.
- Dodano `tests/test_d5_service_split.py`.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 23 tests in 0.110s
OK
```

## Ocena techniczna
Po D5 większość komend jest cienkimi adapterami. Logika świata, ruchu, komunikacji, zapisu, magii i craftingu jest przesunięta do warstwy aplikacyjnej.

## Pozostałe ryzyka
- `GameContext` nadal udostępnia cały `GameServer`, więc usługi mają dostęp do zbyt szerokiego API.
- Komunikacja nadal zwraca tekst tylko nadawcy; nie ma pełnego broadcastu do innych połączeń.
- Magic/crafting nadal są grywalnym rdzeniem, nie pełnym systemem produkcyjnym.
- Ranking nadal jest komunikatem lokalnym, bez realnego zapytania top-listy.

## Następny etap
D6 powinien ograniczyć `GameContext` i wprowadzić jawne porty/aplikacyjne gatewaye dla świata, NPC, repozytorium i obecności graczy. To zmniejszy sprzężenie usług z `GameServer`.
