# Explicit Defense Resolution

## Cel

Ta warstwa wydziela obronę jako jawny, typowany i testowalny wynik procesu bojowego.
Nie zmienia balansu i nie dodaje nowych opcji gracza.
Od D47 sama obrona jest wybierana dynamicznie z kandydatów, a nie ręcznie przez aktywny styl.

## Chybienie a obrona

- `MISS` oznacza nieudane dojście akcji do skutku bez skutecznej obrony.
- `DEFENDED` oznacza, że akcja została zatrzymana przez jedną z obron.
- `HIT` oznacza, że obrona nie zatrzymała akcji.

W obecnym etapie rozstrzygnięcie obrony jest jawne w danych, ale kolejność i progi pozostają zgodne z dotychczasowym resolverem.

## Modele

### `DefenseAttempt`

Pojedyncza próba obrony.

Pola:

- `defense_type`
- `available`
- `attempted`
- `success`
- `chance`
- `roll`
- `reason_code`

### `DefenseOutcome`

Wynik całego procesu obrony.

Pola:

- `resolution`
- `successful_defense`
- `attempts`
- `selected_defense`
- `reason_code`

## Kolejność prób

Obecny przepływ zachowuje dotychczasową kolejność legacy:

```text
test trafienia
  ↓
dodge / hit comparison
  ↓
shield block
  ↓
parry
  ↓
brak skutecznej obrony
```

Jeżeli pierwsza obrona powiedzie się, kolejne nie są wykonywane.

W historycznym trybie legacy postać bez aktywnego stylu mogła korzystać z kolejności:

```text
unik
  ↓
tarcza
  ↓
parowanie
```

W obecnej architekturze D47 obrona jest wybierana dynamicznie z kandydatów, a `active_defense_style` pozostaje jedynie polem zgodności historycznej.

## Dostępność

- Unik: dostępny, jeśli postać żyje.
- Tarcza: dostępna, jeśli postać ma aktywnie wyposażoną tarczę. W walce broń dwuręczna wyłącza tarczę z rozstrzygnięcia, nawet jeśli slot nadal istnieje.
- Parowanie: dostępne, jeśli postać ma aktywnie wyposażoną broń, a jej profil bojowy ma tag `parry_capable`. Broń legacy bez profilu zachowuje dotychczasową kompatybilność.

Aktywa z inventory nie są traktowane jako aktywne wyposażenie.

W D47 dostępność i skuteczność obrony wynikają z kandydatów wyliczanych z:

- umiejętności,
- profilu pancerza,
- profilu broni,
- profilu tarczy,
- sytuacji walki.

## Integracja z `CombatOutcome`

`CombatOutcome` zawiera:

- `defense_result`
- `defense_outcome`

Oba pola są spójne i opisują ten sam wynik.

## Integracja z narracją

`CombatNarrator.render_outcome(...)` otrzymuje jawny wynik obrony i wybiera odpowiedni komunikat dla:

- chybienia,
- uniku,
- parowania,
- bloku tarczą.

Narrator nie odtwarza obrony z tekstu.

## Ograniczenia

Na tym etapie:

- nie ma riposty,
- nie ma kontrataku,
- nie ma automatycznego wyboru najlepszej obrony,
- dostępność parowania zależy od profilu broni,
- legacy weapons zachowują kompatybilność,
- aktywny styl obrony jest deprecated i nie wpływa na resolver,
- nie zmieniono balansu.

## Przyszłe punkty integracji

Ta warstwa stanowi punkt wejścia dla:

- riposty,
- przełamania gardy,
- technik reagujących na obronę,
- świadomego wyboru stylu obrony przez gracza.

## Warstwa reakcji D46

Po powstaniu `CombatOutcome` osobna warstwa reakcji może ocenić, czy wynik otwiera reakcję bojową:

```text
CombatOutcome
  ↓
ReactionTriggerContext
  ↓
ReactionResolver
  ↓
CombatReactionDiscovery
```

Ta warstwa nie należy do `DefenseResolver`. Obrona pozostaje odpowiedzialna wyłącznie za chybienie, unik, parowanie i blok tarczą. Reakcja jest kolejnym, późniejszym etapem opartym na gotowym wyniku obrony.

### Automatyczna riposta D48

Jeżeli `DefenseOutcome` wskazuje udane parowanie, warstwa reakcji może natychmiast zbudować osobny `CombatAction` riposty. Riposta nie zmienia samej obrony i nie należy do `DefenseResolver`.
