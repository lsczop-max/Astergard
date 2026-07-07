from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from astergard.characters.models import Character
from astergard.engine.events import DomainEventType


class QuestObjective(TypedDict):
    type: str
    target: str
    count: int
    current: int


class QuestRewards(TypedDict, total=False):
    gold: int
    rep: int


@dataclass
class Quest:
    id: str
    title: str
    description: str
    start_npc: str
    completion_npc: str
    offer_keywords: tuple[str, ...]
    offer_text: str
    reminder_text: str
    completion_text: str
    objectives: list[QuestObjective]
    rewards: QuestRewards = field(default_factory=QuestRewards)
    auto_complete_on_delivery: bool = False


QUESTS: dict[str, Quest] = {
    "wolf_pelt": Quest(
        "wolf_pelt",
        "Skóra z traktu",
        "Przynieś kupcowi wilczą skórę.",
        "merchant",
        "merchant",
        ("zadanie", "wilki", "skora", "skóra"),
        "Kupiec: Na traktu jest zbyt dużo wilków. Przynieś mi jedną skórę, a zapłacę.",
        "Kupiec: Nadal czekam na wilczą skórę.",
        "Kupiec: Dobra robota. To wystarczy.",
        [{"type": "kill", "target": "wolf", "count": 1, "current": 0}],
        {"gold": 15, "rep": 5},
    ),
    "market_delivery": Quest(
        "market_delivery",
        "Dostawa z targu",
        "Karczmarz potrzebuje świeżych zapasów z rynku.",
        "innkeeper",
        "innkeeper",
        ("zadanie", "dostawa", "targ", "rynku"),
        "Karczmarz: Potrzebuję kosza z rynku. Przynieś go z targu, zanim wystygnie jedzenie.",
        "Karczmarz: Jeszcze czekam na dostawę z rynku.",
        "Karczmarz: Dziękuję. To uratuje wieczór w karczmie.",
        [{"type": "give", "target": "market_delivery_basket_47", "count": 1, "current": 0}],
        {"gold": 18, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "blacksmith_tools": Quest(
        "blacksmith_tools",
        "Zgubione narzędzia",
        "Kowal szuka swoich zaginionych szczypiec.",
        "blacksmith",
        "blacksmith",
        ("zadanie", "narzedzia", "narzędzia", "szczypce", "kowal"),
        "Kowal: Zgubiłem szczypce przy studni. Przynieś je, a odwdzięczę się.",
        "Kowal: Szczypce nadal gdzieś krążą po mieście.",
        "Kowal: Dobrze. Bez nich nie da się pracować.",
        [{"type": "give", "target": "smith_tongs_lost_21", "count": 1, "current": 0}],
        {"gold": 20, "rep": 4},
        auto_complete_on_delivery=True,
    ),
    "fisher_net": Quest(
        "fisher_net",
        "Zagubiona sieć",
        "Rybak z Podgrodzia chce odzyskać swoją sieć.",
        "podgrodzie_rybak",
        "podgrodzie_rybak",
        ("zadanie", "siec", "sieć", "rybak"),
        "Rybak: Moja sieć gdzieś przepadła przy moście. Przynieś ją, zanim połowu zabraknie.",
        "Rybak: Bez sieci nie ma mowy o połowie.",
        "Rybak: Dobra, wraca do mnie cały zarobek na dziś.",
        [{"type": "give", "target": "podgrodzie_fishing_net_75", "count": 1, "current": 0}],
        {"gold": 16, "rep": 3},
        auto_complete_on_delivery=True,
    ),
    "guard_vagrant": Quest(
        "guard_vagrant",
        "Podejrzany włóczęga",
        "Strażnik chce wiedzieć, kim jest włóczęga z placu.",
        "watch_sergeant",
        "watch_sergeant",
        ("zadanie", "wloczega", "włóczęga", "obcy"),
        "Strażnik: Sprawdź, co wie włóczęga. Potem wróć z odpowiedzią.",
        "Strażnik: Najpierw porozmawiaj z włóczęgą.",
        "Strażnik: To wystarczy. Miasto musi wiedzieć, kogo pilnować.",
        [{"type": "talk", "target": "vagrant", "count": 1, "current": 0}],
        {"gold": 8, "rep": 8},
    ),
    "priest_herbs": Quest(
        "priest_herbs",
        "Zioła dla kapłana",
        "Pomocnik kapłana potrzebuje świeżych ziół z ogrodu.",
        "priest_aide",
        "priest_aide",
        ("zadanie", "ziola", "zioła", "napary", "kaplan", "kapłan"),
        "Pomocnik kapłana: Potrzebuję świeżej wiązki ziół z ogrodu. Przynieś ją z powrotem.",
        "Pomocnik kapłana: Zioła jeszcze nie wróciły do świątyni.",
        "Pomocnik kapłana: Dobrze. Te zioła trafią tam, gdzie trzeba.",
        [{"type": "give", "target": "priest_herb_bundle_37", "count": 1, "current": 0}],
        {"gold": 12, "rep": 4},
        auto_complete_on_delivery=True,
    ),
}


class QuestManager:
    def add(self, char: Character, quest_id: str) -> bool:
        if quest_id in char.active_quests or quest_id in char.completed_quests:
            return False
        char.active_quests[quest_id] = {"current": 0}
        return True

    def is_ready(self, char: Character, quest_id: str) -> bool:
        quest = QUESTS.get(quest_id)
        if quest is None or quest_id not in char.active_quests:
            return False
        current = int(char.active_quests[quest_id].get("current", 0))
        return current >= quest.objectives[0]["count"]

    def progress(self, char: Character, obj_type: str, target: str, amount: int = 1) -> list[str]:
        messages: list[str] = []
        for qid, state in char.active_quests.items():
            quest = QUESTS.get(qid)
            if quest is None:
                continue
            for obj in quest.objectives:
                if obj["type"] == obj_type and obj["target"] == target:
                    current = int(state.get("current", 0))
                    state["current"] = min(obj["count"], current + amount)
                    if state["current"] >= obj["count"]:
                        messages.append(f"<green>[Zadanie: {quest.title}] Cel osiągnięty!</green>")
        return messages

    def complete_if_ready(self, char: Character, quest_id: str, event_bus=None) -> str:
        if quest_id not in char.active_quests:
            return "Nie masz takiego zadania."
        quest = QUESTS.get(quest_id)
        if quest is None:
            return "Nie znam takiego zadania."
        if not self.is_ready(char, quest_id):
            return "Jeszcze nie ukończyłeś celu zadania."
        reward_gold = quest.rewards.get("gold", 0)
        reward_rep = quest.rewards.get("rep", 0)
        char.gold += reward_gold
        del char.active_quests[quest_id]
        char.completed_quests.append(quest_id)
        if event_bus is not None:
            event_bus.emit(DomainEventType.QUEST_COMPLETED, username=char.username, character=char, quest_id=quest_id, rep=reward_rep)
        reward_text = f"{reward_gold} monet"
        if reward_rep:
            reward_text += f" i {reward_rep} reputacji"
        return f"<green>Kończysz zadanie: {quest.title}. Otrzymujesz {reward_text}.</green>"

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
                count = objective["count"]
                reward = quest.rewards
                reward_text = []
                if "gold" in reward:
                    reward_text.append(f"{reward['gold']} złota")
                if "rep" in reward:
                    reward_text.append(f"{reward['rep']} rep")
                suffix = f" (nagroda: {', '.join(reward_text)})" if reward_text else ""
                lines.append(f"- {quest.title}: {quest.description} [{current}/{count}]{suffix}")

        if char.completed_quests:
            lines.append("Ukończone zadania:")
            for qid in char.completed_quests:
                quest = QUESTS.get(qid)
                lines.append(f"- {quest.title if quest else qid}")

        return "\n".join(lines)
