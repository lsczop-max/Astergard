from __future__ import annotations

import asyncio
from collections import deque
import unittest

from astergard.npcs.manager import NPCManager
from astergard.testing import TestGameHarness
from astergard.world.manager import WorldManager


TARGETED_NPCS: dict[str, tuple[int, str]] = {
    "innkeeper": (14, "karczmarz"),
    "podgrodzie_karczmarka": (62, "karczmarka"),
    "blacksmith": (33, "kowal"),
    "podgrodzie_pomocnik_kowala": (66, "pomocnik kowala"),
    "podgrodzie_rybak": (69, "rybak"),
    "podgrodzie_straznik_miejski": (66, "strażnik miejski"),
    "podgrodzie_handlarz": (63, "handlarz"),
    "podgrodzie_przekupka": (76, "przekupka"),
    "podgrodzie_zebrak": (75, "żebrak"),
    "podgrodzie_pielgrzym": (62, "pielgrzym"),
}


class D351HNPCDialogueTests(unittest.TestCase):
    def test_requested_npcs_have_social_topics_registered(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            for vnum, (room_id, _) in TARGETED_NPCS.items():
                npc = next(candidate for candidate in server.services.npcs.by_room(room_id) if candidate.vnum == vnum)
                self.assertTrue({"default", "praca", "miejsce", "plotki"}.issubset(npc.dialogue_tree.keys()), vnum)

    def test_blacksmith_is_homed_in_zelazna_pierzeja_and_keeps_palatnerz_separate(self) -> None:
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world)
        npcs.populate()

        blacksmiths = [npc for npc in npcs.by_room(33) if npc.vnum == "blacksmith"]
        self.assertTrue(blacksmiths)
        blacksmith = blacksmiths[0]
        self.assertEqual(blacksmith.home_room_id, 33)
        self.assertEqual(world.locations[33].name, "Żelazna Pierzeja")
        self.assertEqual(world.locations[39].name, "Płatnernia pod Kowadłem")
        reachable: set[int] = {14}
        queue: deque[int] = deque([14])
        while queue:
            room_id = queue.popleft()
            for exit_ in world.locations[room_id].exits.values():
                if exit_.target_room in reachable:
                    continue
                reachable.add(exit_.target_room)
                queue.append(exit_.target_room)
        self.assertIn(33, reachable)

    def test_known_topics_and_unknown_default_work(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            merchant = next(candidate for candidate in server.services.npcs.by_room(0) if candidate.vnum == "merchant")
            self.assertEqual(merchant.dialogue("niewiadomy"), merchant.dialogue("default"))
            self.assertNotEqual(merchant.dialogue("praca"), merchant.dialogue("default"))
            self.assertNotEqual(merchant.dialogue("miejsce"), merchant.dialogue("default"))
            self.assertNotEqual(merchant.dialogue("plotki"), merchant.dialogue("default"))

    def test_talk_routes_to_topics_without_breaking_other_commands(self) -> None:
        async def run() -> None:
            with TestGameHarness() as harness:
                char = harness.create_character("dialogue_probe", room_id=0)
                topic = await harness.execute(char, "rozmawiaj kupiec praca")
                self.assertIn("Praca kupca", topic.output)

                offer = await harness.execute(char, "oferta")
                self.assertIn("krzesiwo", offer.output)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
