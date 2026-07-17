# D37 Combat Techniques Framework

Ten etap rozszerza framework specjalizacji bojowych o techniki walki, ale nie uruchamia ich w resolverze walki.

## Różnica między klasą broni a specjalizacją

- `WeaponClass` to szeroka kategoria fizyczna broni.
- Specjalizacja broni to konkretna ścieżka treningu, np. `miecze` albo `sztylety`.
- Technika może wymagać klasy, specjalizacji albo obu naraz.

Klasa nie odblokowuje techniki sama z siebie.

## Model techniki

`CombatTechnique` zawiera:

- `id`
- `name`
- `description`
- `required_weapon_classes`
- `required_weapon_specializations`
- `required_defense_specializations`
- `required_skill_percent`
- `required_skill_source`
- `enabled`
- `stamina_cost`
- `cooldown_seconds`

Pola `stamina_cost` i `cooldown_seconds` są przygotowane na przyszłość i nie wpływają jeszcze na walkę.

## Źródło poziomu

`required_skill_source` wskazuje, z którego obszaru pobierany jest poziom:

- `WEAPON_SPECIALIZATION`
- `DEFENSE_SPECIALIZATION`

To pozwala odróżnić techniki oparte na ataku od technik opartych na obronie, bez kodowania wyjątków po `id`.

## Dane technik

Techniki są definiowane w JSON:

- `astergard/data/combat_techniques.json`

Loader:

- wczytuje katalog,
- sprawdza wymagane pola,
- odrzuca nieznane klasy broni,
- odrzuca nieznane specjalizacje,
- odrzuca progi spoza zakresu `0-100`,
- odrzuca duplikaty identyfikatorów,
- zwraca niemutowalny katalog.

## Walidacja użycia

`can_use_technique(profile, technique)` zwraca `TechniqueEligibilityResult` z polami:

- `allowed`
- `reason_code`
- `message`

Walidator sprawdza:

- czy technika jest włączona,
- czy postać ma aktywną broń,
- czy aktywna broń odpowiada wymaganej klasie,
- czy aktywna specjalizacja jest zgodna z techniką,
- czy postać zna wymagane specjalizacje,
- czy poziom odpowiedniej umiejętności jest wystarczający.

Nie sprawdza:

- staminy,
- cooldownu,
- stanu walki,
- celu,
- zasięgu,
- obrażeń,
- losowania powodzenia.

## Macierz pierwszych technik

| Technika | Klasy | Wymagana specjalizacja | Źródło poziomu |
|---|---|---|---|
| Riposta | LIGHT, MEDIUM | miecze, szable, sztylety | DEFENSE_SPECIALIZATION |
| Rozbrojenie | LIGHT, MEDIUM, POLEARM | miecze, szable, włócznie, halabardy | WEAPON_SPECIALIZATION |
| Ogłuszenie | HEAVY | młoty, buławy, cepy | WEAPON_SPECIALIZATION |
| Przełamanie gardy | MEDIUM, HEAVY, POLEARM | topory, młoty, halabardy | WEAPON_SPECIALIZATION |
| Przebicie pancerza | MEDIUM, HEAVY, POLEARM | topory, młoty, włócznie, halabardy | WEAPON_SPECIALIZATION |
| Kontratak | LIGHT, MEDIUM | miecze, szable, sztylety | DEFENSE_SPECIALIZATION |

## Ograniczenia obecnego etapu

- techniki nie wykonują jeszcze akcji w walce,
- nie zmieniają obrażeń,
- nie wpływają na AI,
- nie pobierają staminy,
- nie mają cooldownów w logice gry,
- nie dodają NPC-trenerów,
- nie wymagają zmian schematu bazy danych.

Techniki takie jak `riposte` i `counterattack` są przygotowane również pod warstwę reakcji bojowych, ale w tym etapie pozostają jedynie danymi możliwymi do sprawdzenia przez `CombatReactionCatalog`.

## D48

`riposte` jest pierwszą techniką, która może zostać automatycznie wykonana jako osobna reakcja po udanym parowaniu. Sama technika nadal nie zmienia wzorów walki i nie dodaje balansu poza istniejącymi danymi.

## Następny etap

W przyszłości można podłączyć:

- faktyczne wykonanie techniki,
- koszty zasobów,
- cooldowny,
- animację i narrację walki,
- integrację z AI przeciwnika,
- warstwę reakcji po `CombatOutcome`.
