from __future__ import annotations

from collections.abc import Awaitable, Callable

from astergard.server.context import GameContext
from astergard.combat.manager import COMBAT_STYLES, normalize_combat_style
from astergard.characters.creation import ORIGIN_DEFINITIONS
from astergard.characters.professions import profession_label
from astergard.rules.combat_specialization import defense_style_label
from astergard.rules.skills import all_skill_definitions
from astergard.narrative import describe_kondycja, describe_skill_level, describe_stat, join_prose

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def build_character_sheet_handlers() -> dict[str, CommandHandler]:
    def _identity_lines(ctx: GameContext) -> list[str]:
        origin = ORIGIN_DEFINITIONS.get(ctx.character.origin)
        origin_name = origin.label if origin is not None else (ctx.character.origin or "brak")
        lines = [
            f"Nazywasz się {ctx.character.name or ctx.character.username}.",
            f"Masz {ctx.character.age or 'nieznany'} lat.",
            f"Twoje pochodzenie to {origin_name}.",
        ]
        if ctx.character.birth_region:
            lines.append(f"Twoim miejscem urodzenia jest {ctx.character.birth_region}.")
        if ctx.character.gender_id:
            lines.append(f"Płeć: {ctx.character.gender_description}.")
        return lines

    def _background_lines(ctx: GameContext) -> list[str]:
        origin = ORIGIN_DEFINITIONS.get(ctx.character.origin)
        origin_name = origin.label if origin is not None else (ctx.character.origin or "brak")
        lines = [
            f"Ścieżka główna: {profession_label(ctx.character.main_profession)}.",
            f"Ścieżka poboczna: {profession_label(ctx.character.secondary_profession)}.",
            f"Reputacja startowa: {ctx.character.starting_reputation}.",
            f"Reputacja globalna: {ctx.character.global_reputation}.",
        ]
        if origin_name:
            lines.append(f"Korzenie: {origin_name}.")
        return lines

    async def cmd_postac(ctx: GameContext, arg: str | None, index: int) -> str:
        identity = _identity_lines(ctx)
        stride = "pewnym, spokojnym krokiem" if ctx.character.stats.zrecznosc >= 10 else "ostrożnym, wyważonym krokiem"
        body = [
            f"Przed tobą stoi {ctx.character.name or ctx.character.username}.",
            *identity[1:],
            f"Sposób obrony: {defense_style_label(ctx.character.active_defense_style)}.",
            f"Poruszasz się {stride}.",
        ]
        return "\n".join(body)

    async def cmd_score(ctx: GameContext, arg: str | None, index: int) -> str:
        stats = ctx.character.stats
        return (
            "Kto jesteś:\n"
            + "\n".join(_identity_lines(ctx))
            + "\n\n"
            f"Siła: {describe_stat(stats.sila)}\n"
            f"Zręczność: {describe_stat(stats.zrecznosc)}\n"
            f"Wytrzymałość: {describe_stat(stats.wytrzymalosc)}\n"
            f"Percepcja: {describe_stat(stats.percepcja)}\n"
            f"Siła woli: {describe_stat(stats.sila_woli)}\n"
            f"Kondycja: {describe_kondycja(stats.kondycja, stats.max_kondycja)}\n"
            f"Styl walki: {COMBAT_STYLES.get(ctx.character.combat_style, COMBAT_STYLES['zrownowazony']).label}.\n"
            f"Sposób obrony: {defense_style_label(ctx.character.active_defense_style)}."
        )

    async def cmd_profile(ctx: GameContext, arg: str | None, index: int) -> str:
        starter_inventory = ", ".join(item.display_name() for item in ctx.character.inventory) or "brak"
        return (
            "O tobie:\n"
            + "\n".join(_identity_lines(ctx))
            + "\n\n"
            "Twoja droga:\n"
            + "\n".join(_background_lines(ctx))
            + "\n\n"
            f"Na początku niesiesz: {starter_inventory}.\n"
            f"Na sobie masz teraz: {ctx.character.equipment_summary()}\n"
            f"Sposób obrony: {defense_style_label(ctx.character.active_defense_style)}."
        )

    async def cmd_skills(ctx: GameContext, arg: str | None, index: int) -> str:
        lines: list[str] = []
        for definition in all_skill_definitions():
            level = ctx.character.skills.level(definition.key)
            lines.append(f"{definition.label}: {describe_skill_level(level)}.")
        return "\n".join(lines)


    async def cmd_style(ctx: GameContext, arg: str | None, index: int) -> str:
        if not arg:
            available = ", ".join(COMBAT_STYLES)
            return f"Walczysz teraz {COMBAT_STYLES[ctx.character.combat_style].label}. Znasz też style: {available}."
        style = normalize_combat_style(arg)
        if style not in COMBAT_STYLES:
            available = ", ".join(COMBAT_STYLES)
            return f"Nie rozpoznajesz takiego stylu walki. Znasz style: {available}."
        ctx.character.combat_style = style
        return f"Przyjmujesz {COMBAT_STYLES[style].label}."

    async def cmd_reputation(ctx: GameContext, arg: str | None, index: int) -> str:
        local = join_prose([f"{zone} {value:+d}" for zone, value in sorted(ctx.character.local_reputation.items())]) or "brak wyraźnych śladów"
        crimes = join_prose([f"{crime} {count:+d}" for crime, count in sorted(ctx.character.crimes.items())]) or "brak"
        wanted = "\n".join(ctx.character.wanted_posts[:5]) or "brak"
        factions = join_prose([f"{name} {value:+d}" for name, value in sorted(ctx.character.reputation.items())]) or "brak"
        return (
            f"Twoje imię w świecie: {ctx.character.title}.\n"
            f"Rozgłos: {ctx.character.renown}.\n"
            f"Jak mówią o tobie ludzie: {ctx.character.global_reputation}.\n\n"
            f"W różnych miejscach pamiętają cię tak: {local}.\n"
            f"Na twoim koncie zapisano: {crimes}.\n\n"
            f"Jeśli ktoś cię szuka, zostawia takie ślady:\n{wanted}\n\n"
            f"Stosunek frakcji do ciebie:\n{factions}"
        )

    return {"score": cmd_score, "profile": cmd_profile, "postac": cmd_postac, "skills": cmd_skills, "style": cmd_style, "reputation": cmd_reputation}
