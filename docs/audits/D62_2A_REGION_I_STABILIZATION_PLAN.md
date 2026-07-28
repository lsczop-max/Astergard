# D62.2A Region I Stabilization Plan

## Run Summary

- Full `pytest` finished with `88 failed, 495 passed` in `119.33s`.
- Environment failures: `24`, all in `tests/test_d59_websocket_gateway.py` and all caused by sandbox socket creation denial.
- Non-socket failures: `64`.
- Classification of the 64 non-socket failures:
  - pure stale geometry assertions: `11`
  - live service / protocol / persistence regressions: `12`
  - lost functional contracts that need migration or replacement: `41`

## Current Working Tree

- Keep the current uncommitted tree intact.
- Do not touch `client/mudlet/releases/Astergard.mpackage`.
- Do not touch `client/mudlet/maps/astergard_map.json`.

## `apply_content_pack()` Audit

`apply_content_pack()` now skips every `LocationContent` whose `room_id` belongs to the canonical Region I asset.

- Exact scope of skipped content: all 170 Region I rooms from `astergard/world/data/region_i.json`
  - `0, 1, 14, 20-186`
  - excluding `2-13` and `15-19`
- What is no longer overlaid:
  - canonical names
  - descriptions
  - inspectables
  - forms and exit_forms
  - exit kinds
  - scene profiles
  - items and hidden items
- Assessment:
  - good as a safety stopgap to prevent stale overlays from corrupting the new topology
  - too broad to remain final, because it erases all authored Region I content
- Preferred target mechanism:
  - one canonical Region I content pack, selected from the same canonical asset family as the topology
  - no room-by-room exceptions scattered across the codebase
  - content should be attached by source region / room id once, then merged into runtime in one place

## Failure Catalog

### Pure Geometry Assertions

- `tests/test_core.py::AstergardCoreTests::test_world_has_500_symmetric_locations`
  - Old dependency: global 500-room world contract.
  - New target: runtime now has 483 rooms after Region I replacement.
  - Decision: update or delete the old 500-room assertion.

- `tests/test_d34_world_area_expansion.py::D34WorldAreaExpansionTests::test_authored_rooms_keep_world_graph_size_and_have_inspectables`
  - Old dependency: world size 500 and old `Tyły Karczmy` overlay on room 15.
  - New target: room 15 is removed; Region I rooms now follow the canonical cards.
  - Decision: rewrite test around canonical Region I rooms, not the legacy 500-room count.

- `tests/test_d34_world_area_expansion.py::D34WorldAreaExpansionTests::test_key_city_landmarks_have_descriptions_and_links`
  - Old dependency: city landmark names at `21, 22, 23, 25, 35, 41, 48, 59`.
  - New target:
    - `21` `Dziedziniec Suchych Studni`
    - `22` `Strażnica Bramy`
    - `23` `Ulica Wartownicza`
    - `25` `Niski Ratusz`
    - `35` `Skład Podróżny`
    - `41` `Magazyn Rudy`
    - `48` `Nabrzeże Żurawi`
    - `59` `Kapliczka Przydrożna`
  - Decision: rewrite assertions to the canonical card names and links.

- `tests/test_d34_world_area_expansion.py::D34WorldAreaExpansionTests::test_player_can_travel_into_expanded_area_and_inspect_generic_detail`
  - Old dependency: movement from room `3` into the old city expansion.
  - New target: the canonical `centrum` rooms are now named and routed differently.
  - Decision: update the travel path to a canonical exit; do not keep the old movement expectation.

- `tests/test_d35_1a_astergard_world_rewrite.py::D351AAstergardWorldRewriteTests::test_astergard_graph_is_organic_not_full_grid`
  - Old dependency: legacy city indexing across `0..59`.
  - New target: canonical `centrum` rooms `0,1,14,21-57,77-81`.
  - Decision: rewrite geometry expectations for the canonical city graph.

- `tests/test_d35_1b_outer_region_world_rewrite.py::D351BOuterRegionWorldRewriteTests::test_d351b_graph_is_connected_and_not_full_grid`
  - Old dependency: old boundary links from `56 -> 60` and older Podgrodzie geometry.
  - New target:
    - `56` is now `Opuszczona Chata`
    - `60` is `Błotna Brama`
    - `58-76` live in `trakt-gorniczy`
  - Decision: rewrite to the canonical tract topology.

- `tests/test_d35_1b_outer_region_world_rewrite.py::D351BOuterRegionWorldRewriteTests::test_d351b_replaces_placeholder_text`
  - Old dependency: old `Podgrodzie` zone strings.
  - New target: rooms `60-79` are split between `trakt-gorniczy`, `trakt-nadrzeczny`, and `centrum`.
  - Decision: rewrite zone assertions, not the topology.

- `tests/test_d35_1c_silent_forest_world_rewrite.py::D351CSilentForestWorldRewriteTests::test_d351c_forest_graph_is_connected_organic_and_has_transitions`
  - Old dependency: `109 -> 210` transition to the old forest world.
  - New target: room `109` is `Ostatni Znak Toporem` in `polnocny-las`; there is no canonical Region I connection to `210` yet.
  - Decision: update the test or defer the outside-region link as `HUMAN_DECISION`.

- `tests/test_d35_1e_mountains_pass_world_rewrite.py::D351EMountainsPassWorldRewriteTests::test_d351e_graph_is_sparse_connected_and_has_expected_chokepoints`
  - Old dependency: `0 -> 125` and pass-to-mountain adjacency inherited from the old world.
  - New target: `0` is still `Brama Dymnych Chorągwi`, but the canonical JSON does not restore the old boundary link.
  - Decision: rewrite for canonical Region I only.

- `tests/test_d35_1e_mountains_pass_world_rewrite.py::D351EMountainsPassWorldRewriteTests::test_d351e_replaces_pass_and_mountain_placeholder_text`
  - Old dependency: `Straznica_Przeleczy` / `Gory_Mekhara` zone identities.
  - New target: `125-134` are now canonical `polnocny-las` cards with pass/fort names.
  - Decision: update the test to the new region identity or mark the old region split as `HUMAN_DECISION`.

- `tests/test_d58_world_description_audit.py::D58WorldDescriptionAuditTests::test_audit_covers_exactly_500_locations_without_missing_or_duplicate_ids`
  - Old dependency: 500-room audit.
  - New target: canonical runtime currently has 483 rooms after removing the deprecated IDs.
  - Decision: update the audit to the new authoritative room set.

### Live Service / Protocol / Persistence Regressions

- `tests/test_d13_npc_ai_respawn.py::D13NPCAITests::test_patrol_moves_only_inside_same_zone_and_emits_event`
  - Old dependency: `meekhan_soldier` patrols from room `0` inside the old `Centrum_Twierdza`.
  - New target: room `0` is now `Brama Dymnych Chorągwi` in `centrum`.
  - Decision: keep the NPC AI contract, but re-anchor the patrol test to the canonical city topology.

- `tests/test_d26_admin_gm_engine.py::D26AdminGMEngineTests::test_gm_can_inspect_and_teleport_player`
  - Old dependency: teleport target `5`.
  - New target: room `5` no longer exists in the canonical Region I.
  - Decision: update the test to a surviving canonical room such as `21` or `29`; do not keep the removed room.

- `tests/test_d3_application_services.py::D3ApplicationServiceTests::test_bootstrapper_builds_complete_service_graph`
  - Old dependency: bootstrap contract still assumed the old world shape.
  - New target: bootstrap now builds the active Region I runtime from the canonical asset.
  - Decision: verify the service graph against the new runtime topology, not the old 500-room topology.

- `tests/test_d36_identity.py::D36IdentityTests::test_crime_is_recorded_and_survives_save_load`
  - Old dependency: save/load path on the legacy world state.
  - New target: persistence now sees canonical Region I room ids and removed legacy ids.
  - Decision: preserve the persistence contract, but retest with canonical rooms.

- `tests/test_d36_identity.py::D36IdentityTests::test_quest_completion_updates_reputation_renown_and_title`
  - Old dependency: quest completion against legacy content anchors.
  - New target: canonical Region I content locations must supply the quest flow.
  - Decision: migrate the quest anchors; do not weaken the persistence or reputation contract.

- `tests/test_d40_minimap_payload.py::MinimapPayloadTests::test_map_payload_is_enabled_via_env`
  - Old dependency: movement from room `60` via `poludnie`.
  - New target: room `60` is `Pola Pogranicza` with exits `ne`/`se` in the new topology.
  - Decision: update the test path to a canonical exit; the payload contract itself is still valid.

- `tests/test_d40_minimap_payload.py::MinimapPayloadTests::test_map_payload_is_off_by_default`
  - Old dependency: same stale movement path from room `60`.
  - New target: same canonical room `60` and canonical exits.
  - Decision: update the movement step, keep the off-by-default map contract.

- `tests/test_d40_minimap_payload.py::MinimapPayloadTests::test_map_payload_omits_hidden_exits_in_full_and_incremental_updates`
  - Old dependency: movement from room `0` via `poludnie` and a legacy traversal path.
  - New target: `0` now has canonical exits `n` and `e`.
  - Decision: rewrite the movement step and keep the hidden-exit contract.

- `tests/test_d55_mudlet_client.py::MudletClientTests::test_room_info_is_sent_after_movement`
  - Old dependency: movement/room-info sequence on the old path.
  - New target: canonical GMCP room info must still serialize from active rooms.
  - Decision: retest with a valid canonical move.

- `tests/test_d55_mudlet_client.py::MudletClientTests::test_session_loop_sends_room_info_on_room_change`
  - Old dependency: same stale movement contract.
  - New target: canonical room changes must still emit `Room.Info`.
  - Decision: rewrite the move path, do not drop the protocol contract.

- `tests/test_d59_session_resilience.py::D59SessionResilienceTests::test_movement_room_info_drain_precedes_text_and_cleanup_on_reset`
  - Old dependency: movement ordering on the old room graph.
  - New target: canonical movement must still preserve room-info drain ordering.
  - Decision: retest on a valid canonical move.

- `tests/test_d59_web_protocol_v1.py::WebProtocolV1Tests::test_movement_emits_room_info_before_command_text`
  - Old dependency: same stale movement path and old room sequencing.
  - New target: canonical movement must still emit room info before command text.
  - Decision: rewrite the move path; keep the protocol ordering contract.

### Lost Functional Contracts

- `tests/test_d33_world_content_framework.py`
  - Failing tests:
    - `test_content_pack_overlays_named_rooms_without_changing_world_size`
    - `test_look_shows_room_story_without_menu_like_hints`
    - `test_player_can_inspect_authored_detail_with_polish_alias`
    - `test_sense_commands_expose_senses_and_respect_context`
  - Old dependency: content overlays on `0`, `1`, `21`, and the starter city.
  - New target:
    - `0` `Brama Dymnych Chorągwi`
    - `1` `Plac Przed Wartownią`
    - `14` `Karczma pod Żurawiem`
    - `20` `Trakt Przy Murze`
    - `21` `Dziedziniec Suchych Studni`
  - Decision: restore Region I content packing, then rewrite the assertions to canonical card text.

- `tests/test_d34_world_area_expansion.py`
  - Failing tests:
    - `test_authored_rooms_keep_world_graph_size_and_have_inspectables`
    - `test_key_city_landmarks_have_descriptions_and_links`
    - `test_player_can_travel_into_expanded_area_and_inspect_generic_detail`
  - Old dependency: legacy 500-room authored city belt.
  - New target: canonical rooms from the cards, especially `21, 22, 23, 25, 35, 41, 48, 59`.
  - Decision: rewrite to the canonical topology and keep the content contract.

- `tests/test_d35_1b_podgrodzie_life.py`
  - Failing tests:
    - `test_npc_moves_within_zone_using_existing_exit`
    - `test_npc_returns_home_and_stays_in_zone`
    - `test_podgrodzie_is_not_empty`
    - `test_populate_still_builds_living_scheduler_cast`
    - `test_scheduler_does_not_leave_map`
    - `test_spawn_places_new_npcs_in_expected_rooms`
  - Old dependency: `Podgrodzie` rooms `60-79`.
  - New target:
    - `60` `Błotna Brama`
    - `62` `Zajazd Pod Mokrym Kołem`
    - `63` `Plac Bydlęcy`
    - `66` `Podmurze Przy Palisadzie`
    - `69` `Studnia Przedmieścia`
    - `72` `Zagroda Gęsi`
    - `75` `Błotny Rozjazd`
    - `76` `Stary Kamień Mytny`
    - `77` `Droga do Pól`
    - `78` `Niska Łąka`
  - Decision: migrate NPC spawns and daily routines; the old `Podgrodzie` zone label is no longer authoritative.

- `tests/test_d35_1g_local_quests.py::D351GLocalQuestTests::test_delivery_quest_starts_completes_and_rewards`
  - Old dependency: delivery quest anchored to the old `Podgrodzie` content.
  - New target: canonical `centrum` / `trakt` route, especially `47` `Rynek Żelazny` and `14` `Karczma pod Żurawiem`.
  - Decision: keep the quest, move it onto canonical rooms, and revalidate reward/reputation flow.

- `tests/test_d35_1h_npc_dialogues.py::D351HNPCDialogueTests::test_requested_npcs_have_social_topics_registered`
  - Old dependency: dialogue topics for `innkeeper`, `podgrodzie_karczmarka`, `blacksmith`, `podgrodzie_pomocnik_kowala`, `podgrodzie_rybak`, `podgrodzie_straznik_miejski`, `podgrodzie_handlarz`, `podgrodzie_przekupka`, `podgrodzie_zebrak`, `podgrodzie_pielgrzym`.
  - New target:
    - `14` `Karczma pod Żurawiem`
    - `62` `Zajazd Pod Mokrym Kołem`
    - `12` `Kuźnia przy Murze`
    - `66` `Podmurze Przy Palisadzie`
    - `69` `Studnia Przedmieścia`
    - `63` `Plac Bydlęcy`
    - `76` `Stary Kamień Mytny`
  - Decision: repoint dialogue topics to canonical rooms and keep the social-topic contract.

- `tests/test_d35_1j_world_reactions.py`
  - Failing tests:
    - `test_helping_podgrodzie_raises_reputation`
    - `test_bad_weather_slows_patrol_npcs`
    - `test_completed_quest_unlocks_better_offer`
  - Old dependency: `Podgrodzie` reputation and patrol loops.
  - New target:
    - quest route through `47` and `14`
    - patrol NPCs in `112` `Dziedziniec Garnizonu`
  - Decision: preserve the reaction system, but migrate the triggering rooms and reputation hooks.

- `tests/test_d35_1k_haldun_production.py`
  - Failing tests:
    - `test_haldun_daily_routines_keep_npcs_in_region`
    - `test_haldun_dialogues_quests_and_shops_work_through_real_commands`
    - `test_haldun_region_has_specific_descriptions_items_and_symmetric_exits`
  - Old dependency: the named `Haldun` region.
  - New target:
    - `80` `Droga do Haldun`
    - `81` `Krzyżowy Kamień`
    - `82` `Pierwsze Zagony`
    - `83` `Studnia Haldun`
    - `84` `Zagony pod Wierzbami`
    - `85` `Chata Sołtysa`
    - `86` `Obora pod Wierzbami`
    - `87` `Stodoły Zachodnie`
    - `88` `Młynny Rów`
    - `89` `Mostek nad Strugą`
    - `90` `Pola Jęczmienne`
    - `91` `Sad Kwaśnych Jabłek`
    - `92` `Pastwisko Koni`
    - `93` `Kapliczka Żniwiarzy`
    - `94` `Droga ku Fortecy`
  - Decision: migrate content and NPCs; exact zone identity is `HUMAN_DECISION` because the cards split the old Haldun belt across multiple canonical regions.

- `tests/test_d35_1l_forteca_dungrim_production.py`
  - Failing tests:
    - `test_dungrim_dialogues_and_quests_work_through_real_commands`
    - `test_dungrim_patrols_use_existing_schedule_and_patrol_state`
    - `test_dungrim_region_has_symmetric_exits_and_working_schedule`
    - `test_populate_places_dungrim_npcs_with_schedules_dialogues_and_equipment`
  - Old dependency: `Forteca_Dungrim`.
  - New target:
    - `110` `Brama Dungrim`
    - `111` `Przedbramie Wilczych Haków`
    - `112` `Dziedziniec Garnizonu`
    - `113` `Studnia Forteczna`
    - `114` `Stajnie Patroli`
    - `115` `Kuchnia Garnizonowa`
    - `116` `Koszary Zachodnie`
    - `117` `Kuźnia Wojskowa`
    - `118` `Izba Oficerska`
    - `119` `Mur Nad Traktem`
    - `120` `Sala Dowódcy`
    - `121` `Zbrojownia Dungrim`
    - `122` `Magazyn Główny`
    - `123` `Skład Racji`
    - `124` `Wyjazd na Zachodni Trakt`
  - Decision: migrate the fortress content package onto the canonical `polnocny-las` belt.

- `tests/test_d35_1m_straznica_przeleczy_production.py`
  - Failing tests:
    - `test_dialogues_quests_and_shops_work_through_real_commands`
    - `test_patrols_move_existing_patrol_npc_inside_pass_zone`
    - `test_populate_places_pass_npcs_with_equipment_dialogues_and_schedules`
    - `test_schedule_and_region_consistency_stay_symmetric`
  - Old dependency: `Straznica_Przeleczy`.
  - New target:
    - `125` `Brama Strażnicy Przełęczy`
    - `126` `Dziedziniec Meldunkowy`
    - `127` `Wieża Zwiadowców`
    - `128` `Izba Przewodnika`
    - `129` `Plac Karawan`
    - `130` `Stajnie Wozów`
    - `131` `Izba Podróżnych`
    - `132` `Kaplica Przełęczy`
    - `133` `Ambona Myśliwego`
    - `134` `Brama do Dungrim`
  - Decision: migrate pass content and NPC schedules to the canonical pass belt.

- `tests/test_d35_1n_trakty_production.py`
  - Failing tests:
    - `test_dialogues_quests_and_deliveries_work_through_real_commands`
    - `test_patrols_and_schedules_keep_guard_on_route`
    - `test_populate_spawns_road_npcs_with_equipment_dialogues_and_schedules`
    - `test_region_content_and_symmetry_stay_coherent`
  - Old dependency: `Trakty`.
  - New target:
    - `135` `Kapliczka Podróżnych za Murem`
    - `136` `Pierwszy Kamień Milowy`
    - `137` `Mokra Koleina`
    - `138` `Rozstaje Trzech Wozów`
    - `139` `Stary Słup Mytny`
    - `140` `Droga przy Łanach`
    - `141` `Mostek Kupiecki`
    - `142` `Karczemne Popasowisko`
    - `143` `Zakręt pod Topolami`
    - `144` `Miejsce po Starym Ognisku`
    - `145` `Trakt Haldunski`
    - `146` `Kopiec Graniczny`
    - `147` `Bród na Zimnej Strudze`
    - `148` `Kładka Przewoźników`
    - `149` `Wójtowski Kamień`
    - `150` `Skręt ku Dungrim`
    - `151` `Wysoka Grobla`
    - `152` `Szlak Solnych Wozów`
    - `153` `Czarna Koleina`
    - `154` `Zawiany Przepust`
    - `155` `Długi Prostak`
    - `156` `Rozdroże Straży`
  - Decision: migrate route NPCs and delivery/escort loops; zone label `Trakty` is no longer the authoritative region identity.

- `tests/test_d35_1q_local_quests_expansion.py::D351QLocalQuestExpansionTests::test_new_quests_start_progress_and_complete_through_real_commands`
  - Old dependency: quest progression on rooms `0, 1, 25, 60, 63, 66, 76`.
  - New target:
    - `25` `Niski Ratusz`
    - `1` `Plac Przed Wartownią`
    - `0` `Brama Dymnych Chorągwi`
    - `66` `Podmurze Przy Palisadzie`
    - `60` `Błotna Brama`
    - `63` `Plac Bydlęcy`
    - `76` `Stary Kamień Mytny`
  - Decision: keep the quest framework and migrate objectives to canonical rooms and items.

- `tests/test_d35_1r_world_audit.py::D351RWorldAuditTests::test_world_graph_content_and_population_are_consistent`
  - Old dependency: world-audit coverage across the old 500-room world.
  - New target: canonical Region I rooms plus still-existing detached outer regions.
  - Decision: rewrite the audit to the new active world contract.

- `tests/test_d56_location_narrative_generator.py`
  - Failing tests:
    - `test_generated_text_is_accepted_for_authored_location`
    - `test_compare_and_export_round_trip`
    - `test_pilot_review_samples_thirty_rooms`
    - `test_identity_axes_are_reported_separately`
    - `test_fingerprint_changes_generation_when_enabled`
  - Old dependency: narrative generation against old authored locations and 500-location identity audit.
  - New target:
    - canonical Region I cards and the planned pilot loops
    - especially `0`, `1`, `14`, `20`, `21`, `47`, `62`, `84`, `87-186`
  - Decision: rewrite narrative tests around the canonical card set, not the legacy world description audit.

- `tests/test_d57_regional_knowledge_banks.py::D57RegionalKnowledgeBankTests::test_style_guide_and_text_audit_are_buildable`
  - Old dependency: `Centrum_Twierdza` style bank.
  - New target: canonical `centrum` card bank.
  - Decision: update the region-style lookup and keep the text-audit contract.

- `tests/test_d58_2_centrum_pilot.py`
  - Failing tests:
    - `test_pilot_renders_do_not_reintroduce_old_templates_or_raw_aliases`
    - `test_pilot_renders_match_the_saved_audit`
    - `test_pilot_rooms_keep_their_landmarks_and_inspectables`
  - Old dependency: the old pilot content saved in the D58 audit.
  - New target: canonical pilot rooms from the cards and plan, especially `0, 1, 14, 20, 21, 22, 23, 24, 25, 47, 59`.
  - Decision: update the pilot fixture or mark the exact room-to-pilot mapping as `HUMAN_DECISION` where the cards do not state it unambiguously.

### Human Decisions Required

- Whether the old named regions `Haldun`, `Forteca_Dungrim`, `Straznica_Przeleczy`, and `Trakty` should remain as semantic labels or be fully replaced by the new canonical `regionId` set.
- Whether admin teleport tests should keep an arbitrary removed room id like `5` or be rewritten to a canonical surviving room.
- Whether the old outside-region links to `210`, `335`, and related areas should remain deferred until later region rebuilds.
- Whether the pilot content should be attached from the card set now or only after a dedicated pilot-description migration.

## Stabilization Order

1. Restore a Region I content pack so canonical rooms regain names, descriptions, inspectables, items, and hidden items.
2. Rewrite the stale geometry assertions to the canonical room set and the canonical exits.
3. Migrate NPC spawns and daily schedules to the new carded room ids.
4. Migrate quests and shop/economy hooks to the canonical route rooms.
5. Repoint narrative banks and pilot audits to the canonical `regionId` values.
6. Re-run `ruff`, `mypy`, and the full `pytest` suite.

## Notes on the Runtime

- The active runtime now has 483 rooms, not 500.
- The canonical Region I topology is connected and validated, but legacy content and old-region tests still assume the prior map.
- The remaining non-socket failures are not random; they cluster around the exact systems that still reference the old geography.
