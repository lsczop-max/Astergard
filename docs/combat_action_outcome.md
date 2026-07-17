# Combat Action and Outcome

## Cel

`CombatAction` i `CombatOutcome` są kanonicznymi, typowanymi modelami pojedynczej akcji bojowej.
Oddzielają intencję od rozstrzygnięcia:

- `CombatAction` opisuje, co aktor próbuje zrobić.
- `CombatOutcome` opisuje, co faktycznie wydarzyło się po rozstrzygnięciu.

Oba modele są czystymi strukturami danych.
Nie emitują eventów, nie modyfikują stanu świata i nie generują narracji.

Od D48 pojedyncza technika reakcyjna, taka jak riposta, jest reprezentowana jako osobny `CombatAction` z własnym `action_id` i `parent_action_id`.

## Różnica między intencją, akcją i wynikiem

Warstwa walki rozróżnia trzy poziomy:

1. `CombatIntent`
   - przyszły, jeszcze nie wdrożony poziom zamiaru taktycznego;
   - może określać chęć ataku, ucieczki lub użycia techniki.

2. `CombatAction`
   - konkretna, kanoniczna akcja przekazana do resolvera;
   - zawiera identyfikatory stron, typ akcji, aktywną broń i opcjonalne metadane;
   - nie zmienia świata.

3. `CombatOutcome`
   - wynik rozstrzygnięcia;
   - zawiera informację o trafieniu, obronie, obrażeniach, celu, końcu walki i kodzie przyczyny;
   - nie zmienia świata.

## `CombatAction`

Minimalna struktura:

- `action_id`
- `actor_id`
- `target_id`
- `action_type`
- `weapon_id`
- `weapon_specialization_id`
- `technique_id`
- `metadata`

### Znaczenie pól

- `action_id` służy do korelacji logów, eventów i diagnostyki.
- `actor_id` i `target_id` używają tożsamości bojowej, nie samej nazwy.
- `action_type` jest rozszerzalny, ale obecnie podstawowy przepływ używa `BASIC_ATTACK`.
- `action_type` rozróżnia także działania reakcyjne, np. `REACTION`.
- `weapon_id` wskazuje aktywnie wyposażony przedmiot.
- `weapon_specialization_id` jest przygotowane pod późniejsze techniki.
- `technique_id` pozostaje `None` dla zwykłych ataków.
- `metadata` jest opcjonalne i nie zastępuje właściwych pól modelu.

### Pola reakcyjne

- `parent_action_id` wskazuje źródłową akcję, która uruchomiła reakcję.
- `reaction_id` koreluje reakcję z odkryciem reakcji.
- `reaction_depth` zabezpiecza przed pętlami reakcji.

### Tworzenie

Kanoniczny builder:

- pobiera aktora i cel,
- odczytuje aktywnie wyposażoną broń,
- ustala identyfikatory bojowe,
- zwraca niemutowalny `CombatAction`.

Nie wykonuje rzutu trafienia i nie zmienia stanu walki.

## `CombatOutcome`

Minimalna struktura:

- `action_id`
- `actor_id`
- `target_id`
- `result_type`
- `hit`
- `defense_result`
- `damage`
- `hit_location`
- `wound_ids`
- `effect_ids`
- `target_defeated`
- `combat_ended`
- `reason_code`

### Znaczenie pól

- `result_type` rozróżnia trafienie, chybienie, obronę, brak celu i pokonanie celu.
- `hit` wskazuje, czy atak faktycznie doszedł do skutku.
- `defense_result` przechowuje wynik obrony bez zgadywania przyszłych technik.
- `damage` jest końcową wartością po obecnych modyfikatorach.
- `hit_location` przechowuje autorytatywną lokalizację trafienia.
- `body_location` i `body_location_group` przechowują jawny, szczegółowy wynik lokalizacji trafienia.
- `legacy_body_part` jest deterministycznym adapterem przejściowym dla starego systemu ran i wyposażenia.
- `hit_quality` opisuje jakość trafienia używaną przez kolejne warstwy resolvera.
- `armor_coverage_outcome` i `armor_layers` opisują lokalne pokrycie pancerzem bez zmiany balansu obrażeń.
- `wound_ids` i `effect_ids` są przygotowane pod przyszłe rozwinięcia.
- `target_defeated` opisuje realny stan po akcji.
- `combat_ended` sygnalizuje zakończenie walki, ale nie implikuje jednego konkretnego powodu.
- `reason_code` służy do czytelnych odmów i stanów błędnych.
- `defense_outcome` przechowuje jawny wynik obrony, a od D48 osobna warstwa reakcji może z niego zbudować kolejną akcję.

## Przepływ gracza

Docelowo i obecnie kompatybilnie:

```text
zabij
  ↓
walidacja celu
  ↓
kanoniczne rozpoczęcie walki
  ↓
CombatAction
  ↓
istniejący resolver
  ↓
CombatOutcome
  ↓
eventy i narracja
```

W praktyce `zabij` nadal korzysta z istniejącego resolvera, ale teraz zawsze przechodzi przez strukturalną akcję i wynik.

## Przepływ NPC

NPC korzysta z tego samego punktu rozstrzygnięcia:

```text
heartbeat
  ↓
CombatAction
  ↓
istniejący resolver
  ↓
CombatOutcome
  ↓
eventy i narracja
```

Różnica dotyczy tylko źródła zamiaru i wyboru celu.
Nie ma osobnego wzoru obrażeń dla NPC.

## Granice odpowiedzialności

- `CombatAction` opisuje zamiar.
- `CombatOutcome` opisuje rezultat.
- `CombatManager` nadal posiada logikę rozstrzygającą.
- `CombatNarrator` otrzymuje dane strukturalne i renderuje komunikat.
- eventy opisują faktyczne skutki, nie samą konstrukcję akcji.
- `HitLocationOutcome.location` jest źródłem prawdy dla lokalizacji trafienia; legacy body part jest tylko mapowaniem przejściowym.

## Kompatybilność ze starym API

Stare wywołania pozostają obsługiwane:

- publiczne komendy działają jak dotąd,
- heartbeat działa jak dotąd,
- AI działa jak dotąd,
- narracja pozostaje kompatybilna z istniejącym interfejsem.

Nowe modele są dodane obok starej ścieżki, nie zamiast niej.

## Ograniczenia

Obecny etap nie obejmuje:

- technik,
- nowych typów akcji bojowych w logice walki,
- pancerza jako osobnego resolvera,
- ran jako osobnego resolvera,
- staminy,
- cooldownów,
- frontu i tyłu,
- taktyki AI.

## Przygotowanie do D43

Ten etap tworzy stabilny punkt wejścia dla kolejnych warstw:

- jawnej obrony,
- profili broni,
- efektów technik,
- bardziej strukturalnej narracji,
- rozdzielenia resolvera na mniejsze odpowiedzialności, jeśli będzie to później potrzebne.

## D48

Po `CombatOutcome` warstwa reakcji może utworzyć osobny `CombatAction` dla riposty i przepuścić go ponownie przez ten sam resolver. Dzięki temu akcja reakcyjna i jej wynik pozostają odrębne od pierwotnego ataku.
