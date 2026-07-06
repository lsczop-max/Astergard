from __future__ import annotations

import json
import sqlite3
from typing import Any

from astergard.database.connections import SQLiteConnectionFactory
from astergard.items.models import Item
from astergard.npcs.models import NPC, NPCFactory
from astergard.world.manager import WorldManager
from astergard.world.models import Exit


class WorldStateRepository:
    """Durable persistence for mutable world state.

    The procedural world still comes from WorldManager.generate_world(), but D12
    persists mutable deltas that matter in a running MUD: ground items, door
    lock states, hidden elements, NPC identity/location/state/shop inventory and
    the respawn queue. This prevents every server restart from silently resetting
    the live world.
    """

    def __init__(self, connection_factory: SQLiteConnectionFactory) -> None:
        self.connection_factory = connection_factory

    def has_snapshot(self) -> bool:
        try:
            with self.connection_factory.connection() as con:
                row = con.execute("SELECT 1 FROM world_snapshots WHERE id = 1").fetchone()
            return row is not None
        except sqlite3.OperationalError as exc:
            if "world_snapshots" in str(exc):
                return False
            raise

    def save(self, world: WorldManager, npcs: dict[str, NPC]) -> None:
        payload = self._serialize(world, npcs)
        try:
            with self.connection_factory.connection() as con:
                con.execute(
                    """
                    INSERT INTO world_snapshots(id, world_json, updated_at)
                    VALUES(1, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET
                      world_json = excluded.world_json,
                      updated_at = CURRENT_TIMESTAMP,
                      save_version = save_version + 1
                    """,
                    (json.dumps(payload, ensure_ascii=False),),
                )
        except sqlite3.OperationalError as exc:
            if "world_snapshots" in str(exc):
                return
            raise

    def load_into(self, world: WorldManager, npcs: dict[str, NPC], factory: NPCFactory) -> bool:
        try:
            with self.connection_factory.connection() as con:
                row = con.execute("SELECT world_json FROM world_snapshots WHERE id = 1").fetchone()
        except sqlite3.OperationalError as exc:
            if "world_snapshots" in str(exc):
                return False
            raise
        if row is None:
            return False
        payload = json.loads(str(row[0]))
        self._hydrate(world, npcs, factory, payload)
        return True

    def save_version(self) -> int:
        try:
            with self.connection_factory.connection() as con:
                row = con.execute("SELECT save_version FROM world_snapshots WHERE id = 1").fetchone()
        except sqlite3.OperationalError as exc:
            if "world_snapshots" in str(exc):
                return 0
            raise
        return int(row[0]) if row else 0

    def _serialize(self, world: WorldManager, npcs: dict[str, NPC]) -> dict[str, Any]:
        locations: dict[str, Any] = {}
        for loc_id, loc in world.locations.items():
            locations[str(loc_id)] = {
                "items": [item.to_dict() for item in loc.items],
                "npc_ids": list(loc.npc_ids),
                "hidden_elements": [self._serialize_hidden(item) for item in loc.hidden_elements],
                "exits": {
                    direction: {
                        "target_room": exit_.target_room,
                        "is_door": exit_.is_door,
                        "is_locked": exit_.is_locked,
                        "key_vnum": exit_.key_vnum,
                    }
                    for direction, exit_ in loc.exits.items()
                },
            }
        return {
            "locations": locations,
            "npcs": {npc_id: self._serialize_npc(npc) for npc_id, npc in npcs.items()},
            "respawn_queue": list(world.respawn_queue),
        }

    def _hydrate(self, world: WorldManager, npcs: dict[str, NPC], factory: NPCFactory, payload: dict[str, Any]) -> None:
        for loc in world.locations.values():
            loc.items.clear()
            loc.npc_ids.clear()
            loc.hidden_elements.clear()
        locations = payload.get("locations", {})
        if isinstance(locations, dict):
            for raw_id, loc_payload in locations.items():
                if not isinstance(loc_payload, dict):
                    continue
                location = world.get_location(int(raw_id))
                if location is None:
                    continue
                loc = location
                loc.items = [Item.from_dict(item) for item in loc_payload.get("items", []) if isinstance(item, dict)]
                loc.npc_ids = [str(npc_id) for npc_id in loc_payload.get("npc_ids", [])]
                loc.hidden_elements = [self._hydrate_hidden(item) for item in loc_payload.get("hidden_elements", []) if isinstance(item, dict)]
                exits = loc_payload.get("exits", {})
                if isinstance(exits, dict):
                    loc.exits = {
                        str(direction): Exit(
                            target_room=int(data.get("target_room", 0)),
                            is_door=bool(data.get("is_door", False)),
                            is_locked=bool(data.get("is_locked", False)),
                            key_vnum=data.get("key_vnum"),
                        )
                        for direction, data in exits.items()
                        if isinstance(data, dict)
                    }
        npcs.clear()
        raw_npcs = payload.get("npcs", {})
        if isinstance(raw_npcs, dict):
            for npc_id, npc_payload in raw_npcs.items():
                if not isinstance(npc_payload, dict):
                    continue
                npc = factory.create(str(npc_payload.get("vnum", "wolf")), int(npc_payload.get("room_id", 0)))
                npc.id = str(npc_id)
                npc.name = str(npc_payload.get("name", npc.name))
                npc.short_desc = str(npc_payload.get("short_desc", npc.short_desc))
                npc.long_desc = str(npc_payload.get("long_desc", npc.long_desc))
                npc.zone = str(npc_payload.get("zone", npc.zone))
                npc.faction = str(npc_payload.get("faction", npc.faction))
                npc.ai_state = str(npc_payload.get("ai_state", npc.ai_state))
                npc.room_id = int(npc_payload.get("room_id", npc.room_id))
                npc.home_room_id = int(npc_payload.get("home_room_id", npc.home_room_id))
                npc.respawn_delay_seconds = int(npc_payload.get("respawn_delay_seconds", npc.respawn_delay_seconds))
                npc.threat_tier = str(npc_payload.get("threat_tier", npc.threat_tier))
                npc.threat_label = str(npc_payload.get("threat_label", npc.threat_label))
                npc.is_merchant = bool(npc_payload.get("is_merchant", npc.is_merchant))
                npc.merchant_gold = int(npc_payload.get("merchant_gold", npc.merchant_gold))
                npc.shop_inventory = [Item.from_dict(item) for item in npc_payload.get("shop_inventory", []) if isinstance(item, dict)]
                char_payload = npc_payload.get("character")
                if isinstance(char_payload, dict):
                    self._hydrate_npc_character(npc, char_payload)
                npcs[npc.id] = npc
        for loc in world.locations.values():
            loc.npc_ids = [npc_id for npc_id in loc.npc_ids if npc_id in npcs]
            for npc_id in list(npcs):
                npc = npcs[npc_id]
                if npc.room_id == loc.id and npc_id not in loc.npc_ids and len(loc.npc_ids) < 3:
                    loc.npc_ids.append(npc_id)
        respawn = payload.get("respawn_queue", [])
        world.respawn_queue = [dict(item) for item in respawn if isinstance(item, dict)]

    def _serialize_hidden(self, data: dict[str, object]) -> dict[str, Any]:
        result = dict(data)
        item = result.get("data")
        if isinstance(item, Item):
            result["data"] = item.to_dict()
            result["data_type"] = "item"
        return result

    def _hydrate_hidden(self, data: dict[str, Any]) -> dict[str, object]:
        result: dict[str, object] = dict(data)
        if result.get("data_type") == "item" and isinstance(result.get("data"), dict):
            result["data"] = Item.from_dict(result["data"])  # type: ignore[arg-type]
        return result

    def _serialize_npc(self, npc: NPC) -> dict[str, Any]:
        return {
            "vnum": npc.vnum,
            "name": npc.name,
            "short_desc": npc.short_desc,
            "long_desc": npc.long_desc,
            "zone": npc.zone,
            "faction": npc.faction,
            "ai_state": npc.ai_state,
            "room_id": npc.room_id,
            "home_room_id": npc.home_room_id,
            "respawn_delay_seconds": npc.respawn_delay_seconds,
            "threat_tier": npc.threat_tier,
            "threat_label": npc.threat_label,
            "is_merchant": npc.is_merchant,
            "merchant_gold": npc.merchant_gold,
            "shop_inventory": [item.to_dict() for item in npc.shop_inventory],
            "character": {
                "stats": npc.character.stats.__dict__,
                "skills": npc.character.skills.values,
                "inventory": [item.to_dict() for item in npc.character.inventory],
                "equipment": {slot: item.to_dict() if item is not None else None for slot, item in npc.character.equipment.items()},
                "wounds": npc.character.wounds,
                "gold": npc.character.gold,
                "is_alive": npc.character.is_alive,
                "in_combat": npc.character.in_combat,
                "combat_style": npc.character.combat_style,
                "state": npc.character.state,
            },
        }

    def _hydrate_npc_character(self, npc: NPC, data: dict[str, Any]) -> None:
        from astergard.characters.models import CharacterSkills, CharacterStats

        stats = data.get("stats")
        if isinstance(stats, dict):
            npc.character.stats = CharacterStats(**stats)
        skills = data.get("skills")
        if isinstance(skills, dict):
            npc.character.skills = CharacterSkills(skills)
        inventory = data.get("inventory", [])
        npc.character.inventory = [Item.from_dict(item) for item in inventory if isinstance(item, dict)]
        equipment = data.get("equipment", {})
        if isinstance(equipment, dict):
            npc.character.equipment = {slot: Item.from_dict(item) if isinstance(item, dict) else None for slot, item in equipment.items()}
        wounds = data.get("wounds")
        if isinstance(wounds, dict):
            npc.character.wounds = {str(part): int(level) for part, level in wounds.items()}
        npc.character.gold = int(data.get("gold", npc.character.gold))
        if "state" in data:
            npc.character.state = str(data["state"])
            npc.character.sync_flags_from_state()
        else:
            npc.character.is_alive = bool(data.get("is_alive", npc.character.is_alive))
            npc.character.in_combat = bool(data.get("in_combat", npc.character.in_combat))
            npc.character.sync_state_from_flags()
        npc.character.combat_style = str(data.get("combat_style", npc.character.combat_style))
