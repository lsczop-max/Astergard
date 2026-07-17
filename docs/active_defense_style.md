# Active Defense Style

## Cel

Aktywny styl obrony jest jawną, wybieraną przez postać preferencją określającą podstawowy sposób reagowania na ataki.
Nie zastępuje on znanych specjalizacji obronnych. Porządkuje tylko to, która obrona jest w danym momencie podstawową obroną postaci.

## Różnica między specjalizacją a stylem

- Specjalizacja obronna opisuje, czego postać się nauczyła.
- Aktywny styl obrony opisuje, jak postać przede wszystkim próbuje odeprzeć cios.

Postać może znać kilka specjalizacji, ale aktywnie używa tylko jednego stylu.

## Mapowanie

- `uniki` → `DODGE`
- `parowanie` → `PARRY`
- `tarcze` → `SHIELD`

Nazwy gracza są naturalne i diegetyczne. Identyfikatory techniczne pozostają w warstwie domenowej i serializacji.

## Warunki wyboru

Wyboru stylu można dokonać tylko wtedy, gdy:

- postać zna odpowiadającą specjalizację obronną;
- styl istnieje w katalogu;
- postać nie jest martwa;
- stan wyposażenia nie przeczy stylowi;
- wybór nie jest tożsamy z obecnym ustawieniem.

Warunki sprzętowe:

- `DODGE`: wymaga jedynie znanej specjalizacji uniku;
- `PARRY`: wymaga aktywnej broni i tagu `parry_capable` w profilu broni; legacy weapons zachowują zgodność z wcześniejszymi zapisami;
- `SHIELD`: wymaga aktywnie wyposażonej tarczy i braku aktywnej broni dwuręcznej.

## Zachowanie resolvera

Resolver obrony działa w dwóch trybach:

- `active_defense_style` ustawiony: wykonywana jest jedna jawna próba odpowiadająca stylowi;
- `active_defense_style = None`: działa tryb legacy, zachowujący dawną kolejność obron.

Tryb legacy pozostaje wyłącznie dla zgodności starszych zapisów. Nie jest docelowym sposobem gry.

## Serializacja

`active_defense_style` jest zapisywany jako część stanu postaci.

- brak pola → `None`;
- nieznana wartość → czyszczenie przy odczycie i ostrzeżenie diagnostyczne;
- wartości techniczne są normalizowane do kanonicznych nazw stylów.

## NPC

NPC mogą mieć zapamiętany aktywny styl obrony.
Jeżeli nie mają preferencji, korzystają z trybu legacy.
AI nie wybiera jeszcze stylu taktycznie.

## Komendy gracza

Podstawowa komenda:

- `bron sie unikiami`
- `bron sie parowaniem`
- `bron sie tarczą`

Aliasowe formy:

- `ustaw obrone uniki`
- `ustaw obrone parowanie`
- `ustaw obrone tarcza`

Komenda służy do ustawienia preferencji, nie do wykonywania obrony wprost.

## Ograniczenia obecnego etapu

- brak riposty;
- brak kontrataku;
- brak aktywnego wyboru obrony na poziomie pojedynczego ataku;
- brak automatycznej zmiany stylu przez AI;
- brak zmian w matematyce trafienia, obrażeń, pancerza i ran.

## Znaczenie dla przyszłych etapów

Aktywny styl obrony tworzy stabilny punkt wejścia dla późniejszych reakcji bojowych:

- riposty;
- kontrataku;
- reakcji zależnych od stylu;
- technik obronnych.

W D46 po udanym parowaniu lub innej skutecznej obronie system reakcji może rozpoznać dostępność dalszego działania, ale nie wykonuje go automatycznie. Styl obrony nadal opisuje podstawową preferencję, a nie reakcję samą w sobie.
