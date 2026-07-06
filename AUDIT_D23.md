# AUDIT D23 — Save/Load Engine

## Cel
Domknięcie silnikowego cyklu zapisu i odczytu po D22: centralny save/load engine, manifesty zapisu, checkpointy, restore i recovery świata.

## Zakres wykonania
- Dodano `astergard/engine/save_load.py`.
- Dodano `SaveLoadEngine`, `SavePolicy`, `SaveResult`.
- Dodano `database/save_manifest_repository.py`.
- Dodano migrację `007_save_manifests.sql`.
- `GameServices` otrzymał jawny `save_load`.
- `EngineLifecycle` używa `SaveLoadEngine` zamiast ręcznie zapisywać graczy i świat.
- Rozłączenie sesji używa `save_character()` i `save_world()`.
- Dodano manifesty dla: character, world, full flush, backup, restore, world recovery.
- Dodano checkpoint/restore oparty o istniejący `BackupService`.

## Testy
Uruchomiono:

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 91 tests in 1.583s
OK
```

## Nowe testy
- `test_flush_all_records_manifests_and_versions`
- `test_checkpoint_and_restore_round_trip_database_file`
- `test_recover_world_reports_snapshot_presence`

## Krytyczna ocena
D23 domyka podstawowy save/load engine, ale nie jest to jeszcze pełny event-sourced persistence ani snapshot diff na poziomie obiektu. Zapis nadal jest snapshotowy, co jest akceptowalne dla obecnego rdzenia MUD-a. Następny etap powinien skupić się na Command Engine: cooldowny, permissions, help generowany z rejestru i walidacja argumentów.

## Następny etap
D24 — Command Engine.
