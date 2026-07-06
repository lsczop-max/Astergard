from __future__ import annotations
import random

class TimeAndWeatherManager:
    def __init__(self) -> None:
        self.tick_count = 0
        self.hour = 6
        self.weather_by_zone: dict[str, str] = {}

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
