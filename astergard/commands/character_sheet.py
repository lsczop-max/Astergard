from __future__ import annotations

from collections.abc import Awaitable, Callable

from astergard.server.context import GameContext
from astergard.combat.manager import COMBAT_STYLES, normalize_combat_style

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
        return (
            f"Siła: {stats.describe_stat(stats.sila)}\n"
            f"Zręczność: {stats.describe_stat(stats.zrecznosc)}\n"
            f"Kondycja: {stats.kondycja}/{stats.max_kondycja}\n"
            f"Styl walki: {ctx.character.combat_style}"
        )

    async def cmd_skills(ctx: GameContext, arg: str | None, index: int) -> str:
        return "\n".join(f"{name}: {_skill_desc(data['level'])}" for name, data in ctx.character.skills.values.items())


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
        return "\n".join(f"{name}: {value}" for name, value in ctx.character.reputation.items())

    return {"score": cmd_score, "skills": cmd_skills, "style": cmd_style, "reputation": cmd_reputation}
