from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from astergard.gmcp import location_room_info
from astergard.world.manager import REGION_LABELS, REGION_RANGES, WorldManager

PACKAGE_NAME = "Astergard"
PACKAGE_VERSION = "0.1.0"
MAP_VERSION = "0.1.0"
MINIMUM_MUDLET_VERSION = "4.12.0"

CLIENT_DIRNAME = Path("client") / "mudlet"
MANIFEST_FILENAME = "manifest.json"
MAP_FILENAME = "astergard_map.json"
PACKAGE_ARCHIVE_NAME = "Astergard.mpackage"

CLIENT_FILE_LIST = [
    "main.lua",
    "installer.lua",
    "README.md",
    "manifest.json",
    "src/bootstrap.lua",
    "src/core/init.lua",
    "src/core/json.lua",
    "src/gmcp/init.lua",
    "src/mapper/init.lua",
    "src/movement/init.lua",
    "src/gui/init.lua",
    "src/updater/init.lua",
    "tools/smoke_test.lua",
]


@dataclass(frozen=True, slots=True)
class MudletPaths:
    repo_root: Path
    client_root: Path
    maps_dir: Path
    releases_dir: Path
    package_dir: Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def mudlet_paths(base: Path | None = None) -> MudletPaths:
    root = base or repo_root()
    client_root = root / CLIENT_DIRNAME
    return MudletPaths(
        repo_root=root,
        client_root=client_root,
        maps_dir=client_root / "maps",
        releases_dir=client_root / "releases",
        package_dir=client_root / "package",
    )


def compare_versions(left: str, right: str) -> int:
    def parse(value: str) -> tuple[int, int, int]:
        parts = [int(piece) for piece in re.findall(r"\d+", value)[:3]]
        while len(parts) < 3:
            parts.append(0)
        return parts[0], parts[1], parts[2]

    left_parts = parse(left)
    right_parts = parse(right)
    if left_parts == right_parts:
        return 0
    return 1 if left_parts > right_parts else -1


def validate_manifest_data(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = {
        "package",
        "version",
        "map_version",
        "minimum_mudlet_version",
        "package_url",
        "map_url",
        "client_root_url",
        "files",
    }
    missing = sorted(required_keys.difference(manifest))
    if missing:
        errors.append(f"Brak pól manifestu: {', '.join(missing)}")
    for key in ("version", "map_version", "minimum_mudlet_version"):
        value = str(manifest.get(key, ""))
        if not re.fullmatch(r"\d+\.\d+\.\d+", value):
            errors.append(f"Niepoprawna wersja w polu {key}: {value!r}")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        errors.append("Pole files musi być niepustą listą plików.")
    else:
        for entry in files:
            if not isinstance(entry, str) or not entry:
                errors.append("Lista files zawiera niepoprawną ścieżkę.")
                break
    return errors


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_world_map(world: WorldManager) -> list[str]:
    errors: list[str] = []
    seen_coords: dict[tuple[str, int, int, int], int] = {}
    for room in sorted(world.locations.values(), key=lambda item: item.id):
        if not room.name.strip():
            errors.append(f"Lokacja {room.id} nie ma nazwy.")
        if room.zone not in REGION_LABELS:
            errors.append(f"Lokacja {room.id} ma nieznany region {room.zone!r}.")
        coord_key = (room.zone, room.map_x, room.map_y, room.map_z)
        existing = seen_coords.get(coord_key)
        if existing is not None and existing != room.id:
            errors.append(
                f"Kolizja współrzędnych w regionie {room.zone}: lokacje {existing} i {room.id} zajmują {coord_key[1:]}"
            )
        else:
            seen_coords[coord_key] = room.id
        for direction, exit_ in room.exits.items():
            if exit_.target_room not in world.locations:
                errors.append(
                    f"Lokacja {room.id} ma wyjście {direction!r} do brakującej lokacji {exit_.target_room}."
                )
    return errors


def map_room_record(room, world: WorldManager) -> dict[str, Any]:
    info = location_room_info(room, world).to_dict()
    record: dict[str, Any] = {
        "num": info["num"],
        "name": info["name"],
        "area": info["area"],
        "area_label": info.get("area_label", info["area"]),
        "coords": info["coords"],
        "exits": info["exits"],
    }
    if info.get("special_exits"):
        record["special_exits"] = info["special_exits"]
    return record


def world_map_payload(world: WorldManager) -> dict[str, Any]:
    rooms = [map_room_record(room, world) for room in sorted(world.locations.values(), key=lambda item: item.id)]
    return {
        "package": PACKAGE_NAME,
        "version": PACKAGE_VERSION,
        "map_version": MAP_VERSION,
        "minimum_mudlet_version": MINIMUM_MUDLET_VERSION,
        "generated_from": "astergard.world.manager.WorldManager",
        "regions": [
            {"zone": zone, "label": label, "start": start, "end": end}
            for start, end, zone, label in REGION_RANGES
        ],
        "rooms": rooms,
    }


def export_map_file(world: WorldManager, output_path: Path) -> Path:
    payload = world_map_payload(world)
    write_json(output_path, payload)
    return output_path


def ensure_client_tree(paths: MudletPaths) -> None:
    paths.client_root.mkdir(parents=True, exist_ok=True)
    paths.maps_dir.mkdir(parents=True, exist_ok=True)
    paths.releases_dir.mkdir(parents=True, exist_ok=True)
    paths.package_dir.mkdir(parents=True, exist_ok=True)


def build_release_archive(paths: MudletPaths, archive_path: Path) -> Path:
    ensure_client_tree(paths)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths.client_root.rglob("*")):
            if path.is_dir():
                continue
            if path.is_relative_to(paths.releases_dir):
                continue
            archive.write(path, path.relative_to(paths.client_root))
    return archive_path
