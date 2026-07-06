from __future__ import annotations

from astergard.application.use_case_contexts import QuestContext
from astergard.commands.helpers import find_npc_in_manager
from astergard.quests.manager import QuestManager
from astergard.engine.events import DomainEventType


class QuestApplicationService:
    def __init__(self, quests: QuestManager) -> None:
        self.quests = quests

    def talk(self, ctx: QuestContext, arg: str | None) -> str:
        if not arg:
            return "Z kim chcesz rozmawiać?"
        npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, arg)
        if npc is None:
            return "Nie widzisz takiej osoby."
        if "zadanie" in arg or "wilki" in arg:
            added = self.quests.add(ctx.character, "wolf_pelt")
            if added:
                ctx.event_bus.emit(DomainEventType.QUEST_ACCEPTED, username=ctx.character.username, quest_id="wolf_pelt", npc=npc.vnum)
                return "<green>Otrzymujesz nowe zadanie: Wilcza skóra</green>\nKupiec: Przynieś mi wilczą skórę."
            return "Kupiec: Nadal czekam na skórę."
        return npc.dialogue("default")

    def render_quest_log(self, character) -> str:
        return self.quests.render(character)
