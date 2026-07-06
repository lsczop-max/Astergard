from __future__ import annotations
from astergard.characters.models import Character
from astergard.rules.reputation import ReputationRules, default_reputation_rules

class FactionManager:
    MEEKHAN = "MEEKHAN"
    SE_HARIEN = "SE_HARIEN"
    REBELS = "REBELS"

    def __init__(self, rules: ReputationRules | None = None) -> None:
        self.rules = rules or default_reputation_rules()

    def adjust(self, char: Character, faction: str, amount: int) -> None:
        current = char.reputation.get(faction, 0)
        char.reputation[faction] = self.rules.clamp(current + amount)

    def register_kill(self, char: Character, victim_faction: str) -> None:
        if victim_faction == self.REBELS:
            self.adjust(char, self.MEEKHAN, self.rules.meekhan_gain_for_rebel_kill)
        if victim_faction == self.MEEKHAN:
            self.adjust(char, self.MEEKHAN, self.rules.meekhan_loss_for_meekhan_kill)

    def hostile_to_guards(self, char: Character) -> bool:
        return self.rules.guards_are_hostile(char.reputation.get(self.MEEKHAN, 0))
