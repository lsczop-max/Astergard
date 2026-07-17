from __future__ import annotations

from datetime import date
import random

from astergard.narrative import describe_season, describe_time_of_day, describe_weather, describe_world_state


def _season_for_month(month: int) -> str:
    if month in {3, 4, 5}:
        return "wiosna"
    if month in {6, 7, 8}:
        return "lato"
    if month in {9, 10, 11}:
        return "jesien"
    return "zima"

class TimeAndWeatherManager:
    def __init__(self) -> None:
        self.tick_count = 0
        self.hour = 6
        self.season = _season_for_month(date.today().month)
        self.world_state = "spokojnie"
        self.weather_by_zone: dict[str, str] = {}
        self._ambient_by_weather = {
            "slonecznie": ["Przez gałęzie przeciska się ciepły blask.", "Ptaki krążą wyżej niż zwykle, a na kamieniach szybko schnie woda."],
            "deszcz": ["Na ziemi perli się deszcz, a koleiny błyszczą od nowej wody.", "Krople uderzają o dachy, płachty i liście z równym szelestem."],
            "burza": ["Grzmot przechodzi gdzieś nad okolicą.", "Wiatr wciska deszcz w każdą szczelinę, a luźne płótna trzepoczą przy ścianach."],
            "mgla": ["Mgła przygłusza wszystkie kroki.", "Zacierają się krawędzie drogi, okien i dalszych murów."],
            "sniezyca": ["Płatki śniegu zaciskają drogę w białą ciszę.", "Wiatr niesie śnieg poziomo i zasypuje ślady."],
        }

    def tick(self, zones: list[str]) -> list[str]:
        self.tick_count += 1
        messages: list[str] = []
        if self.tick_count % 60 == 0:
            self.hour = (self.hour + 1) % 24
            if self.hour == 6:
                messages.append("<gold>Świt rozlewa się nad rubieżami i budzi świat do życia.</gold>")
            if self.hour == 20:
                messages.append("<indigo>Noc zsuwa się na ziemię i zamyka ostatnie odgłosy dnia.</indigo>")
        if self.tick_count % 240 == 0:
            for zone in zones:
                weather = random.choice(["slonecznie", "deszcz", "mgla"])
                if zone == "Polnoc_Gory" and weather == "deszcz":
                    weather = "sniezyca"
                self.weather_by_zone[zone] = weather
        return messages

    def hit_modifier(self, zone: str) -> float:
        return 0.8 if self.weather_by_zone.get(zone) == "mgla" else 1.0

    def regen_modifier(self, zone: str) -> float:
        return 0.5 if self.weather_by_zone.get(zone) == "sniezyca" else 1.0

    def ambient_event(self, zone: str) -> str | None:
        weather = self.weather_by_zone.get(zone)
        if weather is None:
            return random.choice([
                "Ktoś zamyka okiennice po drugiej stronie ulicy.",
                "Pies przebiega przez przejście i znika za rogiem.",
                "Gdzieś dalej trzaśnie gałąź, a potem wraca zwykły ruch ulicy.",
            ]) if random.random() < 0.4 else None
        choices = self._ambient_by_weather.get(weather, [])
        if not choices or random.random() >= 0.45:
            return None
        return random.choice(choices)

    def describe_time_layer(self) -> str:
        return describe_time_of_day(self.hour)

    def describe_weather_layer(self, zone: str) -> str:
        return describe_weather(self.weather_by_zone.get(zone))

    def describe_season_layer(self) -> str:
        return describe_season(self.season)

    def describe_world_state_layer(self) -> str:
        return describe_world_state(self.world_state)
