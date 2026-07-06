# AUDIT D35.1F — Kopalnia Żelaza i Jaskinie Wilków

## Cel
D35.1F domyka dwa brakujące biomy północno-wschodniego Regionu I: Kopalnię Żelaza oraz Jaskinie Wilków. Obszary nie są już placeholderami ani proceduralnym łańcuchem lokacji.

## Wykonane zmiany
- Dodano 35 ręcznie nazwanych lokacji Kopalni Żelaza (`390-424`).
- Dodano 20 ręcznie nazwanych lokacji Jaskiń Wilków (`455-474`).
- Dodano opisy, inspectables, podstawowe przedmioty i ukryte elementy.
- Dodano wertykalną topologię kopalni: powierzchnia, górne chodniki, drugi poziom i głębokie sztolnie.
- Dodano organiczną topologię jaskiń: legowiska, ślepe jamy, rozgałęzienia i skróty.
- Zastąpiono proceduralny graf tych obszarów ręcznie projektowanymi połączeniami.
- Dodano testy regresyjne `tests/test_d35_1f_mines_caves_world_rewrite.py`.

## Krytyczna ocena
Mapa Kopalni i Jaskiń jest już sensownym szkieletem gameplayowym, ale nadal nie jest pełnym dungeonem produkcyjnym. Brakuje NPC, bossów, blokad, kluczy, dropu, pułapek, skryptowanych wydarzeń i powiązanych questów. To powinno wejść dopiero w D36, po zamknięciu całej mapy Regionu I.

## Następny etap
D35.1G — Ruiny Karshold i Bagna Hookri.
