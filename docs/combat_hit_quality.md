# Combat Hit Quality

## Cel

Jakość trafienia określa, jak dobrze udany atak został przeprowadzony.
To nie jest jeszcze osobny krytyk ani losowy mnożnik obrażeń.

## Poziomy

- `GLANCING`
- `CLEAN`
- `POWERFUL`
- `DEVASTATING`

## Znaczenie

- `GLANCING` przesuwa rozkład w stronę kończyn i powierzchownych stref,
- `CLEAN` pozostaje neutralne,
- `POWERFUL` lekko wzmacnia strefy centralne,
- `DEVASTATING` mocniej przesuwa rozkład ku kluczowym rejonom, ale nie gwarantuje głowy ani szyi.

## Ograniczenia

- jakość trafienia nie daje jeszcze krytycznej rany sama z siebie,
- nie zmienia balansu obrażeń,
- nie jest osobnym źródłem losowego sukcesu,
- jest wejściem dla lokalizacji trafienia i przyszłych efektów,
- nie losuje lokalizacji ponownie po jej ustaleniu przez `HitLocationOutcome`.
