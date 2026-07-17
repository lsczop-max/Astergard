# D52.1 Authoritative Hit Location Integration

## Wniosek

`HitLocationOutcome.location` is the single source of truth.

Od D52.1 runtime walki nie losuje lokalizacji drugi raz. Jedno losowanie w `resolve_hit_location()` zasila:

- `CombatOutcome`
- `CombatEvent`
- narrator
- `ArmorCoverageOutcome`
- pipeline ran
- ripostę
- przyszły D53

Stary wybór części ciała pozostaje tylko jako adapter zgodnościowy dla systemu ran i części legacy API.

## Poprzedni podwójny przepływ

```text
HitLocationResolver.resolve()
  -> CombatOutcome / event / narrator / armor
legacy choose_body_part()
  -> wounds / armor_for / legacy compatibility
```

## Nowy pojedynczy przepływ

```text
resolve_hit_location()
  -> HitLocationOutcome.location
  -> CombatOutcome.hit_location
  -> CombatEvent.hit_location
  -> ArmorCoverageResolver.resolve()
  -> legacy body part adapter
  -> wounds
  -> narrator
```

## Pozostawione użycia `choose_body_part()`

| Plik | Funkcja | Typ | Powód |
| --- | --- | --- | --- |
| `astergard/combat/manager.py` | `choose_body_part()` | legacy API | Zgodność wsteczna dla starych testów i zewnętrznych wywołań. Runtime walki nie używa już tej metody. |
| `tests/test_d39_tactical_combat.py` | monkeypatch `choose_body_part` | legacy test | Testuje starszy kontrakt zachowania. |
| `tests/test_d22_state_machines.py` | monkeypatch `choose_body_part` | legacy test | Zachowuje kompatybilność historycznych scenariuszy. |

## Pozostawione użycia `resolve_hit_location`

| Plik | Funkcja | Typ | Powód |
| --- | --- | --- | --- |
| `astergard/combat/manager.py` | `attack()` | runtime | Jedyny produkcyjny resolver lokalizacji. |
| `tests/test_d52_body_locations_and_armor_coverage.py` | testy lokalizacji | test | Walidacja deterministycznego rozkładu i integracji. |
| `tests/test_d52_1_authoritative_hit_location.py` | testy integralności | test | Potwierdza pojedyncze wywołanie resolvera. |

## Pozostawione użycia `ArmorCoverageResolver.resolve`

| Plik | Funkcja | Typ | Powód |
| --- | --- | --- | --- |
| `astergard/combat/manager.py` | `attack()` | runtime | Rozstrzyga lokalne pokrycie po ustaleniu lokalizacji. |
| `tests/test_d52_body_locations_and_armor_coverage.py` | testy lokalizacji i pokrycia | test | Weryfikacja pokrycia i kolejności warstw. |
| `tests/test_d52_1_authoritative_hit_location.py` | testy integralności | test | Potwierdza brak drugiego losowania lokalizacji. |

## Legacy adapter

Adapter jest centralny i deterministyczny:

- `HEAD`, `NECK` -> `glowa`
- `CHEST`, `ABDOMEN`, `BACK` -> `korpus`
- `LEFT_SHOULDER`, `LEFT_ARM`, `LEFT_HAND` -> `lewa_reka`
- `RIGHT_SHOULDER`, `RIGHT_ARM`, `RIGHT_HAND` -> `prawa_reka`
- `LEFT_THIGH`, `LEFT_LEG`, `LEFT_FOOT` -> `lewa_noga`
- `RIGHT_THIGH`, `RIGHT_LEG`, `RIGHT_FOOT` -> `prawa_noga`

`legacy_body_part_for_location()` nie używa RNG i nie zmienia rozkładu trafień.

## Status matematyki

Nie zmieniono:

- prawdopodobieństw lokalizacji,
- obron,
- obrażeń,
- penetracji,
- ciężkości ran,
- śmierci,
- riposty.

Zmieniło się tylko źródło lokalizacji używane przez dalszy pipeline.
