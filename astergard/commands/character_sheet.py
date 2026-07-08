from __future__ import annotations

from collections.abc import Awaitable, Callable

from astergard.server.context import GameContext
from astergard.combat.manager import COMBAT_STYLES, normalize_combat_style
from astergard.characters.creation import ORIGIN_DEFINITIONS
from astergard.characters.professions import profession_label
from astergard.rules.skills import all_skill_definitions

CommandHandler = Callable[[GameContext, str | None, int], Awaitable[str]]


def _skill_desc(level: int) -> str:
    if level <= 20:
        return "początkujący"
    if level <= 40:
        return "średni"
    if level <= 60:
        return "sprawny"
    if level <= 80:
        return "mistrzowski"
    return "legendarny"


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
        if ctx.character.culture:
            lines.append(f"Twoja kultura to {ctx.character.culture}.")
        if ctx.character.religion:
            lines.append(f"Wyznajesz: {ctx.character.religion}.")
        if ctx.character.gender_description:
            lines.append(f"Opis, jaki nosisz przy sobie: {ctx.character.gender_description}.")
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
        if ctx.character.appearance:
            lines.append(f"Wygląd: {ctx.character.appearance}.")
        if ctx.character.history:
            lines.append(f"Historia: {ctx.character.history}.")
        if origin_name:
            lines.append(f"Korzenie: {origin_name}.")
        return lines

    async def cmd_postac(ctx: GameContext, arg: str | None, index: int) -> str:
        return ctx.character.equipment_summary()

    async def cmd_score(ctx: GameContext, arg: str | None, index: int) -> str:
        stats = ctx.character.stats
        return (
            "Kto jesteś:\n"
            + "\n".join(_identity_lines(ctx))
            + "\n\n"
            "Jak walczysz:\n"
            f"Siła: {stats.describe_stat(stats.sila)}.\n"
            f"Zręczność: {stats.describe_stat(stats.zrecznosc)}.\n"
            f"Kondycja: {stats.describe_kondycja()}.\n"
            f"Styl walki: {ctx.character.combat_style}."
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
            f"Na sobie masz teraz: {ctx.character.equipment_summary()}"
        )

    async def cmd_skills(ctx: GameContext, arg: str | None, index: int) -> str:
        lines: list[str] = []
        for definition in all_skill_definitions():
            level = ctx.character.skills.level(definition.key)
            lines.append(f"{definition.label}: {_skill_desc(level)}")
        return "\n".join(lines)


    async def cmd_style(ctx: GameContext, arg: str | None, index: int) -> str:
        if not arg:
            available = ", ".join(COMBAT_STYLES)
            return f"Aktualny styl walki: {ctx.character.combat_style}. Dostępne style: {available}."
        style = normalize_combat_style(arg)
        if style not in COMBAT_STYLES:
            available = ", ".join(COMBAT_STYLES)
            return f"Nieznany styl walki. Dostępne style: {available}."
        ctx.character.combat_style = style
        return f"Przyjmujesz styl walki: {style}."

    async def cmd_reputation(ctx: GameContext, arg: str | None, index: int) -> str:
        local = ", ".join(f"{zone}: {value}" for zone, value in sorted(ctx.character.local_reputation.items())) or "brak"
        crimes = ", ".join(f"{crime}: {count}" for crime, count in sorted(ctx.character.crimes.items())) or "brak"
        wanted = "\n".join(f"- {entry}" for entry in ctx.character.wanted_posts[:5]) or "brak"
        factions = "\n".join(f"{name}: {value}" for name, value in sorted(ctx.character.reputation.items())) or "brak"
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
