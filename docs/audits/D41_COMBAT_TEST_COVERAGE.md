# D41 Combat Test Coverage

To jest mapa pokrycia testami, nie pomiar linii kodu. Ocena jest jakościowa, oparta na rzeczywistych testach scenariuszowych i regresyjnych.

## Mapa

| Obszar | Istniejące testy | Co chronią | Braki | Ryzyko |
| --- | --- | --- | --- | --- |
| Trafienie | `tests/test_d14_combat_balance.py`, `tests/test_d39_tactical_combat.py` | zależność od zręczności, skill, reach, morale, profesji, formacji | brak twardych testów min/max szansy i powtarzalności z logów | średnie |
| Obrona | `tests/test_d14_combat_balance.py`, `tests/test_d39_tactical_combat.py`, `tests/test_d51_combat_event_narration.py` | tarcza, parry, dodge, narracja wyników obrony | brak testu na świadomy wybór obrony i obronę przeciw kilku napastnikom | wysokie |
| Pancerz | `tests/test_d39_tactical_combat.py`, `tests/test_d14_combat_balance.py` | redukcja obrażeń, obciążenie, wpływ na defensywę | brak testu warstw i typów obrażeń wpływających na pancerz | wysokie |
| Rany | `tests/test_d22_state_machines.py`, `tests/test_d12_world_persistence.py` | śmierć, stan postaci, persistence ran | brak testów krwawienia, ogłuszenia, utraty przytomności | wysokie |
| Walka grupowa | `tests/test_d14_combat_balance.py`, `tests/test_d13_npc_ai_respawn.py` | rozgrywanie turnów i uproszczone starcie 1v1 / wiele par | brak frontu, tyłu, osłony sojusznika, limitu napastników | wysokie |
| AI | `tests/test_d13_npc_ai_respawn.py`, `tests/test_d18_npc_threat_tiers.py` | agresja, patrol, guard, threat profiles | brak wyboru technik i roli bojowej | średnie |
| Narracja | `tests/test_d51_combat_event_narration.py`, `tests/test_d15_combat_styles.py` | strukturalny payload, perspektywy, memory narrator | brak testu odseparowanego renderera outcome -> tekst | średnie |
| Persistence walki | pośrednio `tests/test_d12_world_persistence.py`, `tests/test_d10_persistence_migrations.py` | rany, NPC, świat snapshot | brak utrwalania `active_fights` i stanu walki | wysokie |

## Testy, które są mocne domenowo

* `tests/test_d14_combat_balance.py::test_shield_can_block_successful_hit`
* `tests/test_d14_combat_balance.py::test_weapon_parry_can_stop_hit_without_shield`
* `tests/test_d22_state_machines.py::test_combat_death_uses_character_state_machine`
* `tests/test_d13_npc_ai_respawn.py::test_aggressive_npc_initiates_combat_with_player_in_room`
* `tests/test_d42_animal_drops.py::test_corpse_contains_generated_animal_loot_after_death`
* `tests/test_d51_combat_event_narration.py::test_combat_result_carries_semantic_event_payload`

## Testy, które są bardziej implementacyjne niż domenowe

* `tests/test_d4_application_use_cases.py::test_command_handlers_are_thin_after_d4`
  * sprawdza liczbę linii w pliku, nie zachowanie domeny
* `tests/test_d21_rules_engine.py::test_combat_manager_uses_injected_attack_cost_rule`
  * bezpośrednio testuje prywatną metodę
* `tests/test_d17_balance_tuning.py::test_tuned_style_extremes_are_reduced`
  * silnie zakotwiczone w konkretnych liczbach balansu
* `tests/test_d16_combat_balance_simulation.py`
  * bardzo dobre jako regresja balansu, ale nie wystarcza do poprawności przepływu

## Główne braki testowe

1. brak testu, że `zabij` rozpoczyna pełen combat loop lub świadomie go nie rozpoczyna;
2. brak testu, że `ucieczka` czyści combat state;
3. brak testu na aktywną broń jako osobny stan od inventory;
4. brak testu na restart podczas walki;
5. brak testu walki grupowej z rolami i osłanianiem;
6. brak testu na wybór obrony jako świadomą decyzję.

## Szacunkowe pokrycie głównych obszarów

To nie jest coverage line-by-line. To ocena, jak dużo reguł domenowych jest dziś zabezpieczonych przez istniejące testy.

* Trafienie: około 75%
* Obrona: około 65%
* Pancerz: około 60%
* Rany: około 55%
* Walka grupowa: około 30%
* AI: około 45%
* Narracja: około 80%
* Persistence walki: około 35%

Najsilniejsze pokrycie jest tam, gdzie testy sprawdzają przepływ i payload. Najsłabsze tam, gdzie potrzebny jest model wieloaktowy lub stan długotrwały.
