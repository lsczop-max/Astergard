# AUDIT D11 — Persistence repositories, audit log and backup/restore

## Cel etapu
D10 wprowadził migracje SQLite, ale `PlayerRepository` nadal łączył zbyt wiele odpowiedzialności: konta, hasła, zapis stanu postaci, serializację JSON, migracje i połączenia. D11 rozdziela tę warstwę bez zmiany API używanego przez grę.

## Wykonane zmiany
- Dodano `astergard/database/connections.py` z `SQLiteConnectionFactory`.
- Dodano `astergard/database/serialization.py` z `CharacterStateSerializer`.
- Dodano `astergard/database/account_repository.py` z `AccountRepository`.
- Dodano `astergard/database/character_state_repository.py` z `CharacterStateRepository`.
- Dodano `astergard/database/audit_repository.py` z `AuditRepository` i `AuditEvent`.
- Dodano `astergard/database/backup.py` z `BackupService`.
- Dodano migrację `004_audit_events.sql`.
- Przepisano `PlayerRepository` jako fasadę kompatybilności nad wyspecjalizowanymi repozytoriami.
- Dodano publiczne metody `save_version`, `create_backup`, `restore_backup`.
- Dodano prosty ranking w repozytorium, aby istniejący `SystemService` miał realną implementację.

## Testy dodane lub zaktualizowane
- `tests/test_d11_repositories_backup.py`
  - sprawdza podział repozytoriów,
  - sprawdza audyt rejestracji, weryfikacji i zapisu,
  - sprawdza backup/restore z zachowaniem stanu postaci.
- `tests/test_d10_persistence_migrations.py`
  - zaktualizowany do schematu wersji 4.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 41 tests in 0.291s
OK
```

## Krytyczna ocena
D11 usuwa nadmierne skupienie odpowiedzialności w `PlayerRepository`, ale repozytoria nadal zapisują stan postaci jako JSON w jednej tabeli `players`. To jest akceptowalne dla grywalnego rdzenia, lecz nie jest idealne dla pełnego MUD-a produkcyjnego.

## Następny etap
D12 powinien rozbić model trwałości świata: osobny zapis stanu świata, NPC, respawn queue, ekonomii świata i audytu administracyjnego. Obecnie świat jest deterministycznie generowany i większość jego stanu nie jest trwale zapisywana.
