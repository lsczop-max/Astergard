from __future__ import annotations

from dataclasses import dataclass

from astergard.application.services.exploration_parts import ExplorationTargetResolver
from astergard.application.services.exploration_scene import ExplorationSceneRenderer
from astergard.application.use_case_contexts import ExplorationContext
from astergard.commands.polish import normalize_phrase


@dataclass(slots=True)
class ExplorationPerceptionService:
    target_resolver: ExplorationTargetResolver
    scene_renderer: ExplorationSceneRenderer

    def look(self, ctx: ExplorationContext, arg: str | None, index: int) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "<red>Wokół ciebie nie ma świata, tylko pustka.</red>"
        if self._is_short_look(arg):
            return self.scene_renderer.render(ctx, loc, True)
        if arg:
            resolved = self.target_resolver.resolve(ctx, loc, arg, index)
            if resolved is not None:
                return resolved
            return "Nie dostrzegasz niczego, co przyciągnęłoby uwagę."
        return self.scene_renderer.render(ctx, loc, False)

    def sense(self, ctx: ExplorationContext, arg: str | None, index: int) -> str:
        loc = ctx.world.get_location(ctx.character.room_id)
        if not loc:
            return "<red>Wokół ciebie nie ma świata, tylko pustka.</red>"
        command = ctx.current_command or "zbadaj"
        if arg:
            look = self.look(ctx, arg, index)
            if look != "Nic ciekawego tam nie widzisz.":
                return look
        if command == "nasluchuj":
            ambient = ctx.world.pop_ambient_message(loc.zone)
            if ambient:
                return ambient
            return "Słyszysz szum wiatru, cichy ruch i pojedynczy odgłos z oddali."
        if command == "powachaj":
            return self._smell_room(loc.zone)
        if command == "dotknij":
            return self._touch_room(loc.inspectables)
        if command in {"usiadz", "odpocznij"}:
            return "Przysiadasz na chwilę i zbierasz oddech. Świat nie zwalnia, ale ty na moment możesz."
        if command == "rozejrzyj":
            return self.look(ctx, None, index)
        return self.look(ctx, None, index)

    def _is_short_look(self, arg: str | None) -> bool:
        if not arg:
            return False
        normalized = normalize_phrase(arg, drop_stopwords=True)
        return normalized in {"krotko", "krotki", "krotka", "krótko", "krótki", "krótka"}

    def _smell_room(self, zone: str) -> str:
        if zone == "Gory_Mekhara":
            return "Czujesz zimny kamień, mokry pył i metaliczną nutę z głębi gór."
        if zone == "Bagna_Hookri":
            return "W powietrzu unosi się torf, stęchła woda i zapach roślin gnijących bez słońca."
        if zone in {"Puszcza_Ciszy", "Knieja_Cichych_Sciezek"}:
            return "Pachnie żywicą, mokrą korą i liśćmi, które dawno przestały być świeże."
        if zone in {"Centrum_Twierdza", "Podgrodzie"}:
            return "Czujesz dym z palenisk, skórę, mokry bruk i odrobinę pieczonego chleba."
        return "Czujesz wilgoć, kurz i zapach osiadający na murach, deskach i ubraniu."

    def _touch_room(self, inspectables) -> str:
        for aliases in inspectables:
            first_word = aliases.split()[0]
            if "kam" in first_word or "głaz" in first_word or "glaz" in first_word:
                return "Kamień jest zimny i szorstki, z chropowatą krawędzią wyczuwalną pod palcami."
            if "drew" in first_word or "drzew" in first_word or "kora" in first_word:
                return "Kora jest sucha na wierzchu, ale pod spodem trzyma wilgoć i żywą tkankę drzewa."
            if "woda" in first_word or "studnia" in first_word or "cembrowin" in first_word:
                return "Wilgoć osiada na palcach niemal natychmiast."
        return "Dotykasz powierzchni wokół siebie. Jest chłodna, nierówna i naznaczona czasem."
