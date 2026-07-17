# D41 Combat Flow

## Obecny przepływ

### A. Gracz atakuje NPC

```text
komenda `zabij`
    ↓
`CommandDispatcher.execute_line()`
    ↓
`build_combat_handlers().cmd_kill`
    ↓
`CombatApplicationService.attack_npc()`
    ↓
`find_npc_in_manager()`
    ↓
`CombatManager.attack()`
    ↓
`CombatNarrator.render()` dla atakującego / obserwatora / obrońcy
    ↓
`COMBAT_ATTACKED`
    ↓
`WorldReactionService.on_combat_attacked()`
    ↓
opcjonalnie: corpse / reputation / crime / quest progress
```

### Co jest ważne

* to jest pojedynczy cios, nie wejście do pętli walki;
* `attack_npc()` nie wywołuje `combat.start()` ani `enter_combat()`;
* po zakończeniu nie ma automatycznego dalszego starcia.

### Diagnostyka z harnessu

W teście ręcznym:

* przed `zabij`: `active_fights == []`, `in_combat == False`
* po `zabij`: `active_fights == []`, `in_combat == False`

To potwierdza, że command path jest jednorazową akcją.

---

### B. NPC inicjuje walkę

```text
`HeartbeatService.tick_once()`
    ↓
`NPCManager.ai_tick()`
    ↓
`_aggression_tick()` / `_guard_tick()`
    ↓
`combat.start(npc.id, player.username)`
    ↓
`npc.character.enter_combat()`
    ↓
`player.enter_combat()`
    ↓
`HeartbeatService.process_combat_rounds()`
    ↓
`CombatManager.process_active_round()`
    ↓
`process_pair_round()`
    ↓
`CombatManager.attack()`
    ↓
`CombatEvent` + narracja + śmierć / rany / obrona
```

### Co jest ważne

* tylko ta ścieżka buduje pełny aktywny fight loop;
* heartbeat jest zegarem starcia;
* jeśli postać umrze, `HeartbeatService` usuwa NPC i emituje `npc.died`.

---

### C. Ucieczka

```text
komenda `ucieczka`
    ↓
`CombatApplicationService.flee()`
    ↓
`MovementRules.movement_blocked()`
    ↓
`_flee_chance()`
    ↓
`move_direct()`
    ↓
`COMBAT_FLED`
```

### Problem

Po udanej ucieczce:

* ruch następuje,
* ale `active_fights` pozostaje bez czyszczenia,
* `in_combat` pozostaje `True`.

To oznacza stan pośredni, który później może nadal napędzać walkę.

Diagnostyka harnessu:

```text
before_flee 101 True [('npc_id', 'player')]
after_flee 100 True [('npc_id', 'player')]
```

---

## Ścieżki końcowe

### Śmierć NPC

1. `CombatManager.attack()` wyznacza `dead=True`
2. `CombatApplicationService.attack_npc()` spawnuje zwłoki, rejestruje zabójstwo i reputację
3. `NPCManager.remove_dead()` usuwa NPC
4. `COMBATANT_DIED`, `NPC_DIED`, `REPUTATION_CHANGED`, `QUEST_PROGRESS_UPDATED`

### Śmierć w heartbeat

1. `CombatManager.process_active_round()` rozstrzyga atak
2. `HeartbeatService.process_combat_rounds()` usuwa martwego NPC i spawnuje zwłoki
3. `npc.died` trafia do event busa

### Ucieczka

1. `move_direct()` zmienia pokój
2. `COMBAT_FLED` trafia do event busa
3. obecny model nie zamyka jednak walki

---

## Docelowy flow do integracji D42+

```text
CombatIntent
    ↓
walidacja aktora, celu i stanu
    ↓
wybór aktywnej broni
    ↓
wybór zwykłego ataku lub techniki
    ↓
walidacja specjalizacji i techniki
    ↓
CombatAction
    ↓
inicjatywa / harmonogram
    ↓
test trafienia
    ↓
wybór i rozstrzygnięcie obrony
    ↓
lokalizacja trafienia
    ↓
interakcja z pancerzem
    ↓
obrażenia
    ↓
rany / efekty
    ↓
CombatOutcome
    ↓
eventy
    ↓
narracja dla uczestników i obserwatorów
```

## Warstwa D42

```text
intent
    ↓
CombatAction
    ↓
obecny resolver
    ↓
CombatOutcome
    ↓
eventy i narracja
```

### Znaczenie warstwy

* `intent` pozostaje przyszłą intencją taktyczną;
* `CombatAction` jest strukturą wejścia do resolvera;
* `CombatOutcome` jest strukturą wyniku;
* obecny resolver zachowuje logikę balansu i rozstrzygania;
* narracja i eventy korzystają z wyniku, nie z samej konstrukcji akcji.

### Kompatybilność

Stare ścieżki pozostają ważne, ale teraz mają strukturalny punkt wejścia i wyjścia, który można później wykorzystać dla technik, obrony i efektów.

## Warstwa D43

```text
test trafienia
    ↓
DefenseOutcome
    ↓
CombatOutcome
    ↓
eventy i narracja
```

### Znaczenie warstwy

* `DefenseOutcome` rozdziela próbę obrony od końcowego wyniku akcji;
* `CombatOutcome` niesie zgodny rezultat walki wraz z obroną;
* kolejność prób pozostaje taka sama jak w dotychczasowym resolverze;
* obrona jest teraz widoczna w danych, a nie tylko w tekście.

## Warstwa D44

```text
aktywna broń
    ↓
WeaponProfile
    ↓
parry / hand checks
    ↓
DefenseOutcome
```

### Znaczenie warstwy

* `WeaponProfile` oddziela specjalizację postaci od właściwości konkretnego przedmiotu;
* dostępność parowania zależy od tagu `parry_capable` w profilu broni;
* legacy weapons bez profilu zachowują dotychczasową kompatybilność;
* wymagania rąk i zgodność z tarczą są sprawdzane dopiero na etapie rozstrzygnięcia obrony;
* nie jest to jeszcze redesign obrażeń ani technik.

### Minimalny podział odpowiedzialności

## Warstwa D45

```text
znana specjalizacja obrony
    ↓
active_defense_style
    ↓
jawna pojedyncza próba obrony
```

### Znaczenie warstwy

* postać wybiera jeden podstawowy styl obrony;
* resolver używa tego stylu jako domyślnej, jawnej obrony;
* brak wyboru zachowuje legacy fallback z D43;
* nie zmienia to wzorów, tylko porządkuje wybór obrony;
* komenda gracza i podgląd postaci pokazują aktualny styl.

* `CombatIntentValidator`
* `CombatActionBuilder`

## Warstwa D46

```text
CombatOutcome
    ↓
ReactionTriggerContext
    ↓
ReactionResolver
    ↓
CombatReactionDiscovery
```

### Znaczenie warstwy

* reakcja nie jest częścią `DefenseResolver`;
* po rozstrzygnięciu obrony system może wykryć dostępność riposty lub innej reakcji;
* wynik reakcji jest osobnym, strukturalnym obiektem diagnostycznym;
* obecny przepływ nie wykonuje jeszcze dodatkowego ataku z reakcji;
* `CombatAction` i `CombatOutcome` pozostają niezmienione po utworzeniu.

## Warstwa D47

```text
CombatAction
    ↓
dynamiczny wybór obrony
    ↓
DefenseOutcome
```

### Znaczenie warstwy

* obrona przestała zależeć od ręcznie wybieranego stylu jako głównego mechanizmu wyboru;
* resolver buduje kandydatów obrony na podstawie umiejętności, wyposażenia i pancerza;
* `active_defense_style` pozostał wyłącznie polem historycznej zgodności;
* obrona jest teraz wybierana jako najlepszy kandydat, a nie przez ręczne przełączenie gracza.

## Warstwa D48

```text
CombatOutcome(PARRIED)
    ↓
CombatReactionDiscovery
    ↓
CombatReactionExecutor
    ↓
CombatAction(REACTION, riposte)
    ↓
CombatOutcome
```

### Znaczenie warstwy

* skuteczne parowanie może uruchomić automatyczną ripostę;
* riposta jest osobnym `CombatAction`;
* riposta ma własny `CombatOutcome` i własne eventy;
* reakcja nie tworzy pętli, ponieważ jej głębokość jest ograniczona polityką reakcji;
* pierwotny atak i riposta pozostają osobnymi akcjami, mimo że obie korzystają z tego samego resolvera.
* `InitiativeResolver`
* `AttackResolver`
* `DefenseResolver`
* `HitLocationResolver`
* `ArmorResolver`
* `DamageResolver`
* `WoundResolver`
* `CombatEffectResolver`
* `CombatNarrationRenderer`

Nie są to jeszcze wymagania implementacyjne. To jest najmniejszy sensowny podział, który zachowuje dzisiejszy model danych.
