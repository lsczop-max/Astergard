from __future__ import annotations

from pathlib import Path

from astergard.world.manager import WorldManager

from tools.mudlet_support import (
    PACKAGE_ARCHIVE_NAME,
    MAP_FILENAME,
    PACKAGE_NAME,
    CLIENT_FILE_LIST,
    build_release_archive,
    export_map_file,
    load_manifest,
    mudlet_paths,
    validate_manifest_data,
    validate_world_map,
    write_json,
)


def _ensure_manifest(paths) -> dict[str, object]:
    manifest_path = paths.client_root / "manifest.json"
    manifest = load_manifest(manifest_path)
    errors = validate_manifest_data(manifest)
    if errors:
        raise SystemExit("\n".join(errors))
    return manifest


def _ensure_expected_files(paths) -> None:
    missing = [rel for rel in CLIENT_FILE_LIST if not (paths.client_root / rel).exists()]
    if missing:
        raise SystemExit("Brak wymaganych plików klienta: " + ", ".join(missing))


def _write_package_index(paths, manifest: dict[str, object]) -> Path:
    index_path = paths.package_dir / "package_index.json"
    write_json(
        index_path,
        {
            "package": PACKAGE_NAME,
            "files": CLIENT_FILE_LIST,
            "manifest_version": manifest["version"],
            "map_version": manifest["map_version"],
        },
    )
    return index_path


def main() -> int:
    paths = mudlet_paths()
    world = WorldManager()
    world.generate_world()
    errors = validate_world_map(world)
    if errors:
        raise SystemExit("\n".join(errors))

    export_map_file(world, paths.maps_dir / MAP_FILENAME)
    manifest = _ensure_manifest(paths)
    _ensure_expected_files(paths)
    package_index = _write_package_index(paths, manifest)

    archive_path = paths.releases_dir / PACKAGE_ARCHIVE_NAME
    build_release_archive(paths, archive_path)

    print(f"Pakiet {PACKAGE_NAME} {manifest['version']} zbudowany.")
    print(f"Mapa: {paths.maps_dir / MAP_FILENAME}")
    print(f"Archiwum: {archive_path}")
    print(f"Indeks pakietu: {package_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
