# D50 Defense Probability Rebalance

## Methodology
- Single-action trials per configuration: 1000
- Duel trials per ordered pair: 100
- Max rounds per duel: 80
- Seeding: deterministic hash-derived offsets per configuration
- Baseline: /home/lukasz/Dokumenty/astergard_d34_world_area/docs/audits/D49_DEFENSE_RIPOSTE_DATA.json

## D49 -> D50 Summary
- Self-duel draw rate: 100.0% -> 0.8%
- Self-duel average rounds: 80.00 -> 19.81
- Riposte damage share: 0.0% -> 17.7%
- Riposte execution rate: 4985.3% -> 351.0%
- Limit-exceeded duels: 25 -> 1

## Single Actions
| Build | D49 def. | D50 def. | Delta | D49 hit. | D50 hit. | D49 riposte | D50 riposte |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 0.0% | 9.1% | 9.1% | 100.0% | 90.9% | 0.0% | 0.0% |
| B | 100.0% | 35.8% | -64.2% | 0.0% | 64.2% | 0.0% | 0.0% |
| C | 100.0% | 47.3% | -52.7% | 0.0% | 52.7% | 0.0% | 0.0% |
| D | 100.0% | 59.6% | -40.4% | 0.0% | 40.4% | 0.0% | 0.0% |
| F | 100.0% | 49.1% | -50.9% | 0.0% | 50.9% | 0.0% | 0.0% |
| G | 65.7% | 5.6% | -60.1% | 34.3% | 94.4% | 0.0% | 0.0% |

## Self Duels
| Build | D49 draw | D50 draw | D49 rounds | D50 rounds | D49 riposte | D50 riposte |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.0% | 0.0% | 8.01 | 8.21 | 0.0% | 0.0% |
| B | 100.0% | 3.0% | 80.00 | 43.00 | 0.0% | 0.0% |
| C | 100.0% | 0.0% | 80.00 | 12.60 | 0.0% | 5.9% |
| D | 100.0% | 0.0% | 80.00 | 9.57 | 0.0% | 47.0% |
| F | 100.0% | 0.0% | 80.00 | 14.06 | 0.0% | 0.0% |
| G | 10.0% | 0.0% | 15.29 | 3.66 | 0.0% | 0.0% |

## Riposte Comparison
| Build | D49 atk win | D50 atk win | D49 riposte | D50 riposte | D49 rounds | D50 rounds |
| --- | --- | --- | --- | --- | --- | --- |
| C | 0.0% | 49.0% | 0.0% | 6.7% | 80.00 | 12.00 |
| D | 0.0% | 51.0% | 0.0% | 49.0% | 80.00 | 9.21 |
| F | 0.0% | 51.0% | 0.0% | 2.6% | 80.00 | 13.40 |

## Problems
No balance blockers detected.

## Verdict
- DEFENSE_REBALANCE_ACCEPTABLE