# AUDIT D10 — Persistence, SQLite migrations and repository boundaries

## Scope
D10 hardens the persistence layer after D9. The goal was to stop treating database schema evolution as hidden repository code and make save/load behavior explicit, versioned and testable.

## Changes made
- Added `astergard/database/migrations.py`.
- Added SQL migrations:
  - `001_initial.sql` — base `players` table.
  - `002_audit_timestamps.sql` — `created_at` and `updated_at` fields.
  - `003_save_slots.sql` — `save_version` field.
- Updated `PlayerRepository` to apply migrations through `MigrationRunner`.
- Added `PlayerRepository.current_schema_version()` for diagnostics and tests.
- Updated `PlayerRepository.save()` to increment `save_version` and update `updated_at` on every save.
- Added migration and persistence regression tests.

## Test result

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 38 tests in 0.213s
OK
```

## Critical review
D10 improves schema control but does not yet split persistence into multiple repositories. `PlayerRepository` still serializes a full aggregate into JSON columns. This is acceptable for the current playable core, but not final for a production-scale MUD.

## Remaining risks
- Full inventory, quest and combat state are stored as JSON blobs rather than normalized tables.
- There is no online migration strategy for a live server.
- Password hashing still uses salted SHA-256 because the original prompt required it; production should move to `hashlib.pbkdf2_hmac`, `argon2`, or `bcrypt`.
- No automated backup/restore command has been added yet.

## Recommended D11
Normalize persistence boundaries:
- `PlayerAccountRepository`
- `CharacterStateRepository`
- `WorldStateRepository`
- `AuditLogRepository`

D11 should also add backup/restore utilities and save/load integration tests around logout and crash recovery.
