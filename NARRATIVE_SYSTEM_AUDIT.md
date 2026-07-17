# Initial Narrative Audit

Baseline state before the new pipeline:

* `WorldManager.generate_world()` creates a 500-room graph.
* Room content is overlaid by `astergard/world/content.py`.
* Scene rendering for `look`/`sense` is handled by `astergard/narrative.py`.
* Mutable world state is persisted by `astergard/database/world_state_repository.py`.
* Weather/time events come from `astergard/weather/time_weather.py`.
* Observations and search are exposed through `astergard/application/services/*`.

Observed problems in the authored content:

* many descriptions were functional but template-heavy;
* several endings repeated the same closure patterns across dozens of rooms;
* inspectable keys were often semantic aliases rather than user-facing labels;
* some sensory anchors repeated too often;
* current data has no typed semantic model for generation, planning or critique.

Baseline checks before changes:

* `pytest`: 301 passed
* `ruff check`: unavailable in the local environment
* `mypy astergard tests`: success

This audit is intentionally conservative. The existing world data is usable, but
it is not yet backed by a dedicated generation and critique pipeline.
