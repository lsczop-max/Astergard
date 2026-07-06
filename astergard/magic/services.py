from __future__ import annotations
import random
from astergard.characters.models import Character, Effect
from astergard.rules.magic import MagicRules, default_magic_rules

class MagicService:
    def __init__(self, rules: MagicRules | None = None) -> None:
        self.rules = rules or default_magic_rules()

    def add_or_refresh(self, char: Character, effect: Effect) -> None:
        for existing in char.active_effects:
            if existing.name == effect.name:
                existing.duration_ticks = effect.duration_ticks
                return
        current = getattr(char.stats, effect.modifier_stat)
        setattr(char.stats, effect.modifier_stat, current + effect.value)
        char.active_effects.append(effect)

    def cast_strength(self, caster: Character) -> str:
        if caster.stats.kondycja < self.rules.strength_spell_stamina_cost:
            return "Brakuje ci kondycji."
        caster.stats.kondycja -= self.rules.strength_spell_stamina_cost
        self.add_or_refresh(caster, Effect("Wzmocnienie", "sila", self.rules.strength_spell_bonus, self.rules.strength_spell_duration_ticks))
        return "<green>Czujesz, jak siła napływa do mięśni.</green>"

    def tick(self, char: Character) -> list[str]:
        messages: list[str] = []
        for effect in list(char.active_effects):
            effect.duration_ticks -= 1
            if effect.duration_ticks <= 0:
                setattr(char.stats, effect.modifier_stat, getattr(char.stats, effect.modifier_stat) - effect.value)
                char.active_effects.remove(effect)
                messages.append(f"Czujesz, że działanie {effect.name} dobiegło końca.")
        return messages

    def magic_bolt(self, caster: Character, defender: Character) -> str:
        if caster.stats.kondycja < self.rules.magic_bolt_stamina_cost:
            return "Brakuje ci kondycji."
        caster.stats.kondycja -= self.rules.magic_bolt_stamina_cost
        if caster.stats.sila_woli + random.randint(1, self.rules.magic_bolt_roll_sides) <= defender.stats.sila_woli + random.randint(1, self.rules.magic_bolt_roll_sides):
            return "Grot Źródła gaśnie, zanim dosięga celu."
        part = random.choice(list(defender.wounds.keys()))
        defender.wounds[part] = min(self.rules.max_wound_level, defender.wounds[part] + self.rules.magic_bolt_wound_increase)
        if random.random() < self.rules.backlash_chance:
            self.add_or_refresh(caster, Effect("Odrzut Źródła", "sila_woli", self.rules.backlash_willpower_penalty, self.rules.backlash_duration_ticks))
        return f"<red>Błękitny płomień uderza w {part} celu.</red>"
