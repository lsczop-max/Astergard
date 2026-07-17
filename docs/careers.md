# Career Framework

System karier w Astergardzie oddziela styl życia postaci od jej sposobu walki.

## Filozofia

- `profession` nadal opisuje początkowy profil i ekwipunek.
- `career` opisuje powołanie życiowe.
- `organization` otwiera dostęp do szkół.
- `school` grupuje techniki i mistrzów.

System nie implementuje jeszcze questów, reputacji, ekonomii ani awansów mechanicznych.

## Hierarchia

1. `Career`
2. `Organization`
3. `School`
4. `Master`
5. `Technique`

## Modele

### Career

Pola:

- `id`
- `name`
- `description`
- `organizations`
- `allowed_schools`
- `starting_benefits`
- `advancement_path`

### Organization

Pola:

- `id`
- `name`
- `description`
- `career_id`
- `schools`
- `trainers`
- `reputation_rules`

### School

Pola:

- `id`
- `name`
- `description`
- `organization`
- `techniques`
- `bonuses`
- `masters`

### Character

Postać przechowuje:

- `career_id`
- `organization_id`
- `school_id`
- `organization_rank`

## Walidacja

Na tym etapie dostępne są wyłącznie funkcje:

- `can_join_career()`
- `leave_career()`
- `join_career()`
- `can_join_organization()`
- `leave_organization()`
- `join_organization()`
- `can_join_school()`
- `leave_school()`
- `join_school()`

Walidacja sprawdza zgodność hierarchii i podstawową spójność danych.

## Domain Integrity

### Niezmienniki

- nowa postać nie należy do żadnego powołania, organizacji ani szkoły,
- organizacja wymaga powołania,
- szkoła wymaga organizacji,
- szkoła musi należeć do organizacji, do której należy postać,
- ranga organizacyjna nie istnieje bez organizacji.

### Dozwolone przejścia

- `join_career()` ustawia powołanie,
- `leave_career()` czyści całe drzewo kariery,
- `join_organization()` ustawia organizację i w razie zmiany opuszcza szkołę oraz zeruje rangę,
- `leave_organization()` czyści organizację, szkołę i rangę,
- `join_school()` ustawia szkołę,
- `leave_school()` czyści szkołę.

### Niedozwolone stany

- organizacja bez powołania,
- szkoła bez organizacji,
- szkoła spoza organizacji,
- ranga bez organizacji,
- nieznane identyfikatory pozostawione w zapisie bez czyszczenia.

### Bezpieczny interfejs i dług techniczny

Model `Character` pozostaje mutowalny, więc bezpośredni zapis pól nadal technicznie omija walidator.
Bezpieczny punkt wejścia do domeny to funkcje `join_*`, `leave_*` oraz `validate_career_integrity()`.
Pełna blokada ręcznych zapisów wymagałaby większej przebudowy modelu obiektu i nie została wykonana na tym etapie.

## Przyszły rozwój

W kolejnych etapach można dołożyć:

- reputację dla organizacji,
- koszty nauki,
- questy powiązane z awansem,
- ograniczenia wejścia do szkół,
- mechanikę zmiany powołania,
- integrację z systemem postępu i nagród.
