# COMBAT_DESIGN_D51

## Cel

Rozdzielić walkę na:

- rozstrzygnięcie mechaniczne,
- semantyczny model zdarzenia,
- narrację zależną od perspektywy,
- kontrolę powtórzeń,
- warstwę integracji z event bus.

## Aktualny kształt

- `CombatManager` nadal odpowiada za inicjatywę, trafienie, aktywną obronę, pancerz, rany i śmierć.
- Wynik ataku jest teraz wzbogacany o `CombatEvent`.
- `CombatNarrator` generuje trzy perspektywy komunikatu:
  - napastnik,
  - obrońca,
  - obserwator.

## Zasady projektowe

- Tekst nie jest źródłem prawdy.
- Zdarzenie mechaniczne opisuje to, co naprawdę zaszło.
- Narracja tylko interpretuje wynik.
- Powtórzenia są tłumione na poziomie narratora, bez psucia sensu zdarzenia.
- Rodzina broni jest rozpoznawana z metadanych i z nazwy, jeśli metadane są niepełne.

## Zmiany mechaniczne wykonane w tym etapie

- Dodano `CombatEvent`.
- Dodano `CombatNarrator`.
- Ujednolicono perspektywy komunikatów.
- Poprawiono aktywną obronę tak, by liczyła prawidłową relację napastnik-obrońca.
- Wzmocniono rozpoznawanie rodzin broni.
- Zmniejszono zbyt agresywną lethality w modelu ran.
- Zbalansowano berserkera w helperze symulacji balansowej.

## Pozostałe kroki

- Rozbudować model ran o stan funkcjonalny kończyn i krwawienie.
- Dodać obciążenie pancerza jako realny czynnik w obronie i ucieczce.
- Uzupełnić AI o reakcje na morale.
- Rozszerzyć narrację o otoczenie i świadków.
