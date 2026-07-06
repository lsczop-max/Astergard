# AUDIT D19 — Engine Core Completion

## Cel
Domknięcie warstwy silnikowej przed dalszym rozwojem contentu: event bus, scheduler, tick lifecycle, save lifecycle, kontrolowane shutdown oraz crash-safe state flush.

## Zmiany wykonane

### 1. Event bus
Dodano moduły:
- `astergard/engine/events.py`
- `astergard/engine/__init__.py`

Najważniejsze elementy:
- `EngineEvent`
- `EventBus.subscribe()`
- `EventBus.unsubscribe()`
- `EventBus.publish()`
- `EventBus.emit()`
- izolacja błędów subskrybentów
- historia eventów i rejestr błędów

### 2. Scheduler ticków
Dodano:
- `astergard/engine/scheduler.py`

Najważniejsze elementy:
- `ScheduledTask`
- `Scheduler.every()`
- `Scheduler.run_due()`
- ochrona przed ponownym wykonaniem zadania w tym samym ticku
- izolacja błędów tasków

### 3. Engine lifecycle
Dodano:
- `astergard/engine/lifecycle.py`

Najważniejsze elementy:
- `EngineLifecycle.run_forever()`
- `EngineLifecycle.tick()`
- `EngineLifecycle.request_shutdown()`
- `EngineLifecycle.flush_player_states()`
- `EngineLifecycle.flush_world_state()`
- `EngineLifecycle.flush_all()`

### 4. Integracja z bootstrapem
Zmieniono:
- `astergard/application/bootstrap.py`

`GameServices` otrzymał:
- `event_bus`
- `scheduler`

### 5. Integracja z serwerem
Zmieniono:
- `astergard/server/game.py`

`GameServer` korzysta teraz z `EngineLifecycle` zamiast uruchamiać heartbeat jako surową pętlę bez warstwy lifecycle.

### 6. Integracja z heartbeat
Zmieniono:
- `astergard/application/heartbeat.py`

Heartbeat emituje eventy:
- `world.respawn_tick_completed`
- `character.tick_completed`
- `npc.died`

Zapis świata został przeniesiony do lifecycle/autosave zamiast być twardo zaszyty w każdym ticku heartbeat.

## Testy dodane
Dodano:
- `tests/test_d19_engine_core.py`

Pokrycie testowe:
- event bus izoluje błędnych subskrybentów,
- scheduler wykonuje taski deterministycznie,
- lifecycle zapisuje postać i świat,
- shutdown serwera wymusza flush świata.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 72 tests in 1.296s
OK
```

## Ocena krytyczna
D19 domyka rdzeń lifecycle, ale nie jest jeszcze pełnym systemem obserwowalności. Event bus ma historię w pamięci i zapis audytowy przez repozytorium, ale nie ma jeszcze metryk wydajnościowych, eksportu statystyk ani narzędzi diagnostycznych dla GM/operatora.

## Następny etap
D20 — Domain Event System:
- jawny katalog eventów domenowych,
- zdarzenia ruchu, walki, śmierci, loot, quest, reputacja, handel,
- event audit jako first-class concern,
- testy subskrypcji per domain.
