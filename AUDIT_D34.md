# AUDIT D34 — World Area Expansion I

## Cel
D34 rozszerza pierwszy grywalny obszar twierdzy z kilku ręcznie opisanych lokacji do większego, spójnego content packa startowego. Celem nie jest jeszcze pełne wypełnienie 500 lokacji, tylko zapewnienie, że gracz po wyjściu ze startu nie trafia natychmiast w powtarzalne, proceduralne opisy.

## Wykonane zmiany
- Rozszerzono `astergard/world/content.py`.
- Dodano content overlay dla ponad 60 lokacji startowego regionu.
- Zachowano pełny graf 500 lokacji generowany przez `WorldManager`.
- Dodano unikalne nazwy lokacji w pierwszej dzielnicy twierdzy, m.in. rynek, warsztaty, zaułki, karczmę, składy, lazaret, zbrojownię, bramy i obrzeża.
- Dodano powtarzalny, ale parametryzowany system atmosfery i detali dla lokacji dzielnicowych.
- Każda nowa lokacja contentowa ma `inspectables`, czyli rzeczy do obejrzenia komendami `spójrz na ...`, `obejrzyj ...`, `ob ...`.
- Dodano kilka jawnych i ukrytych przedmiotów w nowych lokacjach.

## Nowe testy
Dodano `tests/test_d34_world_area_expansion.py`:
- sprawdza, że content pack zawiera co najmniej 60 lokacji,
- sprawdza, że graf świata nadal ma 500 lokacji,
- sprawdza, że lokacje contentowe mają inspectables,
- sprawdza wejście do rozszerzonego obszaru i oglądanie detalu,
- sprawdza obecność ukrytych przedmiotów z rozszerzonego contentu.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 141 tests in 2.874s
OK
```

## Krytyczna ocena
D34 poprawia pierwsze wrażenie i eksplorację startowego obszaru, ale nie rozwiązuje jeszcze głównego problemu świata: większość z 500 lokacji nadal jest proceduralna. Obecny content pack jest celowo lekki i bez osobnych plików danych; przy dalszym wzroście powinien zostać przeniesiony do danych strukturalnych, np. JSON/YAML albo Pythonowych definicji per region.

## Następny etap
D35 powinien wydzielić content do osobnych pakietów regionów i dodać loader contentu, np.:
- `world/content_packs/centrum_twierdza.py`,
- walidację unikalnych room_id,
- raport pokrycia contentem,
- mapę startowego regionu generowaną z realnego grafu.
