# D49 Defense and Riposte Balance Simulation

## Verdict
`DEFENSE_AND_RIPOSTE_REBALANCE_REQUIRED`

## Methodology
- Production pipeline only: `CombatManager`, `CombatAction`, `DefenseResolver`, `CombatReactionExecutor`, damage, and wounds.
- No second resolver was introduced.
- Deterministic seeds were used for all runs.
- Single-action simulations:
  - 1000 trials per configuration
  - 20 single-action configurations
  - 20,000 total single-action trials
- Full duel simulations:
  - 100 trials per ordered pair
  - 42 duel configurations
  - 4,200 total duel trials
- Seed policy:
  - a stable hash-derived seed offset per configuration
  - each trial receives a dedicated seed derived from the configuration key and trial index

## Configuration Set
- Supported archetypes: `A`, `B`, `C`, `D`, `F`, `G`
- Unsupported archetype: `E` (`NOT_YET_SUPPORTED`)
- `E` was excluded from duel matrices and single-action statistics as an intentionally unsupported dual-wield scenario.

### Supported archetypes
- `A` - bez specjalizacji
- `B` - tarczownik z młotem
- `C` - tarczownik z mieczem
- `D` - szermierz
- `F` - unikający
- `G` - broń drzewcowa

## Single-Action Simulation Summary

| Build | Defended | Hit | First attempt | Second attempt | Third attempt | Riposte avail. | Riposte exec. | Riposte hit | Riposte damage share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0 | 0 | 0 | 0.0% |
| B | 100.0% | 0.0% | 100.0% | 0.0% | 0.0% | 0 | 0 | 0 | 0.0% |
| C | 100.0% | 0.0% | 100.0% | 0.0% | 0.0% | 0 | 0 | 0 | 0.0% |
| D | 100.0% | 0.0% | 100.0% | 0.0% | 0.0% | 1000 | 1000 | 1000 | 0.0% |
| F | 100.0% | 0.0% | 100.0% | 0.0% | 0.0% | 0 | 0 | 0 | 0.0% |
| G | 65.7% | 34.3% | 100.0% | 96.5% | 0.0% | 0 | 0 | 0 | 0.0% |

### Defensive order and effective value

| Build | DODGE mean | SHIELD mean | PARRY mean | Notes |
| --- | ---: | ---: | ---: | --- |
| A | 36.75 | 0.00 | 36.75 | Dodge and parry tie, so both are tried. |
| B | 0.00 | 85.75 | 0.00 | Shield dominates and ends the sequence. |
| C | 20.97 | 104.13 | 58.80 | Shield dominates parry and dodge. |
| D | 92.34 | 0.00 | 139.65 | Parry dominates dodge. |
| F | 122.50 | 0.00 | 44.10 | Dodge dominates parry. |
| G | 35.55 | 0.00 | 27.44 | Dodge is first, parry is second. |

## Armor Probe

| Armor | DODGE mean | SHIELD mean | PARRY mean | Interpretation |
| --- | ---: | ---: | ---: | --- |
| unarmored | 72.90 | 73.50 | 73.50 | Baseline. |
| light_armor | 67.55 | 73.50 | 69.82 | Light armor mostly preserves defensive access. |
| medium_armor | 41.94 | 62.47 | 58.80 | Medium armor sharply suppresses dodge. |
| heavy_armor | 0.00 | 51.45 | 44.10 | Heavy armor removes dodge entirely, but not block/parry. |

## Weapon Probe

| Weapon | PARRY mean | Riposte available | Riposte exec. | Riposte hit | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| garrison_short_sword | 73.50 | 68 | 68 | 68 | Full riposte-capable profile. |
| court_sabre | 69.82 | 81 | 81 | 81 | Full riposte-capable profile. |
| duelist_dagger | 66.15 | 72 | 72 | 72 | Full riposte-capable profile. |
| battle_axe | 22.05 | 0 | 0 | 0 | Weak parry, no riposte. |
| war_hammer | 0.00 | 0 | 0 | 0 | No riposte. |
| war_mace | 0.00 | 0 | 0 | 0 | No riposte. |
| watch_spear | 58.80 | 0 | 0 | 0 | Can parry, cannot riposte. |
| watch_halberd | 29.40 | 0 | 0 | 0 | Can parry weakly, cannot riposte. |
| war_flail | 0.00 | 0 | 0 | 0 | No riposte. |
| war_staff | 58.80 | 0 | 0 | 0 | Can parry, cannot riposte. |

## Full Duel Summary

### Self-duels

| Build | Attacker win | Defender win | Draw | Avg rounds | Median rounds | Limit exceeded | Avg defenses / round | Riposte damage share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 65.0% | 35.0% | 0.0% | 8.01 | 8.00 | 0 | 1.93 | 0.0% |
| B | 0.0% | 0.0% | 100.0% | 80.00 | 80.00 | 100 | 2.00 | 0.0% |
| C | 0.0% | 0.0% | 100.0% | 80.00 | 80.00 | 100 | 2.00 | 0.0% |
| D | 0.0% | 0.0% | 100.0% | 80.00 | 80.00 | 100 | 2.00 | 0.0% |
| F | 0.0% | 0.0% | 100.0% | 80.00 | 80.00 | 100 | 2.00 | 0.0% |
| G | 43.0% | 47.0% | 10.0% | 15.29 | 7.00 | 10 | 2.00 | 0.0% |

### Ordered win-rate matrix

Attacker win rate, row = attacker, column = defender.

| Atk \ Def | A | B | C | D | F | G |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 65% | 0% | 0% | 0% | 0% | 0% |
| B | 100% | 0% | 0% | 0% | 0% | 64% |
| C | 100% | 0% | 0% | 0% | 0% | 64% |
| D | 100% | 11% | 0% | 0% | 0% | 45% |
| F | 100% | 0% | 0% | 0% | 0% | 1% |
| G | 100% | 0% | 0% | 0% | 0% | 43% |

## Riposte Comparisons

Comparison used asymmetrical mirrored pairs: a build with `riposte` against the same build without `riposte`, in both attacker orientations.

| Build | Win-rate delta | Avg-round delta | Riposte damage share | Interpretation |
| --- | ---: | ---: | ---: | --- |
| C | 0.00 pp | 0.00% | 0.0% | Riposte is mechanically available but not balance-shifting in this setup. |
| D | 0.00 pp | 0.00% | 0.0% | Riposte executes, but does not change the measured outcome. |
| F | 0.00 pp | 0.00% | 0.0% | No measurable riposte effect. |

## Observations

### 1. How often attacks are stopped by any defense
- `B`, `C`, `D`, and `F` stop 100% of single attacks in the sampled configuration.
- `G` stops 65.7% of single attacks and still allows 34.3% hits.
- `A` stops 0% of single attacks.

### 2. How often first, second, and third defenses are resolved
- `A` always uses the first and second candidate.
- `B`, `C`, `D`, and `F` use only the first candidate.
- `G` uses the first candidate every time and the second candidate in 96.5% of attacks.
- The third candidate was not used in the measured archetypes.

### 3. Success rates of shield, dodge, and parry
- `B` and `C` have a 100% shield block success rate in single-action tests.
- `D` has a 100% parry success rate.
- `F` has a 100% dodge success rate.
- `G` is mixed:
  - dodge success rate: 3.5%
  - parry success rate: 64.46%

### 4. Does parry fire when shield or dodge have higher effective value?
- Yes, the resolver follows the dynamic sort.
- `C`: shield > parry > dodge, so shield is first.
- `D`: parry > dodge, so parry is first.
- `G`: dodge > parry, so dodge is first and parry becomes the fallback.

### 5. Does the lower order matter?
- In `A`, the second candidate is always reached, so the lower order is meaningful.
- In `G`, the second candidate is relevant in 96.5% of attacks.
- In `B`, `C`, `D`, and `F`, the first candidate already resolves the attack, so lower candidates do not influence the measured outcome.

### 6. Riposte impact
- Riposte is technically discovered and executed in `D`.
- It does not add measurable damage in the sampled runs.
- It does not change win rate or average rounds in the measured asymmetrical comparisons.
- In this balance state, riposte is not offensive pressure yet.

## Problems and Recommendations

### HIGH
1. Specialized defensive builds (`B`, `C`, `D`, `F`) produce 100% draw-rate self-duels at the 80-round limit.
   - Evidence: all four builds hit `limit_exceeded = 100` and `average_rounds = 80.00`.
   - Consequence: long or effectively unresolved fights.
   - Recommendation: reduce stacked defensive certainty or increase offensive penetration in a later balance pass.

2. Build `A` is too weak against specialized defenders.
   - Evidence: attacker win rate vs `B`, `C`, `D`, `F`, and `G` is `0%`, `0%`, `0%`, `0%`, and `0%` respectively.
   - Consequence: the baseline build cannot pressure the specialization builds.
   - Recommendation: audit the baseline offensive profile and the defense threshold spread.

3. The defense system currently produces hard polarity instead of gradual trade-offs.
   - Evidence: `B`/`C`/`D`/`F` are near-impenetrable, while `A` is consistently defeated as an attacker.
   - Consequence: the current parameters create strong stalemates and a narrow viable band.
   - Recommendation: revisit the balance relationship between armor, shield, and learned defense values.

### MEDIUM
4. `G` is the only sampled archetype that produces a mixed, non-stalemate self-duel.
   - Evidence: `43%` attacker wins, `47%` defender wins, `10%` draws.
   - Consequence: the build is healthier than the shield/parry stalemates, but still often reaches the round cap.
   - Recommendation: keep it as the current reference for middle-ground tuning.

### INFORMATIONAL
5. Riposte is available and executable, but it does not yet move the balance needle.
   - Evidence: `riposte_damage share = 0.0%`, `win-rate delta = 0.00 pp`, `avg-round delta = 0.00%`.
   - Consequence: the technical slice is present, but its current parameterization is balance-neutral.
   - Recommendation: keep the implementation, defer tuning to a dedicated riposte-balance pass.

## Final Assessment
- Dynamic defense works and the pipeline is deterministic.
- The system is not yet balance-acceptable because several builds are effectively stalemate builds.
- Riposte is structurally correct but has no measurable combat weight in the current tuning.
