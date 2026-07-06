# AUDIT D9 — GameContext assembly boundary

## Cel
Usunąć z `GameContext` odpowiedzialność za budowę kontekstów use-case oraz wiedzę o pełnym kontenerze `GameServices`.

## Zmiany wykonane
- Dodano `astergard/application/context_assembler.py`.
- `GameContext` stał się prostym nośnikiem jawnych portów use-case.
- `GameContext` nie przechowuje już `_services` ani `services`.
- Budowanie `ExplorationContext`, `InventoryContext`, `CombatContext`, `QuestContext`, `EconomyContext`, `MagicCraftingContext`, `SystemContext` i `CommunicationContext` przeniesiono do `GameContextAssembler`.
- `GameServer` używa `GameContextAssembler` do tworzenia kontekstu komendy.
- Zachowano kompatybilność z wcześniejszymi testami przez port `players_in_room` i właściwości `world`/`repo`.

## Testy
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 35 tests in 0.141s
OK
```

## Ocena krytyczna
D9 poprawia granicę między warstwą serwera i aplikacji. Nadal jednak `GameServer` eksponuje pola kompatybilności (`world`, `repo`, `npcs`, itd.), co jest praktyczne dla testów i starego API, ale docelowo powinno zostać schowane za portami read-only. Następny etap: D10 — uporządkowanie repozytoriów i migracji SQLite.
