from __future__ import annotations
import random

class TimeAndWeatherManager:
    def __init__(self) -> None:
        self.tick_count = 0
        self.hour = 6
        self.weather_by_zone: dict[str, str] = {}
        self._ambient_by_weather = {
            "slonecznie": ["Przez gałęzie przeciska się ciepły blask.", "Ptaki krążą wyżej niż zwykle, jakby świat był dziś lżejszy."],
            "deszcz": ["Na ziemi perli się deszcz, a koleiny błyszczą jak świeże blizny.", "Słychać miarowy szelest kropli o liście i dachy."],
            "mgla": ["Mgła przygłusza wszystkie kroki.", "W cieniu dróg coś porusza się wolniej niż człowiek by chciał."],
            "sniezyca": ["Płatki śniegu zaciskają drogę w białą ciszę.", "Wiatr niesie śnieg poziomo, tnąc widok na pół."],
        }

    def tick(self, zones: list[str]) -> list[str]:
        self.tick_count += 1
        messages: list[str] = []
        if self.tick_count % 60 == 0:
            self.hour = (self.hour + 1) % 24
            if self.hour == 6:
                messages.append("<gold>Słońce wschodzi nad rubieżami Imperium...</gold>")
            if self.hour == 20:
                messages.append("<indigo>Cień nocy okrywa świat...</indigo>")
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
                "Wiatr przechodzi przez okolicę i zaraz znika.",
                "Przez chwilę słychać krzyk ptaka, potem znowu pozostaje cisza.",
                "Gdzieś dalej trzaśnie gałąź, jakby las poprawiał własny oddech.",
            ]) if random.random() < 0.4 else None
        choices = self._ambient_by_weather.get(weather, [])
        if not choices or random.random() >= 0.45:
            return None
        return random.choice(choices)
