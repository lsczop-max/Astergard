# AUDIT D7 — Use-case contexts

## Cel
Rozdzielić wspólny `GameContext` na wąskie konteksty przypadków użycia, aby komendy i usługi aplikacyjne nie korzystały z całego kontenera usług ani z warstwy TCP.

## Wykonane zmiany
- Dodano `astergard/application/use_case_contexts.py`.
- `GameContext` przestał publicznie eksponować `services`.
- Dodano wąskie konteksty:
  - `ExplorationContext`,
  - `InventoryContext`,
  - `CombatContext`,
  - `QuestContext`,
  - `EconomyContext`,
  - `MagicCraftingContext`,
  - `SystemContext`,
  - `CommunicationContext`.
- Usługi aplikacyjne nie importują już `GameContext` z `astergard.server.context`.
- Komendy tworzą kontekst właściwy dla danego use-case i przekazują go do usługi.
- Dodano testy kontraktowe D7.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 29 tests in 0.135s
OK
```

## Ocena krytyczna
D7 istotnie ogranicza coupling, ale komendy nadal wywołują prywatne `_services`, bo dispatcher nadal działa na jednym `GameContext`. To jest kompromis kompatybilności pośredniej. Następny etap powinien usunąć tę zależność przez rejestrację gotowych command handlers z wstrzykniętymi usługami albo przez `CommandBus`.

## Następny etap
D8 — wprowadzenie `CommandBus` / fabryk handlerów, tak aby komendy nie znały kontenera usług nawet prywatnie.
