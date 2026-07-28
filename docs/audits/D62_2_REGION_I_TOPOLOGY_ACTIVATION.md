# D62.2 Region I Topology Activation Audit

## Scope

- Canonical Region I topology is loaded from `astergard/world/data/region_i.json`.
- `WorldManager.generate_world()` now activates the Region I subgraph atomically.
- Old rooms `2-13` and `15-19` are removed from runtime.
- No NPC, quest, shop, trainer, or Mudlet package migration was attempted in this step.

## What Changed

- Region I room metadata is now copied from the canonical JSON into runtime.
- Region I exits are rebuilt from the canonical JSON edge list.
- All exits from Region I to rooms outside the canonical set are removed.
- Content overlay is skipped for Region I in one explicit point in `apply_content_pack()`.
- GMCP area labels now recognize the new Region I `regionId` values.

## Deliberately Deferred

- No legacy boundary links were reintroduced for rooms `187`, `190`, `195`, `200`, `210`, or `335`.
- No pilot descriptions were attached yet.
- No NPC / shop / trainer / quest remapping was performed.
- No persistence migration was performed.
- No second source of truth was introduced for the topology.

## Validation

- Targeted D62 tests passed.
- `ruff check .` passed.
- `mypy .` passed.
- Full `pytest` was run and the remaining failures are dominated by:
  - tests that still assert the old 500-room geography or old content overlay,
  - websocket gateway tests blocked by sandbox socket restrictions.

## Notes

- Region I rooms now use JSON `regionId` values as runtime `zone` values.
- This is intentional for topology activation, but it breaks older content and regional tests that still assume the previous zone model.
- The activation is mechanically correct, but the repository still needs later content and systems migration to bring old region-specific tests back into alignment.
