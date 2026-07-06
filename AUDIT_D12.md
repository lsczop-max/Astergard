# AUDIT D12 — trwały zapis świata, NPC i kolejki respawnu

## Cel
D12 zamyka lukę persistence: przed tym etapem restart serwera odtwarzał świat z generatora i startowego `NPCManager.populate()`. Stan gruntu, NPC, ukrytych elementów i kolejki respawnu nie był trwały.

## Wykonane zmiany
- Dodano `astergard/database/world_state_repository.py`.
- Dodano migrację `005_world_state.sql` i tabelę `world_snapshots`.
- `PlayerRepository` otrzymał jawny port `world_state`.
- `GameBootstrapper` ładuje istniejący snapshot świata albo tworzy snapshot startowy po pierwszym `populate()`.
- `HeartbeatService.tick_once()` zapisuje stan świata po ticku NPC/respawnu.
- `GameServer.handle_connection()` zapisuje świat przy zamknięciu sesji.
- Dodano testy D12 dla:
  - trwałości przedmiotów na ziemi,
  - trwałości ukrytych elementów,
  - trwałości NPC i ich ran/stanu AI,
  - trwałości kolejki respawnu,
  - ładowania snapshotu przez bootstrap zamiast repopulacji.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 43 tests in 0.459s
OK
```

## Krytyczna ocena
D12 poprawia trwałość świata, ale nadal nie jest to pełny produkcyjny event sourcing. Snapshot jest pojedynczy (`id = 1`) i zapisuje cały stan świata jako JSON. To jest rozsądne dla grywalnego rdzenia i małej skali 500 lokacji, ale przy większej liczbie lokacji/NPC należy przejść do zapisu różnicowego lub tabel domenowych: `world_location_state`, `npc_state`, `respawn_queue`.

## Następny etap
D13 — rozbudowa NPC AI i respawnu: patrol z komunikatami do graczy, agresja frakcyjna, stabilne usuwanie martwych NPC, ograniczenia populacji oraz testy scenariuszy wielotickowych.
