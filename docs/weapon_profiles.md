# Weapon Profiles

## Cel

Warstwa profili broni oddziela trzy rzeczy, które wcześniej były zlepione w jednym modelu:

- specjalizację postaci,
- konkretny przedmiot,
- właściwości bojowe tego przedmiotu.

Specjalizacja nadal opisuje, czego postać się nauczyła. Profil broni opisuje, jak zachowuje się konkretny egzemplarz wyposażenia. Przedmiot jest nośnikiem profilu, ale nie jest z nim tożsamy.

## Struktura profilu

Każdy profil ma:

- `id`
- `name`
- `specialization_id`
- `weapon_class`
- `tags`
- `hand_requirement`
- `damage_types`
- `base_speed`
- `base_accuracy`
- `base_damage`
- `armor_penetration`
- `reach`
- `enabled`

Pola liczbowe są przygotowaniem pod przyszły balans. Na etapie D44 nie zmieniają obrażeń, trafienia ani kolejności akcji.

## Klasy broni

- `LIGHT`
- `MEDIUM`
- `HEAVY`
- `POLEARM`

Klasa broni jest klasyfikacją techniczną. Nie zastępuje specjalizacji postaci i nie mówi sama w sobie, czy broń nadaje się do parowania.

## Wymagania rąk

- `ONE_HANDED`
- `TWO_HANDED`
- `VERSATILE`

`TWO_HANDED` blokuje współistnienie z tarczą w rozstrzygnięciu walki.
`VERSATILE` przygotowuje przyszłe przełączanie chwytu, ale na obecnym etapie nie wprowadza nowej mechaniki.

## Katalog profili

Katalog jest wczytywany z:

- `astergard/data/weapon_profiles.json`

Loader:

- waliduje klasy,
- waliduje specjalizacje,
- waliduje tagi,
- waliduje typy obrażeń,
- wykrywa zduplikowane identyfikatory,
- zwraca bezpieczny katalog tylko do odczytu.

## Legacy compatibility

Stare przedmioty bez `weapon_profile_id` pozostają grywalne.

Polityka kompatybilności jest celowo konserwatywna:

- brak profilu nie wywraca walki,
- brak profilu nie blokuje parowania,
- brak profilu nie zmienia istniejącego balansu,
- brak profilu nie wymusza zgadywania tagów z nazwy przedmiotu.

Taki przedmiot jest traktowany jako legacy weapon.

## Integracja z `CombatAction`

`CombatAction` przechowuje tylko snapshot:

- `weapon_profile_id`
- `weapon_tags`
- `hand_requirement`

Akcja nie przechowuje całego mutowalnego obiektu profilu.

## Integracja z obroną

Parowanie zależy od profilu:

- profile z tagiem `parry_capable` mogą wspierać parry,
- profile bez tego tagu nie mogą,
- legacy weapons zachowują dotychczasową kompatybilność.

Tarcza nadal działa przez własny slot wyposażenia, ale broń dwuręczna wyłącza ją z rozstrzygnięcia obrony.

## Reprezentatywne profile startowe

Pierwszy katalog zawiera profile dla:

- mieczy
- szabel
- sztyletów
- toporów
- młotów
- buław
- włóczni
- halabard
- cepów
- kijów bojowych

To są profile reprezentatywne, nie pełny słownik wszystkich historycznych odmian uzbrojenia.

## Ograniczenia bieżącego etapu

Na tym etapie:

- nie używamy jeszcze szybkości profilu,
- nie używamy jeszcze penetracji,
- nie używamy jeszcze zasięgu,
- nie zmieniamy obrażeń,
- nie zmieniamy trafienia,
- nie zmieniamy pancerza,
- nie zmieniamy ran.

## Kierunek dalszy

Warstwa profili jest przygotowaniem pod:

- ripostę,
- techniki zależne od tagów,
- rozróżnienie typów obrażeń,
- przyszły balans wyłącznie danymi,
- dalsze ograniczenie aktywnej obrony do konkretnych profili broni.
