from __future__ import annotations

import asyncio
import json
import unittest
import warnings
from collections import deque

from astergard.characters.models import Character
from astergard.combat.actions import DefenseResolution, DefenseType
from astergard.combat.defense import DefenseContext, build_defense_candidates, can_select_defense_style, resolve_defense, select_defense_style
from astergard.database.serialization import CharacterStateSerializer
from astergard.items.models import Item
from astergard.rules.combat_specialization import ActiveDefenseStyle, CombatSpecializationLoadout, learn_specialization
from astergard.testing import TestGameHarness


class ScriptedRng:
    def __init__(self, randint_values: list[int] | None = None, random_values: list[float] | None = None) -> None:
        self.randint_values = deque(randint_values or [])
        self.random_values = deque(random_values or [])

    def randint(self, a: int, b: int) -> int:
        if self.randint_values:
            return self.randint_values.popleft()
        return a

    def random(self) -> float:
        if self.random_values:
            return self.random_values.popleft()
        return 1.0


def _clear_combat_slots(character: Character) -> None:
    for slot in ("bron_glowna", "bron_pomocnicza", "tarcza", "prawa_reka", "lewa_reka"):
        character.equipment[slot] = None


def _parry_weapon() -> Item:
    return Item(
        "miecz profilowany",
        "",
        1.0,
        10,
        "parry_sword",
        item_type="weapon",
        slot="bron_glowna",
        weapon_profile_id="garrison_short_sword",
        weapon_type="miecz",
        parry_bonus=80,
    )


def _shield() -> Item:
    return Item(
        "tarcza profilowana",
        "",
        1.0,
        10,
        "profiled_shield",
        item_type="shield",
        slot="tarcza",
        shield_block=80,
    )


def _two_handed_weapon() -> Item:
    return Item(
        "halabarda profilowana",
        "",
        1.0,
        10,
        "halberd_profiled",
        item_type="weapon",
        slot="bron_glowna",
        weapon_profile_id="watch_halberd",
        weapon_type="halabarda",
        parry_bonus=10,
    )


class D45ActiveDefenseStyleTests(unittest.TestCase):
    def test_selection_requires_knowledge_and_equipment(self) -> None:
        with TestGameHarness() as harness:
            harness.require_server()
            hero = harness.create_character("defense_style_hero", room_id=101)
            hero.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            _clear_combat_slots(hero)

            self.assertTrue(can_select_defense_style(hero, ActiveDefenseStyle.DODGE).allowed)
            self.assertEqual(can_select_defense_style(hero, ActiveDefenseStyle.PARRY).reason_code, "NO_ACTIVE_WEAPON")
            self.assertEqual(can_select_defense_style(hero, ActiveDefenseStyle.SHIELD).reason_code, "NO_ACTIVE_SHIELD")

            hero.equipment["bron_glowna"] = _parry_weapon()
            hero.equipment["tarcza"] = _shield()
            self.assertTrue(can_select_defense_style(hero, ActiveDefenseStyle.PARRY).allowed)
            self.assertTrue(can_select_defense_style(hero, ActiveDefenseStyle.SHIELD).allowed)

            selected = select_defense_style(hero, ActiveDefenseStyle.PARRY)
            self.assertTrue(selected.allowed)
            self.assertEqual(hero.active_defense_style, ActiveDefenseStyle.PARRY.value)
            self.assertEqual(can_select_defense_style(hero, ActiveDefenseStyle.PARRY).reason_code, "DEFENSE_STYLE_ALREADY_ACTIVE")

            hero.equipment["bron_glowna"] = _two_handed_weapon()
            self.assertEqual(can_select_defense_style(hero, ActiveDefenseStyle.SHIELD).reason_code, "INCOMPATIBLE_TWO_HANDED_WEAPON")

            hero.equipment["bron_glowna"] = None
            hero.active_defense_style = None
            self.assertEqual(can_select_defense_style(hero, ActiveDefenseStyle.PARRY).reason_code, "NO_ACTIVE_WEAPON")

    def test_learning_first_defense_sets_active_style_and_keeps_it_after_second_choice(self) -> None:
        hero = Character("learner")
        hero.skills.values["uniki"]["level"] = 12
        hero.skills.values["parowanie"]["level"] = 12
        hero.combat_specializations = CombatSpecializationLoadout()

        first = learn_specialization(hero, "defense", "uniki")
        self.assertTrue(first.allowed)
        self.assertEqual(hero.active_defense_style, ActiveDefenseStyle.DODGE.value)

        second = learn_specialization(hero, "defense", "parowanie")
        self.assertTrue(second.allowed)
        self.assertEqual(hero.active_defense_style, ActiveDefenseStyle.DODGE.value)

    def test_dynamic_resolver_chooses_best_available_candidates(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("attacker", room_id=101)
            defender = harness.create_character("defender", room_id=101)
            defender.combat_specializations = CombatSpecializationLoadout(defense_specializations=("uniki", "parowanie", "tarcze"))
            attacker.equipment["bron_glowna"] = _parry_weapon()
            defender.equipment["bron_glowna"] = _parry_weapon()
            defender.equipment["tarcza"] = _shield()
            defender.skills.values["tarcze"]["level"] = 90
            defender.skills.values["uniki"]["level"] = 60
            defender.skills.values["parowanie"]["level"] = 50

            defender.active_defense_style = ActiveDefenseStyle.DODGE.value
            candidates = build_defense_candidates(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1, 1, 1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual([candidate.defense_type for candidate in candidates], [DefenseType.SHIELD_BLOCK, DefenseType.DODGE, DefenseType.PARRY])
            self.assertGreater(candidates[0].effective_value, candidates[1].effective_value)

            defender.active_defense_style = ActiveDefenseStyle.PARRY.value
            outcome = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(outcome.resolution, DefenseResolution.BLOCKED)
            self.assertTrue(outcome.successful_defense)
            self.assertEqual(outcome.selected_defense, DefenseType.SHIELD_BLOCK)

    def test_failed_active_defense_still_allows_existing_hit_pipeline(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("attacker_hit", room_id=101)
            defender = harness.create_character("defender_hit", room_id=101)
            attacker.equipment["bron_glowna"] = _parry_weapon()
            attacker.skills.values["bron_jednoraczna"]["level"] = 20
            defender.skills.values["uniki"]["level"] = 1
            defender.active_defense_style = ActiveDefenseStyle.DODGE.value

            result = server.combat.attack(attacker, defender)

            assert result.combat_outcome is not None
            self.assertTrue(result.hit)
            self.assertIn(result.combat_outcome.result_type.value, {"HIT", "TARGET_DEFEATED"})
            self.assertIsNotNone(result.combat_outcome.defense_outcome)
            assert result.combat_outcome.defense_outcome is not None
            self.assertGreaterEqual(len(result.combat_outcome.defense_outcome.attempts), 1)
            self.assertFalse(result.combat_outcome.defense_outcome.successful_defense)

    def test_legacy_none_falls_back_to_dynamic_candidates(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("legacy_attacker", room_id=101)
            defender = harness.create_character("legacy_defender", room_id=101)
            _clear_combat_slots(defender)
            defender.active_defense_style = None

            legacy_outcome = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=defender,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual([attempt.defense_type for attempt in legacy_outcome.attempts], [DefenseType.DODGE])

    def test_command_sets_and_reports_style_and_preview_shows_it(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            hero = harness.create_character("command_hero", room_id=101)
            hero.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie", "tarcze"))
            hero.equipment["bron_glowna"] = _parry_weapon()
            ctx = harness.context_for(hero)

            output = asyncio.run(harness.execute(hero, "bron sie parowaniem"))
            self.assertIn("Unosisz broń", output.output)
            self.assertEqual(hero.active_defense_style, ActiveDefenseStyle.PARRY.value)

            preview = asyncio.run(harness.execute(hero, "profil"))
            self.assertIn("Sposób obrony: parowanie", preview.output)

            status = asyncio.run(harness.execute(hero, "bron sie"))
            self.assertIn("Sposób obrony: parowanie", status.output)

            refusal = server.services.combat_service.set_defense_style(ctx.combat_context(), "tarcza")
            self.assertIn("Nie masz tarczy", refusal)

    def test_serialization_preserves_active_style_and_clears_invalid_data(self) -> None:
        character = Character("serializer")
        character.active_defense_style = ActiveDefenseStyle.SHIELD.value

        payload = list(CharacterStateSerializer.to_payload(character))
        profile = json.loads(payload[19])
        self.assertEqual(profile["active_defense_style"], ActiveDefenseStyle.SHIELD.value)

        restored = CharacterStateSerializer.hydrate("serializer", tuple(payload))
        self.assertEqual(restored.active_defense_style, ActiveDefenseStyle.SHIELD.value)

        legacy_profile = dict(profile)
        legacy_profile.pop("active_defense_style", None)
        legacy_payload = list(payload)
        legacy_payload[19] = json.dumps(legacy_profile, ensure_ascii=False)
        legacy_restored = CharacterStateSerializer.hydrate("legacy", tuple(legacy_payload))
        self.assertIsNone(legacy_restored.active_defense_style)

        unknown_profile = dict(profile)
        unknown_profile["active_defense_style"] = "BROKEN"
        unknown_payload = list(payload)
        unknown_payload[19] = json.dumps(unknown_profile, ensure_ascii=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            unknown_restored = CharacterStateSerializer.hydrate("unknown", tuple(unknown_payload))
        self.assertIsNone(unknown_restored.active_defense_style)
        self.assertTrue(caught)

    def test_npc_prefers_active_style_and_legacy_fallback_remains_available(self) -> None:
        with TestGameHarness() as harness:
            server = harness.require_server()
            attacker = harness.create_character("npc_attacker", room_id=101)
            npc = next(npc for npc in server.npcs.by_room(101) if npc.vnum == "wolf")
            npc.character.combat_specializations = CombatSpecializationLoadout(defense_specializations=("parowanie",))
            npc.character.equipment["bron_glowna"] = _parry_weapon()
            npc.character.active_defense_style = ActiveDefenseStyle.PARRY.value

            preferred = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=npc.character,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(randint_values=[1]),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(preferred.resolution, DefenseResolution.PARRIED)

            npc.character.active_defense_style = None
            legacy = resolve_defense(
                DefenseContext(
                    attacker=attacker,
                    defender=npc.character,
                    hit_score=60,
                    dodge_score=1,
                    rng=ScriptedRng(),
                    rules=server.combat.rules,
                )
            )
            self.assertEqual(preferred.resolution, legacy.resolution)
            self.assertEqual([attempt.defense_type for attempt in preferred.attempts], [attempt.defense_type for attempt in legacy.attempts])


if __name__ == "__main__":
    unittest.main()
