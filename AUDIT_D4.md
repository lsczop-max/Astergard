# AUDIT D4 — Application Use Case Services

## Cel

D4 kontynuuje refaktoryzację po D3. Celem było przeniesienie reguł aplikacyjnych z handlerów komend do testowalnych usług use-case, bez zmiany zachowania gry.

## Problem przed D4

Po D3 `GameServer` był już adapterem TCP, ale część handlerów w `astergard/commands/` nadal zawierała logikę gry:

- `commands/inventory.py` przenosił przedmioty, sprawdzał udźwig i zakładał wyposażenie.
- `commands/combat.py` koordynował atak, tworzenie zwłok, progres questów i reputację.
- `commands/economy.py` lokalizował kupca i wykonywał transakcje.
- `commands/social_systems.py` mieszał dialogi z logiką dodawania questów.

To było lepsze niż wcześniejszy `GameServer`, ale nadal łamało zasadę cienkich adapterów.

## Zmiany wykonane

Dodano pakiet:

- `astergard/application/services/`

Dodano usługi:

- `InventoryService`
- `CombatApplicationService`
- `QuestApplicationService`
- `EconomyApplicationService`

Zaktualizowano:

- `astergard/application/bootstrap.py`
- `astergard/commands/inventory.py`
- `astergard/commands/combat.py`
- `astergard/commands/economy.py`
- `astergard/commands/social_systems.py`

## Efekt architektoniczny

Handlery komend są teraz cienkimi adapterami:

- odbierają `GameContext`, argument i indeks,
- pobierają ewentualną lokację lub przekazują kontekst,
- delegują wykonanie do usługi aplikacyjnej.

Reguły gry przeniesiono do warstwy aplikacyjnej, gdzie można je testować bez połączeń TCP.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 18 tests in 0.095s
OK
```

## Nowe testy

Dodano `tests/test_d4_application_use_cases.py`.

Testy sprawdzają:

- delegację ekwipunku do `InventoryService`,
- przenoszenie przedmiotu z lokacji do postaci przez usługę,
- obecność koordynacji walki/questów/frakcji w `CombatApplicationService`,
- cienkość handlerów komend po D4,
- to, że bootstrap używa tych samych instancji managerów w usługach aplikacyjnych.

## Krytyczna ocena

D4 poprawia separację odpowiedzialności, ale nie kończy prac architektonicznych.

Pozostałe problemy:

1. `GameContext` nadal zawiera referencję do całego `GameServer`, więc handlery nadal mogą sięgnąć po zbyt wiele zależności.
2. Nie ma jeszcze abstrakcyjnych portów dla repozytorium, świata i NPC.
3. `CombatApplicationService` nadal zna `GameContext`, co jest przejściowym kompromisem.
4. `commands/exploration.py`, `commands/communication.py`, `commands/magic_crafting.py` oraz `commands/system.py` nadal wymagają analogicznego wydzielenia usług.

## Następny etap

D5 powinien wprowadzić `ApplicationContext` albo `ServiceContainer` jako węższy interfejs dla handlerów i wydzielić usługi:

- `ExplorationService`,
- `CommunicationService`,
- `MagicCraftingApplicationService`,
- `SystemCommandService`.
