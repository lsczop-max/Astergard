from __future__ import annotations

from astergard.application.use_case_contexts import QuestContext
from astergard.commands.helpers import find_npc_in_manager
from astergard.commands.polish import normalize_phrase
from astergard.engine.events import DomainEventType
from astergard.factions.reputation import FactionManager
from astergard.npcs.models import NPC
from astergard.quests.manager import QUESTS, QuestManager

_DIALOGUE_TOPIC_PATTERNS: dict[str, tuple[str, ...]] = {
    "praca": ("praca", "robota", "robote", "roboty", "pracuje", "pracujesz", "pracuje", "zawod", "zajecie", "zajmuje"),
    "miejsce": ("miejsce", "gdzie", "tutaj", "tu", "okolica", "okolice", "stad", "stąd"),
    "plotki": ("plotki", "nowiny", "wiesci", "wiesc", "sluch", "slysz", "slysza", "pogloski"),
}


class QuestApplicationService:
    def __init__(self, quests: QuestManager, factions: FactionManager) -> None:
        self.quests = quests
        self.factions = factions

    def talk(self, ctx: QuestContext, arg: str | None) -> str:
        if not arg:
            return "Z kim chcesz rozmawiać?"
        npc = find_npc_in_manager(ctx.npcs, ctx.character.room_id, arg)
        if npc is None:
            return "Nie widzisz takiej osoby."
        normalized = normalize_phrase(arg, drop_stopwords=True)
        for quest in QUESTS.values():
            if quest.completion_npc == npc.vnum and self.quests.is_ready(ctx.character, quest.id):
                message = self.quests.complete_if_ready(ctx.character, quest.id, ctx.event_bus)
                return f"{npc.name.capitalize()}: {quest.completion_text}\n{message}"
        if self._conversation_blocked(ctx, npc):
            return f"{npc.name.capitalize()}: Z taką reputacją najpierw napraw swoje sprawy."
        topic = self._topic_for(npc, normalized)
        if topic is not None:
            return f"{npc.name.capitalize()}: {npc.dialogue(topic, ctx.character.reputation.get(npc.faction, 0))}"

        quest = self._matching_quest(npc.vnum, normalized, ctx.character.completed_quests)
        if quest is not None and quest.id not in ctx.character.completed_quests and quest.id not in ctx.character.active_quests:
            added = self.quests.add(ctx.character, quest.id)
            if added:
                ctx.event_bus.emit(DomainEventType.QUEST_ACCEPTED, username=ctx.character.username, quest_id=quest.id, npc=npc.vnum)
                return f"<green>Otrzymujesz nowe zadanie: {quest.title}</green>\n{quest.offer_text}"
        if quest is not None and quest.id in ctx.character.active_quests:
            return f"{npc.name.capitalize()}: {quest.reminder_text}"

        if quest is not None and self.factions.rules.quests_are_blocked(ctx.character.global_reputation, ctx.character.wanted_level):
            return f"{npc.name.capitalize()}: Najpierw odbuduj reputację, zanim przyjmiesz kolejne zadanie."

        progress_messages = self.quests.progress(ctx.character, "talk", npc.vnum)
        if progress_messages:
            return "\n".join(progress_messages + [npc.dialogue("default", ctx.character.reputation.get(npc.faction, 0))])

        return npc.dialogue("default", ctx.character.reputation.get(npc.faction, 0))

    def _topic_for(self, npc, normalized_arg: str) -> str | None:
        tokens = normalized_arg.split()
        for topic, patterns in _DIALOGUE_TOPIC_PATTERNS.items():
            if topic in npc.dialogue_tree and any(
                token.startswith(pattern)
                for token in tokens
                for pattern in patterns
            ):
                return topic
        return None

    def _matching_quest(self, npc_vnum: str, normalized_arg: str, completed_quests: list[str]):
        for quest in QUESTS.values():
            if quest.start_npc != npc_vnum or quest.id in completed_quests:
                continue
            normalized_keywords = normalize_phrase(" ".join(quest.offer_keywords), drop_stopwords=True).split()
            if normalized_arg and not any(keyword in normalized_arg for keyword in normalized_keywords):
                continue
            return quest
        return None

    def _conversation_blocked(self, ctx: QuestContext, npc: NPC) -> bool:
        if npc.faction == self.factions.MEEKHAN and self.factions.hostile_to_guards(ctx.character):
            return True
        if npc.is_merchant and self.factions.merchants_are_hostile(ctx.character, npc.faction):
            return True
        return False

    def render_quest_log(self, character) -> str:
        return self.quests.render(character)
