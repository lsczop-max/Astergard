# D41.1 Combat Lifecycle Fixes

## Zakres

Ten etap usuwał trzy blokery wykryte w audycie D41:

* `zabij` nie włączał pełnego cyklu walki,
* `weapon()` mógł wybierać broń z inventory zamiast z aktywnego wyposażenia,
* `ucieczka` nie zamykała walki po skutecznym ruchu.

Nie zmieniano wzorów trafienia, obrony, obrażeń, ran ani balansu.

## Stan przed zmianą

### Komenda `zabij`

`zabij` wykonywał pojedynczy atak przez `CombatApplicationService.attack_npc()`.
Nie przechodził przez kanoniczny start starcia, więc gracz nie trafiał do tego samego combat loop co NPC.

### Aktywna broń

`Character.weapon()` potrafił sięgnąć do inventory.
To zacierało granicę między bronią posiadaną a bronią faktycznie używaną.

### Ucieczka

Skuteczna ucieczka zmieniała pokój, ale nie czyściła relacji bojowych.
Heartbeat mógł nadal widzieć aktywne starcie po opuszczeniu lokacji.

## Kanoniczne rozpoczęcie walki

Docelowy przepływ gracza:

```text
walidacja celu
    ↓
kanoniczny start walki w domenie
    ↓
ustawienie stanu obu stron
    ↓
opcjonalny pierwszy cios
    ↓
kolejne rundy przez heartbeat
```

W tym etapie kanonicznym początkiem starcia jest `CombatManager.start_fight()`.
Metoda:

* rejestruje relację w `active_fights`,
* ustawia `in_combat` po obu stronach,
* nie duplikuje relacji przy ponownym użyciu `zabij`,
* nie daje darmowego dodatkowego ciosu przy już aktywnej walce.

## Kanoniczne zakończenie walki

Docelowy przepływ zakończenia:

```text
walidacja możliwości zakończenia
    ↓
usunięcie relacji z active_fights
    ↓
wyczyszczenie stanu obu stron
    ↓
emisja istniejących zdarzeń domenowych
    ↓
brak dalszych rund dla zakończonego starcia
```

Zakończenie realizuje `CombatManager.end_fight()`.
Metoda:

* usuwa relacje dla jednego uczestnika albo konkretnej pary,
* zachowuje spójność symetrii,
* czyści `in_combat` tylko dla uczestników bez pozostałych walk,
* nie próbuje zmieniać balansu ani resolvera.

## Aktywne wyposażenie

Po poprawce:

* `Character.weapon()` zwraca wyłącznie broń faktycznie wyposażoną w aktywnym slocie,
* `Character.shield()` zwraca wyłącznie rzeczywiście założoną tarczę,
* inventory-only nie liczy się jako aktywne uzbrojenie,
* nie dodawano drugiego systemu ekwipunku.

## Invarianty `active_fights`

Po D41.1 obowiązują następujące reguły:

* para walki występuje najwyżej raz,
* ponowne `zabij` nie tworzy nowej relacji,
* skuteczna ucieczka usuwa relacje dotyczące uciekającego,
* śmierć i rozdzielenie lokacji usuwają nieaktualne walki,
* heartbeat nie powinien przetwarzać zakończonego starcia.

## Znane ograniczenia

* D41.1 nie przebudowuje resolvera.
* D41.1 nie dodaje technik.
* D41.1 nie rozdziela jeszcze walki na intent/action/resolution.
* `CombatManager.start()` i `stop_for()` pozostają kompatybilnościowymi wejściami dla starszych ścieżek.

## Pozostałe problemy D41 na później

Wciąż otwarte pozostają głównie problemy wysokiego poziomu z audytu D41:

* utrwalanie aktywnych walk w snapshotcie świata,
* dalsze rozdzielenie obron i obliczeń na czytelniejsze etapy,
* lepszy model walki grupowej,
* późniejsza integracja technik z D36-D38.
