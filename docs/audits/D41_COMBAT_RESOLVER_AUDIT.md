# D41 Combat Resolver Audit

Zakres: rzeczywisty resolver walki Astergardu, ścieżki wejścia z komend i AI, narracja, zdarzenia domenowe, stan postaci, broń, pancerz, rany, AI, persistence i punkt styku z D36-D38.

Źródło prawdy: kod i testy. Dokumentacja oraz wcześniejsze założenia projektowe są pomocnicze tylko wtedy, gdy nie przeczą kodowi.

## Streszczenie wykonawcze

Obecny system walki jest funkcjonalny, testowalny i częściowo już rozdzielony na warstwy, ale nadal ma kilka twardych luk integracyjnych:

* wejście z komendy gracza uruchamia pojedynczy cios, a nie pełny stan walki;
* wyjście z walki przez `ucieczka` nie czyści stanu walki;
* „aktywny oręż” nie jest odrębnym stanem od ekwipunku, więc parowanie może działać z bronią trzymaną wyłącznie w plecaku;
* aktywne starcia nie są utrwalane w snapshotcie świata;
* model walki grupowej jest obecnie parowy, bez frontu, tyłu, ochrony sojusznika lub wybierania roli obronnej;
* resolver łączy walidację, losowanie, redukcję obrażeń, degradację ekwipunku, ranienie i budowę eventu w jednej funkcji.

To nie blokuje obecnego gameplayu, ale blokuje bezpieczne wpięcie D36-D38 i docelowego przepływu technik.

## Liczba problemów

* BLOCKER: 3
* HIGH: 4
* MEDIUM: 4
* LOW: 2
* INFORMATIONAL: 4

## Obecny przepływ walki

### 1. Komenda gracza

`zabij` -> `CommandDispatcher.execute_line()` -> `build_combat_handlers()` -> `CombatApplicationService.attack_npc()` -> `CombatManager.attack()` -> `CombatNarrator.render()` -> tekst + `COMBAT_ATTACKED`.

### 2. Inicjacja NPC / AI

`HeartbeatService.tick_once()` -> `NPCManager.ai_tick()` -> `_aggression_tick()` / `_guard_tick()` -> `combat.start()` + `enter_combat()` -> `HeartbeatService.process_combat_rounds()` -> `CombatManager.process_active_round()` -> `process_pair_round()` -> `attack()`.

### 3. Ucieczka

`ucieczka` -> `CombatApplicationService.flee()` -> kontrola nóg przez `MovementRules` -> `move_direct()` -> `COMBAT_FLED`.

## Mapa modułów

| Plik | Odpowiedzialność | Wejścia | Wyjścia | Mutacje | Eventy | Testy |
| --- | --- | --- | --- | --- | --- | --- |
| `astergard/combat/manager.py` | Resolver starcia, inicjatywa, trafienie, obrona, obrażenia, rany, śmierć, payload eventu | `Character`, `RandomSource`, `CombatRules` | `CombatResult`, `CombatRoundResult`, `CombatEvent` | stamina, wounds, durability, skills, `active_fights` | brak bezpośrednich; generuje `CombatEvent` | `tests/test_d14_combat_balance.py`, `tests/test_d15_combat_styles.py`, `tests/test_d22_state_machines.py`, `tests/test_d39_tactical_combat.py`, `tests/test_d51_combat_event_narration.py` |
| `astergard/combat/events.py` | Strukturalny payload starcia | pola domenowe i nazwy broni | `CombatEvent` | brak | brak | `tests/test_d51_combat_event_narration.py` |
| `astergard/combat/narration.py` | Render komunikatów z `CombatEvent` | `CombatEvent`, perspektywa | tekst dla atakującego, broniącego, obserwatora | pamięć ostatnich fraz | brak | `tests/test_d51_combat_event_narration.py` |
| `astergard/combat/tactics.py` | Modifikatory taktyczne, morale, formacja, zmęczenie, obrażenia od ran | `Character`, `Item` | liczby modyfikatorów | brak | brak | `tests/test_d39_tactical_combat.py` |
| `astergard/combat/wounds.py` | Logika śmierci i opis zdrowia | słownik ran | tekst zdrowia, bool śmierci | brak | brak | `tests/test_d22_state_machines.py`, `tests/test_core.py` |
| `astergard/application/services/combat_service.py` | Use-case gracza: atak NPC, ucieczka, corpses, quest/reputation side effects | `CombatContext`, nazwa celu | tekst komendy | world, NPC, faction, quest, event bus | `COMBAT_ATTACKED`, `COMBATANT_DIED`, `NPC_DIED`, `REPUTATION_CHANGED`, `COMBAT_FLED` | `tests/test_d42_animal_drops.py`, `tests/test_d4_application_use_cases.py`, `tests/test_d13_npc_ai_respawn.py` |
| `astergard/application/heartbeat.py` | Tick świata, NPC AI, combat rounds, respawn | `GameServices`, lista graczy | brak | weather, NPC, combat, respawn, regen | `world.respawn_tick_completed`, `character.tick_completed`, `npc.died` | `tests/test_d13_npc_ai_respawn.py`, `tests/test_d19_engine_core.py`, `tests/test_d12_world_persistence.py` |
| `astergard/npcs/manager.py` | AI, patrol, aggression, guard logic, respawn | gracze, combat, factions | `NPCActionEvent` | NPC state, room membership, combat start | wydarzenia NPC AI | `tests/test_d13_npc_ai_respawn.py`, `tests/test_d18_npc_threat_tiers.py` |
| `astergard/characters/models.py` | Stan postaci, bronie, pancerz, rany, combat flags | dane postaci | `Character` | wounds, equipment, flags, state | brak | `tests/test_d22_state_machines.py`, `tests/test_d41_equipment_slots.py`, `tests/test_d12_world_persistence.py` |
| `astergard/items/models.py` | Model przedmiotu, broń, tarcza, pancerz, sloty | dane itemu | `Item`, `EquipmentSet` | inventory/equipment state przy hydratacji | brak | `tests/test_d14_combat_balance.py`, `tests/test_d41_equipment_slots.py`, `tests/test_d45_quality_pass.py` |
| `astergard/database/serialization.py` | Persistencja postaci, kariery, combat learning | obiekt `Character` / row SQLite | payload SQLite / `Character` | hydracja stanu postaci | brak | `tests/test_d10_persistence_migrations.py`, `tests/test_d12_world_persistence.py`, `tests/test_d39_career_framework.py`, `tests/test_d37_combat_techniques_framework.py`, `tests/test_d38_combat_learning_system.py` |
| `astergard/database/world_state_repository.py` | Snapshot świata: NPC, itemy, hidden elements, respawn | `WorldManager`, `NPC`s | snapshot JSON | world, npc, respawn queue | brak | `tests/test_d12_world_persistence.py`, `tests/test_d18_npc_threat_tiers.py` |
| `astergard/commands/combat.py` | Thin handler dla `zabij` i `ucieczka` | `GameContext`, argument | string | brak bezpośrednich | brak | `tests/test_d4_application_use_cases.py` |
| `astergard/server/game.py` | Orkiestracja serwera i instalacja handlerów | `GameServices`, sieć | `GameServer` | clients, session flow | `session.character_saved` | `tests/test_d19_engine_core.py`, `tests/test_d12_world_persistence.py` |
| `astergard/rules/combat.py` | Parametry balansu walki | brak lub `CombatRules` | `CombatRules` | brak | brak | `tests/test_d21_rules_engine.py` |
| `astergard/rules/movement.py` | Koszt ruchu i blokada nóg | rany nóg | koszt / bool | brak | brak | `tests/test_d21_rules_engine.py`, `tests/test_d42_animal_drops.py` |
| `astergard/rules/combat_specialization.py` | Framework D36-D38 | specjalizacje, techniki, profile ucznia i mistrza | modele, walidacja, katalog technik | znane techniki/specjalizacje | brak | `tests/test_d36_combat_specialization_framework.py`, `tests/test_d37_combat_techniques_framework.py`, `tests/test_d38_combat_learning_system.py` |

## Audyt trafienia

### Wzór

Prawdopodobieństwo trafienia nie jest osobnym procentem. To porównanie dwóch liczbowych wyników:

```text
hit_score =
    zręczność
    + poziom umiejętności broni
    + zasięg broni
    + styl ataku
    + modyfikator formacji
    + morale
    + premia profesji
    - kara za rany
    - kara za zmęczenie
    - opcjonalna kara za pancerz obciążeniowy obrońcy
    + rzut 1..attack_roll_sides

dodge_score =
    zręczność
    + uniki
    + styl obrony
    + modyfikator formacji
    + morale
    + premia profesji
    - kara za rany
    - kara za zmęczenie
    - kara za pancerz obciążeniowy
    + rzut 1..attack_roll_sides

if hit_score <= dodge_score:
    miss / dodge
```

Po przejściu obrony aktywnej atak trafia w losowaną część ciała.

### Co wpływa na trafienie

* `Character.stats.zrecznosc`
* skill uzyskany przez `_weapon_skill_name(weapon)` z `astergard/combat/tactics.py`
* `weapon.reach`
* `CombatStyle.attack_modifier`
* `formation_attack_modifier()`
* `morale_score()`
* `profession_tactical_modifiers().attack`
* kara za rany `wound_attack_penalty()`
* kara za zmęczenie `fatigue_attack_penalty()`
* rzut z `RandomSource.randint(1, attack_roll_sides)`

### Co nie wpływa

* klasa broni z D37
* techniki z D37
* `known_techniques`
* `combat_specializations`

### Ryzyka

* brak twardego minimum / maksimum szansy;
* brak trafień częściowych;
* statystyki mogą dominujeć, jeśli testy scenariuszowe są źle dobrane;
* losowanie jest deterministyczne tylko wtedy, gdy wstrzyknięto stabilny `RandomSource`.

## Audyt obrony

Obrona jest dziś sekwencją testów, a nie osobnym wyborem gracza:

1. uniki
2. tarcza
3. parowanie
4. pancerz

### Tarcza

* osobny test w `_active_defense()`
* wykorzystuje `shield_block`, `tarcze`, `defense_modifier`, morale i formację
* wynik `defended_by="shield"`

### Parowanie

* drugi test w `_active_defense()`
* wykorzystuje `parowanie` i `weapon.parry_bonus`
* wynik `defended_by="parry"`

### Uniki

* w praktyce modelowane jako `dodge_score`
* zależne od zręczności, `uniki`, stylu, formacji, morale, profesji, ran, zmęczenia i obciążenia
* nie są osobnym obiektem decyzji

### Wnioski

Obecna architektura umożliwia późniejsze różnicowanie tarczy, parowania i uników, ale nie daje jeszcze:

* świadomego wyboru obrony,
* osłaniania sojusznika,
* reakcji zależnych od technik,
* osobnych kosztów / stanów dla różnych obron.

## Audyt obrażeń

### Wzór

```text
reduced = weapon_damage + style.damage_modifier + profession.damage - armor.protection - armor.armor_value
```

Jeżeli `reduced <= 0`, atak kończy się na pancerzu:

* `result="armor"`
* brak rany
* zachowana narracja o absorpcji / defleksji / penetracji

Jeżeli `reduced > 0`:

* obliczany jest `wound_gain = _wound_gain(reduced, weapon, style_name)`
* rana trafia do konkretnej części ciała
* wynik może zostać oznaczony jako `hit`, `critical` albo `defeated`

### Zakres i ryzyka

* obrażenia ujemne mogą wystąpić jako wartość pośrednia `reduced`, ale nie stają się „ujemną raną”;
* nie ma osobnego krytyka obrażeń poza etykietą `critical`;
* `wound_gain` nie jest sterowane typem obrażenia w pełni, tylko rodziną broni i stylem;
* obecna kolejność modyfikatorów jest częściowo zapisana w kodzie, a nie w danych.

## Audyt broni

`Item` już przechowuje:

* `weapon_type`
* `damage_type`
* `base_damage`
* `reach`
* `initiative_modifier`
* `parry_bonus`
* `shield_block`
* `armor_value`
* `protection`
* `durability`
* `max_durability`
* `slot`
* `wearable`
* `item_type`

### Rozdział przedmiot / specjalizacja

Specjalizacja postaci jest osobna od przedmiotu:

* postać może znać styl broni,
* przedmiot ma konkretny profil,
* resolver używa jednak `Character.weapon()` oraz `skill_for_weapon()`, więc „aktywny oręż” nie jest osobnym bytem domenowym.

### Szczególny problem

`Character.weapon()` szuka najpierw w slocie, ale potem również w inventory. To oznacza, że obecna logika nie odróżnia:

* „posiadam broń”
* od
* „mam ją aktywnie w dłoni”.

To jest bezpośredni konflikt z przyszłym modelem specjalizacji i technik.

## Audyt pancerzy

Pancerz działa jako:

* wartość ochrony liczona z `protection + armor_value`
* obciążenie redukujące trafienie / inicjatywę przez `armor_burden_penalty()`
* element chroniący konkretną część ciała przez `armor_for(body_part)`

Nie ma jeszcze:

* warstw pancerza,
* odporności na typy obrażeń,
* lokalnych stref pancerza modelowanych jawnie jako osobny byt,
* ścisłego modelu tarczy jako strefy ochrony sojusznika.

## Audyt typów obrażeń i ran

Typ obrażeń obecnie pochodzi z `Item.damage_type` i jest używany głównie do:

* rodzaju broni,
* etykiety narracyjnej,
* pośredniego wyboru skilli broni.

Rana:

* ma lokalizację `wounds[part]`
* ma ciężkość jako liczba całkowita
* wpływa na ruch, trafienie, obronę, inicjatywę i morale

Nie ma jeszcze jawnego modelu:

* krwawienia,
* ogłuszenia,
* utraty przytomności,
* rozróżnienia wszystkich typów obrażeń na poziomie ran.

## Audyt czasu walki

Model czasowy jest dwuetapowy:

* komenda gracza lub AI inicjuje zdarzenie,
* heartbeat co 4 sekundy procesuje aktywne walki.

To znaczy:

* inicjatywa działa w obrębie pary,
* nie ma pełnej kolejki akcji,
* `CombatManager` nie posiada własnego tickera,
* technika z przygotowaniem nie ma jeszcze naturalnego miejsca w resolverze.

## Audyt walki grupowej

Obecny model to lista par `(attacker_id, defender_id)` w `CombatManager.active_fights`.

To umożliwia:

* wielu napastników na jedną ofiarę, jeśli każdy ma osobną parę,
* procesowanie po stronie heartbeat.

To jeszcze nie daje:

* frontu / tyłu,
* zasłaniania sojusznika,
* blokowania wyjścia,
* limitu liczby napastników,
* wyboru celu w obrębie grupy,
* roli „głównego celu” i „dodatkowych napastników”.

## Audyt AI

`NPCManager.ai_tick()`:

* dla `PATROL` może przenieść NPC po lokacji w obrębie strefy,
* dla `AGGRESSIVE` wybiera pierwszego żywego gracza w pokoju i rozpoczyna walkę,
* dla `GUARD` atakuje gracza wrogiego strażnikom.

AI:

* nie wybiera techniki,
* nie ma osobnego wyboru obrony,
* nie klasyfikuje celu taktycznie,
* nie posiada odpowiedzialności za rozstrzygnięcie ciosu.

To jest poprawny punkt integracji na przyszłość, ale nie kompletna sztuczna inteligencja bojowa.

## Audyt narracji

W `CombatManager.attack()` powstaje strukturalny `CombatEvent`, ale jednocześnie powstają już końcowe teksty przez `CombatNarrator.render()`.

To znaczy:

* domena ma payload,
* ale resolver nadal generuje gotowe komunikaty dla uczestników,
* nie ma jeszcze czystego „wyniku domenowego bez narracji”.

`CombatEvent` już zawiera pola przydatne dla przyszłej integracji:

* napastnik,
* cel,
* broń,
* rodzina broni,
* technika,
* obrona,
* lokalizacja trafienia,
* typ obrażeń,
* siła,
* zredukowana siła,
* pancerz,
* poziom rany,
* efekty specjalne,
* tagi narracyjne,
* notatki wynikowe.

To jest dobry fundament do późniejszego `CombatNarrationRenderer`.

## Audyt zdarzeń i efektów ubocznych

Skutki uboczne obecnej walki:

* zmiana kondycji atakującego,
* zmiana ran obrońcy,
* zmiana trwałości broni,
* zmiana trwałości pancerza / tarczy,
* trenowanie skilli,
* śmierć postaci,
* emisja `COMBAT_ATTACKED`,
* emisja `COMBATANT_DIED`,
* emisja `NPC_DIED`,
* emisja `COMBAT_FLED`,
* emisja `REPUTATION_CHANGED`,
* emisja `QUEST_PROGRESS_UPDATED`.

Najważniejsze ryzyko:

* resolver i warstwa aplikacyjna czasem robią zbyt dużo rzeczy w jednym przebiegu,
* integracja z kolejnymi systemami będzie wymagała ostrożnego rozdzielenia odpowiedzialności.

## Powiązanie z D36-D38

### Co już jest gotowe

* `Character.combat_specializations`
* `Character.known_techniques`
* `TechniqueUserProfile`
* `can_use_technique()`
* `can_learn_technique()`
* `learn_technique()`
* `learn_specialization()`

### Co jeszcze nie jest spięte z walką

* `CombatManager.attack()` nie czyta technik,
* `CombatApplicationService.attack_npc()` nie wybiera techniki,
* AI nie wybiera technik,
* `CombatEvent.technique` jest tylko tekstem, a nie wywołaniem techniki,
* `combat_specializations` i `known_techniques` są obecne w modelu, ale nie w resolverze.

### Najmniej ryzykowne punkty integracji

1. wejście komendy / AI intent
2. budowa `CombatAction`
3. walidacja specjalizacji i techniki
4. dopiero potem wywołanie obecnego resolvera walki

## Porównanie z praktykami innych MUD-ów

Ten projekt już częściowo zgadza się z dobrymi praktykami:

* podstawowa walka może być automatyczna po rozpoczęciu starcia przez AI i heartbeat;
* decyzje taktyczne można trzymać przy komendach i przyszłych technikach;
* dane balansu są w dużej mierze konfiguracyjne.

To nadal nie jest gotowy model:

* automatyczna walka gracza nie jest jeszcze spięta z tym samym cyklem co AI,
* „współczesny” model technik wymaga osobnego intentu i wyboru akcji,
* skuteczność jest nadal binarna na poziomie hit/miss/defense, bez wyraźnej skali dla technik.

## Symulacje diagnostyczne

Wykonane scenariusze bez zmian kodu:

* `zabij` gracza na NPC: pojedynczy cios, bez wejścia w aktywną walkę;
* NPC agresywny: wejście do `active_fights` i `in_combat=True` po `ai_tick`;
* `ucieczka`: ruch następuje, ale `in_combat` oraz `active_fights` pozostają bez czyszczenia;
* 1v1 i 2v1: `process_pair_round()` i `process_active_round()` działają deterministycznie z wstrzykniętym RNG;
* tarcza i parowanie działają jako aktywna obrona w `_active_defense()`.

Praktyczny wniosek:

* aktywny loop walki istnieje,
* ale ma dwie różne ścieżki wejścia i nie kończy się spójnie po ucieczce.

## Zalecenie na następny etap

Najmniejszy sensowny podział D42+:

1. `CombatIntent` / walidacja wejścia
2. `CombatActionBuilder`
3. `InitiativeResolver`
4. `AttackResolver`
5. `DefenseResolver`
6. `HitLocationResolver`
7. `ArmorResolver`
8. `DamageResolver`
9. `WoundResolver`
10. `CombatOutcome`
11. `CombatNarrationRenderer`

To nie powinno być jeszcze rozbijane dalej, dopóki nie zostanie ujednolicona ścieżka gracza, AI i ucieczki.
