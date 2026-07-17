# D58.1 Rewrite Order

Kolejność przebudowy regionów wyznaczona przez:
1. znaczenie dla pierwszych godzin gry
2. natężenie ruchu graczy
3. liczbę problemów P0/P1
4. zależności przestrzenne
5. możliwość przetestowania pełnej trasy

## Proponowana kolejność
1. Centrum_Twierdza - P0=0, P1=36, średnia=55.87, coverage=60
2. Podgrodzie - P0=0, P1=14, średnia=43.7, coverage=20
3. Trakty - P0=0, P1=33, średnia=44.73, coverage=45
4. Boczne_Drogi - P0=0, P1=29, średnia=20.5, coverage=30
5. Forteca_Dungrim - P0=0, P1=15, średnia=35.07, coverage=15
6. Straznica_Przeleczy - P0=0, P1=10, średnia=34.8, coverage=10
7. Haldun - P0=0, P1=10, średnia=52.2, coverage=15
8. Osada_Mysliwych - P0=0, P1=14, średnia=30.8, coverage=15
9. Puszcza_Ciszy - P0=0, P1=70, średnia=17.21, coverage=70
10. Knieja_Cichych_Sciezek - P0=0, P1=53, średnia=21.87, coverage=55
11. Gory_Mekhara - P0=0, P1=55, średnia=7.24, coverage=55
12. Kopalnia_Zelaza - P0=0, P1=33, średnia=24.91, coverage=35
13. Ruiny_Karshold - P0=0, P1=30, średnia=17.03, coverage=30
14. Jaskinie_Wilkow - P0=0, P1=20, średnia=12.2, coverage=20
15. Bagna_Hookri - P0=0, P1=25, średnia=5, coverage=25

## Zależności
- Najpierw centrum i podgrodzie: tam gracz uczy się rytmu ruchu i orientacji.
- Potem trakty oraz strefy przejściowe: pozwalają przetestować spójność przejść na dłuższej trasie.
- Następnie regiony wysokiej i niskiej dostępności, gdzie testy są wciąż proste do przejścia.
- Na końcu obszary odcięte, długie lub ciężkie w testowaniu regresji.
