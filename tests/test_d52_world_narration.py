from __future__ import annotations

import unittest

from astergard.items.models import Item
from astergard.narrative import build_world_scene, render_world_scene
from astergard.npcs.models import NPC
from astergard.world.models import Exit


class D52WorldNarrationTests(unittest.TestCase):
    def _scene(self, *, items: list[Item] | None = None, npcs: list[NPC] | None = None, zone: str = "Centrum_Twierdza", weather: str | None = None, season: str | None = "lato", hour: int = 6, title: str = "Zaułek") -> str:
        scene = build_world_scene(
            title=title,
            description="Wąskie przejście między murami i zapleczem karczmy.",
            zone=zone,
            time_of_day=hour,
            season=season,
            weather=weather,
            world_state=None,
            perspective="standard",
            exits={
                "wschod": Exit(2),
                "poludnie": Exit(3),
            },
            items=items or [],
            npcs=npcs or [],
            target_names={"wschod": "plac", "poludnie": "karczma"},
        )
        return render_world_scene(scene)

    def test_single_and_multiple_items_use_natural_number_agreement(self) -> None:
        single = self._scene(items=[Item("tłusty fartuch", "", 0.1, 1, "apron", item_type="clothing")])
        self.assertIn("Na ziemi leży tłusty fartuch.", single)
        self.assertNotIn("Na ziemi spoczywają", single)

        multi = self._scene(
            items=[
                Item("tłusty fartuch", "", 0.1, 1, "apron", item_type="clothing"),
                Item("wyszczerbiony nóż", "", 0.1, 1, "knife", item_type="weapon"),
            ]
        )
        self.assertIn("Na ziemi leżą tłusty fartuch i wyszczerbiony nóż.", multi)

    def test_furniture_uses_standing_presentation(self) -> None:
        text = self._scene(items=[Item("dębowa ława", "", 6.0, 1, "bench", item_type="furniture")])
        self.assertIn("Pod ścianą stoi dębowa ława.", text)

    def test_weather_reacts_to_interior_and_exterior(self) -> None:
        indoor = self._scene(zone="Kopalnia_Zelaza", weather="deszcz", title="Korytarz")
        self.assertIn("Deszcz słychać po dachu.", indoor)

        outdoor = self._scene(zone="Trakty", weather="deszcz", title="Trakt")
        self.assertIn("Deszcz moczy bruk", outdoor)

    def test_npc_rendering_stays_scene_based(self) -> None:
        npc = NPC(
            vnum="test_guard",
            name="Żołnierz",
            short_desc="Żołnierz stoi przy ścianie i poprawia pas zbroi.",
            long_desc="Strażnik z miasta.",
            zone="Centrum_Twierdza",
            faction="MEEKHAN",
            daily_activity="Sprawdza pobliskie przejście.",
        )
        text = self._scene(npcs=[npc])
        npc_line = next(line for line in text.splitlines() if line.startswith("Żołnierz"))
        activity = npc_line.split(", ", 1)[1] if ", " in npc_line else npc_line
        self.assertIn("sprawdza pobliskie przejście", text)
        self.assertEqual(npc_line.count("sprawdza pobliskie przejście"), 1)
        self.assertNotIn(" i ", activity)
        self.assertNotIn(",", activity)
        self.assertNotIn("W pobliżu są", text)

    def test_short_mode_is_more_compact_than_full_mode(self) -> None:
        scene = build_world_scene(
            title="Zaułek",
            description="Wąskie przejście między murami i zapleczem karczmy.",
            zone="Centrum_Twierdza",
            time_of_day=6,
            season="lato",
            weather="slonecznie",
            world_state=None,
            perspective="standard",
            exits={"wschod": Exit(2)},
            items=[Item("żelazny klucz", "", 0.1, 1, "key")],
            npcs=[],
            target_names={"wschod": "plac"},
        )
        full = render_world_scene(scene, mode="standard")
        short = render_world_scene(scene, mode="short")
        self.assertGreater(len(full), len(short))
        self.assertLessEqual(short.count("\n"), full.count("\n"))

    def test_scene_rendering_avoids_commentary_phrases(self) -> None:
        text = self._scene()
        banned_phrases = [
            "wydaje się",
            "sprawia wrażenie",
            "jest miejscem",
            "to miejsce",
            "nie ma tu nic przypadkowego",
            "człowiek jest tu",
            "miasto zaczyna się",
            "droga jest bardziej",
            "należy do",
            "leży w strefie",
        ]
        lowered = text.lower()
        for phrase in banned_phrases:
            self.assertNotIn(phrase, lowered)


if __name__ == "__main__":
    unittest.main()
