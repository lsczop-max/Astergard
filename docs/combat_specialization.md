# D36 Combat Specialization Framework

To jest wyłącznie warstwa danych i walidacji przygotowująca przyszły system walki oparty na specjalizacjach.

## Cel

- zastąpić model uniwersalnych umiejętności modelem trwałych specjalizacji;
- wymusić limity wyboru na poziomie systemu;
- zachować pełną zgodność z obecnym systemem, bez wdrażania nowych zasad walki.

## Zakres

Framework obejmuje:

- specjalizacje broni;
- specjalizacje obrony;
- dodatkowe umiejętności wspierające;
- model trzech etapów nauki;
- loadout z walidacją limitów;
- serializację i odczyt danych.

## Limity

- maksymalnie 2 specjalizacje broni;
- maksymalnie 2 specjalizacje obrony;
- maksymalnie 4 umiejętności dodatkowe.

Walidacja limitów odbywa się w modelu danych, a nie w mechanice walki.

## Specjalizacje broni

Zdefiniowane są następujące specjalizacje:

- miecze;
- szable;
- sztylety;
- topory;
- młoty;
- buławy;
- włócznie;
- halabardy;
- cepy;
- kije bojowe.

Każda definicja posiada:

- `id`;
- `name`;
- `description`;
- `techniques` jako pusta lista startowa;
- `master_trainers` jako pusta lista startowa;
- `allowed_actions` jako pusta lista startowa;
- `future_balance` jako miejsce na przyszłe reguły równoważenia.

## Specjalizacje obrony

Zdefiniowane są:

- tarcze;
- parowanie;
- uniki.

Każda definicja posiada:

- `id`;
- `name`;
- `description`;
- `techniques` jako miejsce na przyszłe techniki.

## Aktywny styl obrony

Warstwa D45 dodaje `active_defense_style` jako domenową preferencję postaci.

Mapowanie:

- `uniki` → `DODGE`;
- `parowanie` → `PARRY`;
- `tarcze` → `SHIELD`.

Styl jest wybierany przez postać, ale nadal wymaga posiadania odpowiedniej specjalizacji i zgodnego stanu wyposażenia. Tryb legacy pozostaje wyłącznie dla starszych zapisów.

## Umiejętności dodatkowe

Framework przewiduje dodatkowe umiejętności, na przykład:

- tropienie;
- zielarstwo;
- targowanie;
- pierwsza pomoc;
- orientacja;
- garbarstwo;
- kowalstwo;
- skradanie;
- otwieranie zamków;
- pułapki;
- wspinaczka;
- pływanie.

Każda umiejętność ma trzy etapy nauki:

- `trainer` 0-30%;
- `academy` 30-60%;
- `master` 60-100%.

To jest wyłącznie model danych. Nie ma jeszcze NPC-trenerów ani mechaniki awansu.

## Loadout

`CombatSpecializationLoadout` przechowuje:

- `weapon_specializations`;
- `defense_specializations`;
- `additional_skills`.

Model posiada:

- `to_dict()`;
- `from_dict()`;
- `validate()`.

## Walidacja

System odrzuca:

- przekroczenie limitu dwóch broni;
- przekroczenie limitu dwóch obron;
- przekroczenie limitu czterech umiejętności dodatkowych;
- powtórzenia tej samej specjalizacji w jednym koszyku;
- nieznane identyfikatory.

## Zgodność z obecnym systemem

Obecny system umiejętności i walka nie zostały usunięte ani zmienione.

Nowy framework działa obok starego i może być podłączony później do:

- tworzenia postaci;
- rozwoju postaci;
- kosztów treningu;
- mechaniki walki.

Aktywny styl obrony z D45 korzysta z tego samego katalogu specjalizacji obronnych, ale dodaje wyłącznie warstwę preferencji, nie nowe specjalizacje.

## Kolejne etapy

W przyszłości można dodać:

- techniki dla specjalizacji broni;
- techniki dla obrony;
- trenerów mistrzowskich;
- reguły kosztów i progresji;
- integrację z istniejącym systemem walki.

Etap technik opisuje osobny dokument: [combat_techniques.md](combat_techniques.md).

Etap nauki technik i specjalizacji opisuje osobny dokument: [combat_learning.md](combat_learning.md).
