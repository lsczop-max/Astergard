from __future__ import annotations

from dataclasses import dataclass

from astergard.characters.models import Character
from astergard.items.models import Item

@dataclass(frozen=True)
class Recipe:
    id: str
    output: Item
    ingredients: dict[str, int]

RECIPES = {
    "skorzana_latka": Recipe("skorzana_latka", Item("skórzana łatka", "Naprawcza łatka z grubej skóry.", 0.1, 3, "leather_patch"), {"wilcza skóra": 1}),
    "prosta_mikstura": Recipe("prosta_mikstura", Item("prosta mikstura", "Napar przywracający siły.", 0.2, 8, "simple_potion", "potion", is_consumable=True, effects_on_consume={"restore_stamina": 20}), {"srebrny pierścień": 1}),
}

class CraftingService:
    def craft(self, char: Character, recipe_id: str) -> str:
        recipe = RECIPES.get(recipe_id)
        if not recipe:
            return "Nie znasz takiej receptury."
        for name, count in recipe.ingredients.items():
            if sum(1 for item in char.inventory if item.name == name) < count:
                return "Brakuje składników."
        for name, count in recipe.ingredients.items():
            removed = 0
            for item in list(char.inventory):
                if item.name == name and removed < count:
                    char.inventory.remove(item)
                    removed += 1
        char.inventory.append(recipe.output)
        return f"Tworzysz: {recipe.output.name}."
