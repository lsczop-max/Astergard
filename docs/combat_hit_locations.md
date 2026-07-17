# Combat Hit Locations

## Cel

Warstwa lokalizacji trafień rozdziela ogólne "trafienie" od konkretnej części ciała.
Nie zmienia obrażeń ani ran. Dostarcza strukturalny wynik, który może później zasilać pancerz, narrację i kolejne etapy systemu urazów.

## Model

### `BodyLocation`

Drobna, ale nadal zarządzalna lokalizacja trafienia:

- `HEAD`
- `NECK`
- `CHEST`
- `ABDOMEN`
- `BACK`
- `LEFT_SHOULDER`
- `RIGHT_SHOULDER`
- `LEFT_ARM`
- `RIGHT_ARM`
- `LEFT_HAND`
- `RIGHT_HAND`
- `LEFT_THIGH`
- `RIGHT_THIGH`
- `LEFT_LEG`
- `RIGHT_LEG`
- `LEFT_FOOT`
- `RIGHT_FOOT`

### `BodyLocationGroup`

Grupa lokalizacji używana do szerszych reguł:

- `HEAD_GROUP`
- `TORSO_GROUP`
- `ARM_GROUP`
- `HAND_GROUP`
- `LEG_GROUP`
- `FOOT_GROUP`

## Resolver

`HitLocationResolver` korzysta z:

- profilu aktywnej broni,
- typu ataku,
- jakości trafienia,
- kontrolowanego RNG.

Wyjściem jest `HitLocationOutcome` z lokalizacją, grupą, wagami i kodem przyczyny.

`HitLocationOutcome.location` jest jedynym autorytatywnym wynikiem lokalizacji trafienia. Runtime walki nie losuje tej informacji ponownie. Starszy model ran korzysta z centralnego adaptera `BodyLocation -> legacy body part`, który jest tylko przejściowy.

Przejściowy adapter jest jawny: `legacy_body_part_for_location()`.

## Zasady

- trafienie zawsze ma jedną lokalizację,
- chybienie i skuteczna obrona nie mają lokalizacji trafienia,
- wysoka jakość tylko przesuwa rozkład, nie gwarantuje głowy,
- profile ataku preferują różne obszary ciała,
- rozkład jest danymi, nie rozgałęzieniami logiki.

## Ograniczenia

- lokalizacja nie wpływa jeszcze na obrażenia,
- nie ma celowanych ataków,
- nie ma punktów krytycznych opartych o samą lokalizację,
- grupa lokalizacji jest przygotowaniem pod przyszłe efekty ran.
