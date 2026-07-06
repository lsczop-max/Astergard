# AUDIT D20 — Domain Event System

## Cel
Domknięcie systemu zdarzeń domenowych po D19: typowane nazwy eventów, publikacja z kluczowych use-case, subskrypcje, izolacja błędów subscriberów, audyt i testy regresji.

## Wykonane zmiany
- Rozszerzono `astergard/engine/events.py`:
  - dodano `DomainEventType` jako kanoniczny rejestr zdarzeń domenowych,
  - `EventBus.subscribe()` i `EventBus.emit()` przyjmują `str` oraz `DomainEventType`,
  - zachowano kompatybilność z D19 przez `EngineEvent.type: str`,
  - dodano `EngineEvent.actor` do jednolitej identyfikacji aktora zdarzenia.
- Rozszerzono konteksty use-case w `application/use_case_contexts.py` o `event_bus`.
- Przeniesiono wstrzykiwanie busa do `application/context_assembler.py`.
- Dodano publikację eventów z głównych systemów:
  - eksploracja: `character.moved`, `world.hidden_element_discovered`,
  - ekwipunek: `item.picked_up`, `item.dropped`, `item.equipped`, `item.unequipped`, `item.consumed`,
  - komunikacja: `character.spoke`, `character.emoted`, `character.shouted`,
  - walka: `combat.attacked`, `combat.fled`, `combatant.died`, `npc.died`,
  - questy: `quest.accepted`, `quest.progress_updated`,
  - reputacja: `reputation.changed`,
  - ekonomia: `economy.item_bought`, `economy.item_sold`,
  - magia/crafting: `magic.cast`, `crafting.attempted`,
  - zapis: `character.saved`.
- Utrzymano audyt przez wildcard subscriber w `EngineLifecycle`.
- Naprawiono błąd w `CommandDispatcher.execute_line()` dla slotowego `GameContext`: komenda trafia teraz do `context.exploration().current_command`, jeżeli kontekst nie ma własnego `__dict__`.

## Testy
Dodano `tests/test_d20_domain_events.py`:
- typowane nazwy eventów działają z `EventBus`,
- ruch emituje `character.moved` i zapisuje audyt,
- ścieżka komendy `wez` emituje `item.picked_up`,
- błąd subscribera nie przerywa event busa.

## Wynik
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 76 tests in 1.378s
OK
```

## Ocena krytyczna
D20 domyka warstwę zdarzeń domenowych w rdzeniu. To nadal nie jest pełny event-sourcing: eventy są audytowane i obserwowalne, ale nie są jedynym źródłem prawdy stanu gry. To jest właściwa decyzja na tym etapie, bo pełny event-sourcing zwiększyłby złożoność bez bezpośredniej korzyści dla grywalnego MUD-a.

## Następny etap
D21 — Rules Engine: centralizacja reguł, usunięcie rozproszonych magic numbers i nadanie regułom nazw, testów oraz wersjonowania.
