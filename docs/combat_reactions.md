# Combat Reactions Framework

## Cel

Warstwa reakcji bojowych jest osobnym etapem po `CombatOutcome`. Nie jest częścią obrony, nie wykonuje ataku i nie modyfikuje świata. Jej zadaniem jest ustalenie, czy wynik walki otwiera możliwość reakcji takiej jak riposta.

## Obrona a reakcja

- Obrona rozstrzyga, czy atak został uniknięty, sparowany lub zatrzymany tarczą.
- Reakcja sprawdza, czy gotowy wynik obrony może uruchomić dalsze działanie.
- Technika jest dopiero potencjalnym źródłem reakcji, a nie samą reakcją.

## Modele

### `CombatReactionType`

- `RIPOSTE`
- `COUNTERATTACK`
- `SHIELD_RESPONSE`
- `DODGE_RESPONSE`
- `CUSTOM`

### `ReactionTriggerType`

- `SUCCESSFUL_PARRY`
- `SUCCESSFUL_DODGE`
- `SUCCESSFUL_SHIELD_BLOCK`
- `ATTACK_MISSED`
- `ACTOR_HIT`
- `ACTOR_WOUNDED`
- `TARGET_DEFEATED`

### `CombatReactionDefinition`

Definicja reakcji jest danymi. Zawiera:

- `id`
- `name`
- `reaction_type`
- `trigger_types`
- `required_technique_id`
- `required_defense_style`
- `required_weapon_tags`
- `required_weapon_specializations`
- `enabled`
- `priority`
- `consumes_reaction_window`

### `CombatReaction`

Strukturalny opis potencjalnej reakcji. Zawiera identyfikator źródłowej akcji, identyfikator reagującego, typ reakcji i typ wyzwalacza.

### `ReactionUserProfile`

Lekki, niemutowalny profil potrzebny do sprawdzenia reakcji. Nie zastępuje pełnego obiektu postaci.

### `ReactionTriggerContext`

Kontekst zbudowany z:

- `source_action`
- `source_outcome`
- `reactor_profile`
- opcjonalnie `opponent_profile`

### `ReactionWindow`

Krótki stan runtime chroniący przed wielokrotnym użyciem tego samego wyniku.

### `CombatReactionDiscovery`

Wynik analizy reakcji. Zawiera:

- `source_action_id`
- `available_reactions`
- `reaction_window`

## Katalog danych

Reakcje są definiowane w:

- `astergard/data/combat_reactions.json`

Loader waliduje:

- typy reakcji,
- typy wyzwalaczy,
- style obrony,
- tagi broni,
- techniki,
- duplikaty identyfikatorów.

## Wyzwalacze

W D46 obsługiwany jest przede wszystkim `SUCCESSFUL_PARRY`. To właśnie ten wynik może ujawnić dostępność riposty.

## Walidacja

`find_available_reactions(context, catalog)` sprawdza:

- spójność źródłowej akcji i wyniku,
- czy wynik odpowiada wyzwalaczowi,
- czy reagujący żyje,
- czy pozostaje w walce,
- czy zna wymaganą technikę,
- czy ma właściwy aktywny styl,
- czy aktywna broń ma wymagane tagi,
- czy posiada wymaganą specjalizację,
- czy reakcja jest włączona.

## Okno reakcji

Reakcje działają w krótkim oknie runtime. Limit głębokości reakcji wynosi obecnie `1`, co zabezpiecza przed pętlą typu:

```text
atak -> riposta -> riposta na ripostę -> ...
```

## Ograniczenia obecnego etapu

- brak wykonania riposty,
- brak dodatkowego ataku,
- brak obrażeń z reakcji,
- brak kosztów i cooldownów,
- brak automatycznej kolejki reakcji,
- brak serializacji okna reakcji.

## D48

W D48 riposta stała się pierwszą wykonywaną reakcją. Po wykryciu dostępnej riposty manager może zbudować osobny `CombatAction`, przepuścić go przez zwykły resolver i otrzymać osobny `CombatOutcome`. Warstwa reakcji nadal nie jest częścią `DefenseResolver`.

## Przyszłe użycie

Warstwa reakcji jest przygotowana pod:

- ripostę,
- kontratak,
- reakcje tarczowe,
- reakcje po uniku,
- późniejsze reakcje szkół i profesji.
