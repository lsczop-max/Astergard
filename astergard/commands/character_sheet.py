from __future__ import annotations

from collections.abc import Awaitable, Callable

from astergard.server.context import GameContext
from astergard.combat.manager import COMBAT_STYLES, normalize_combat_style
from astergard.characters.creation import ORIGIN_DEFINITIONS
from astergard.characters.professions import profession_label
from astergard.rules.skills import all_skill_definitions, skill_threshold

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
    async def cmd_score(ctx: GameContext, arg: str | None, index: int) -> str:
        stats = ctx.character.stats
        origin = ORIGIN_DEFINITIONS.get(ctx.character.origin)
        origin_name = origin.label if origin is not None else (ctx.character.origin or "brak")
        return (
            f"Imię: {ctx.character.name or ctx.character.username}\n"
            f"Opis postaci: {ctx.character.gender_description or 'brak'}\n"
            f"Wiek: {ctx.character.age or 'brak'}\n"
            f"Pochodzenie: {origin_name}\n"
            f"Region urodzenia: {ctx.character.birth_region or 'brak'}\n"
            f"Kultura: {ctx.character.culture or 'brak'}\n"
            f"Religia: {ctx.character.religion or 'brak'}\n"
            f"Profesja główna: {profession_label(ctx.character.main_profession)}\n"
            f"Profesja dodatkowa: {profession_label(ctx.character.secondary_profession)}\n"
            f"Siła: {stats.describe_stat(stats.sila)}\n"
            f"Zręczność: {stats.describe_stat(stats.zrecznosc)}\n"
            f"Kondycja: {stats.kondycja}/{stats.max_kondycja}\n"
            f"Styl walki: {ctx.character.combat_style}"
        )

    async def cmd_profile(ctx: GameContext, arg: str | None, index: int) -> str:
        origin = ORIGIN_DEFINITIONS.get(ctx.character.origin)
        origin_name = origin.label if origin is not None else (ctx.character.origin or "brak")
        starter_inventory = ", ".join(item.display_name() for item in ctx.character.inventory) or "brak"
        equipment = ", ".join(
            f"{slot}: {item.display_name()}" for slot, item in ctx.character.equipment.items() if item is not None
        ) or "brak"
        return (
            f"Imię: {ctx.character.name or ctx.character.username}\n"
            f"Opis postaci: {ctx.character.gender_description or 'brak'}\n"
            f"Wiek: {ctx.character.age or 'brak'}\n"
            f"Pochodzenie: {origin_name}\n"
            f"Region urodzenia: {ctx.character.birth_region or 'brak'}\n"
            f"Kultura: {ctx.character.culture or 'brak'}\n"
            f"Religia / wyznanie: {ctx.character.religion or 'brak'}\n"
            f"Profesja główna: {profession_label(ctx.character.main_profession)}\n"
            f"Profesja dodatkowa: {profession_label(ctx.character.secondary_profession)}\n"
            f"Wygląd: {ctx.character.appearance or 'brak'}\n"
            f"Historia: {ctx.character.history or 'brak'}\n"
            f"Reputacja startowa: {ctx.character.starting_reputation}\n"
            f"Reputacja globalna: {ctx.character.global_reputation}\n"
            f"Ekwipunek startowy: {starter_inventory}\n"
            f"Wyposażenie: {equipment}"
        )

    async def cmd_skills(ctx: GameContext, arg: str | None, index: int) -> str:
        lines: list[str] = []
        for definition in all_skill_definitions():
            data = ctx.character.skills.values.get(definition.key, {"level": 1, "progress": 0})
            threshold = skill_threshold(definition.key, data["level"])
            lines.append(
                f"{definition.label}: {_skill_desc(data['level'])} "
                f"({data['progress']}/{threshold})"
            )
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
            f"Tytuł: {ctx.character.title}\n"
            f"Sława: {ctx.character.renown}\n"
            f"Reputacja globalna: {ctx.character.global_reputation}\n"
            f"Reputacja lokalna: {local}\n"
            f"Przestępstwa: {crimes}\n"
            f"Listy gończe:\n{wanted}\n"
            f"Frakcje:\n{factions}"
        )

    return {"score": cmd_score, "profile": cmd_profile, "skills": cmd_skills, "style": cmd_style, "reputation": cmd_reputation}
