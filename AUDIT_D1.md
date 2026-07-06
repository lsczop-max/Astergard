# D1 Audit i refaktoryzacja rdzenia

## Zakres D1
Celem D1 było sprawdzenie obecnego grywalnego rdzenia, znalezienie krytycznych luk technicznych oraz wykonanie pierwszej twardej poprawki jakościowej zamiast dokładania nowych fasad.

## Wyniki audytu

### Krytyczne problemy znalezione
1. `PlayerRepository` używał `with sqlite3.connect(...) as con`, co zatwierdza transakcję, ale nie zamyka połączenia. Testy przechodziły, ale Python zgłaszał `ResourceWarning: unclosed database`.
2. Zapis postaci obejmował tylko część stanu: `room_id`, złoto, statystyki, umiejętności, rany, reputację i questy.
3. Nie zapisywano ekwipunku, wyposażenia ani aktywnych efektów. W MUD-zie oznacza to utratę przedmiotów po wylogowaniu.
4. Brakowało testu regresji dla pełnego roundtripu postaci.
5. `PROMPT_COVERAGE.md` nadal wymaga dalszej przebudowy, bo nie mapuje jeszcze każdej funkcji na test z precyzją produkcyjną.

## Wykonane poprawki

### Trwałość danych
- Dodano bezpieczny context manager `PlayerRepository.connection()`, który zawsze zamyka połączenie SQLite.
- Dodano kolumny:
  - `inventory_json`,
  - `equipment_json`,
  - `effects_json`.
- Dodano prostą migrację schematu przez `PRAGMA table_info(players)` i `ALTER TABLE`.
- Dodano serializację i deserializację `Item`, w tym kontenerów z zawartością.
- Dodano serializację i deserializację `Effect`.
- `PlayerRepository.save()` i `PlayerRepository.load()` zapisują teraz pełniejszy stan postaci.

### Testy
Dodano `tests/test_persistence.py`:
- `test_full_character_state_roundtrip` sprawdza zapis/odczyt:
  - pokoju,
  - złota,
  - statystyk,
  - ran,
  - reputacji,
  - aktywnych i ukończonych questów,
  - założonej broni,
  - kontenera z zawartością,
  - aktywnego efektu.
- `test_repository_closes_connections_under_resource_warning_as_error` weryfikuje brak wycieków połączeń przy `ResourceWarning` jako błędzie.

## Wyniki weryfikacji

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 7 tests in 0.028s
OK
```

```text
python3 -m compileall -q astergard tests
OK
```

## Co nadal jest niedopracowane
1. Architektura nadal ma zbyt dużo komend w `astergard/server/game.py`.
2. `CommandDispatcher` działa, ale system komend powinien zostać rozbity na pakiety domenowe.
3. NPC AI, questy, ekonomia i crafting są grywalnym rdzeniem, nie pełną symulacją.
4. Brakuje pełnych testów integracyjnych sesji TCP.
5. Brakuje testów obciążeniowych dla wielu klientów, NPC i heartbeat.
6. Ranking jest nadal niedopracowany i nie wykonuje rzeczywistej top-listy SQL.

## Decyzja na D2
Następny etap powinien rozbić `GameServer` i komendy na moduły domenowe:
- `commands/exploration.py`,
- `commands/inventory.py`,
- `commands/combat.py`,
- `commands/social.py`,
- `commands/economy.py`,
- `commands/quests.py`.

Celem D2 nie powinno być dodawanie nowych funkcji, tylko redukcja długu architektonicznego i testy dispatcher → komenda → efekt.
