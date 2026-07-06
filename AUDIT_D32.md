# AUDIT D32 — Ground Containers & Object Disambiguation

## Cel
D32 domyka interakcję z pojemnikami leżącymi w lokacji oraz rozszerza parser obiektów o praktyczne konstrukcje typowe dla polskiego MUD-a.

## Wykonane zmiany
- Pojemniki leżące na ziemi są traktowane tak samo jak pojemniki niesione przez gracza.
- `weź/wyjmij <przedmiot> z <pojemnik>` działa dla pojemników w ekwipunku, wyposażeniu i na ziemi.
- `włóż <przedmiot> do <pojemnik>` działa także wtedy, gdy pojemnik leży w lokacji.
- Dodano komendę `przełóż/przenieś <przedmiot> z <pojemnika> do <pojemnika>`.
- `przeszukaj <pojemnik>` pokazuje zawartość pojemnika, zanim uruchomi zwykły test ukrytych elementów lokacji.
- `spójrz/obejrzyj w <pojemniku>` oraz `obejrzyj <przedmiot> w <pojemniku>` działa także dla pojemników na ziemi.
- Zachowano obsługę indeksu `drugi/trzeci/...`, np. `weź drugi miecz z skrzyni`.

## Pliki zmienione
- `astergard/application/services/inventory_service.py`
- `astergard/application/services/exploration_service.py`
- `astergard/commands/inventory.py`
- `astergard/commands/exploration.py`
- `astergard/commands/parser.py`
- `astergard/commands/polish.py`
- `astergard/commands/registration.py`
- `tests/test_d32_ground_containers.py`

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 133 tests in 2.608s
OK
```

## Krytyczna ocena
D32 poprawia ergonomię interakcji z obiektami, ale nadal nie jest pełnym parserem fleksyjnym. Rozpoznawanie odmiany działa przez konserwatywną tabelę lematów, nie przez analizator morfologiczny. To jest rozsądne dla obecnego etapu, ale docelowo parser powinien mieć słownik aliasów per obiekt oraz mechanizm rozstrzygania wieloznaczności z pytaniem doprecyzowującym.

## Następny etap
D33 — Object Disambiguation UX: gdy kilka obiektów pasuje do frazy, gra powinna pytać „Który dokładnie?” zamiast wybierać pierwszy albo wymagać od razu liczebnika.
