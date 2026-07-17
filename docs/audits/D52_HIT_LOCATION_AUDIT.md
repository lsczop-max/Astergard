# D52 Hit Location Audit

## Stan etapu

Wprowadzono jawny model lokalizacji trafień oraz lokalne pokrycie pancerza.
Warstwa działa obok istniejącego resolvera obrażeń i nie zmienia balansu.

## Co zostało dodane

- `BodyLocation`
- `BodyLocationGroup`
- `HitQuality`
- `HitLocationOutcome`
- `ArmorCoverageProfile`
- `ArmorLayerSnapshot`
- `ArmorCoverageOutcome`
- loader danych lokalizacji trafień
- loader danych pokrycia pancerza

## Integracja

- skuteczny atak otrzymuje lokalizację trafienia,
- skuteczna obrona i chybienie nie tworzą lokalizacji,
- aktywnie wyposażony pancerz jest wykrywany lokalnie,
- inventory-only nie chroni,
- reakcja riposty odziedziczyła ten sam pipeline.

## Ograniczenia

- brak pełnej penetracji,
- brak lokalnej redukcji obrażeń,
- brak krytycznych ran zależnych od lokalizacji,
- brak celowanych ataków.

## Uwagi

Etap jest przygotowaniem pod D53, gdzie lokalizacja i pokrycie mają zacząć wpływać na fizyczny wynik ciosu.
