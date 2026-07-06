# Combat Balance Report

| Scenario | Iterations | Attacker win | Defender win | Draw | Avg rounds | Avg attacker stamina | Avg defender stamina |
|---|---:|---:|---:|---:|---:|---:|---:|
| player_balanced_vs_wolf | 1000 | 66.0% | 22.6% | 11.4% | 22.7 | 45.3 | 6.0 |
| player_defensive_vs_troll | 1000 | 46.1% | 53.8% | 0.1% | 14.9 | 51.7 | 127.2 |
| player_offensive_vs_soldier | 1000 | 63.0% | 28.7% | 8.3% | 20.4 | 34.5 | 57.3 |
| style_zrownowazony_vs_balanced | 1000 | 43.6% | 47.3% | 9.1% | 22.4 | 40.7 | 40.9 |
| style_ofensywny_vs_balanced | 1000 | 49.9% | 45.5% | 4.6% | 17.6 | 37.7 | 50.8 |
| style_defensywny_vs_balanced | 1000 | 39.1% | 43.3% | 17.6% | 28.6 | 33.4 | 33.2 |
| style_ostrozny_vs_balanced | 1000 | 51.9% | 36.2% | 11.9% | 24.7 | 37.2 | 38.0 |
| style_brutalny_vs_balanced | 1000 | 57.2% | 39.4% | 3.4% | 16.4 | 40.8 | 53.4 |
| threat_trash_wolf_vs_player | 1000 | 22.9% | 66.9% | 10.2% | 21.7 | 5.9 | 46.4 |
| threat_standard_soldier_vs_player | 1000 | 30.2% | 57.1% | 12.7% | 25.3 | 45.8 | 36.1 |
| threat_elite_troll_vs_player | 1000 | 51.9% | 48.0% | 0.1% | 13.7 | 133.3 | 56.2 |
| threat_boss_captain_vs_player | 1000 | 100.0% | 0.0% | 0.0% | 14.0 | 184.1 | 58.0 |

## Threat tiers
- `trash`: pomniejszy przeciwnik; stat -1, stamina -10, damage +0, protection +0.
- `standard`: standardowy przeciwnik; stat +0, stamina +0, damage +0, protection +0.
- `elite`: elitarny przeciwnik; stat +2, stamina +20, damage +1, protection +1.
- `boss`: boss; stat +4, stamina +50, damage +2, protection +2.

## Interpretation
- A scenario is suspicious when one side exceeds 85% wins unless it is intentionally asymmetric.
- Draw rate above 20% means fights are too slow or insufficiently lethal.
- Average rounds above 25 for ordinary encounters should trigger review.