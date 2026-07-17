# D41.2 Combat Runtime State Policy

## Cel

Ten etap ustala jedną zasadę domenową: przejściowy stan walki jest stanem runtime i nie należy do trwałego zapisu świata.

Po restarcie serwera, odtworzeniu snapshotu albo wczytaniu starszego zapisu Astergard ma zachować skutki zakończonych akcji, ale nie ma wznawiać niedokończonych rund walki.

## Podział stanu

### Dane trwałe

Zapisują się normalnie:

* zdrowie i kondycja,
* rany,
* śmierć lub życie,
* wyposażenie,
* przedmioty w lokacji,
* doświadczenie i inne trwałe efekty,
* stan świata wynikający z zakończonych działań.

### Dane nietrwałe

Nie są traktowane jako trwały stan walki:

* `active_fights`,
* `in_combat`,
* bieżący przeciwnik,
* numer rundy,
* chwilowa kolejność działań,
* rozpoczęty, ale niedokończony atak,
* przyszłe przygotowania technik,
* przyszłe krótkie cooldowny bojowe.

## Zachowanie po restarcie

Po utworzeniu nowej instancji serwera:

* `CombatManager.active_fights` zaczyna jako pusta kolekcja,
* żadna postać ani NPC nie jest odtwarzana jako uczestnik aktywnej walki,
* heartbeat nie kontynuuje starej rundy,
* trwałe rany i wyposażenie pozostają wczytane.

## Zachowanie starszych zapisów

Starsze snapshoty mogły zawierać pole `in_combat` albo stan pośredni. W tym etapie są one traktowane jako dane przejściowe, które po odczycie są czyszczone.

Jeżeli zapis zawiera dawny stan walki:

* wartość jest ignorowana albo normalizowana do stanu życia,
* nie powstaje zdarzenie `COMBAT_FLED` ani `COMBAT_ENDED`,
* nie ma narracyjnego „wznowienia” starcia,
* pozostałe trwałe dane pozostają nienaruszone.

## Polityka disconnectu

Obecna polityka nie wprowadza osobnego modelu link-dead.

Jeżeli klient rozłącza się w runtime:

* serwer zapisuje postać i świat,
* klient jest usuwany z listy aktywnych połączeń,
* jeżeli walka była aktywna, kanoniczne zakończenie następuje przez istniejące reguły domenowe po utracie uczestnika z listy aktywnych bohaterów,
* samo rozłączenie nie tworzy nowej walki i nie wznawia starej.

Jeżeli uczestnik zostaje całkowicie usunięty ze świata, walka musi być zamknięta przez kanoniczne zakończenie relacji.

## Wpływ na przyszłe rozszerzenia

Ta decyzja upraszcza późniejsze wpięcie technik, przygotowań i krótkich efektów czasowych:

* techniki mogą być obliczane wyłącznie w runtime,
* przerwane przygotowanie nie wymaga migracji historii walk,
* snapshot świata nie musi odtwarzać pół-rozpoczętej akcji bojowej.

## Niezmiennik implementacyjny

Wczytanie świata nie może ustawiać żadnej postaci ani NPC jako aktywnie walczących.

Trwałe efekty walki pozostają zapisane, ale sama walka nie.
