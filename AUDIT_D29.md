# AUDIT D29 — Advanced Polish Command Parser

## Cel
D29 rozszerza polski interfejs komend po realnym teście telnetowym. Priorytetem było doprowadzenie ergonomii parsera bliżej klasycznego polskiego MUD-a: skróty, polskie znaki, podstawowa odmiana nazw, przyimki i ukrywanie komend niedostępnych dla gracza.

## Wykonane zmiany

### 1. Normalizacja języka polskiego
Dodano `astergard/commands/polish.py`:

- usuwanie polskich znaków przy dopasowaniu (`żołnierza` → `zolnierza`),
- czyszczenie interpunkcji,
- normalizacja wielkości liter,
- konserwatywna tabela lematów dla najważniejszych rzeczowników gry,
- usuwanie przyimków i słów pomocniczych w argumentach komend.

### 2. Parser komend
Rozszerzono `astergard/commands/parser.py`:

- `spójrz na żołnierza` jest parsowane jako komenda `spojrz` z argumentem `zolnierz`,
- `weź drugi żelazny klucz` zachowuje indeks `2`,
- kierunki obsługują skróty: `n`, `pn`, `s`, `pd`, `e`, `wsch`, `w`, `zach`, itd.,
- parser usuwa typowe przyimki z argumentów.

### 3. Rejestr komend
Rozszerzono aliasy w `astergard/commands/registration.py`, m.in.:

- `ob`, `sp`, `spójrz`, `patrz`, `zobacz`,
- `ekw`, `plecak`,
- `w`, `weź`, `podnieś`, `podn`,
- `upuść`, `zostaw`, `wyrzuć`,
- `uciekaj`, `uciek`,
- `dziennik`, `misje`,
- `przeszukaj`, `szperaj`.

### 4. Dopasowanie NPC i przedmiotów
Zmieniono `astergard/commands/helpers.py`:

- przedmioty dopasowują się po formach odmienionych i bez polskich znaków,
- NPC można wskazywać skrótem albo formą odmienioną, np. `sp żol`, `spójrz na żołnierza`, `rozmawiaj z kupcem o wilkach`.

### 5. Pomoc zależna od uprawnień
Zmieniono `render_help()` w `astergard/commands/engine.py` i dispatcher:

- zwykły gracz nie widzi komend administracyjnych ani diagnostycznych,
- administrator nadal może dostać pełną pomoc po uzyskaniu odpowiedniej roli.

### 6. Naprawa błędu questów
Naprawiono realny błąd z testu telnetowego:

```text
QuestManager object has no attribute render
```

Dodano `QuestManager.render()`, więc `zadania` / `dziennik` nie wywołuje już błędu systemowego.

## Testy
Dodano `tests/test_d29_polish_parser.py`.

Zakres testów:

- normalizacja polskich znaków,
- skróty arkadiowe `ob`, `ekw`,
- dopasowanie odmienionych nazw przedmiotów,
- dopasowanie skróconych nazw NPC,
- ukrywanie komend admina w pomocy gracza,
- poprawne renderowanie pustego dziennika zadań.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 118 tests in 2.297s
OK
```

## Krytyczna ocena
D29 znacząco poprawia ergonomię, ale to nadal nie jest pełny parser Arkadii. Brakuje jeszcze:

1. pełnego słownika odmian,
2. rozstrzygania wieloznaczności przy kilku obiektach o podobnej nazwie,
3. komend typu `wez wszystko`, `wez wszystko z plecaka`,
4. parsera relacji `wloz X do Y`, `daj X Y`,
5. sugestii dla literówek,
6. autouzupełniania i dokumentacji aliasów per komenda.

## Następny etap
D30 powinien domknąć **Object Interaction Parser**:

- `wez wszystko`,
- `wez drugi miecz`,
- `wloz chleb do plecaka`,
- `daj skóre kupcowi`,
- `obejrzyj drugi klucz`,
- jednoznaczne komunikaty przy konflikcie nazw.
