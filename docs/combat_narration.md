# Combat Narration

## Cel

Warstwa narracji renderuje wynik walki na podstawie danych strukturalnych.
Nie zgaduje wyniku z tekstu i nie wykonuje logiki domenowej.

## Wejścia

Narrator może korzystać z:

- `CombatEvent`
- `CombatOutcome`
- `DefenseOutcome`
- `HitLocationOutcome`
- `ArmorCoverageOutcome`

## Lokalizacja i pancerz

Od D52 narracja może opisywać:

- konkretną część ciała,
- grupę lokalizacji,
- osłonę pancerza,
- fakt, że trafienie uderzyło w aktywny element wyposażenia.

Nie pokazuje technicznych procentów, identyfikatorów profili ani numerów warstw.
Narrator korzysta z lokalizacji przekazanej w `CombatEvent` / `CombatOutcome` i nie losuje jej ponownie.

## Ograniczenia

- narracja nie zmienia rozstrzygnięć,
- nie ujawnia surowych danych diagnostycznych,
- nie wykonuje reakcji ani kolejnych akcji,
- pozostaje kompatybilna z wcześniejszymi komunikatami.
