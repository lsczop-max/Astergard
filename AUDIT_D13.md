# AUDIT D13 — NPC AI and Respawn Hardening

## Cel
D13 wzmacnia system NPC, AI i respawnu po wprowadzeniu trwałego snapshotu świata w D12.

## Zmiany wykonane

### 1. Model NPC
Plik: `astergard/npcs/models.py`

Dodano:
- `NPC.home_room_id` — stały punkt odrodzenia, niezależny od miejsca śmierci,
- `NPC.respawn_delay_seconds` — per-NPC czas respawnu,
- `NPC.dialogue(topic)` — bezpieczne odczytywanie kwestii dialogowych,
- nowy szablon `mountain_troll`.

### 2. NPCManager
Plik: `astergard/npcs/manager.py`

Dodano:
- `NPCActionEvent` jako jawny wynik AI,
- limit `MAX_NPCS_PER_ROOM = 3`,
- `can_spawn_at(room_id)`,
- patrol z walidacją strefy, zamkniętych przejść i limitu populacji,
- agresję NPC wobec graczy w tym samym pokoju,
- agresję strażników wobec graczy z reputacją MEEKHAN < -500,
- respawn oparty o `home_room_id`, `delay`, limit populacji i kolejkę retry,
- log zdarzeń `NPCManager.events`.

### 3. Heartbeat
Plik: `astergard/application/heartbeat.py`

Heartbeat przekazuje teraz do NPC AI:
- aktywnych graczy,
- `CombatManager`,
- `FactionManager`.

Dzięki temu AI może inicjować walki i reagować na reputację bez zależności od warstwy TCP.

### 4. Persistence NPC
Plik: `astergard/database/world_state_repository.py`

Snapshot świata zapisuje teraz także:
- `home_room_id`,
- `respawn_delay_seconds`.

## Testy dodane
Plik: `tests/test_d13_npc_ai_respawn.py`

Testy obejmują:
- patrol tylko w obrębie tej samej strefy,
- zdarzenia patrolu,
- inicjowanie walki przez agresywnego NPC,
- atak strażnika na gracza wrogiego Imperium,
- respawn po czasie,
- brak respawnu przed czasem,
- limit trzech NPC na lokację.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 47 tests in 0.466s
OK
```

## Krytyczna ocena
D13 znacząco poprawia NPC AI, ale nadal nie jest to pełne MMO AI. Brakuje jeszcze:
- ścieżkowania wielopokojowego,
- pamięci agresji po utracie celu,
- AI używającego przedmiotów,
- grupowego wsparcia NPC,
- komunikatów broadcastowanych do realnych klientów w pokoju,
- osobnej pętli walki NPC-vs-player z pełnym rozliczeniem rund.

## Następny etap
D14 powinien rozbudować system walki o pełniejszą pętlę bojową: rundy NPC, parowanie, tarcze, zasięg broni, inicjatywę, rozbrojenie edge-case'ów i testy balansu.
