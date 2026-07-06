# Astergard MUD — autonomiczny build etapowy

Grywalny, modularny rdzeń MUD/SUD w Pythonie 3.12, zbudowany według cyklu: etap → implementacja → test → raport.

## Uruchomienie

```bash
cd astergard_loop_build
python3 -m unittest discover tests
python3 main.py
```

Połączenie z drugiego terminala:

```bash
nc 127.0.0.1 4000
# albo
 telnet 127.0.0.1 4000
```

## Przykładowe komendy

- `spojrz`
- `polnoc`, `poludnie`, `wschod`, `zachod`
- `powiedz tekst`
- `ekwipunek`
- `zaloz miecz`
- `atakuj wilk`
- `rozmawiaj kupiec o wilki`
- `zadania`
- `oferta`, `kup mikstura`, `sprzedaj chleb`
- `szukaj`
- `czaruj wzmocnienie`
- `zapisz`, `quit`

## Ograniczenie uczciwe

To nie jest produkcyjne MMO. To kompleksowy, modularny rdzeń grywalny: wszystkie obszary z promptów mają realny kod, integrację i testy sanity, ale część systemów ma status `core implemented`, nie `production complete`.


## D1 status
Audyt D1 poprawił trwałość danych SQLite: ekwipunek, wyposażenie i aktywne efekty zapisują się w bazie. Testy: `python3 -W error::ResourceWarning -m unittest discover tests` -> 7 OK. Szczegóły: `AUDIT_D1.md`.

## D2 — modularizacja komend

Wersja D2 rozdziela logikę komend z `astergard/server/game.py` do modułów w `astergard/commands/`.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny:

```text
Ran 10 tests in 0.034s
OK
```

## D3 — Application Services Refactor

D3 wydziela z `GameServer` trzy odpowiedzialności:

- `GameBootstrapper` — budowanie grafu usług i rejestracja komend,
- `SessionFlow` — logowanie oraz pętla komend klienta,
- `HeartbeatService` — tick pogody, NPC, respawnu, regeneracji i efektów.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik D3:

```text
Ran 13 tests in 0.073s
OK
```

## D4 — Application Use Case Services

D4 wydziela reguły ekwipunku, walki, questów i handlu z handlerów komend do warstwy aplikacyjnej:

- `astergard/application/services/inventory_service.py`
- `astergard/application/services/combat_service.py`
- `astergard/application/services/quest_service.py`
- `astergard/application/services/economy_application_service.py`

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik D4:

```text
Ran 18 tests in 0.095s
OK
```


## D5 — dalsze wydzielenie usług aplikacyjnych

Dodano usługi: eksploracji, komunikacji, magii/craftingu i komend systemowych. Handlery komend w tych obszarach są teraz cienkimi adapterami.

Testy D5:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 23 tests ... OK`.

## D6 — Context Ports

Wersja D6 usuwa dostęp `ctx.server` z komend i usług aplikacyjnych. `GameContext` zawiera teraz porty aplikacyjne oraz callback `players_in_room`, co ogranicza zależność logiki gry od adaptera TCP.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Oczekiwany wynik D6: `Ran 26 tests ... OK`.

## D7 — Use-case contexts
- Dodano wąskie konteksty przypadków użycia.
- Usługi aplikacyjne nie importują już `GameContext`.
- Testy: 29 OK.
- Status: core implemented; pełna separacja komend od kontenera usług wymaga D8.

## D8 — CommandBus i fabryki handlerów

D8 usuwa znajomość prywatnego kontenera usług z modułów komend. Komendy są teraz tworzone przez fabryki `build_*_handlers(service)`, a aliasy rejestruje `CommandBus`.

Testy D8:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 32 tests ... OK`.


## D9 — Context assembly boundary
- Added `application/context_assembler.py`.
- `GameContext` no longer stores the full `GameServices` container.
- Tests: 35 passing with ResourceWarning treated as error.


## D10 persistence hardening

D10 adds versioned SQLite migrations and explicit schema history. Run tests with:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Current D10 result: `Ran 38 tests ... OK`.

## D11 — persistence split

Wersja D11 rozdziela persistence na repozytoria kont, stanu postaci, audytu oraz backup/restore. Publiczny `PlayerRepository` pozostaje fasadą zgodności dla serwera i testów.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

## D12 — trwały świat
Od D12 serwer utrwala mutable world state: przedmioty na ziemi, ukryte elementy, NPC, ich stan bojowy/AI, kolejkę respawnu oraz blokady przejść. Snapshot świata znajduje się w tabeli `world_snapshots`.

Test:
```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

## D13 — NPC AI i respawn
D13 wzmacnia AI NPC:
- patrole wewnątrz strefy,
- agresja NPC wobec graczy,
- reakcja strażników na reputację,
- respawn z limitem populacji,
- trwały `home_room_id` NPC.

Test:
```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny D13: `Ran 47 tests ... OK`.


## D14 — Combat Balance Core
Dodano inicjatywę, aktywną obronę tarczą, parowanie bronią, zasięg broni, rundy walki NPC/gracz w heartbeat oraz testy regresji walki.

Testy: `python3 -W error::ResourceWarning -m unittest discover tests` — 52 testy OK.

## D15 — Combat styles and observer messages
Dodano style walki (`styl ofensywny`, `styl defensywny`, `styl ostrozny`, `styl brutalny`, `styl zrownowazony`). Styl wpływa na inicjatywę, trafienie, obronę, koszt kondycji i obrażenia. Wyniki rund walki zawierają teraz komunikaty dla obserwatorów.

## D16 — Combat balance simulations

D16 adds repeatable combat balance simulations:

```bash
python3 scripts/combat_balance_report.py --iterations 1000 --output COMBAT_BALANCE_REPORT_D16.md
```

The generated report is included as `COMBAT_BALANCE_REPORT_D16.md`.

## D17 — korekta balansu walki

D17 koryguje parametry walki na podstawie raportu symulacji D16. Dodano pełniejszy loadout bojowy NPC, zmniejszono ekstremalne remisy i poprawiono profil brutalnego stylu walki. Raport liczbowy znajduje się w `COMBAT_BALANCE_REPORT_D17.md`.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

## D18 — NPC threat tiers
Dodano jawne klasy zagrożenia NPC: `trash`, `standard`, `elite`, `boss`.
Profile wpływają na statystyki, kondycję, obrażenia, ochronę i czas respawnu. Raport symulacji znajduje się w `COMBAT_BALANCE_REPORT_D18.md`.


## D19 — Engine Core Completion

Dodano warstwę silnikową:
- `astergard/engine/events.py` — event bus,
- `astergard/engine/scheduler.py` — deterministyczny scheduler ticków,
- `astergard/engine/lifecycle.py` — lifecycle tick/save/shutdown,
- integrację z `GameServer`, `GameBootstrapper` i `HeartbeatService`.

Aktualny wynik testów:

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 72 tests in 1.296s
OK
```


## D20 — Domain Event System
Dodano typowany system zdarzeń domenowych, publikację eventów z eksploracji, ekwipunku, walki, questów, ekonomii, komunikacji, magii/craftingu oraz audyt przez lifecycle.

Testy: `Ran 76 tests ... OK`.

## D21 — Rules Engine
- Dodano pakiet `astergard/rules/` i `RuleSet`.
- Reguły walki, ruchu, ekonomii, reputacji, skilli, magii i respawnu są centralizowane oraz wstrzykiwane do usług.
- Testy: `tests/test_d21_rules_engine.py`.
- Status: core implemented / tested.


## D22 — State Machine Layer

Wersja D22 dodaje jawne maszyny stanów dla sesji, postaci, NPC oraz przygotowuje stan walki.

Uruchomienie testów:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Oczekiwany wynik D22:

```text
Ran 88 tests
OK
```

## D23 — Save/Load Engine

Dodano centralny silnik zapisu i odczytu:

- `SaveLoadEngine.flush_all()`
- `SaveLoadEngine.save_character()`
- `SaveLoadEngine.save_world()`
- `SaveLoadEngine.create_checkpoint()`
- `SaveLoadEngine.restore_checkpoint()`
- manifesty w tabeli `save_manifests`

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```


## D24 — Command Engine

Warstwa komend ma teraz jawny silnik: metadane, aliasy, wymagane argumenty, cooldowny, uprawnienia i pomoc generowaną z rejestru.

Najważniejsze pliki:
- `astergard/commands/engine.py`
- `astergard/commands/dispatcher.py`
- `astergard/application/command_bus.py`
- `astergard/commands/registration.py`

Testy D24: `tests/test_d24_command_engine.py`.

## D25 Testing Engine
- Dodano `astergard/testing/` z fake I/O, harnessami i runnerem scenariuszy.
- Dodano `scripts/run_command_regression.py`.
- Testy: `python3 -W error::ResourceWarning -m unittest discover tests` → 101 testów OK.
- Regresja manualno-automatyczna: `python3 scripts/run_command_regression.py`.


## D26 Admin / GM Engine

This build includes a real Admin/GM command layer with role checks and audit logging.

Example commands for an actor with `admin_role = "gm"` or username `admin`:

```text
inspect <player>
teleport <player> <room_id>
goto <room_id>
summon <player>
heal [player]
spawnnpc <vnum> [room_id]
worldstats
listsessions
```

Destructive commands require inline confirmation:

```text
adminkill <player> confirm
restore <backup_path> confirm
```

Run tests:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
python3 scripts/run_command_regression.py
```

## D27 — Observability & Diagnostics

Dodano centralną obserwowalność silnika:

- metryki komend,
- metryki ticków,
- liczniki eventów domenowych,
- diagnostykę schedulera,
- komendy GM: `metrics`, `events`, `lag`, `diagnostics`.

Wymagany poziom uprawnień: `HELPER` albo wyższy.

Przykładowe użycie w grze:

```text
metrics
events 10
lag
diagnostics
```

## D29 — Advanced Polish Command Parser

D29 rozszerza polski interfejs komend:

- normalizacja polskich znaków,
- skróty typu `ob`, `sp`, `ekw`, `podn`,
- podstawowe formy odmienione najważniejszych rzeczowników,
- przyimki w stylu `spójrz na żołnierza`,
- ukrywanie komend admina przed zwykłym graczem,
- naprawa dziennika zadań.

Przykłady:

```text
ob
sp żol
spójrz na żołnierza
weź żelazny klucz
podnieś klucza
ekw
dziennik
uciekaj
```

Testy D29:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 118 tests ... OK`.

## D30 — Object Interaction Parser

Dodano polskie komendy interakcji z obiektami:

```text
weź wszystko
upuść wszystko
włóż klucza do plecaka
daj skórę kupcowi
```

Ekwipunek pokazuje teraz zawartość pojemników. Testy D30 znajdują się w `tests/test_d30_object_interaction_parser.py`.

Test:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny D30: `Ran 123 tests ... OK`.

## D31 — Container Interaction Engine

D31 dodaje pełniejszą obsługę pojemników w polskim parserze:

```text
weź klucza z plecaka
wyjmij klucz z plecaka
weź wszystko z plecaka
obejrzyj w plecaku
obejrzyj klucz w plecaku
```

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 129 tests ... OK`.

## D32 — Ground Containers & Object Disambiguation

D32 rozszerza obsługę pojemników i obiektów:

```text
weź drugi miecz z skrzyni
wyjmij wszystko z plecaka
włóż pierścień do skrzyni
przełóż klucz z skrzyni do plecaka
przeszukaj skrzynię
obejrzyj klucz w skrzyni
```

Pojemniki mogą być teraz w ekwipunku, wyposażeniu albo leżeć na ziemi w lokacji.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik D32: `Ran 133 tests ... OK`.

## D33 — World Content Framework I

Dodano pierwszy ręcznie pisany pakiet zawartości świata. Proceduralne 500 lokacji pozostaje, ale wybrane lokacje startowe mają teraz unikalne nazwy, opisy i szczegóły do obejrzenia.

Przykłady:

```text
spojrz
spojrz na brame
obejrzyj mur
poludnie
spojrz na mur
```

Testy D33:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 137 tests ... OK`.


## D34 — World Area Expansion I

Rozszerzono ręcznie pisany content startowego obszaru twierdzy do ponad 60 lokacji. Lokacje mają unikalne nazwy, opisy, inspectables oraz część jawnych i ukrytych przedmiotów.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 141 tests ... OK`.

## D35.1C — Puszcza Ciszy World Rewrite

Etap D35.1C ręcznie przebudowuje Puszczę Ciszy (`210–279`): 70 unikalnych lokacji, organiczne połączenia, inspectables, pierwsze jawne i ukryte elementy leśne oraz przejścia do Osady Myśliwych, traktów i przyszłej Kniei Cichych Ścieżek.

Testy:

```bash
python3 -W error::ResourceWarning -m unittest discover tests
```

Wynik referencyjny: `Ran 153 tests ... OK`.
