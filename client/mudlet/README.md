# Astergard Mudlet Client

Stabilny pakiet kliencki dla Mudleta 4.x.

## Wymagania

- Mudlet 4.12.0 lub nowszy
- Włączone GMCP
- Dostęp do GitHuba lub surowych plików `raw.githubusercontent.com`

## Instalacja

Wklej w Mudlecie jedną komendę Lua:

```lua
local home = getMudletHomeDir() .. "/Astergard"
if type(lfs) == "table" and lfs.mkdir then lfs.mkdir(home) end
downloadFile("https://raw.githubusercontent.com/lsczop-max/Astergard/develop/client/mudlet/installer.lua", home .. "/installer.lua")
tempTimer(2, function() dofile(home .. "/installer.lua") end)
```

Po pobraniu instalatora uruchomi się on sam i dociągnie resztę plików do profilu Mudleta.
Po pierwszej instalacji pakiet powinien ładować się automatycznie przy starcie profilu.

## Aktualizacja

- `/ast_sprawdz_aktualizacje`
- `/ast_aktualizuj`

Aktualizator pobiera `manifest.json`, porównuje wersje i aktualizuje pliki dopiero po potwierdzeniu.

## Komendy

- `/ast_wersja`
- `/ast_konfiguracja`
- `/ast_gui_on`
- `/ast_gui_off`
- `/ast_mapa`
- `/ast_mapa_centruj`
- `/ast_mapa_info`
- `/ast_mapa_przeladuj`
- `/ast_numpad_on`
- `/ast_numpad_off`
- `/ast_numpad_test`
- `/ast_sprawdz_aktualizacje`
- `/ast_aktualizuj`

## Numpad

- `8` -> północ
- `2` -> południe
- `4` -> zachód
- `6` -> wschód
- `7` -> północny zachód
- `9` -> północny wschód
- `1` -> południowy zachód
- `3` -> południowy wschód
- `5` -> rozejrzyj się
- `*` -> góra
- `/` -> dół
- `0` -> przejście specjalne

## Mapa

Mapa jest generowana z danych świata serwera:

`astergard.world.manager.WorldManager -> tools.export_mudlet_map -> client/mudlet/maps/astergard_map.json`

Klient importuje mapę z JSON-a i ustawia aktualny pokój na podstawie trwałego identyfikatora lokacji.

## Ograniczenia

- Pierwsza wersja nie automatyzuje walki.
- Aktualizator działa przez pobieranie plików, nie przez ciche samouaktualnianie.
- Binarny format mapy Mudleta (`.dat`) nie jest źródłem prawdy; źródłem prawdy jest JSON eksportowany z serwera.
