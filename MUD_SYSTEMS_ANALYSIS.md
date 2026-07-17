# ASTERGARD D54 - Full MUD Systems Analysis

## Scope

This report analyzes the current MUD stack in Astergard as a living server:

- composition and bootstrapping,
- session/login/command flow,
- parser and dispatcher,
- world model and narration,
- time, weather, and ambient simulation,
- NPC population and AI,
- combat,
- quests,
- economy, crafting, and magic,
- persistence and save/load,
- observability and admin tooling,
- tests and audit tooling.

The goal is to describe how the systems fit together, where state lives, and which parts are tightly coupled.

## Executive Summary

Astergard is not a collection of independent mechanics. It is a layered simulation with one explicit composition root and a central world loop:

1. `GameBootstrapper` wires the full object graph.
2. `SessionFlow` owns login and command-loop orchestration.
3. `CommandDispatcher` resolves Polish commands into use-case handlers.
4. `ExplorationService` renders the world and handles movement.
5. `NPCManager`, `TimeAndWeatherManager`, and the heartbeat keep the world moving when the player does nothing.
6. Combat, quests, economy, magic, and crafting are coordinated around events and shared world state.

The strongest part of the architecture is that world state, NPC movement, weather, and narration all operate on the same underlying location graph. The biggest sources of complexity are content density, narrative consistency, and the amount of state that is currently spread across world generation, content overlays, and runtime AI.

## 1. Composition Root

The whole server is assembled in [astergard/application/bootstrap.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/bootstrap.py).

Important points:

- `GameBootstrapper.build()` creates the ruleset first, then repositories, world, NPC manager, combat, factions, quests, economy, event bus, scheduler, and observability.
- World generation happens before population.
- NPC state can be loaded from save data; if not, the world is freshly populated and persisted.
- `register_commands()` binds the command handlers after the services exist.
- `GameServices` is the central service container used across the application layer.

This is a clean composition-root pattern. The server layer does not need to know how world generation or service wiring works.

## 2. Session and Command Flow

The player lifecycle is handled in [astergard/application/session_flow.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/session_flow.py).

Observed flow:

- login / character creation,
- initial render,
- optional minimap payload,
- command loop,
- movement and actions routed through the dispatcher.

The login layer is intentionally narrative-heavy, but it is still part of the same server flow.

The command pipeline is:

1. `CommandParser.parse()` normalizes input.
2. `CommandDispatcher.execute_line()` resolves the command, permission checks, and cooldowns.
3. The command handler runs on the context object.
4. The output is colorized and returned to the client.
5. Observability records execution timing and outcome.

The dispatcher is simple and readable. It is also a single choke point for all player actions, which makes it a good place for permissions, metrics, and error handling.

See:

- [astergard/commands/dispatcher.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/commands/dispatcher.py)
- [astergard/commands/parser.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/commands/parser.py)

## 3. Command Parsing Model

The parser is language-aware rather than keyword-only.

Notable behavior:

- Polish normalization and stopword stripping.
- Direction aliases such as `n`, `pn`, `nw`, `gora`, `dol`.
- Multiword commands like `do srodka` and `na zewnatrz`.
- Ordinal selection for indexed targets.
- Relation-sensitive parsing for commands such as `spojrz`, `obejrzyj`, `daj`, `wez`, `wloz`.

This is a strong fit for a Polish MUD. The parser is still light enough to remain maintainable, but expressive enough to support the current command vocabulary.

## 4. World Model

The domain model is defined in [astergard/world/models.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/world/models.py).

Core entities:

- `Location`
- `Exit`

The location model includes:

- room identity,
- name and description,
- zone,
- exits,
- items,
- NPC ids,
- hidden elements,
- inspectables,
- grammatical forms,
- scene anchor.

The exit model includes more than just target room:

- door state,
- locked state,
- key reference,
- exit kind,
- visibility,
- width,
- slope,
- material,
- requirements,
- description.

This is important because the renderer can describe exits as part of the scene rather than as a universal “direction list”.

## 5. World Generation and Content

The world is created in [astergard/world/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/world/manager.py) and then enriched by [astergard/world/content.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/world/content.py).

The world structure is large and region-based:

- centered around a 500-room map,
- split into named region ranges,
- connected by hand-authored exits,
- overlaid with content generators and local adjustments.

From a systems perspective, this means:

- `WorldManager` owns topology and room graph,
- `content.py` owns region flavor, object placement, and presentation metadata,
- runtime services read both and never need to know how rooms were authored.

This separation is useful, but it also means repeated phrases or templated region text can appear if content generation is too uniform. The narrative layer can reduce this, but it cannot fully hide weak underlying content.

## 6. Narrative Rendering

The scene renderer is the key immersion layer:

- [astergard/narrative.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/narrative.py)
- [astergard/application/services/exploration_service.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/services/exploration_service.py)

The renderer builds a `WorldScene` containing:

- title,
- base description,
- zone and terrain,
- time of day,
- season,
- weather,
- world state,
- visibility,
- lighting,
- temperature,
- exits,
- items,
- NPCs,
- sensory clauses and notable elements.

The render pipeline now produces a proper scene instead of a loose list of fragments:

1. room title,
2. base description,
3. time/weather/season/world-state clauses,
4. sound / smell / wear / life clauses,
5. items,
6. NPC activity,
7. exits.

That is a good architectural shape. The renderer can still be improved stylistically, but structurally it is doing the right job: it converts live state into one coherent view.

The most important integration point is `move_direct()`, which now ends with a full `look()` on arrival. That makes movement and perception consistent.

## 7. Time, Weather, and Ambient World State

The simulation clock lives in [astergard/weather/time_weather.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/weather/time_weather.py).

Responsibilities:

- time progression,
- season selection,
- zone weather,
- ambient events,
- world-state layers.

The weather manager is deliberately simple:

- one hour counter,
- one seasonal layer,
- zone-specific weather values,
- periodic weather changes,
- ambient text generation.

This works well for a MUD because it keeps the simulation readable and cheap. The downside is that it is still coarse-grained. Weather is mostly descriptive and only lightly mechanical.

## 8. NPC System

The NPC stack is one of the strongest simulation parts.

Files:

- [astergard/npcs/models.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/npcs/models.py)
- [astergard/npcs/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/npcs/manager.py)

What it covers:

- NPC identity and presentation,
- faction and AI state,
- merchant behavior,
- inventory and shop stock,
- dialogue,
- home room,
- respawn delay,
- daily schedule and daily activity,
- scene line rendering.

What the manager does:

- populates the world with NPCs,
- prevents overcrowding,
- moves NPCs through local routes,
- applies daily routines by day phase,
- advances guard, patrol, and aggressive behavior,
- emits action events.

This makes the world feel alive even when the player is absent. NPCs are not only stat blocks; they have schedules and local movement.

Remaining limitation:

- scene lines can still become verbose if base short descriptions, routine fragments, and activity strings stack too aggressively.

## 9. Combat System

Combat is split into several layers:

- [astergard/combat/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/combat/manager.py)
- [astergard/application/services/combat_service.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/application/services/combat_service.py)
- [astergard/combat/narration.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/combat/narration.py)
- [astergard/combat/tactics.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/combat/tactics.py)
- [astergard/combat/wounds.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/combat/wounds.py)

Mechanical profile:

- initiative-driven turns,
- style modifiers,
- weapon reach,
- skills,
- dodge,
- fatigue,
- wounds,
- morale,
- formation modifiers,
- tactical professions,
- body-part targeting.

The application service then coordinates side effects:

- corpse spawning,
- faction changes,
- reputation changes,
- quest progress,
- death removal,
- event emission.

This is a good separation:

- the combat manager handles combat math,
- the application service handles world consequences.

## 10. Quests

Quest logic lives in [astergard/quests/manager.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/quests/manager.py) and the application layer service around it.

Quest model:

- id,
- title,
- description,
- start and completion NPC,
- offer/reminder/completion text,
- objectives,
- rewards,
- optional auto-complete on delivery.

Supported objective types:

- `talk`
- `give`
- `kill`

This is a compact quest system. It is event-friendly and easy to author, but it is not a graph quest engine. That is appropriate for a MUD of this size.

## 11. Economy, Crafting, and Magic

Economy:

- [astergard/economy/services.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/economy/services.py)

Magic:

- [astergard/magic/services.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/magic/services.py)

Crafting:

- [astergard/crafting/services.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/crafting/services.py)

These are intentionally lightweight compared with the world simulation.

Economy is transactional:

- buy,
- sell,
- pricing rules,
- merchant stock,
- gold transfer.

Magic is status-driven and effect-driven, with a small number of spell behaviors.

Crafting exists as a service layer, not as a deeply systemic economy simulation.

That is consistent with the rest of the project: the game is primarily a world simulation and interaction system, not a complex economic sandbox.

## 12. Persistence and Save/Load

Persistence is anchored by:

- [astergard/database/repository.py](/home/lukas/Dokumenty/astergard_d34_world_area/astergard/database/repository.py)
- [astergard/engine/save_load.py](/home/lukas/Dokumenty/astergard_d34_world_area/astergard/engine/save_load.py)

The repository layer stores player and world state, while the save/load engine bridges runtime services and persistence.

Important characteristics:

- world state can be rehydrated,
- NPC population can be loaded or regenerated,
- the system tracks visited rooms and runtime world changes,
- the architecture is stateful but not fragile because the composition root centralizes loading.

## 13. Event Bus, Scheduler, and Heartbeat

The runtime loop is built around:

- [astergard/engine/events.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/engine/events.py)
- [astergard/engine/scheduler.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/engine/scheduler.py)
- [astergard/engine/lifecycle.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/engine/lifecycle.py)
- [astergard/server/game.py](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/server/game.py)

The heartbeat tick drives:

- time/weather changes,
- NPC AI,
- respawn,
- magic decay or timing,
- scheduled work,
- observability updates.

This is the “world continues without the player” mechanism. It is a core MUD property and Astergard has a real implementation of it.

## 14. Observability and Admin

Relevant files:

- [astergard/observability/*](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/observability/)
- [astergard/admin/*](/home/lukasz/Dokumenty/astergard_d34_world_area/astergard/admin/)

What this layer gives:

- command metrics,
- tick metrics,
- scheduler visibility,
- admin auditing,
- admin permissions,
- world tools.

This is useful in a live MUD because content and runtime state are both hard to inspect without tooling.

## 15. Test and Audit Coverage

The repository includes broad test coverage across:

- parsing,
- world rendering,
- minimap payloads,
- combat,
- NPC behavior,
- living world behavior,
- content framework,
- persistence.

Important audit and report assets:

- [scripts/audit_world_narration.py](/home/lukasz/Dokumenty/astergard_d34_world_area/scripts/audit_world_narration.py)
- [WORLD_NARRATION_REPORT_D52.md](/home/lukasz/Dokumenty/astergard_d34_world_area/WORLD_NARRATION_REPORT_D52.md)
- [WORLD_SPOJRZ_ALL_D54.md](/home/lukasz/Dokumenty/astergard_d34_world_area/WORLD_SPOJRZ_ALL_D54.md)
- [WORLD_SPOJRZ_5_PER_REGION_D54.md](/home/lukasz/Dokumenty/astergard_d34_world_area/WORLD_SPOJRZ_5_PER_REGION_D54.md)

The audit tooling is especially valuable because it checks the exact failure modes that matter in a text MUD:

- repetition,
- raw identifiers,
- poor grammar,
- weak scene composition,
- missing metadata.

## 16. Strengths

1. One clear composition root.
2. Unified runtime context across world, NPCs, combat, quests, economy, and observation.
3. A real scene renderer instead of raw field dumping.
4. Polish-aware command parsing.
5. NPC daily routines and local movement.
6. Event-driven side effects for combat and quests.
7. Persistence that supports a living world, not only player save files.
8. Separate observability and admin layers.

## 17. Risks and Technical Debt

1. Content density is high, so repeated phrasing can still leak through if a region generator is too generic.
2. NPC scene lines can become too long when short description, routine fragment, and activity all stack together.
3. Weather is descriptive-first, not mechanically deep. That is fine, but it means weather mostly affects immersion rather than gameplay.
4. The world is very large, so local handcrafted quality varies by region.
5. Some systems are still “wide” rather than deeply normalized, which is practical for a MUD but means content quality depends on author discipline.
6. The narrative layer is doing a lot of work to hide structural repetition in content data.

## 18. Recommended Next Passes

If the goal is to keep improving the system without adding mechanics, the highest-value next steps are:

1. Tighten NPC scene-line composition so routine fragments never read like duplicated actions.
2. Audit region generators for repeated openers and fallback clauses.
3. Expand location-specific sound and smell vocabularies for the remaining weakest regions.
4. Continue using report-driven review on full `spojrz` outputs rather than only checking isolated rooms.
5. Keep mechanical systems stable and focus future work on content quality and simulation texture.

## 19. Bottom Line

Astergard already has the structure of a real MUD:

- an explicit world graph,
- living NPCs,
- clock/weather simulation,
- event-driven combat and questing,
- a Polish command parser,
- narrative scene rendering,
- persistence and observability.

What distinguishes the current state is not missing mechanics, but the quality of content layering. The engine is already capable of supporting a convincing world; most remaining work is content discipline, phrasing quality, and reducing residual templating.
