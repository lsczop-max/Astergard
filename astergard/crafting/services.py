from __future__ import annotations

from dataclasses import dataclass

from astergard.characters.models import Character
from astergard.commands.polish import normalize_phrase, tokens_match
from astergard.items.models import Item


@dataclass(frozen=True, slots=True)
class Recipe:
    id: str
    output: Item
    ingredients: dict[str, int]
    aliases: tuple[str, ...] = ()
    required_skill: str | None = None
    minimum_skill_level: int = 0
    description: str = ""


def _recipe(
    recipe_id: str,
    output: Item,
    ingredients: dict[str, int],
    *,
    aliases: tuple[str, ...] = (),
    required_skill: str | None = None,
    minimum_skill_level: int = 0,
    description: str = "",
) -> Recipe:
    return Recipe(
        recipe_id,
        output,
        ingredients,
        aliases=aliases,
        required_skill=required_skill,
        minimum_skill_level=minimum_skill_level,
        description=description,
    )


RECIPES: dict[str, Recipe] = {
    "skorzana_latka": _recipe(
        "skorzana_latka",
        Item("skórzana łatka", "Naprawcza łatka z grubej skóry.", 0.1, 3, "leather_patch"),
        {"skóra wilka": 1},
        aliases=("łatka skórzana", "naprawa skóry"),
        required_skill="oprawianie",
        minimum_skill_level=1,
        description="Naprawia prostą odzież i lekkie rzemiosło skórzane.",
    ),
    "prosta_mikstura": _recipe(
        "prosta_mikstura",
        Item("prosta mikstura", "Napar przywracający siły.", 0.2, 8, "simple_potion", "potion", is_consumable=True, effects_on_consume={"restore_stamina": 20}),
        {"górskie zioła": 1},
        aliases=("mikstura", "napar", "ziołowy napar"),
        required_skill="pierwsza_pomoc",
        minimum_skill_level=1,
        description="Prosty napar zebrany w terenie.",
    ),
    "smolna_pochodnia": _recipe(
        "smolna_pochodnia",
        Item("smolna pochodnia", "Pochodnia dobrze trzymająca ogień w wilgotnym lesie.", 0.6, 4, "pitch_torch", "tool"),
        {"kawał smolnego drewna": 1, "świeca łojowa": 1},
        aliases=("pochodnia", "smolna latarnia"),
        required_skill="kowalstwo",
        minimum_skill_level=1,
        description="Pochodnia odporna na wilgoć i nocny wiatr.",
    ),
    "prowiant_podrozny": _recipe(
        "prowiant_podrozny",
        Item("prowiant podróżny", "Zapas jedzenia spięty tak, by przetrwał drogę.", 0.8, 6, "travel_ration", "food", is_consumable=True, effects_on_consume={"restore_stamina": 14}),
        {"chleb": 1, "sól w worku": 1},
        aliases=("racja", "prowiant", "zapas na droge"),
        description="Skromny, ale praktyczny posiłek na szlak.",
    ),
    "zszyta_sakwa": _recipe(
        "zszyta_sakwa",
        Item("zszyta sakwa", "Wzmocniona sakwa z nowymi szwami.", 0.9, 7, "stitched_sack", "tool", is_container=True, capacity=10),
        {"igła i nitka": 1, "sakwa podróżna": 1},
        aliases=("napraw sakwe", "sakwa", "sakwa zszyta"),
        required_skill="oprawianie",
        minimum_skill_level=2,
        description="Lżejszy sposób na naprawę pojemnika niż kupno nowego.",
    ),
    "ostrze_pilnikowe": _recipe(
        "ostrze_pilnikowe",
        Item("ostrzone ostrze", "Nóż z dopracowaną krawędzią tnącą.", 0.4, 9, "filed_blade", "weapon", "prawa_reka", damage_type="cieta", base_damage=3, reach=1, initiative_modifier=1, parry_bonus=1),
        {"pilnik": 1, "krótki nóż": 1},
        aliases=("ostrzenie", "ostrz", "noz"),
        required_skill="kowalstwo",
        minimum_skill_level=2,
        description="Drobna robota warsztatowa poprawiająca broń ręczną.",
    ),
    "torfowy_napar": _recipe(
        "torfowy_napar",
        Item("torfowy napar", "Gorzki napar z mokradła, tłumiący zmęczenie i chłód.", 0.2, 7, "bog_tea", "food", is_consumable=True, effects_on_consume={"restore_stamina": 16}),
        {"torfowe ziele": 1, "woda w bukłaku": 1},
        aliases=("napar z bagna", "napar torfowy"),
        required_skill="pierwsza_pomoc",
        minimum_skill_level=2,
        description="Praktyczny napój dla tych, którzy wracają z mokradła po zmroku.",
    ),
    "uszczelniona_sakwa": _recipe(
        "uszczelniona_sakwa",
        Item("uszczelniona sakwa", "Sakwa wzmocniona żywicą i świeżym przeszyciem.", 0.9, 11, "sealed_sack", "tool", is_container=True, capacity=12),
        {"sakwa podróżna": 1, "żywica sosnowa": 1},
        aliases=("napraw sakwe", "sakwa uszczelniona"),
        required_skill="oprawianie",
        minimum_skill_level=2,
        description="Daje pojemnikowi drugie życie bez kupowania nowego.",
    ),
    "latarnia_patrolowa": _recipe(
        "latarnia_patrolowa",
        Item("latarnia patrolowa", "Latarnia z grubszym szkłem i lepszym knotem.", 1.2, 12, "patrol_lantern", "tool"),
        {"stara latarnia": 1, "oliwa do lamp": 1},
        aliases=("latarnia", "lampa patrolowa"),
        required_skill="kowalstwo",
        minimum_skill_level=1,
        description="Lepsze światło na drogę, kładkę i wieczorny patrol.",
    ),
    "wzmocnione_rekawice": _recipe(
        "wzmocnione_rekawice",
        Item("wzmocnione rękawice", "Rękawice podszyte futrem i skórą.", 0.6, 13, "reinforced_gloves", "armor", "dlonie", protection=1),
        {"skórzane rękawice": 1, "skóra wilka": 1},
        aliases=("rekawice", "rękawice", "rękawice wzmocnione"),
        required_skill="oprawianie",
        minimum_skill_level=2,
        description="Nadają się do pracy w chłodzie i do marszu po trakcie.",
    ),
}


class CraftingService:
    def _find_recipe(self, recipe_id: str) -> Recipe | None:
        normalized = normalize_phrase(recipe_id, drop_stopwords=True)
        for recipe in RECIPES.values():
            names = {normalize_phrase(recipe.id, drop_stopwords=True), *(normalize_phrase(alias, drop_stopwords=True) for alias in recipe.aliases), normalize_phrase(recipe.output.name, drop_stopwords=True)}
            if normalized in names:
                return recipe
        return None

    def _missing_ingredients(self, char: Character, recipe: Recipe) -> list[str]:
        missing: list[str] = []
        for name, count in recipe.ingredients.items():
            owned = sum(1 for item in char.inventory if tokens_match(name, item.name) or (item.vnum is not None and tokens_match(name, item.vnum)))
            if owned < count:
                missing.append(f"{name} x{count - owned}")
        return missing

    def craft(self, char: Character, recipe_id: str) -> str:
        if not recipe_id:
            return "Co chcesz stworzyć?"
        recipe = self._find_recipe(recipe_id)
        if not recipe:
            known = ", ".join(recipe.output.name for recipe in RECIPES.values())
            return f"Nie znasz takiej receptury. Znane receptury to: {known}."
        if recipe.required_skill is not None and char.skills.level(recipe.required_skill) < recipe.minimum_skill_level:
            return "Nie masz jeszcze dość wprawy, by to wykonać."
        missing = self._missing_ingredients(char, recipe)
        if missing:
            return "Brakuje składników: " + ", ".join(missing) + "."
        for name, count in recipe.ingredients.items():
            removed = 0
            for item in list(char.inventory):
                if removed >= count:
                    break
                if tokens_match(name, item.name) or (item.vnum is not None and tokens_match(name, item.vnum)):
                    char.inventory.remove(item)
                    removed += 1
        char.inventory.append(recipe.output)
        if recipe.description:
            return f"Tworzysz {recipe.output.name}. {recipe.description}"
        return f"Tworzysz {recipe.output.name}."
