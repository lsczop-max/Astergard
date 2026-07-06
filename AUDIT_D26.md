# AUDIT D26 — Admin / GM Engine

## Status
Implemented and tested against the real D25 codebase.

## Scope
D26 adds a real administrative layer instead of the previously declared but unverifiable D26 report.

## New modules
- `astergard/admin/permissions.py`
- `astergard/admin/audit_logger.py`
- `astergard/admin/admin_service.py`
- `astergard/admin/gm_commands.py`

## Modified modules
- `astergard/commands/engine.py` — expanded permission model.
- `astergard/application/command_bus.py` — command definitions now carry permission metadata.
- `astergard/commands/registration.py` — registers Admin/GM commands.
- `astergard/application/use_case_contexts.py` — adds `AdminContext`.
- `astergard/application/context_assembler.py` — assembles admin context.
- `astergard/server/context.py` — exposes admin context to handlers.
- `astergard/server/game.py` — exposes active player list to admin context.
- `astergard/application/bootstrap.py` — wires `AdminAuditLogger` and `AdminService`.

## Commands added
- `inspect [gracz]`
- `teleport <gracz> <lokacja>`
- `goto <lokacja>`
- `summon <gracz>`
- `heal [gracz]`
- `adminkill <gracz> confirm`
- `give <gracz> <item>`
- `setstat <gracz> <stat> <wartość>`
- `spawnnpc <vnum> [lokacja]`
- `saveworld`
- `checkpoint`
- `restore <ścieżka> confirm`
- `worldstats`
- `auditlog [limit]`
- `scheduler`
- `listsessions`

## Permission model
Roles are ordered:

1. `PLAYER`
2. `HELPER`
3. `GM`
4. `ADMIN`
5. `OWNER`

The username `admin` is treated as `OWNER` for emergency/bootstrap access. Tests can assign `character.admin_role` dynamically.

## Safety controls
- GM/admin handlers are thin adapters over `AdminService`.
- Successful admin mutations are recorded by `AdminAuditLogger`.
- Destructive commands require explicit `confirm`.
- Permission denial is enforced by the command engine before handler execution.

## Tests added
`tests/test_d26_admin_gm_engine.py` covers:
- player denial for GM commands,
- GM inspect and teleport,
- admin world save and audit log,
- destructive kill confirmation,
- GM NPC spawn and session listing,
- role ordering.

## Test result

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 107 tests in 1.946s
OK
```

Command regression script also runs successfully:

```text
python3 scripts/run_command_regression.py
```

## Critical notes
This D26 is real and test-backed, but still core-level rather than production-grade. Missing production features:
- persistent admin-role table,
- command confirmation session state instead of inline `confirm`,
- structured audit browsing from SQLite by global filters,
- live shutdown orchestration through network loop,
- full restore reload of in-memory state after DB restore.

## Next recommended stage
D27 — Observability & Diagnostics:
- metrics registry,
- tick latency counters,
- command latency counters,
- event bus counters,
- scheduler diagnostics,
- GM diagnostic commands backed by metrics.
