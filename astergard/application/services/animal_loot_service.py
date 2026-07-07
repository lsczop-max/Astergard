from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from astergard.items.models import Item
from astergard.npcs.models import NPC


@dataclass(frozen=True, slots=True)
class DropEntry:
    chance: float
    factory: Callable[[], Item]
    min_count: int = 1
    max_count: int = 1


class AnimalLootService:
    def build_loot(self, npc: NPC) -> list[Item]:
        table = self._table_for(npc.vnum)
        if not table:
            return []
        loot: list[Item] = []
        for entry in table:
            if random.random() > entry.chance:
                continue
            count = entry.min_count if entry.min_count >= entry.max_count else random.randint(entry.min_count, entry.max_count)
            for _ in range(max(1, count)):
                loot.append(entry.factory())
        return loot

    def _table_for(self, vnum: str) -> tuple[DropEntry, ...]:
        return self._tables().get(vnum, ())

    def _tables(self) -> dict[str, tuple[DropEntry, ...]]:
        return {
            "wolf": (
                DropEntry(0.9, lambda: self._make_item("wilcza skóra", "Szorstka skóra zdjęta z wilka.", 1.0, 8, "wolf_pelt")),
                DropEntry(0.8, lambda: self._make_item("wilcze mięso", "Kawał mięsa z wilka, jeszcze nadający się do obróbki.", 0.9, 6, "wolf_meat", "food", True, {"restore_stamina": 8})),
                DropEntry(0.45, lambda: self._make_item("wilcze kły", "Długie kły wilka, przydatne do trofeów i prostych narzędzi.", 0.2, 5, "wolf_fangs")),
                DropEntry(0.35, lambda: self._make_item("wilcze pazury", "Ostre pazury wilka, małe, ale cenione przez łowców.", 0.1, 4, "wolf_claws")),
                DropEntry(0.65, lambda: self._make_item("wilcze futro", "Gęste futro z wilka, dobre na kaptur albo podszewkę.", 0.8, 7, "wolf_fur", "armor")),
            ),
            "puszcza_szczur": (
                DropEntry(0.9, lambda: self._make_item("skóra szczura", "Cienka, ale użyteczna skóra zdjęta z leśnego szczura.", 0.2, 2, "forest_rat_hide")),
                DropEntry(0.8, lambda: self._make_item("mięso szczura", "Skromna porcja mięsa z leśnego szczura.", 0.25, 2, "forest_rat_meat", "food", True, {"restore_stamina": 3})),
                DropEntry(0.45, lambda: self._make_item("szczurze zęby", "Małe zęby leśnego szczura, bardziej trofeum niż surowiec.", 0.05, 2, "forest_rat_teeth")),
            ),
            "puszcza_kruk": (
                DropEntry(0.85, lambda: self._make_item("pióra kruka", "Czarne pióra kruka, lekkie i cenione przez skrybów oraz rzemieślników.", 0.08, 3, "forest_raven_feathers")),
                DropEntry(0.55, lambda: self._make_item("mięso kruka", "Twarde mięso kruka, tylko dla cierpliwych kucharzy.", 0.3, 1, "forest_raven_meat", "food", True, {"restore_stamina": 2})),
                DropEntry(0.3, lambda: self._make_item("krucze pazury", "Krzywe pazury kruka, małe, ale ostre.", 0.04, 2, "forest_raven_claws")),
            ),
            "puszcza_lis": (
                DropEntry(0.9, lambda: self._make_item("lisia skóra", "Gęsta skóra lisa o rudym odcieniu.", 0.9, 7, "forest_fox_hide")),
                DropEntry(0.75, lambda: self._make_item("lisie mięso", "Ciemniejsze mięso lisa, po obróbce jeszcze nadaje się do jedzenia.", 0.8, 5, "forest_fox_meat", "food", True, {"restore_stamina": 6})),
                DropEntry(0.45, lambda: self._make_item("lisie kły", "Smukłe kły lisa, dobre na drobne trofea.", 0.08, 3, "forest_fox_fangs")),
                DropEntry(0.5, lambda: self._make_item("lisie futro", "Miękkie futro lisa, pożądane przez handlarzy skór.", 0.7, 6, "forest_fox_fur", "armor")),
            ),
            "puszcza_pies_dziki": (
                DropEntry(0.88, lambda: self._make_item("skóra dzikiego psa", "Twarda skóra dzikiego psa, dobra po garbarni.", 1.1, 8, "forest_wild_dog_hide")),
                DropEntry(0.8, lambda: self._make_item("mięso dzikiego psa", "Mięso dzikiego psa, twarde, ale użyteczne.", 1.0, 6, "forest_wild_dog_meat", "food", True, {"restore_stamina": 7})),
                DropEntry(0.4, lambda: self._make_item("dzikie kły", "Kły dzikiego psa, krótsze niż wilcze, ale wciąż groźne.", 0.12, 4, "forest_wild_dog_fangs")),
                DropEntry(0.45, lambda: self._make_item("dzikie pazury", "Pazury dzikiego psa, przydatne jako małe trofea.", 0.06, 3, "forest_wild_dog_claws")),
                DropEntry(0.55, lambda: self._make_item("dzikie futro", "Szorstkie futro dzikiego psa, warte wyprawienia.", 0.8, 6, "forest_wild_dog_fur", "armor")),
            ),
            "puszcza_wilk_mlody": (
                DropEntry(0.88, lambda: self._make_item("skóra młodego wilka", "Szara skóra młodego wilka.", 0.95, 7, "forest_young_wolf_hide")),
                DropEntry(0.78, lambda: self._make_item("mięso młodego wilka", "Nieduży kawał mięsa z młodego wilka.", 0.85, 5, "forest_young_wolf_meat", "food", True, {"restore_stamina": 7})),
                DropEntry(0.42, lambda: self._make_item("wilcze kły", "Kły młodego wilka, jeszcze niepełne, ale ostre.", 0.1, 4, "forest_young_wolf_fangs")),
                DropEntry(0.38, lambda: self._make_item("wilcze pazury", "Młode pazury wilka, małe lecz ostre.", 0.05, 3, "forest_young_wolf_claws")),
                DropEntry(0.58, lambda: self._make_item("wilcze futro", "Gęste futro młodego wilka, dobre na podszycie.", 0.7, 6, "forest_young_wolf_fur", "armor")),
            ),
            "puszcza_wilk": (
                DropEntry(0.92, lambda: self._make_item("skóra wilka", "Gruba skóra zdjęta z leśnego wilka.", 1.1, 8, "forest_wolf_hide")),
                DropEntry(0.82, lambda: self._make_item("mięso wilka", "Pojedyncza porcja mięsa z wilka.", 0.95, 6, "forest_wolf_meat", "food", True, {"restore_stamina": 8})),
                DropEntry(0.48, lambda: self._make_item("wilcze kły", "Silne kły wilka, cenione przez łowców.", 0.12, 5, "forest_wolf_fangs")),
                DropEntry(0.4, lambda: self._make_item("wilcze pazury", "Ostre pazury wilka, dobre do trofeów.", 0.06, 4, "forest_wolf_claws")),
                DropEntry(0.7, lambda: self._make_item("wilcze futro", "Gęste futro leśnego wilka, bardzo pożądane przez handlarzy skór.", 0.9, 8, "forest_wolf_fur", "armor")),
            ),
            "puszcza_jelen": (
                DropEntry(0.9, lambda: self._make_item("skóra jelenia", "Miękka skóra zdjęta z jelenia.", 1.2, 9, "deer_hide")),
                DropEntry(0.75, lambda: self._make_item("mięso jelenia", "Pewna porcja jeleniny, przydatna do kuchni i suszenia.", 1.1, 7, "deer_meat", "food", True, {"restore_stamina": 9})),
                DropEntry(0.45, lambda: self._make_item("rogi jelenia", "Ciężkie rogi jelenia, dobre na trofeum.", 1.4, 10, "deer_horns")),
            ),
            "puszcza_dzik": (
                DropEntry(0.85, lambda: self._make_item("skóra dzika", "Gruba skóra dzika, szorstka i ciężka.", 1.5, 10, "boar_hide")),
                DropEntry(0.75, lambda: self._make_item("mięso dzika", "Twarde mięso dzika, po odpowiednim przygotowaniu bardzo sycące.", 1.4, 8, "boar_meat", "food", True, {"restore_stamina": 10})),
                DropEntry(0.5, lambda: self._make_item("kły dzika", "Ciężkie kły dzika, cenione przez łowców i rzemieślników.", 0.3, 11, "boar_tusks")),
            ),
            "bagna_zaba": (
                DropEntry(0.8, lambda: self._make_item("skóra żaby", "Wilgotna skóra stworzenia z mokradeł.", 0.2, 4, "frog_skin")),
                DropEntry(0.65, lambda: self._make_item("mięso żaby", "Niewielka porcja mięsa z bagiennej żaby.", 0.2, 3, "frog_meat", "food", True, {"restore_stamina": 4})),
            ),
            "mountain_troll": (
                DropEntry(0.8, lambda: self._make_item("skóra trolla", "Gruba, twarda skóra trolla górskiego.", 2.6, 18, "troll_hide")),
                DropEntry(0.7, lambda: self._make_item("mięso trolla", "Ciężkie mięso trolla, trudne do obróbki.", 2.4, 12, "troll_meat", "food", True, {"restore_stamina": 12})),
                DropEntry(0.4, lambda: self._make_item("pazury trolla", "Wielkie pazury trolla, bardziej groźne niż eleganckie.", 0.5, 10, "troll_claws")),
            ),
            "podgrodzie_ges": (
                DropEntry(0.95, lambda: self._make_item("pióra gęsi", "Lekka wiązka piór gęsich, dobra na wypchane poduszki albo lotki.", 0.1, 5, "goose_feathers")),
                DropEntry(0.7, lambda: self._make_item("mięso gęsi", "Mięso gęsi nadające się do pieczenia.", 0.8, 6, "goose_meat", "food", True, {"restore_stamina": 7})),
                DropEntry(0.45, lambda: self._make_item("skóra gęsi", "Cienka skóra i tłuszcz przydatny w prostych wyrobach.", 0.3, 4, "goose_skin")),
            ),
        }

    def _make_item(
        self,
        name: str,
        description: str,
        weight: float,
        value: int,
        vnum: str,
        item_type: str = "misc",
        is_consumable: bool = False,
        effects_on_consume: dict[str, int | str] | None = None,
    ) -> Item:
        return Item(
            name,
            description,
            weight,
            value,
            vnum,
            item_type,
            is_consumable=is_consumable,
            effects_on_consume=dict(effects_on_consume or {}),
        )
