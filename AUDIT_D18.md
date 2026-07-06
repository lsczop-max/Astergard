# AUDIT D18 — NPC threat tiers and archetype balance

## Cel
D18 wprowadza jawne klasy zagrożenia NPC: `trash`, `standard`, `elite`, `boss`, żeby przeciwnicy nie różnili się tylko nazwą i statystykami zaszytymi w fabryce.

## Zmiany wykonane
- Dodano `astergard/npcs/threat.py`.
- Dodano `ThreatProfile` oraz mapowanie `NPC_THREAT_BY_VNUM`.
- Rozszerzono `NPC` o `threat_tier` i `threat_label`.
- `NPCFactory` finalizuje NPC przez profil zagrożenia.
- Dodano bossa `warband_captain`.
- Profil zagrożenia wpływa na statystyki, kondycję, obrażenia, ochronę i czas respawnu.
- Snapshot świata zapisuje `threat_tier`, `threat_label` oraz styl walki NPC.
- Rozszerzono symulacje balansu o scenariusze threat-tier.
- Dodano testy `tests/test_d18_npc_threat_tiers.py`.

## Wynik testów
```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 68 tests in 1.373s
OK
```

## Wynik symulacji
Wygenerowano `COMBAT_BALANCE_REPORT_D18.md` dla 1000 walk na scenariusz.

Najważniejsza obserwacja: boss (`warband_captain`) ma 100% zwycięstw przeciwko testowemu graczowi. To jest dopuszczalne dla klasy `boss`, ale nie powinno być normą dla zwykłych bossów fabularnych bez mechanik drużynowych. W D19 należy dodać mechaniki drużyny albo obniżyć boss-tier dla solo contentu.

## Krytyczna ocena
D18 dodaje potrzebną warstwę projektową dla NPC, ale balans jest nadal jednowymiarowy: profil zagrożenia skaluje liczby, a nie zachowania. Brakuje jeszcze:
- osobnych taktyk AI per tier,
- oznaczenia w `look`, że NPC jest groźny,
- tabeli loot/reward zależnej od tieru,
- reguł, które bossy są solo, a które drużynowe,
- kontroli spawn density na poziomie zagrożenia regionu.

## Następny etap
D19 — loot/reward tables per threat tier oraz czytelna prezentacja zagrożenia w lokacji.
