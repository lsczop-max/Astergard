from __future__ import annotations

from astergard.world.manager import WorldManager

from tools.mudlet_support import (
    MAP_FILENAME,
    mudlet_paths,
    validate_world_map,
    export_map_file,
)


def main() -> int:
    paths = mudlet_paths()
    world = WorldManager()
    world.generate_world()
    errors = validate_world_map(world)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    output_path = export_map_file(world, paths.maps_dir / MAP_FILENAME)
    print(f"Zapisano mapę Mudleta: {output_path}")
    print(f"Lokacje: {len(world.locations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
