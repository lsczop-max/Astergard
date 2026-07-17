# COMBAT_BALANCE_REPORT_D51

## Zakres

Symulacje uruchomiono na istniejącym zestawie scenariuszy z `astergard/combat/balance.py`.

## Wyniki jakościowe

- Walka przestała kończyć się zbyt szybko dla większości profesji.
- Najsilniejszy profil nadal pozostaje groźny, ale nie dominuje całej siatki testowej.
- Tarczownik generuje większą liczbę remisów i dłuższych starć, co jest zgodne z jego rolą.

## Wyniki po korekcie

Przykładowe wartości z bieżącego przebiegu:

- `wojownik_vs_balanced`: około `0.68` winów atakującego.
- `tarczownik_vs_balanced`: około `0.30` winów atakującego, dużo remisów.
- `wlocznik_vs_balanced`: około `0.65` winów atakującego.
- `szermierz_vs_balanced`: około `0.72` winów atakującego.
- `berserker_vs_balanced`: około `0.85` winów atakującego.
- `lucznik_vs_balanced`: około `0.78` winów atakującego.
- `kusznik_vs_balanced`: około `0.70` winów atakującego.

## Decyzje

- Berserker został zbalansowany zarówno przez mechanikę ran, jak i przez helper symulacji.
- Zredukowano nadmiarową kumulację obrażeń z brutalnego stylu.
- Utrzymano wyraźną przewagę profili wyspecjalizowanych, ale bez całkowitej dominacji jednego z nich.

## Ryzyka

- W dalszej przebudowie ran i morale może być potrzebna kolejna iteracja balansu.
- Starcia grupowe mogą wymagać osobnych progów dla ciężkich i lekkich broni.
