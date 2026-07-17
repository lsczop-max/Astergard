# Combat Armor Coverage

## Cel

Pokrycie pancerza określa, które aktywnie założone elementy chronią konkretną lokalizację trafienia.
To warstwa diagnostyczna i przygotowawcza. Nie zmienia jeszcze redukcji obrażeń.
Wejściem do tej warstwy jest już rozstrzygnięta lokalizacja z `HitLocationOutcome.location`. Resolver nie wybiera lokalizacji ponownie.

## Model

### `ArmorCoverageProfile`

Profil opisujący, jak dany element wyposażenia chroni ciało:

- `covered_locations`
- `coverage_fraction`
- `layer_order`
- `armor_material`
- `armor_category`

### `ArmorLayerSnapshot`

Snapshot aktywnej warstwy pancerza:

- `item_id`
- `profile_id`
- `material`
- `armor_category`
- `coverage_fraction`
- `layer_order`
- `condition`

### `ArmorCoverageOutcome`

Wynik pokrycia dla pojedynczej lokalizacji:

- `body_location`
- `covering_layers`
- `fully_unarmored`
- `partial_coverage`
- `total_coverage_indicator`

## Zasady

- liczy się wyłącznie aktywnie wyposażony pancerz,
- przedmioty w inventory nie chronią,
- częściowe pokrycie działa probabilistycznie z użyciem RNG,
- wiele warstw jest zachowywanych w kolejności warstw,
- stan wyposażenia jest rejestrowany, ale nie zmienia jeszcze redukcji obrażeń.

## Ograniczenia

- nie ma jeszcze pełnej penetracji,
- nie ma rozpadu warstw,
- nie ma redukcji obrażeń zależnej od konkretnej lokalizacji,
- `total_coverage_indicator` jest wskaźnikiem diagnostycznym, nie finalną redukcją.
