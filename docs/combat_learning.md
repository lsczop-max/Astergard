# D38 Combat Learning System

Ten etap wprowadza zapis i walidację nauki technik oraz specjalizacji. Nie wykonuje żadnych efektów bojowych.

## Etapy nauki

Umiejętności treningowe są opisane trzema progami:

- `trainer` 0-30%
- `academy` 30-60%
- `master` 60-100%

To jest opis architektury, a nie jeszcze mechanika szkolenia.

## Mistrzowie

Model `MasterTrainer` zawiera:

- `id`
- `name`
- `description`
- `location_id`
- `taught_specializations`
- `taught_techniques`
- `requirements`

Przykładowi mistrzowie:

- Mistrz Miecza
- Mistrz Młota
- Mistrz Halabardy

## Wymagania mistrza

`MasterTrainerRequirements` przygotowuje pola dla:

- minimalnego poziomu umiejętności;
- wymaganej specjalizacji;
- wymaganej obrony;
- reputacji;
- questa;
- przedmiotu;
- kosztu nauki.

W obecnym etapie egzekwowane są tylko:

- minimalny poziom umiejętności;
- wymagane specjalizacje.

Pozostałe pola są przechowywane jako dane na przyszłość.

## Znane techniki

Postać przechowuje osobną kolekcję znanych technik.

Technika trafia tam dopiero po udanej nauce. Nie jest nadawana automatycznie.

## Znane specjalizacje

Postać przechowuje także znane specjalizacje broni, obrony i umiejętności dodatkowych.

Limity:

- 2 specjalizacje broni;
- 2 specjalizacje obrony;
- 4 umiejętności dodatkowe.

## Walidacja

`can_learn_technique()` sprawdza:

- czy technika istnieje;
- czy postać jej nie zna;
- czy posiada wymagane specjalizacje;
- czy posiada wymaganą obronę;
- czy osiągnęła wymagany poziom;
- czy mistrz może jej uczyć.

`learn_technique()`:

- zapisuje technikę;
- blokuje ponowną naukę;
- nie uruchamia efektów walki.

Analogiczny mechanizm istnieje dla nauki specjalizacji.

## Serializacja

`CharacterStateSerializer` zapisuje w istniejącym `creator_json`:

- znane techniki;
- znane specjalizacje.

To zachowuje zgodność ze starszymi zapisami, bo brakujące dane po prostu domyślają się do pustych kolekcji.

## Następny etap

W przyszłości można podłączyć:

- komendy nauki;
- NPC w świecie;
- koszty szkolenia;
- questy i reputację;
- powiązanie z resolverem walki;
- powiązanie z warstwą reakcji bojowych, aby techniki takie jak riposta mogły być rozpoznawane po wyniku walki.
