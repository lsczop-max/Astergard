from __future__ import annotations

from dataclasses import dataclass

from astergard.application.use_case_contexts import ExplorationContext
from astergard.narrative import build_world_scene, join_prose, render_world_scene


@dataclass(slots=True)
class ExplorationSceneRenderer:
    def render(self, ctx: ExplorationContext, location, short_look: bool) -> str:
        ambient = self._render_ambient(location, ctx)
        target_names = {
            direction: target.name.lower()
            for direction, exit_ in location.exits.items()
            if (target := ctx.world.get_location(exit_.target_room)) is not None
        }
        scene = build_world_scene(
            title=location.name,
            description=location.description,
            zone=location.zone,
            time_of_day=ctx.weather.hour,
            season=ctx.weather.season,
            weather=ctx.weather.weather_by_zone.get(location.zone),
            world_state=ctx.weather.world_state,
            perspective="standard",
            exits=location.exits,
            items=list(location.items),
            npcs=list(ctx.npcs.by_room(location.id)),
            target_names=target_names,
            exit_forms=location.exit_forms,
            scene_profile=location.scene_profile,
        )
        if ctx.character.has_light_source() and scene.visibility in {"ciemność", "słaba widoczność", "półmrok"}:
            scene.visibility = "światło niesione"
        rendered = render_world_scene(scene, mode="short" if short_look else "standard")
        if ambient:
            rendered += "\n" + ambient
        other_lines = [
            f"{player.username} {player.equipment_summary().rstrip('.')}"
            for player in ctx.players_in_room(location.id)
            if player is not ctx.character
        ]
        if other_lines and not short_look:
            rendered += "\n" + "Obok ciebie stoją jeszcze " + join_prose(other_lines) + "."
        return rendered.strip()

    def _render_ambient(self, location, ctx: ExplorationContext) -> str:
        ambient = ctx.world.pop_ambient_message(location.zone)
        if ambient is not None:
            return ambient
        ambient = ctx.weather.ambient_event(location.zone)
        if ambient is not None:
            return ambient
        return ""
