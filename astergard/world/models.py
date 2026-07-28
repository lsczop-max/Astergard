from __future__ import annotations
from dataclasses import dataclass, field
from astergard.items.models import Item

@dataclass
class Exit:
    target_room: int
    is_door: bool = False
    is_locked: bool = False
    key_vnum: str | None = None
    kind: str = ""
    description: str = ""
    visible: bool = True
    width: str = "normal"
    slope: str = "plaski"
    material: str = ""
    requirements: tuple[str, ...] = ()

@dataclass
class Location:
    id: int
    name: str
    description: str
    zone: str
    map_x: int = 0
    map_y: int = 0
    map_z: int = 0
    exits: dict[str, Exit] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    npc_ids: list[str] = field(default_factory=list)
    hidden_elements: list[dict[str, object]] = field(default_factory=list)
    inspectables: dict[str, str] = field(default_factory=dict)
    forms: dict[str, str] = field(default_factory=dict)
    exit_forms: dict[str, dict[str, str]] = field(default_factory=dict)
    scene_profile: str = ""
    scene_anchor: str = ""
    dynamic_hooks: tuple[str, ...] = ()
