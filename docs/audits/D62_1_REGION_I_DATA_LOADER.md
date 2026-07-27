# D62.1 - Region I data loader audit

## Cel

Przygotować kanoniczny runtime asset Regionu I bez aktywowania nowej topologii
w `WorldManager.generate_world()`.

## Wykonane kroki

- Przeniesiono źródłowy JSON do `astergard/world/data/region_i.json`.
- Zaktualizowano `docs/maps/region_i_import/README_IMPORT.md`, aby wskazywał
  kanoniczną lokalizację runtime assetu.
- Dodano loader i walidator w `astergard/world/region_i_loader.py`.
- Dodano testy pokrywające:
  - liczbę lokacji,
  - liczbę połączeń,
  - zbiór ID,
  - brak brakujących ID,
  - start w pokoju 14,
  - osiągalność całej mapy,
  - normalizację kierunków,
  - brak wpływu na aktywny world runtime.

## Walidacje

- ID lokacji są unikalne.
- Współrzędne są unikalne.
- Krawędzie mają znane kierunki.
- `reverseDirection` jest zgodny z kierunkiem runtime.
- `bidirectional` jest wymagane i musi mieć wartość `true`.
- Wszystkie końce krawędzi wskazują na istniejące pokoje.
- Cała mapa jest osiągalna z pokoju 14.

## Nierozstrzygnięte decyzje projektowe

- Nie dodano jeszcze starych połączeń granicznych do pokoi `187`, `190`,
  `195`, `200`, `210` ani `335`.
- Integracja loadera z `WorldManager.generate_world()` została celowo
  odroczona.
- Migracja zapisów graczy i snapshotów świata pozostaje osobnym etapem.

## Uwagi

Ten etap przygotowuje wyłącznie kanoniczny asset i walidację formatu.
Nie zmienia NPC, contentu, questów, ekonomii ani aktywnego generatora świata.
