from __future__ import annotations
from astergard.characters.models import Character
from astergard.rules.reputation import ReputationRules, default_reputation_rules

class FactionManager:
    MEEKHAN = "MEEKHAN"
    SE_HARIEN = "SE_HARIEN"
    REBELS = "REBELS"

    def __init__(self, rules: ReputationRules | None = None) -> None:
        self.rules = rules or default_reputation_rules()

    def adjust(self, char: Character, faction: str, amount: int, zone: str | None = None) -> None:
        current = char.reputation.get(faction, 0)
        char.reputation[faction] = self.rules.clamp(current + amount)
        char.add_global_reputation(amount)
        char.add_renown(amount)
        if zone is not None:
            char.add_local_reputation(zone, amount)
        self._refresh_identity(char)

    def register_kill(self, char: Character, victim_faction: str) -> None:
        if victim_faction == self.REBELS:
            self.adjust(char, self.MEEKHAN, self.rules.meekhan_gain_for_rebel_kill)
        if victim_faction == self.MEEKHAN:
            self.adjust(char, self.MEEKHAN, self.rules.meekhan_loss_for_meekhan_kill)

    def hostile_to_guards(self, char: Character) -> bool:
        return self.rules.guards_are_hostile(char.reputation.get(self.MEEKHAN, 0), char.wanted_level)

    def merchants_are_hostile(self, char: Character, faction: str) -> bool:
        return self.rules.merchants_are_hostile(char.reputation.get(faction, 0), char.wanted_level) or char.global_reputation <= self.rules.merchant_hostile_threshold

    def merchants_are_friendly(self, char: Character, faction: str) -> bool:
        return self.rules.merchants_are_friendly(char.reputation.get(faction, 0)) or char.global_reputation >= self.rules.merchant_friend_threshold

    def record_crime(self, char: Character, crime: str, zone: str | None = None, detail: str | None = None) -> None:
        char.record_crime(crime, zone, detail)
        char.add_global_reputation(-10)
        if zone is not None:
            char.add_local_reputation(zone, -10)
        char.wanted_level = max(char.wanted_level, self.rules.wanted_level_for(char.crimes))
        self._refresh_identity(char)

    def _refresh_identity(self, char: Character) -> None:
        char.sync_identity(title=self.rules.title_for(char.renown, char.wanted_level), wanted_level=char.wanted_level)
