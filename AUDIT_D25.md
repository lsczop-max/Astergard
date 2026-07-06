# AUDIT D25 — Testing Engine

## Cel
D25 domyka warstwę testowania gry: fake I/O dla sesji, harness integracyjny, runner scenariuszy komend oraz regresję podstawowej ścieżki gracza.

## Zmiany wykonane
- Dodano pakiet `astergard/testing/`.
- Dodano `FakeReader` i `FakeWriter` zgodne z minimalnym interfejsem `asyncio.StreamReader/StreamWriter` używanym przez serwer.
- Dodano `TestGameHarness`, który buduje realny `GameServer` na tymczasowej bazie SQLite i wykonuje komendy przez prawdziwy dispatcher oraz kontekst gry.
- Dodano `ScenarioRunner` i `ScenarioStep` do pisania czytelnych testów regresyjnych komend.
- Dodano skrypt `scripts/run_command_regression.py` uruchamiający scenariusz sanity bez ręcznego telnetu.
- Dodano `tests/test_d25_testing_engine.py`.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 101 tests in 1.750s
OK
```

## Wynik scenariusza regresyjnego
```text
python3 scripts/run_command_regression.py
Scenario: basic_gameplay
> spojrz
[ Zaułek 0 (Centrum_Twierdza) ]
> cechy
Siła: przeciętny
> ekwipunek
Wyposażenie: brak
> pomoc
Dostępne komendy:
```

## Krytyczna ocena
D25 znacząco poprawia zdolność weryfikacji silnika, ale nadal nie jest pełnym frameworkiem testów obciążeniowych. Brakuje jeszcze testów wielu równoczesnych klientów, długiego soak testu, metryk opóźnień ticka i automatycznego coverage report. To powinno wejść do późniejszego etapu observability/performance.

## Następny etap
D26 — Admin/GM Engine: komendy administracyjne, inspect, teleport, spawn, give, saveworld, shutdown oraz testy uprawnień.
