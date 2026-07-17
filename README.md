# Astergard MUD

Astergard to ręcznie rozwijany MUD fantasy w Pythonie 3.12.
Stawia na immersję, naturalny język poleceń, ręcznie pisany świat i stabilny rdzeń serwera.

## Uruchomienie

```bash
python3 main.py
```

Połączenie z drugiego terminala:

```bash
nc 127.0.0.1 4000
# albo
telnet 127.0.0.1 4000
```

Nowa postać zaczyna w karczmie, a tworzenie postaci odbywa się w dialogu z karczmarzem i kronikarzem, bez klasycznego menu kreatora.

Walka jest opisana narracyjnie: system rozróżnia perspektywę napastnika, obrońcy i obserwatora, a komunikaty wynikają z rzeczywistego rozstrzygnięcia mechanicznego.

## Najczęstsze komendy

- `spojrz`
- `postać`
- `cechy`
- `profil`
- `reputacja`
- `polnoc`, `poludnie`, `wschod`, `zachod`
- `gora`, `dol`
- `powiedz tekst`
- `ekwipunek`
- `stan`
- `pomoc zbroja`
- `zaloz miecz`
- `atakuj wilk`
- `styl ofensywny`
- `uciekaj polnoc`
- `rozmawiaj kupiec o wilki`
- `zbadaj`, `nasluchuj`, `nasluchaj`, `powachaj`, `dotknij`, `rozejrzyj`
- `zadania`
- `oferta`, `kup mikstura`, `sprzedaj chleb`
- `szukaj`
- `czaruj wzmocnienie`
- `zapisz`, `quit`
- `pomoc <komenda>`

## O projekcie

Astergard zachowuje własny świat, własne lore i własne rozwiązania. Dokumentacja historyczna oraz notatki z kolejnych iteracji są w plikach `AUDIT_*.md` i pozostałych dokumentach projektu.

## Klient Mudlet

Oficjalny pakiet kliencki Mudlet dla Astergardu znajduje się w:

- [client/mudlet/README.md](/home/lukasz/Dokumenty/astergard_d34_world_area/client/mudlet/README.md)

## Testy

```bash
ruff check .
mypy .
pytest
```
