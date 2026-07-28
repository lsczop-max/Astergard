# D62.2D Region I WebSocket Contract Repair

## Scope

- Stabilized the active Region I on top of the canonical runtime asset.
- Kept the working tree uncommitted and preserved unrelated user changes.
- Did not touch:
  - `client/mudlet/releases/Astergard.mpackage`
  - `client/mudlet/maps/astergard_map.json`

## What Was Stabilized

- `blacksmith` now homes in room `33` (`Żelazna Pierzeja`).
- `woodcutter` now homes in room `64`, matching the existing `wood_delivery` contract keyed off `podgrodzie_firewood_64`.
- Region-aware zone handling remains canonical:
  - `centrum`
  - `trakt`
  - `trakt-gorniczy`
  - `trakt-nadrzeczny`
  - `polnocny-las`
  - `nadrzeczne-mokradla`
- The 15 pilot descriptions continue to be active through the normal runtime path.
- The canonical Region I topology remains atomically loaded from `astergard/world/data/region_i.json`.

## Root Cause

- The websocket gateway tests were still asserting the pre-change Region I topology:
  - several login and command tests hard-coded `room_id = 60`,
  - the movement contract test used `poludnie` even though the canonical start room `14` now exits `wschod -> 1`,
  - the room-info filter test was still built around a room that did not match the new start-room exit layout.
- Those stale assumptions made the test suite wait on the wrong room-change contract after the topology rewrite.
- The existing `recv()` calls also had no per-read timeout wrapper, so a missing frame could stall the test indefinitely instead of failing fast with a clear timeout.

## Fix

- Updated the gateway tests to the canonical Region I topology:
  - moved the relevant test characters from room `60` to room `14`,
  - changed the movement test to use `wschod` from room `14` to room `1`,
  - kept the contract that `room.info` arrives before the command result text,
  - asserted that the emitted `room.info` points at room `1`,
  - aligned the room-info exit expectations with the new Region I exits.
- Added a test-only websocket proxy that wraps every `recv()` in `asyncio.wait_for()`, so missing messages fail quickly and readably without changing production behavior.

## Validation

- `./.venv/bin/ruff check .`
  - passed
- `./.venv/bin/mypy .`
  - passed
- `./.venv/bin/pytest -q -k 'not test_d59_websocket_gateway'`
  - passed
  - result: `552 passed, 30 deselected, 51 subtests passed`
- `./.venv/bin/pytest -q tests/test_d59_websocket_gateway.py -k test_move_emits_room_info_before_command_text`
  - passed
- `./.venv/bin/pytest -q tests/test_d59_websocket_gateway.py`
  - passed
  - result: `30 passed`

## Full Pytest Status

- The websocket gateway portion now completes cleanly in this environment.
- The prior stall was caused by stale test topology assumptions, not by the production gateway.

## Functional Recovery

- Restored canonical Region I exploration and navigation.
- Restored canonical GMCP and minimap behavior for the active topology.
- Restored the blacksmith service contract in the right city district.
- Restored the `wood_delivery` quest start contract by relocating `woodcutter` to a live room.

## Remaining Constraint

- No remaining blocker was observed during local validation.

## Verdict

- `D62_2D_READY_FOR_LOCAL_VALIDATION`
