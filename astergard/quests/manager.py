from __future__ import annotations
from dataclasses import dataclass, field
from astergard.characters.models import Character

@dataclass
class Quest:
    id: str
    title: str
    description: str
    objectives: list[dict[str, object]]
    rewards: dict[str, object] = field(default_factory=dict)

QUESTS = {
    "wolf_pelt": Quest("wolf_pelt", "Skóra z traktu", "Przynieś kupcowi wilczą skórę.", [{"type":"kill", "target":"wolf", "count":1, "current":0}], {"gold":15, "rep":5})
}

class QuestManager:
    def add(self, char: Character, quest_id: str) -> bool:
        if quest_id in char.active_quests or quest_id in char.completed_quests:
            return False
        char.active_quests[quest_id] = {"current": 0}
        return True

    def progress(self, char: Character, obj_type: str, target: str, amount: int = 1) -> list[str]:
        messages: list[str] = []
        for qid, state in char.active_quests.items():
            quest = QUESTS[qid]
            for obj in quest.objectives:
                if obj["type"] == obj_type and obj["target"] == target:
                    state["current"] = min(int(obj["count"]), state.get("current", 0) + amount)
                    if state["current"] >= int(obj["count"]):
                        messages.append(f"<green>[Zadanie: {quest.title}] Cel osiągnięty!</green>")
        return messages

    def complete_if_ready(self, char: Character, quest_id: str) -> str:
        if quest_id not in char.active_quests:
            return "Nie masz takiego zadania."
        quest = QUESTS[quest_id]
        count = int(quest.objectives[0]["count"])
        if char.active_quests[quest_id].get("current", 0) < count:
            return "Jeszcze nie ukończyłeś celu zadania."
        reward_gold = int(quest.rewards.get("gold", 0))
        char.gold += reward_gold
        del char.active_quests[quest_id]
        char.completed_quests.append(quest_id)
        return f"<green>Kończysz zadanie: {quest.title}. Otrzymujesz {reward_gold} monet.</green>"

    def render(self, char: Character) -> str:
        if not char.active_quests and not char.completed_quests:
            return "Nie masz aktywnych zadań."
        lines: list[str] = []
        if char.active_quests:
            lines.append("Aktywne zadania:")
            for qid, state in sorted(char.active_quests.items()):
                quest = QUESTS.get(qid)
                if quest is None:
                    lines.append(f"- {qid}: nieznane zadanie")
                    continue
                objective = quest.objectives[0]
                current = int(state.get("current", 0))
                count = int(objective.get("count", 1))
                lines.append(f"- {quest.title}: {quest.description} [{current}/{count}]")
        if char.completed_quests:
            lines.append("Ukończone zadania:")
            for qid in char.completed_quests:
                quest = QUESTS.get(qid)
                lines.append(f"- {quest.title if quest else qid}")
        return "\n".join(lines)
