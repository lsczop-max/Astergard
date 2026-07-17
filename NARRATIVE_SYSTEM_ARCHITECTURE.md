# Narrative System Architecture

This repo now has a dedicated location-description pipeline under
`astergard/location_narrative/`.

Pipeline:

1. `world_adapter.py` extracts permanent location facts and dynamic state.
2. `planner.py` builds a semantic `DescriptionPlan`.
3. `realizer.py` turns the plan into prose and examinable details.
4. `validator.py` checks factual and structural constraints.
5. `critic.py` aggregates the validation outcome into scored feedback.
6. `reviser.py` applies targeted fixes for rejected drafts.
7. `similarity.py` compares descriptions deterministically.
8. `generator.py` orchestrates the full draft -> critique -> revise loop.

The existing scene renderer in `astergard/narrative.py` remains intact for
runtime room rendering. The new CLI entrypoints live in the same module for
compatibility with `python -m astergard.narrative ...`.

The generator is intentionally deterministic and does not depend on external
LLM services.
