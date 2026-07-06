# AUDIT D27 — Observability & Diagnostics

## Cel etapu
D27 domyka infrastrukturę diagnostyczną silnika Astergard po D26 Admin/GM Engine.
Celem było dodanie obserwowalności bez zewnętrznych zależności: metryk komend, metryk ticków, liczników eventów, diagnostyki schedulera i komend GM do odczytu tych danych.

## Dodane moduły
- `astergard/observability/__init__.py`
- `astergard/observability/metrics.py`

## Zmienione moduły
- `astergard/application/bootstrap.py`
  - dodano `ObservabilityService` do `GameServices`,
  - zbudowano wspólny `Scheduler`, `EventBus` i `ObservabilityService` w jednym miejscu assembly.
- `astergard/application/use_case_contexts.py`
  - `AdminContext` otrzymał port `observability`.
- `astergard/application/context_assembler.py`
  - przekazuje `ObservabilityService` do `AdminContext` i `GameContext`.
- `astergard/server/context.py`
  - `GameContext` otrzymał jawny port `observability` do metryk dispatchera.
- `astergard/commands/dispatcher.py`
  - mierzy czas wykonania komend,
  - rejestruje powodzenie/błąd/odmowę uprawnień/brak argumentu/cooldown.
- `astergard/engine/lifecycle.py`
  - mierzy czas ticków,
  - rejestruje wynik ticka w observability.
- `astergard/admin/admin_service.py`
  - dodano metody: `metrics`, `events`, `lag`, `diagnostics`.
- `astergard/admin/gm_commands.py`
  - dodano handlery komend diagnostycznych.
- `astergard/commands/registration.py`
  - dodano komendy diagnostyczne do rejestru z wymaganym poziomem `HELPER`.

## Nowe komendy diagnostyczne
- `metrics` / `metryki` — metryki uptime, eventów, komend, ticków i schedulera.
- `events` / `eventy` — liczniki eventów domenowych.
- `lag` — diagnostyka czasu ticków i błędów schedulera.
- `diagnostics` / `diag` — pełny raport łączący metryki, ticki i eventy.

## Testy dodane w D27
- `tests/test_d27_observability.py`

Zakres testów:
- rejestrowanie metryk komend,
- zliczanie eventów domenowych,
- raportowanie ticków po lifecycle tick,
- blokada dostępu dla zwykłego gracza,
- pełny raport diagnostyczny dla roli HELPER.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 112 tests in 2.116s
OK
```

## Regresja komend
```text
python3 scripts/run_command_regression.py
OK — scenariusz basic_gameplay wykonał komendy przez realny dispatcher.
```

## Krytyczna ocena
D27 jest realnym etapem infrastrukturalnym. Silnik zyskał obserwowalność potrzebną do dalszego rozwoju i diagnostyki lagów, błędów eventów oraz kosztu komend.

Ograniczenia:
- metryki są in-memory, nie są jeszcze zapisywane do osobnej tabeli historycznej,
- brak eksportu Prometheus/OpenTelemetry,
- brak dashboardu WWW,
- brak agregacji per-strefa/per-NPC/per-command group.

Te ograniczenia są akceptowalne na poziomie silnika core. Produkcyjny telemetry stack powinien być osobnym etapem dopiero po stabilizacji rozgrywki.

## Następny etap
D28 — Release Hardening infrastruktury silnika:
- finalny audit zależności,
- smoke tests uruchomienia serwera,
- cleanup dokumentacji,
- benchmark podstawowy,
- finalny ZIP silnika przed powrotem do systemów gry.
