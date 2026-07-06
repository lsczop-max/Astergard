# AUDIT D3 — Application Services Refactor

## Cel
D3 usuwa kolejną warstwę centralizacji z `astergard/server/game.py` bez zmiany zachowania gry. `GameServer` pozostaje adapterem sieciowym, a tworzenie świata, usług, rejestracja komend, heartbeat i sesja klienta zostały wydzielone.

## Zmiany wykonane

### 1. Nowa warstwa aplikacyjna
Dodano pakiet:

- `astergard/application/bootstrap.py`
- `astergard/application/heartbeat.py`
- `astergard/application/session_flow.py`
- `astergard/application/__init__.py`

### 2. `GameBootstrapper`
Nowa klasa `GameBootstrapper` odpowiada za:

- utworzenie `PlayerRepository`,
- wygenerowanie świata,
- populację NPC,
- zbudowanie usług domenowych,
- rejestrację komend w dispatcherze.

`GameServer` nie zna już kolejności budowania świata, NPC i command registry.

### 3. `HeartbeatService`
Nowa klasa `HeartbeatService` odpowiada za:

- tick pogody,
- tick NPC AI,
- tick respawnu,
- regenerację kondycji graczy,
- tick efektów magicznych.

Dzięki `tick_once()` heartbeat jest testowalny bez uruchamiania serwera TCP.

### 4. `SessionFlow`
Nowa klasa `SessionFlow` odpowiada za:

- logowanie,
- tworzenie postaci,
- wysłanie pierwszego widoku lokacji,
- pętlę komend klienta.

`GameServer.handle_connection()` jest teraz cienką orkiestracją zasobów połączenia.

### 5. Rejestracja komend
`commands/registration.py` przyjmuje teraz bezpośrednio `CommandDispatcher`, a nie cały `GameServer`. To zmniejsza sprzężenie command registry z warstwą sieciową.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 13 tests in 0.073s
OK
```

## Nowe testy
Dodano `tests/test_d3_application_services.py`:

- test kompletności grafu usług z `GameBootstrapper`,
- test heartbeat bez sieci,
- test wymuszenia delegacji w `server/game.py`.

## Stan po D3
`GameServer` jest nadal kompatybilny ze starszymi testami i komendami, ale odpowiedzialności zostały wyraźniej rozdzielone:

- `GameServer` — adapter TCP i cykl życia połączenia,
- `GameBootstrapper` — budowanie grafu usług,
- `SessionFlow` — przepływ sesji klienta,
- `HeartbeatService` — cykliczna aktualizacja świata,
- `commands/*` — adaptery komend,
- pakiety domenowe — logika gry.

## Krytyczna ocena
D3 poprawia strukturę, ale nadal pozostają problemy:

1. Komendy nadal zawierają część logiki aplikacyjnej.
2. Brakuje osobnych application services dla inventory, combat, quests i economy.
3. `GameContext` nadal przekazuje pełny `GameServer`, przez co komendy mają zbyt szeroki dostęp.
4. Brakuje statycznego enforcementu zależności warstw.

## Następny etap: D4
D4 powinien wydzielić usługi aplikacyjne dla najważniejszych systemów:

- `InventoryApplicationService`,
- `CombatApplicationService`,
- `QuestApplicationService`,
- `EconomyApplicationService`.

Celem D4 jest to, żeby handlery komend stały się cienkimi adapterami wejścia/wyjścia, a reguły gry przeniosły się do testowalnych usług.
