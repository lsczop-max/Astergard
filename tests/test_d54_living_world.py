from __future__ import annotations

import unittest

from astergard.items.models import Item
from astergard.narrative import build_world_scene, render_world_scene
from astergard.npcs.models import NPC
from astergard.world.models import Exit


class D54LivingWorldTests(unittest.TestCase):
    def test_npc_scene_line_changes_with_phase_and_weather(self) -> None:
        npc = NPC(
            vnum="test_innkeeper",
            name="karczmarz",
            short_desc="Karczmarz ociera dłonie o fartuch",
            long_desc="Karczmarz dogląda sali.",
            zone="Centrum_Twierdza",
            faction="MEEKHAN",
            daily_schedule={
                "świt": "otwiera karczmę i ustawia stoły przy wejściu",
                "dzień": "przelicza monety przy ladzie",
                "wieczór": "zamyka okiennice i zlicza kufle",
                "noc": "trzyma się bliżej ognia i nasłuchuje sali",
            },
        )

        morning = npc.scene_line(6, None, "Centrum_Twierdza")
        night = npc.scene_line(22, "deszcz", "Centrum_Twierdza")

        self.assertNotEqual(morning, night)
        morning_action = morning.split(", ", 1)[1] if ", " in morning else morning
        night_action = night.split(", ", 1)[1] if ", " in night else night
        self.assertIn("otwiera karczmę", morning_action)
        self.assertIn("nasłuchuje sali", night_action)
        self.assertNotIn(" i ", morning_action)
        self.assertNotIn(" i ", night_action)
        self.assertNotIn(",", morning_action)
        self.assertNotIn(",", night_action)

    def test_render_world_scene_includes_life_sounds_smells(self) -> None:
        scene = build_world_scene(
            title="Karczma pod Żurawiem",
            description="Niski budynek przy ulicy.",
            zone="Centrum_Twierdza",
            time_of_day=14,
            season="lato",
            weather="deszcz",
            world_state=None,
            perspective="standard",
            exits={"polnoc": Exit(2)},
            items=[Item("beczka piwa", "Beczka z piwem.", 14.0, 10, "beer_barrel", is_container=True, capacity=60)],
            npcs=[
                NPC(
                    vnum="test_guard",
                    name="strażnik",
                    short_desc="Strażnik opiera włócznię o ramię",
                    long_desc="Strażnik pilnuje wejścia.",
                    zone="Centrum_Twierdza",
                    faction="MEEKHAN",
                    daily_schedule={"dzień": "patroluje salę", "wieczór": "zamyka drzwi"},
                )
            ],
            target_names={"polnoc": "plac"},
        )
        text = render_world_scene(scene)

        self.assertIn("Pachnie piwem", text)
        self.assertIn("Ławy są wygładzone", text)
        self.assertIn("patroluje salę", text)

    def test_forest_scene_uses_sensory_observations(self) -> None:
        scene = build_world_scene(
            title="Leśna Polana",
            description="Szeroka polana między drzewami.",
            zone="Puszcza_Ciszy",
            time_of_day=10,
            season="jesien",
            weather="mgla",
            world_state=None,
            perspective="standard",
            exits={"wschod": Exit(210)},
            items=[],
            npcs=[],
            target_names={"wschod": "ścieżka"},
        )
        text = render_world_scene(scene)

        self.assertTrue("żywica" in text or "mokra kora" in text)
        self.assertTrue("ptaki" in text or "liście" in text)
        self.assertTrue("Korzenie" in text or "ślad" in text or "mchu" in text)


if __name__ == "__main__":
    unittest.main()
