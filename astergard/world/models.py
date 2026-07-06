from __future__ import annotations
from dataclasses import dataclass, field
from astergard.items.models import Item

@dataclass
class Exit:
    target_room: int
    is_door: bool = False
    is_locked: bool = False
    key_vnum: str | None = None

@dataclass
class Location:
    id: int
    name: str
    description: str
    zone: str
    exits: dict[str, Exit] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    npc_ids: list[str] = field(default_factory=list)
    hidden_elements: list[dict[str, object]] = field(default_factory=list)
    inspectables: dict[str, str] = field(default_factory=dict)
