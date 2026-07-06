# Prompt Coverage 1-100

Statusy:
- `core implemented` — istnieje działający kod i test sanity, ale nie pełna produkcyjna głębia.
- `production gap` — obszar wymaga dalszego rozwinięcia, lecz ma kod bazowy.

## 1-10: Serwer, ANSI, DB, parser, dispatcher, świat, ruch, look, obecność, komunikacja
Status: core implemented.
Dowody: `server/game.py`, `utils.py`, `database/repository.py`, `commands/parser.py`, `commands/dispatcher.py`, `world/manager.py`.
Testy: `tests/test_core.py`.

## 11-20: Statystyki, skills, heartbeat, inventory, equipment, rany, walka, obrażenia
Status: core implemented.
Dowody: `characters/models.py`, `items/models.py`, `combat/manager.py`, `combat/wounds.py`, `server/game.py`.
Testy: `tests/test_core.py`.

## 21-30: Ucieczka, NPC, AI, spawn/respawn, dialogi, frakcje, questy, ekonomia, sklepy
Status: core implemented.
Dowody: `npcs/models.py`, `npcs/manager.py`, `quests/manager.py`, `factions/reputation.py`, `economy/services.py`, `server/game.py`.
Testy: `tests/test_core.py`.

## 31-40: Pogoda, drzwi/klucze, ukryte elementy, degradacja, prompt, leaderboard, magia, consumables, zwłoki
Status: core implemented; leaderboard jest minimalny.
Dowody: `weather/time_weather.py`, `world/manager.py`, `magic/services.py`, `items/models.py`, `combat/manager.py`, `server/game.py`.
Testy: `tests/test_core.py`.

## 41-60: Rozszerzenia systemów i test suite
Status: core implemented where applicable; test suite istnieje jako sanity/regression, nie pełne 90% coverage.
Dowody: `tests/test_core.py`, `README.md`, `MANUAL_TEST_PLAN.md`.

## 61-100: Crafting, gildie, drużyny, bossowie, wojny, administracja, backup/profiling/release
Status: mixed core implemented / production gap.
Dowody: `crafting/services.py`, `admin/tools.py`, struktura pakietów, dokumentacja.
Brak produkcyjny: nie ma kompletnej symulacji wojny frakcji, housing, party/raid i pełnego GM panelu. Obecny build zawiera przygotowany modularny rdzeń oraz narzędzia bazowe, bez pustych plików-fasad.

## D2 update — dowód modularizacji

D2 nie dodaje nowych systemów fabularnych. Poprawia spełnienie wymagań architektonicznych promptów 5, 7–10, 14–16, 18–21, 25, 27–30, 33, 37–40 przez przeniesienie handlerów do modułów domenowych.

Dowody:
- `astergard/commands/registration.py` — jawna rejestracja komend.
- `astergard/commands/exploration.py` — look/ruch/szukaj.
- `astergard/commands/inventory.py` — ekwipunek, get/drop/wear/remove/consume.
- `astergard/commands/combat.py` — atak i ucieczka.
- `astergard/commands/economy.py` — oferta/kup/sprzedaj.
- `tests/test_d2_modularity.py` — testy regresji architektury D2.

## D3 refinement coverage

D3 nie dodaje nowych systemów funkcjonalnych, ale wzmacnia pokrycie architektoniczne promptów 1–13 oraz 60:

- Prompty 1–5: serwer, sesja, dispatcher i rejestracja komend zostały rozdzielone na warstwy.
- Prompty 6–10: świat, ruch, obecność i komunikacja dalej działają po refaktoryzacji.
- Prompty 11–13: heartbeat jest osobnym, testowalnym serwisem aplikacyjnym.
- Prompt 60: dodano testy regresji architektury aplikacyjnej.

Dowody:

- `astergard/application/bootstrap.py`
- `astergard/application/session_flow.py`
- `astergard/application/heartbeat.py`
- `tests/test_d3_application_services.py`

Status: `architecture refined`, nie `feature expansion`.

## D4 refinement coverage

D4 wzmacnia architekturę promptów 14–16, 18–21, 25, 27–30 i 60 przez wydzielenie use-case services z handlerów komend.

Dowody:

- `astergard/application/services/inventory_service.py`
- `astergard/application/services/combat_service.py`
- `astergard/application/services/quest_service.py`
- `astergard/application/services/economy_application_service.py`
- `tests/test_d4_application_use_cases.py`

Status: `application layer refined`. To nadal nie jest pełna produkcyjna implementacja wszystkich systemów, ale usuwa kolejną klasę fasad: logika gry nie siedzi już bezpośrednio w handlerach dla ekwipunku, walki, questów i ekonomii.


## D5 coverage update

- Eksploracja: `application/services/exploration_service.py`, `commands/exploration.py`, `tests/test_d5_service_split.py`.
- Komunikacja: `application/services/communication_service.py`, `commands/communication.py`, `tests/test_d5_service_split.py`.
- Magia/crafting: `application/services/magic_crafting_service.py`, `commands/magic_crafting.py`, `tests/test_d5_service_split.py`.
- Komendy systemowe: `application/services/system_service.py`, `commands/system.py`, `tests/test_d5_service_split.py`.

Status: core implemented. Nadal nie production-grade dla broadcastu komunikacji, rankingu i pełnego systemu magicznego.

## D6 refinement — Context Ports

- Refaktoryzacja architektoniczna wspierająca prompty dotyczące modularności, dispatcherów, serwera, obecności graczy i testowalności.
- Dowód w kodzie:
  - `astergard/server/context.py::GameContext`
  - `astergard/server/game.py::GameServer.make_context`
  - `astergard/commands/helpers.py::find_npc`
  - `tests/test_d6_context_ports.py`
- Status: `core implemented + regression tested`.
- Ograniczenie: `GameContext` nadal niesie kontener `services`; D7 powinien rozbić porty per use case.

## D7 — Use-case contexts
- Dodano wąskie konteksty przypadków użycia.
- Usługi aplikacyjne nie importują już `GameContext`.
- Testy: 29 OK.
- Status: core implemented; pełna separacja komend od kontenera usług wymaga D8.

## D8 — aktualizacja pokrycia architektury

- Warstwa komend nie wywołuje już `ctx._services`.
- `CommandBus` wiąże aliasy gracza z handlerami zbudowanymi przez fabryki modułów komend.
- Dotyczy promptów architektonicznych: dispatcher, modularność komend, separation of concerns, testowalność i integracja warstwy aplikacyjnej.
- Status: `core implemented / architecture hardened`.


## D9 refinement
- Context construction moved from `server/context.py` to `application/context_assembler.py`.
- `GameContext` is now an explicit port carrier, not a service-container adapter.
- Added regression tests in `tests/test_d9_context_assembly.py`.


## D10 coverage update

Persistence-related prompt coverage was strengthened. Database requirements now map to:

- `astergard/database/migrations.py`
- `astergard/database/migrations/001_initial.sql`
- `astergard/database/migrations/002_audit_timestamps.sql`
- `astergard/database/migrations/003_save_slots.sql`
- `astergard/database/repository.py`
- `tests/test_d10_persistence_migrations.py`

Status: core implemented and regression-tested. Not production-grade for live MMO scale because most aggregate state is still stored as JSON columns.

## D11 — Persistence repositories and backup/restore

- `astergard/database/connections.py` — jawne zarządzanie połączeniem SQLite.
- `astergard/database/account_repository.py` — konta, hasła i weryfikacja.
- `astergard/database/character_state_repository.py` — trwały stan postaci.
- `astergard/database/audit_repository.py` — audyt zdarzeń konta i zapisu.
- `astergard/database/backup.py` — backup i restore bazy.
- `astergard/database/migrations/004_audit_events.sql` — historia audytu.
- `tests/test_d11_repositories_backup.py` — testy D11.

Status: core implemented. Nie jest to jeszcze produkcyjny model relacyjny całego świata; persistence świata i NPC przechodzi do D12.

## D12 coverage update
- Prompt 24 / NPC respawn: `astergard/database/world_state_repository.py`, `tests/test_d12_world_persistence.py` — kolejka respawnu jest trwała.
- Prompt 14–15 / przedmioty w lokacji: `WorldStateRepository` — przedmioty na ziemi są zapisywane i odtwarzane.
- Prompt 22–23 / NPC: `WorldStateRepository` — NPC, lokacja, stan AI, rany i inventory NPC są utrwalane.
- Prompt 33 / hidden elements: `WorldStateRepository` — ukryte elementy lokacji są zapisywane, w tym ukryte przedmioty.
- Prompt 32 / drzwi i blokady: `WorldStateRepository` — stan wyjść i zamków jest częścią snapshotu świata.

## D13 — NPC AI and respawn hardening
- Prompt 22 / NPC model: `astergard/npcs/models.py` — NPC ma trwały `home_room_id`, `respawn_delay_seconds`, dialog fallback i dodatkowy szablon `mountain_troll`.
- Prompt 23 / AI: `astergard/npcs/manager.py::NPCManager.ai_tick` — obsługa `PATROL`, `AGGRESSIVE` i `GUARD` z eventami.
- Prompt 23 / patrol zones: `NPCManager._patrol_tick` — NPC nie wychodzi poza własną strefę, ignoruje zamknięte przejścia i respektuje limit populacji lokacji.
- Prompt 23 + 26 / guard reputation: `NPCManager._guard_tick` + `FactionManager.hostile_to_guards` — strażnik atakuje gracza z reputacją MEEKHAN poniżej -500.
- Prompt 24 / respawn: `NPCManager.respawn_tick` — respawn oparty o opóźnienie, `home_room_id`, limit 3 NPC na lokację i retry queue.
- Persistence D12+D13: `WorldStateRepository` zapisuje i odtwarza `home_room_id` oraz `respawn_delay_seconds`.
- Testy: `tests/test_d13_npc_ai_respawn.py`.

Status: core implemented and regression-tested. Nadal nie production-grade: brak pathfindingu, pamięci walki, grupowego AI i broadcastu zdarzeń do klientów.


## D14 coverage update
- Prompty walki 16–21 oraz częściowo 65–66: rozszerzone o inicjatywę, zasięg, tarcze, parowanie, rundę aktywnych walk i testy regresji.
- Status: core implemented; nie production-grade dla pełnego balansu wielu na wielu.

## D15 coverage update
- Walka / prompt 19–21: core+ — dodano style walki, inicjatywę stylów, koszty kondycji i komunikaty obserwatorów.
- Persistence / prompt 3, 11, 12: core+ — styl walki jest zapisywany w SQLite migracją `006_combat_style.sql`.
- Testy / prompt 60: core+ — dodano testy `tests/test_d15_combat_styles.py`.

## D16 coverage update

- Combat simulation and balance reporting: `astergard/combat/balance.py`, `scripts/combat_balance_report.py`, `COMBAT_BALANCE_REPORT_D16.md`.
- NPC combat style profiles: `astergard/npcs/combat_profiles.py`, integration in `astergard/npcs/models.py`.
- Tests: `tests/test_d16_combat_balance_simulation.py`.
- Status: core implemented and measured. Full production balance remains open for D17+.

## D17 — korekta balansu po symulacjach

- Zakres: walka, style walki, NPC loadout, symulacje balansu.
- Kod: `astergard/combat/manager.py`, `astergard/npcs/models.py`, `astergard/combat/balance.py`.
- Testy: `tests/test_d17_balance_tuning.py`.
- Raport: `AUDIT_D17.md`, `COMBAT_BALANCE_REPORT_D17.md`.
- Status: core implemented / balance tuned, not production-grade.

## D18 update
- NPC AI / combat balance: rozszerzone o threat tiers (`astergard/npcs/threat.py`).
- NPCFactory: finalizacja NPC przez profil zagrożenia.
- Persistence świata: zapis `threat_tier`, `threat_label`, `combat_style`.
- Testy: `tests/test_d18_npc_threat_tiers.py`.
- Raport: `COMBAT_BALANCE_REPORT_D18.md`.


## D19 — Engine Core Completion

Status: CORE IMPLEMENTED / TESTED

Dowody w kodzie:
- `astergard/engine/events.py::EventBus`
- `astergard/engine/events.py::EngineEvent`
- `astergard/engine/scheduler.py::Scheduler`
- `astergard/engine/lifecycle.py::EngineLifecycle`
- `astergard/application/bootstrap.py::GameServices.event_bus`
- `astergard/application/bootstrap.py::GameServices.scheduler`
- `astergard/server/game.py::GameServer.global_heartbeat`
- `astergard/server/game.py::GameServer.shutdown`

Dowody testowe:
- `tests/test_d19_engine_core.py::EngineCoreD19Tests.test_event_bus_isolates_failing_subscribers`
- `tests/test_d19_engine_core.py::EngineCoreD19Tests.test_scheduler_runs_due_tasks_without_repeating_same_tick`
- `tests/test_d19_engine_core.py::EngineCoreD19Tests.test_lifecycle_flush_all_persists_character_and_world`
- `tests/test_d19_engine_core.py::EngineCoreD19Tests.test_game_server_shutdown_requests_lifecycle_flush`

Zakres nieprodukcyjny:
- brak eksportera metryk,
- brak trwałej kolejki eventów poza audytem,
- brak osobnego procesu monitorującego.


## D20 Domain Event System
- Status: core implemented / tested.
- Kod: `astergard/engine/events.py`, `astergard/application/use_case_contexts.py`, `astergard/application/context_assembler.py`, `astergard/application/services/*`.
- Testy: `tests/test_d20_domain_events.py`.
- Pokrycie: zdarzenia ruchu, ekwipunku, komunikacji, walki, śmierci NPC, questów, reputacji, ekonomii, magii/craftingu i zapisu postaci.
- Ograniczenie: system jest event-bus + audit trail, nie pełnym event-sourcingiem.

## D21 — Rules Engine
- Dodano pakiet `astergard/rules/` i `RuleSet`.
- Reguły walki, ruchu, ekonomii, reputacji, skilli, magii i respawnu są centralizowane oraz wstrzykiwane do usług.
- Testy: `tests/test_d21_rules_engine.py`.
- Status: core implemented / tested.


## D22 — State Machine Layer

Status: IMPLEMENTED / TESTED.

Dowody w kodzie:
- `astergard/state/machines.py`
- `astergard/server/session.py::ClientConnection.transition_state`
- `astergard/characters/models.py::Character.transition_state`
- `astergard/characters/models.py::Character.enter_combat`
- `astergard/characters/models.py::Character.leave_combat`
- `astergard/characters/models.py::Character.die`
- `astergard/npcs/models.py::NPC.transition_ai_state`
- `astergard/combat/manager.py::CombatManager.attack`
- `astergard/database/world_state_repository.py`

Testy:
- `tests/test_d22_state_machines.py`

Zakres:
- sesja: `CONNECTED`, `ENTER_PASSWORD`, `IN_GAME`, `DISCONNECTED`,
- postać: `ALIVE`, `IN_COMBAT`, `DEAD`,
- NPC AI: `IDLE`, `PATROL`, `AGGRESSIVE`, `GUARD`, `DEAD`,
- walka: przygotowany `CombatState` pod dalszą refaktoryzację aktywnych walk.

## D23 — Save/Load Engine
Status: core implemented + tested.

Dowody w kodzie:
- `astergard/engine/save_load.py`
- `astergard/database/save_manifest_repository.py`
- `astergard/database/migrations/007_save_manifests.sql`
- `astergard/engine/lifecycle.py`
- `astergard/server/game.py`

Testy:
- `tests/test_d23_save_load_engine.py`

Zakres:
- pełny flush graczy i świata,
- manifesty zapisu,
- checkpoint,
- restore,
- recovery świata,
- wersjonowanie schematu do migracji 007.


## D24 — Command Engine

Status: core implemented / tested.

Dowody w kodzie:
- `astergard/commands/engine.py` — metadane, registry, cooldown tracker, uprawnienia.
- `astergard/commands/dispatcher.py` — walidacja argumentów, cooldowny, permission check, help.
- `astergard/application/command_bus.py` — definicje komend i instalacja aliasów.
- `astergard/commands/registration.py` — katalog komend z opisem, użyciem, grupą i cooldownem.

Dowody w testach:
- `tests/test_d24_command_engine.py`.

Zakres nieprodukcyjny:
- brak trwałych cooldownów,
- brak pełnego parsera typowanych argumentów,
- role admina są minimalne.

## D25 — Testing Engine
Status: IMPLEMENTED / TESTED

Dowody implementacji:
- `astergard/testing/fakes.py` — fake reader/writer dla testów sesji.
- `astergard/testing/harness.py` — integracyjny `TestGameHarness`.
- `astergard/testing/scenarios.py` — runner scenariuszy komend.
- `scripts/run_command_regression.py` — uruchamialny scenariusz regresyjny.
- `tests/test_d25_testing_engine.py` — testy jednostkowe i integracyjne warstwy testing.

Kryteria akceptacji:
- realny dispatcher uruchamiany przez harness: spełnione,
- fake I/O bez sieci: spełnione,
- regresja komend: spełnione,
- zapis/odczyt przez harness: spełnione.

## D26 — Admin / GM Engine

Status: core implemented and tested.

Evidence:
- `astergard/admin/permissions.py`
- `astergard/admin/audit_logger.py`
- `astergard/admin/admin_service.py`
- `astergard/admin/gm_commands.py`
- `tests/test_d26_admin_gm_engine.py`

Covered capabilities:
- role-based permissions,
- GM/admin command registration,
- inspect, teleport, goto, summon, heal, kill-confirm, give, setstat, spawnnpc, saveworld, checkpoint, restore-confirm, worldstats, auditlog, scheduler, listsessions,
- audit logging,
- destructive command confirmation,
- regression-tested dispatcher integration.

Limitations:
- admin roles are dynamic/in-memory attributes unless represented by username `admin`; persistent role management remains a later persistence/content task.

## D27 — Observability & Diagnostics

Status: core implemented and tested.

Dowody w kodzie:
- `astergard/observability/metrics.py`
- `astergard/commands/dispatcher.py`
- `astergard/engine/lifecycle.py`
- `astergard/admin/admin_service.py`
- `astergard/admin/gm_commands.py`
- `astergard/commands/registration.py`
- `tests/test_d27_observability.py`

Komendy:
- `metrics` / `metryki`
- `events` / `eventy`
- `lag`
- `diagnostics` / `diag`

Testy:
- metryki komend,
- liczniki eventów,
- tick metrics,
- blokada uprawnień,
- raport diagnostyczny.

## D29 — Advanced Polish Command Parser

Status: implemented / tested.

Dowody w kodzie:
- `astergard/commands/polish.py` — normalizacja języka polskiego i proste lematy,
- `astergard/commands/parser.py` — parser skrótów, przyimków i indeksów,
- `astergard/commands/registration.py` — rozszerzone aliasy polskie,
- `astergard/commands/helpers.py` — dopasowanie NPC/przedmiotów po formach odmienionych,
- `astergard/commands/engine.py` — pomoc zależna od uprawnień,
- `astergard/quests/manager.py` — render dziennika zadań.

Testy:
- `tests/test_d29_polish_parser.py`.

## D30 — Object Interaction Parser
Status: core implemented / tested.

Dowody:
- `astergard/commands/polish.py` — `is_all_phrase`, `split_relation`, dodatkowe lematy.
- `astergard/commands/parser.py` — zachowanie relatorów dla komend obiektowych.
- `astergard/application/services/inventory_service.py` — `get_all_items`, `drop_all_items`, `put_item`, `give_item`.
- `astergard/commands/registration.py` — aliasy `wloz`, `włóż`, `daj`, `oddaj`, `przekaż`.
- `tests/test_d30_object_interaction_parser.py` — testy regresji.

## D31 — Container Interaction Engine

Status: implemented / tested.

Pokrycie:
- `astergard/application/services/inventory_service.py` — wyjmowanie z pojemników, wyjmowanie wszystkiego, rekurencyjne szukanie pojemników.
- `astergard/application/services/exploration_service.py` — oglądanie zawartości pojemnika i przedmiotu w pojemniku.
- `astergard/commands/parser.py` — zachowanie konektorów `z`, `ze`, `w`, `we` dla komend relacyjnych.
- `astergard/commands/registration.py` — nowa komenda `take_from` i aliasy `wyjmij`, `wyciągnij`.
- `tests/test_d31_container_interaction_engine.py` — testy regresji parsera i interakcji z pojemnikami.

Komendy:
```text
weź klucza z plecaka
wyjmij klucz z plecaka
weź wszystko z plecaka
obejrzyj w plecaku
obejrzyj klucz w plecaku
```

## D32 — Ground Containers & Object Disambiguation

Status: implemented / tested.

Pokrycie:
- pojemniki na ziemi,
- wyjmowanie z pojemników w lokacji,
- wkładanie do pojemników w lokacji,
- przekładanie między pojemnikami,
- przeszukiwanie pojemników,
- liczebniki porządkowe dla podobnych obiektów.

Dowody:
- `astergard/application/services/inventory_service.py`
- `astergard/application/services/exploration_service.py`
- `tests/test_d32_ground_containers.py`


## D33 — World Content Framework I
- Status: implemented / tested.
- Kod: `astergard/world/content.py`, `astergard/world/models.py`, `astergard/world/manager.py`, `astergard/application/services/exploration_service.py`.
- Testy: `tests/test_d33_world_content_framework.py`.
- Zakres: pierwsza warstwa ręcznie pisanego contentu świata, inspectables, opisane szczegóły lokacji, integracja z `spojrz/obejrzyj`.
