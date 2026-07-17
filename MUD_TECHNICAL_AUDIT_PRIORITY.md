# ASTERGARD D54 - Technical Audit With Priorities

## Verdict

Astergard is structurally solid as a MUD server. The main risks are not missing mechanics, but:

- schema and state coupling,
- hardcoded NPC/world behavior,
- an overgrown exploration service,
- coarse weather/time simulation,
- content-template repetition.

No blocking runtime defect stands out from the current codebase review. The issues below are the ones most likely to hurt maintenance, extension work, and long-term consistency.

## Priority Scale

- `P1` - high impact, likely to hurt development or correctness soon.
- `P2` - medium impact, mostly maintainability or consistency debt.
- `P3` - lower-priority cleanup.

## P1-1. World snapshot persistence is too monolithic

### Evidence

- [astergard/database/world_state_repository.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/database/world_state_repository.py:81)
- [astergard/database/world_state_repository.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/database/world_state_repository.py:111)
- [astergard/database/world_state_repository.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/database/world_state_repository.py:203)

### What is happening

`WorldStateRepository` serializes almost the entire mutable world into one JSON blob:

- every location,
- all ground items,
- hidden elements,
- exits,
- NPC identity and room state,
- NPC character data,
- respawn queue.

### Why it matters

This is convenient, but it creates a high-coupling save format:

- schema changes are expensive,
- partial recovery is hard,
- one corrupted branch can make the whole snapshot risky,
- migration discipline becomes critical as the game grows.

### Recommendation

Split state into a small number of durable tables or versioned subdocuments:

- world topology deltas,
- location contents,
- NPC runtime state,
- respawn queue.

If the JSON snapshot stays, add explicit versioning and per-section validation.

## P1-2. NPC behavior is still driven by large hardcoded vnum switches

### Evidence

- [astergard/npcs/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/npcs/manager.py:47)
- [astergard/npcs/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/npcs/manager.py:210)
- [astergard/npcs/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/npcs/manager.py:252)

### What is happening

NPC population and route logic depend on:

- a long list of explicit `spawn(...)` calls,
- hardcoded `vnum` groups in `_route_depth_for()`,
- local route selection by zone and depth,
- daily routine labels interpreted elsewhere.

### Why it matters

This is the biggest long-term content scaling risk:

- adding a new NPC often requires touching multiple branches,
- behavior is easy to classify inconsistently,
- route depth and daily activity are data-like, but encoded as code,
- the same role knowledge is duplicated in several places.

### Recommendation

Move NPC archetype metadata into the factory or content layer:

- role,
- route depth,
- daily routine profile,
- hostility / merchant / civilian behavior,
- allowed zones.

The manager should execute behavior, not encode most of the behavior taxonomy.

## P1-3. ExplorationService is a god service for world perception

### Evidence

- [astergard/application/services/exploration_service.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/services/exploration_service.py:37)
- [astergard/application/services/exploration_service.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/services/exploration_service.py:117)
- [astergard/application/services/exploration_service.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/services/exploration_service.py:190)

### What is happening

One class currently handles:

- room rendering,
- exit lookup and semantic phrasing,
- inspectables,
- container inspection,
- NPC and item lookup,
- movement,
- search,
- sensory verbs,
- ambient injection.

### Why it matters

This is not a bug, but it is a maintenance hotspot:

- unrelated changes are likely to collide,
- subtle regressions in one branch can affect look/move/search/sense,
- unit tests must cover many branches to keep behavior stable.

### Recommendation

Split this into smaller internal helpers or services:

- scene rendering adapter,
- movement use case,
- inspection/search use case,
- exit phrasing helper.

The public service can stay the same; the internals need less entanglement.

## P2-4. Time and weather simulation is intentionally light, but very coarse

### Evidence

- [astergard/weather/time_weather.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/weather/time_weather.py:18)
- [astergard/weather/time_weather.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/weather/time_weather.py:33)
- [astergard/weather/time_weather.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/weather/time_weather.py:56)

### What is happening

The weather system:

- advances time in simple hourly steps,
- randomly assigns weather every 240 ticks,
- stores weather per zone,
- emits ambient lines from a small pool.

### Why it matters

The model is fine for a classic MUD, but it behaves like a descriptive layer more than a world climate model:

- weather has little memory,
- zone ecology is shallow,
- seasonal and weather transitions are mostly textual.

### Recommendation

If more world depth is desired, add a small weather state machine:

- onset,
- persistence,
- decay,
- zone-specific weather tendencies.

That would improve coherence without adding heavy mechanics.

## P2-5. Narrative quality depends heavily on content discipline

### Evidence

- [astergard/world/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/world/manager.py:27)
- [astergard/world/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/world/manager.py:120)
- [astergard/narrative.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/narrative.py:725)
- [astergard/narrative.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/narrative.py:766)

### What is happening

World generation uses region fallback descriptions and a large content pack overlay. The renderer is strong, but it still depends on decent source data.

### Why it matters

If a region has weak source text, the renderer cannot fully hide it. This is not a technical bug, but it is the main quality ceiling for the world:

- repeated opener patterns can leak through,
- generic fallback phrasing can make a region feel templated,
- narrative quality becomes uneven if authored content is inconsistent.

### Recommendation

Keep reviewing region data separately from engine work:

- high-traffic city zones first,
- then roads and travel spaces,
- then wilderness and dungeons.

## P2-6. Save/autosave lifecycle is broad and can amplify write frequency

### Evidence

- [astergard/engine/lifecycle.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/engine/lifecycle.py:31)
- [astergard/engine/lifecycle.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/engine/lifecycle.py:75)
- [astergard/server/game.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/server/game.py:141)

### What is happening

The engine periodically autosaves:

- world state,
- player states,
- full flushes on shutdown or failure,
- character save on disconnect.

### Why it matters

This is operationally safe, but it can become noisy:

- frequent writes,
- overlapping save triggers,
- harder reasoning about what caused a persisted state change.

### Recommendation

Keep the current safety behavior, but add clearer separation between:

- periodic autosave,
- disconnect save,
- shutdown flush,
- failure recovery flush.

That will help debugging persistence issues later.

## System-by-System Status

### Strong

- bootstrap and dependency wiring,
- command dispatcher,
- Polish parser,
- combat separation,
- quest progression,
- observability,
- living world hooks.

### Adequate

- persistence,
- time/weather,
- world generation,
- inventory and item presentation,
- admin tooling.

### Needs Ongoing Attention

- NPC behavior taxonomy,
- snapshot schema evolution,
- narrative consistency in region content,
- exploration-service complexity.

## Bottom Line

The codebase is past the stage where the main problem is missing features. The main technical risk is that the world is becoming rich enough that content and state models need to be more data-driven, less hardcoded, and easier to evolve independently.

If you want the next pass, the highest-value work is:

1. decouple NPC archetypes from manager switches,
2. split world snapshot persistence into versioned sections,
3. reduce exploration-service branching density,
4. continue pruning region template text.
