# Dynamic Defense

## Cel

Warstwa dynamicznej obrony wybiera automatycznie najlepszą dostępną odpowiedź na atak na podstawie:

- wyuczonych specjalizacji obronnych,
- aktywnego wyposażenia,
- profilu pancerza,
- profilu broni,
- aktualnego stanu postaci i sytuacji walki.

Nie używa już ręcznie wybieranego stylu obrony jako źródła decyzji resolvera.

## `DefenseCandidate`

Pojedynczy kandydat obrony zawiera:

- `defense_type`
- `learned_skill`
- `equipment_modifier`
- `armor_modifier`
- `situational_modifier`
- `effective_value`
- `available`
- `reason_code`

`effective_value` jest liczony jako:

```text
learned_skill × equipment_modifier × armor_modifier × situational_modifier
```

## Profile

### Profil pancerza

`ArmorProfile` dostarcza mnożniki dla:

- uniku,
- bloku,
- parowania.

### Profil broni

`WeaponProfile` dostarcza między innymi:

- `parry_modifier`
- tagi broni
- wymagania rąk

### Profil tarczy

`ShieldProfile` dostarcza:

- `block_modifier`

## Kolejność rozstrzygania

Resolver buduje kandydatów, sortuje ich malejąco po `effective_value`, a następnie rozpatruje ich jeden po drugim.

Jeżeli pierwsza obrona się uda, kolejne nie są sprawdzane.

## Legacy

`active_defense_style` pozostaje wyłącznie polem zgodności historycznej. Nie wpływa na dynamiczny resolver obrony.

## Przygotowanie pod ripostę

Dynamiczna obrona zwraca jawny `DefenseOutcome`, który może później zasilić warstwę reakcji. Riposta nie należy do samego resolvera obrony.
