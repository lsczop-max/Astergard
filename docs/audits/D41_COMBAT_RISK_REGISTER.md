# D41 Combat Risk Register

## BLOCKER

### B1. Komenda `zabij` nie włącza pełnego combat loop

* Plik: `astergard/application/services/combat_service.py`
* Funkcja: `attack_npc()`
* Status: RESOLVED w D41.1
* Dowód: wywołuje tylko `ctx.combat.attack(...)`; nie ma `combat.start()` ani `enter_combat()`
* Konsekwencja: gracz dostaje pojedynczy cios, ale nie wchodzi do tej samej pętli co NPC
* Aktualny stan: `attack_npc()` korzysta z kanonicznego startu walki, ustawia stan obu stron i wykonuje pierwszy cios tylko przy nowym starciu
* Etap naprawy: D41.1
* Ryzyko regresji: średnie

### B2. Aktywny oręż nie jest odrębnym stanem od inventory

* Plik: `astergard/characters/models.py`
* Funkcje: `weapon()`, `shield()`
* Status: RESOLVED w D41.1
* Dowód: `weapon()` po slotach szuka też w inventory; `shield()` po slotach szuka także w `bron_pomocnicza` i `lewa_reka`
* Konsekwencja: parowanie i atak mogą korzystać z broni posiadanej, a nie aktywnie używanej
* Aktualny stan: `weapon()` zwraca wyłącznie aktywnie wyposażoną broń; inventory-only nie jest uznawane za uzbrojenie
* Etap naprawy: D41.1
* Ryzyko regresji: niskie

### B3. Ucieczka nie czyści stanu walki

* Plik: `astergard/application/services/combat_service.py`
* Funkcja: `flee()`
* Status: RESOLVED w D41.1
* Dowód: po udanym ruchu wysyła `COMBAT_FLED`, ale nie wywołuje `combat.stop_for()` ani `leave_combat()`
* Konsekwencja: postać może zmienić pokój, ale nadal pozostaje w walce
* Aktualny stan: po skutecznej ucieczce walka jest zamykana kanonicznym API, a `active_fights` i stany stron są czyszczone
* Etap naprawy: D41.1
* Ryzyko regresji: średnie

## HIGH

### H1. Aktywne starcia nie są utrwalane

* Plik: `astergard/combat/manager.py`, `astergard/database/world_state_repository.py`
* Dowód: `CombatManager.active_fights` jest czystą listą w pamięci; snapshot świata zapisuje NPC i świat, ale nie walkę
* Konsekwencja: restart serwera kasuje trwające starcia
* Aktualny stan: `RESOLVED` jako świadoma polityka runtime, wymuszona normalizacją po odczycie i testami regresyjnymi
* Rozwiązanie na później: jeśli kiedyś pojawi się trwała walka, będzie to osobny projekt domenowy
* Etap: D41.2
* Ryzyko regresji: niskie

### H2. Walki grupowe są tylko listą par

* Plik: `astergard/combat/manager.py`
* Funkcje: `process_active_round()`, `process_pair_round()`
* Dowód: każda relacja to para `(attacker_id, defender_id)`; brak centralnego modelu grupy
* Konsekwencja: brak frontu, tyłu, osłony sojusznika i wybierania priorytetowego celu
* Rozwiązanie na później: wprowadzić `CombatEncounter` / `CombatSide` lub podobny nośnik
* Etap: D42-D43
* Ryzyko regresji: średnie

### H3. Obrona jest całkowicie sekwencyjna i niejawna

* Plik: `astergard/combat/manager.py`
* Funkcja: `_active_defense()`
* Dowód: kolejność zawsze `shield -> parry -> fallback`; gracz nie wybiera obrony
* Konsekwencja: trudne będzie osadzenie świadomych technik obrony i różnic między stylami
* Aktualny stan: `RESOLVED` jako jawny `DefenseOutcome` z uporządkowaną listą `DefenseAttempt`
* D44 doprecyzował warunek dostępności parowania: profile broni z `parry_capable` są jawnie obsługiwane, a legacy weapons zachowują kompatybilność
* D45 dodał świadomie wybierany aktywny styl obrony, który zawęża rozstrzygnięcie do jednej jawnej obrony, przy zachowaniu legacy fallback dla starych zapisów
* Rozwiązanie na później: rozdzielić `DefenseChoice` od `DefenseResolution`
* Etap: D43
* Ryzyko regresji: średnie

### H4. AI zaczyna walkę, ale nie wybiera taktyki

* Plik: `astergard/npcs/manager.py`
* Funkcje: `_aggression_tick()`, `_guard_tick()`
* Dowód: AI wybiera tylko cel i wywołuje `combat.start()`
* Konsekwencja: brak miejsca na przyszłe techniki / style wyboru akcji
* Rozwiązanie na później: dodać warstwę intentu lub taktycznej decyzji
* Etap: D42-D44
* Ryzyko regresji: niskie

## MEDIUM

### M1. Resolver miesza walidację, losowanie, obrażenia i event building

* Plik: `astergard/combat/manager.py`
* Funkcja: `attack()`
* Dowód: w jednej funkcji wykonuje się hit check, defense, armor, wounds, durability, skill train i payload
* Konsekwencja: trudniej testować i później wpinąć techniki bez ryzyka regresji
* Rozwiązanie na później: wydzielić kolejne resolvery w D42+
* Etap: D42
* Ryzyko regresji: wysokie

### M2. Narracja jest generowana w resolverze, nie wyłącznie z outcome

* Plik: `astergard/combat/manager.py`, `astergard/combat/narration.py`
* Dowód: `attack()` już renderuje teksty dla wszystkich perspektyw
* Konsekwencja: trudniejszy przyszły podział między `CombatOutcome` a warstwę tekstową
* Rozwiązanie na później: utrzymać payload strukturalny, a renderer wywoływać wyżej
* Etap: D43
* Ryzyko regresji: średnie

### M3. Ucieczka wybiera pierwszy dostępny kierunek

* Plik: `astergard/application/services/combat_service.py`
* Funkcja: `flee()`
* Dowód: `direction = next(iter(loc.exits))`
* Konsekwencja: ruch ucieczki jest arbitralny, nie taktyczny
* Rozwiązanie na później: ucieczka powinna wybierać lub przyjmować kierunek jako intencję
* Etap: D42-D43
* Ryzyko regresji: niskie

### M4. Typy obrażeń są zbyt słabo rozróżnione

* Plik: `astergard/items/models.py`, `astergard/combat/events.py`, `astergard/combat/manager.py`
* Dowód: `damage_type` istnieje, ale wpływa głównie na rodzinę broni i etykiety
* Konsekwencja: trudniej wprowadzić głębsze różnice między cięciem, kłuciem, obuchowym i miażdżeniem
* Rozwiązanie na później: ujednolicić model typów obrażeń zanim pojawią się efekty technik
* Etap: D43
* Ryzyko regresji: średnie

## LOW

### L1. `normalize_weapon_family()` jest heurystyczne

* Plik: `astergard/combat/events.py`
* Dowód: klasyfikuje po nazwie, `weapon_type`, `damage_type`, `vnum`
* Konsekwencja: customowe przedmioty mogą dostać nieidealną rodzinę
* Rozwiązanie na później: doprecyzować metadata w itemach tam, gdzie to krytyczne
* Etap: D43
* Ryzyko regresji: niskie

### L2. Parowanie może trenować `parowanie` nawet przy obronie tarczą

* Plik: `astergard/combat/manager.py`
* Dowód: block success wywołuje `defender.skills.train("parowanie", ...)`
* Konsekwencja: nieco rozmywa to rozdział między tarczą a parowaniem
* Rozwiązanie na później: po wpięciu technik rozdzielić model rozwoju obrony
* Etap: D44
* Ryzyko regresji: niskie

## INFORMATIONAL

### I1. Obecny model ma dobry strukturalny payload

* Plik: `astergard/combat/events.py`
* Wniosek: `CombatEvent` już ma większość pól potrzebnych do przyszłych technik
* Warto zachować: tak

### I2. RNG jest wstrzykiwany i testowalny

* Plik: `astergard/combat/manager.py`
* Wniosek: można testować deterministycznie przez `RandomSource`
* Warto zachować: tak

### I3. `WorldStateRepository` robi prawidłowy snapshot świata

* Plik: `astergard/database/world_state_repository.py`
* Wniosek: NPC, hidden elements i respawn queue są trwałe
* Warto zachować: tak

### I4. Combat styles i taktowanie są już danymi

* Plik: `astergard/rules/combat.py`, `astergard/combat/tactics.py`
* Wniosek: balans jest już w dużej mierze konfigurowalny
* Warto zachować: tak
