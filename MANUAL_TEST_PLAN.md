# Manual Test Plan

1. Uruchom `python3 main.py`.
2. Połącz się przez `nc 127.0.0.1 4000`.
3. Utwórz postać i hasło.
4. Wpisz `spojrz`.
5. Wpisz `ekwipunek`, `zaloz miecz`, `cechy`.
6. Wpisz `oferta`, `kup mikstura` przy lokacji startowej.
7. Wpisz `rozmawiaj kupiec o wilki`, potem `zadania`.
8. Poruszaj się kierunkami.
9. Znajdź NPC i użyj `atakuj wilk`.
10. Wpisz `zapisz`, `quit`, zaloguj się ponownie.

## D25 — Testing Engine
1. Uruchom pełne testy: `python3 -W error::ResourceWarning -m unittest discover tests`.
2. Uruchom scenariusz regresyjny: `python3 scripts/run_command_regression.py`.
3. Oczekiwany wynik: scenariusz `basic_gameplay` pokazuje odpowiedzi dla `spojrz`, `cechy`, `ekwipunek`, `pomoc`.
