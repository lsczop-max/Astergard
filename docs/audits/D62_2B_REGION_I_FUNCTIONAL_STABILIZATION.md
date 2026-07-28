# D62.2B Region I Functional Stabilization

## Context

- Canonical Region I topology lives in `astergard/world/data/region_i.json`.
- Pilot descriptions live in `astergard/world/data/region_i_pilot_content.json`.
- This pass stabilizes functional fallout after atomic activation of the new Region I.
- The working tree is intentionally left dirty and uncommitted.
- `client/mudlet/releases/Astergard.mpackage` and `client/mudlet/maps/astergard_map.json` were not touched.

## Verification Summary

- Full `pytest`: `531 passed, 50 failed`
- Environment failures: `24`
  - all from `tests/test_d59_websocket_gateway.py`
  - all caused by sandbox socket creation denial
- Non-socket failures: `26`

## Fixed From D62.2A

- Baseline D62.2A non-socket regressions: `64`
- Remaining non-socket failures now: `26`
- Fixed regressions: `38`

## What Was Regained

- Canonical Region I topology is active in runtime.
- Pilot descriptions are attached for the 15 authored rooms.
- Room metadata now follows the canonical Region I asset.
- GMCP room serialization and minimap payloads still work on the active runtime path.
- Guard / theft / quest reputation handling was stabilized for the new canonical zone ids.
- Region-aware narrative and exploration logic now recognizes:
  - `centrum`
  - `trakt`
  - `trakt-gorniczy`
  - `trakt-nadrzeczny`
  - `polnocny-las`
  - `nadrzeczne-mokradla`

## Remaining Non-Socket Failures

### Pure stale geometry or old-ID assertions

- `tests/test_core.py::AstergardCoreTests::test_world_has_500_symmetric_locations`
  - Decision: update to the new active runtime size.

- `tests/test_d3_application_services.py::D3ApplicationServiceTests::test_bootstrapper_builds_complete_service_graph`
  - Decision: update to the canonical runtime size.

- `tests/test_d34_world_area_expansion.py::D34WorldAreaExpansionTests::test_authored_rooms_keep_world_graph_size_and_have_inspectables`
  - Decision: rewrite around canonical pilot rooms instead of legacy size assumptions.

- `tests/test_d34_world_area_expansion.py::D34WorldAreaExpansionTests::test_key_city_landmarks_have_descriptions_and_links`
  - Decision: update names and inspectables to the canonical cards.

- `tests/test_d34_world_area_expansion.py::D34WorldAreaExpansionTests::test_player_can_travel_into_expanded_area_and_inspect_generic_detail`
  - Decision: rewrite the inspectable path to a canonical room / canonical inspectable.

- `tests/test_d35_1a_astergard_world_rewrite.py::D351AAstergardWorldRewriteTests::test_astergard_graph_is_organic_not_full_grid`
  - Decision: update to the canonical city room set.

- `tests/test_d35_1b_outer_region_world_rewrite.py::D351BOuterRegionWorldRewriteTests::test_d351b_graph_is_connected_and_not_full_grid`
  - Decision: rewrite to the canonical `trakt-gorniczy` / `trakt-nadrzeczny` / `centrum` topology.

- `tests/test_d35_1b_outer_region_world_rewrite.py::D351BOuterRegionWorldRewriteTests::test_d351b_replaces_placeholder_text`
  - Decision: replace old zone labels with canonical region ids.

- `tests/test_d35_1c_silent_forest_world_rewrite.py::D351CSilentForestWorldRewriteTests::test_d351c_forest_graph_is_connected_organic_and_has_transitions`
  - Decision: remove stale links to `210` and assert canonical entrances instead.

- `tests/test_d35_1e_mountains_pass_world_rewrite.py::D351EMountainsPassWorldRewriteTests::test_d351e_graph_is_sparse_connected_and_has_expected_chokepoints`
  - Decision: rewrite around the new canonical edges and canonical expowisko entrances.

- `tests/test_d35_1e_mountains_pass_world_rewrite.py::D351EMountainsPassWorldRewriteTests::test_d351e_replaces_pass_and_mountain_placeholder_text`
  - Decision: replace legacy zone names with canonical region ids.

- `tests/test_d35_1l_forteca_dungrim_production.py::D351LFortecaDungrimProductionTests::test_dungrim_patrols_use_existing_schedule_and_patrol_state`
  - Decision: update zone expectations to canonical `polnocny-las`.

- `tests/test_d35_1l_forteca_dungrim_production.py::D351LFortecaDungrimProductionTests::test_dungrim_region_has_symmetric_exits_and_working_schedule`
  - Decision: update zone expectations to canonical `polnocny-las`.

- `tests/test_d35_1l_forteca_dungrim_production.py::D351LFortecaDungrimProductionTests::test_populate_places_dungrim_npcs_with_schedules_dialogues_and_equipment`
  - Decision: update zone expectations to canonical `polnocny-las`.

- `tests/test_d35_1r_world_audit.py::D351RWorldAuditTests::test_world_graph_content_and_population_are_consistent`
  - Decision: update to the canonical room count and active zone ids.

- `tests/test_d56_location_narrative_generator.py::D56LocationNarrativeGeneratorTests::test_compare_and_export_round_trip`
  - Decision: stop sampling removed room `2`.

- `tests/test_d56_location_narrative_generator.py::D56LocationNarrativeGeneratorTests::test_identity_axes_are_reported_separately`
  - Decision: update to the canonical active room set.

- `tests/test_d56_location_narrative_generator.py::D56LocationNarrativeGeneratorTests::test_pilot_review_samples_thirty_rooms`
  - Decision: update the sample set so it does not include removed ids.

- `tests/test_d57_regional_knowledge_banks.py::D57RegionalKnowledgeBankTests::test_sensory_selection_stays_region_tied`
  - Decision: update the test to canonical banks, not legacy `Puszcza_Ciszy` / `Bagna_Hookri`.

- `tests/test_d57_regional_knowledge_banks.py::D57RegionalKnowledgeBankTests::test_style_guide_and_text_audit_are_buildable`
  - Decision: update to canonical active room ids.

- `tests/test_d57_regional_knowledge_banks.py::D57RegionalKnowledgeBankTests::test_surface_selection_is_deterministic_and_region_specific`
  - Decision: update to canonical region ids and region-aware bank lookup.

- `tests/test_d58_world_description_audit.py::D58WorldDescriptionAuditTests::test_audit_covers_exactly_500_locations_without_missing_or_duplicate_ids`
  - Decision: update the audit to the 483-room runtime.

- `tests/test_d36_identity.py::D36IdentityTests::test_quest_completion_updates_reputation_renown_and_title`
  - Decision: update the local reputation assertion to the canonical zone key `centrum`.

- `tests/test_d43_puszcza_ciszy_hunting_expowisko.py::PuszczaCiszyHuntingExpowiskoTests::test_beginner_road_rooms_spawn_new_animals`
  - Decision: update the zone assertion to `nadrzeczne-mokradla`.

### Functional contracts that still need a migration decision

- `tests/test_d35_1h_npc_dialogues.py::D351HNPCDialogueTests::test_requested_npcs_have_social_topics_registered`
  - Missing contract: the generic `blacksmith` NPC is still spawned only from removed room `12`.
  - Old dependency: room `12` from the retired legacy city layout.
  - Candidate new homes from cards:
    - `36` `Sklep pod Ostrzem`
    - `39` `Płatnernia pod Kowadłem`
  - Decision: `HUMAN_DECISION`
  - Reason: the cards do not make the migration unambiguous enough to guess.

- `tests/test_d35_1j_world_reactions.py::D351JWorldReactionTests::test_bad_reputation_triggers_guard_aggression`
  - Observed failure: the test runs the guard tick at a time when the guard patrol can already move away.
  - Old dependency: a fixed daytime guard position in the legacy city shape.
  - Canonical zone: `centrum`
  - Decision: update the test setup, not the guard aggression contract.

## Migration Table

| Stara funkcja | Stara lokacja | Nowa funkcja | Nowa lokacja | Zależne systemy | Wymagane testy |
|---|---|---|---|---|---|
| Generic city blacksmith | `12` | metal / armor service | `HUMAN_DECISION` | NPC spawning, dialogue, shops, quests | `tests/test_d35_1h_npc_dialogues.py` |
| City guard / reputation checks | `25` | city guard / reputation checks | `centrum` | faction reactions, identity, dialog | `tests/test_d35_1j_world_reactions.py`, `tests/test_d36_identity.py` |
| Legacy `Podgrodzie` belt | `60-79` | canonical `trakt-gorniczy` + `trakt-nadrzeczny` + `centrum` border rooms | `58-86` | NPC spawns, patrols, exploration | `tests/test_d35_1b_outer_region_world_rewrite.py`, `tests/test_d43_puszcza_ciszy_hunting_expowisko.py` |
| Legacy forest gate to `210` | `109 -> 210` | no automatic outside-region link | `HUMAN_DECISION` | exploration, world topology, audit | `tests/test_d35_1c_silent_forest_world_rewrite.py` |
| Legacy pass link to `335` | `125 -> 335` / `129 -> 335` / `334 -> 335` | no automatic outside-region link | `HUMAN_DECISION` | topology, audit | `tests/test_d35_1e_mountains_pass_world_rewrite.py` |
| Legacy 500-room audit | whole world | 483-room runtime | canonical Region I + remaining runtime | bootstrap, audit, narrative, persistence | `tests/test_core.py`, `tests/test_d3_application_services.py`, `tests/test_d58_world_description_audit.py` |

## Player-Facing Recovery Assessment

- Restored:
  - canonical Region I map layout
  - 15 pilot descriptions
  - GMCP room info on canonical rooms
  - minimap payload generation on the active topology
  - basic guard, theft and quest reputation handling after the Region I switch
  - region-aware exploration and narrative selection for the new canonical zone ids
- Still pending:
  - one or more migrated service NPC homes, specifically the generic blacksmith
  - test rewrites that still assume the old 500-room geography
  - websocket integration tests blocked by the sandbox environment

## Conclusion

- Fixed regressions from the D62.2A baseline: `38`
- Remaining real regressions: `26` non-socket failures, all currently tied to stale geometry, old zone labels, or one unresolved NPC migration decision
- Human decisions required: see `HUMAN_DECISION` entries above
- Verdict: `D62_2B_BLOCKED`
