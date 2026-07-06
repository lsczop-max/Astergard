# AUDIT D33 — World Content Framework I

## Cel
D33 rozpoczyna przejście od pustego, proceduralnego świata do grywalnego świata z ręcznie autorską zawartością. Nie zmienia grafu 500 lokacji, tylko nakłada na wybrane lokacje warstwę contentu: unikalne nazwy, opisy, obiekty do obejrzenia, przedmioty i ukryte znaleziska.

## Wykonane zmiany

### 1. Nowy moduł contentu świata
Dodano `astergard/world/content.py`:

- `LocationContent` — definicja nakładki contentowej na lokację,
- `make_content_pack()` — pierwszy ręcznie pisany pakiet lokacji,
- `apply_content_pack()` — bezpieczne nakładanie contentu na proceduralny świat.

### 2. Rozszerzenie modelu lokacji
`Location` otrzymała:

- `inspectables: dict[str, str]`

To pozwala tworzyć lokacyjne szczegóły typu:

- brama,
- mur,
- studnia,
- skrzynki,
- skóry,
- dachy.

Gracz może wpisywać np.:

```text
spójrz na bramę
obejrzyj mur
ob studnie
patrz na skóry
```

### 3. Pierwszy content pack
Ręcznie opracowano pierwsze lokacje startowe:

- `0` — Brama Dymnych Chorągwi,
- `1` — Plac Przed Wartownią,
- `20` — Trakt Przy Murze,
- `21` — Dziedziniec Suchych Studni,
- `22` — Zaułek Garbarzy,
- `23` — Ulica Przy Składach,
- `24` — Cichy Przesmyk.

Każda z tych lokacji ma unikalny opis i listę szczegółów do obejrzenia.

### 4. Integracja z `look`
`ExplorationService.look()` pokazuje teraz listę:

```text
Możesz obejrzeć: brama, mur, warta, koleiny.
```

oraz rozpoznaje ręcznie opisane detale przed NPC i przedmiotami.

### 5. Poprawki parsera polskiego
Dodano odmiany:

- `bramę`, `bramy`, `brama` → `brama`.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 137 tests in 2.723s
OK
```

## Nowe testy
Dodano `tests/test_d33_world_content_framework.py`:

- test nakładania content packa bez zmiany liczby 500 lokacji,
- test widoczności obiektów do obejrzenia w `spojrz`,
- test `obejrzyj bramę`,
- test unikalnej lokacji po przejściu na południe.

## Krytyczna ocena
D33 nie rozwiązuje jeszcze problemu pustego świata w całości. To pierwszy framework i pierwszy content pack. Skala jest mała, ale kierunek jest właściwy: od teraz kolejne lokacje powinny być dopisywane jako dane contentowe, nie jako hardcode w serwisie eksploracji.

## Następny etap
D34 — World Content Pack II: rozbudowa pierwszego obszaru do 50–100 ręcznie dopracowanych lokacji z kategoriami: bramy, rynek, garnizon, zaułki, warsztaty, karczma, magazyny i kapliczka.
