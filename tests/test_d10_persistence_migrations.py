from __future__ import annotations

import json
import sqlite3
import shutil
import tempfile
import unittest
import warnings
from pathlib import Path

import pytest

from astergard.database.migrations import MigrationRunner
from astergard.database.repository import PlayerRepository


class PersistenceMigrationTests(unittest.TestCase):
    def _copy_legacy_migrations(self, root: Path) -> Path:
        source = Path(__file__).resolve().parents[1] / "astergard" / "database" / "migrations"
        destination = root / "legacy_migrations"
        destination.mkdir()
        for path in sorted(source.glob("[0-9][0-9][0-9]_*.sql")):
            if int(path.name[:3]) <= 10:
                shutil.copy2(path, destination / path.name)
        return destination

    def _build_legacy_repository(self, db: Path, migrations_dir: Path) -> PlayerRepository:
        repo = PlayerRepository(str(db), migration_runner=MigrationRunner(migrations_dir))
        self.assertEqual(repo.current_schema_version(), 10)
        return repo

    def _seed_player_with_effects(self, repo: PlayerRepository, username: str, effects: list[dict[str, object]]) -> None:
        self.assertTrue(repo.register(username, "secret"))
        with repo.connection() as con:
            con.execute(
                "UPDATE players SET effects_json=? WHERE username=?",
                (json.dumps(effects, ensure_ascii=False), username),
            )
            save_version = con.execute("SELECT save_version FROM players WHERE username=?", (username,)).fetchone()[0]
        self.assertEqual(save_version, 1)

    def _build_null_effects_repository(self, db: Path, username: str) -> PlayerRepository:
        with sqlite3.connect(db) as con:
            con.executescript(
                """
                CREATE TABLE schema_migrations(
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO schema_migrations(version, name) VALUES
                    (1, '001_initial.sql'),
                    (2, '002_audit_timestamps.sql'),
                    (3, '003_save_slots.sql'),
                    (4, '004_career_paths.sql'),
                    (5, '005_world_state.sql'),
                    (6, '006_combat_style.sql'),
                    (7, '007_save_manifests.sql'),
                    (8, '008_identity.sql'),
                    (9, '009_creator_profile.sql'),
                    (10, '010_visited_rooms.sql'),
                    (11, '011_remove_legacy_magic_effects.sql');
                CREATE TABLE players(
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    room_id INTEGER NOT NULL,
                    gold INTEGER NOT NULL,
                    stats_json TEXT NOT NULL,
                    skills_json TEXT NOT NULL,
                    wounds_json TEXT NOT NULL,
                    reputation_json TEXT NOT NULL,
                    global_reputation INTEGER NOT NULL DEFAULT 0,
                    local_reputation_json TEXT NOT NULL DEFAULT '{}',
                    renown INTEGER NOT NULL DEFAULT 0,
                    title TEXT NOT NULL DEFAULT 'Wędrowiec',
                    crimes_json TEXT NOT NULL DEFAULT '{}',
                    wanted_level INTEGER NOT NULL DEFAULT 0,
                    wanted_posts_json TEXT NOT NULL DEFAULT '[]',
                    quests_json TEXT NOT NULL DEFAULT '{}',
                    completed_json TEXT NOT NULL DEFAULT '[]',
                    inventory_json TEXT NOT NULL DEFAULT '[]',
                    equipment_json TEXT NOT NULL DEFAULT '{}',
                    effects_json TEXT,
                    combat_style TEXT NOT NULL DEFAULT 'zrownowazony',
                    creator_json TEXT NOT NULL DEFAULT '{}',
                    visited_room_ids_json TEXT NOT NULL DEFAULT '[]',
                    save_version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE audit_events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            con.execute(
                """
                INSERT INTO players(
                    username,password_hash,salt,room_id,gold,stats_json,skills_json,wounds_json,reputation_json,
                    global_reputation,local_reputation_json,renown,title,crimes_json,wanted_level,wanted_posts_json,
                    quests_json,completed_json,inventory_json,equipment_json,effects_json,combat_style,creator_json,
                    visited_room_ids_json,save_version
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    username,
                    "hash",
                    "salt",
                    7,
                    42,
                    json.dumps({"sila": 10, "zrecznosc": 10, "wytrzymalosc": 10, "percepcja": 10, "sila_woli": 10, "kondycja": 100}, ensure_ascii=False),
                    json.dumps({"brawl": {"level": 1, "progress": 0}}, ensure_ascii=False),
                    json.dumps({"glowa": 0, "korpus": 0, "prawa_reka": 0, "lewa_reka": 0, "prawa_noga": 0, "lewa_noga": 0}, ensure_ascii=False),
                    json.dumps({"MEEKHAN": 2}, ensure_ascii=False),
                    3,
                    json.dumps({"MEEKHAN": 2}, ensure_ascii=False),
                    3,
                    "Kapitan",
                    json.dumps({"kradzież": 1}, ensure_ascii=False),
                    4,
                    json.dumps(["test"], ensure_ascii=False),
                    json.dumps({}, ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                    json.dumps({}, ensure_ascii=False),
                    None,
                    "agresywny",
                    json.dumps({}, ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                    1,
                ),
            )
        return PlayerRepository(str(db))

    def test_migrations_are_applied_once_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "mud.db"
            repo = PlayerRepository(str(db))
            self.assertEqual(repo.current_schema_version(), 11)
            with repo.connection() as con:
                rows = con.execute("SELECT version, name FROM schema_migrations ORDER BY version").fetchall()
            self.assertEqual([row[0] for row in rows], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            self.assertEqual(len(rows), 11)

    def test_legacy_magic_effects_are_migrated_once_and_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "mud.db"
            migrations_dir = self._copy_legacy_migrations(root)
            repo_v10 = self._build_legacy_repository(db, migrations_dir)
            self._seed_player_with_effects(
                repo_v10,
                "Lukas",
                [
                    {"name": "Wzmocnienie", "modifier_stat": "sila", "value": 4, "duration_ticks": 19, "marker": "legacy-1"},
                    {"name": "Opatrunek", "modifier_stat": "kondycja", "value": 5, "duration_ticks": 3, "marker": "keep-1"},
                    {"name": "Wzmocnienie", "modifier_stat": "sila", "value": 4.0, "duration_ticks": 7, "marker": "keep-2"},
                    {"name": "Odrzut Źródła", "modifier_stat": "sila_woli", "value": -2, "duration_ticks": 10, "marker": "legacy-2"},
                ],
            )
            with repo_v10.connection() as con:
                raw_before = json.loads(con.execute("SELECT effects_json FROM players WHERE username=?", ("Lukas",)).fetchone()[0])
            self.assertEqual([effect["name"] for effect in raw_before], ["Wzmocnienie", "Opatrunek", "Wzmocnienie", "Odrzut Źródła"])
            self.assertEqual(repo_v10.save_version("Lukas"), 1)

            repo = PlayerRepository(str(db))
            self.assertEqual(repo.current_schema_version(), 11)
            with repo.connection() as con:
                effects_json, save_version = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("Lukas",),
                ).fetchone()
            self.assertEqual(save_version, 1)
            migrated_effects = json.loads(effects_json)
            self.assertEqual(effects_json, json.dumps(migrated_effects, ensure_ascii=False, separators=(",", ":")))
            self.assertEqual([effect["name"] for effect in migrated_effects], ["Opatrunek", "Wzmocnienie"])
            self.assertEqual(migrated_effects[0]["modifier_stat"], "kondycja")
            self.assertEqual(migrated_effects[0]["value"], 5)
            self.assertEqual(migrated_effects[0]["duration_ticks"], 3)
            self.assertEqual(migrated_effects[0]["marker"], "keep-1")
            self.assertEqual(migrated_effects[1]["modifier_stat"], "sila")
            self.assertEqual(migrated_effects[1]["value"], 4.0)
            self.assertEqual(migrated_effects[1]["duration_ticks"], 7)
            self.assertEqual(migrated_effects[1]["marker"], "keep-2")

            repo_again = PlayerRepository(str(db))
            with repo_again.connection() as con:
                effects_json_again, save_version_again = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("Lukas",),
                ).fetchone()
            self.assertEqual(save_version_again, 1)
            self.assertEqual(json.loads(effects_json_again), migrated_effects)

            loaded = repo.load("Lukas")
            self.assertEqual([effect.name for effect in loaded.active_effects], ["Opatrunek", "Wzmocnienie"])
            self.assertEqual(loaded.active_effects[0].modifier_stat, "kondycja")
            self.assertEqual(loaded.active_effects[0].value, 5)
            self.assertEqual(loaded.active_effects[0].duration_ticks, 3)
            self.assertEqual(loaded.active_effects[1].modifier_stat, "sila")
            self.assertEqual(loaded.active_effects[1].value, 4)
            self.assertEqual(loaded.active_effects[1].duration_ticks, 7)

            repo.save(loaded)
            reloaded = repo.load("Lukas")
            self.assertEqual([effect.name for effect in reloaded.active_effects], ["Opatrunek", "Wzmocnienie"])
            self.assertEqual(reloaded.active_effects[0].modifier_stat, "kondycja")
            self.assertEqual(reloaded.active_effects[0].value, 5)
            self.assertEqual(reloaded.active_effects[0].duration_ticks, 3)
            self.assertEqual(reloaded.active_effects[1].modifier_stat, "sila")
            self.assertEqual(reloaded.active_effects[1].value, 4)
            self.assertEqual(reloaded.active_effects[1].duration_ticks, 7)
            with repo.connection() as con:
                effects_json_after_save, save_version_after_save = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("Lukas",),
                ).fetchone()
            self.assertEqual(save_version_after_save, 2)
            self.assertEqual(json.loads(effects_json_after_save), [
                {"name": "Opatrunek", "modifier_stat": "kondycja", "value": 5, "duration_ticks": 3},
                {"name": "Wzmocnienie", "modifier_stat": "sila", "value": 4, "duration_ticks": 7},
            ])

    def test_legacy_magic_signature_requires_exact_integer_value(self) -> None:
        cases = [
            (4, True),
            (4.0, False),
            ("4", False),
            ("4.9", False),
            (True, False),
            (None, False),
        ]
        for value, should_remove in cases:
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    db = root / "mud.db"
                    migrations_dir = self._copy_legacy_migrations(root)
                    repo_v10 = self._build_legacy_repository(db, migrations_dir)
                    self._seed_player_with_effects(
                        repo_v10,
                        "tester",
                        [
                            {
                                "name": "Wzmocnienie",
                                "modifier_stat": "sila",
                                "value": value,
                                "duration_ticks": 5,
                                "marker": "candidate",
                            }
                        ],
                    )

                    repo = PlayerRepository(str(db))
                    with repo.connection() as con:
                        effects_json = con.execute("SELECT effects_json FROM players WHERE username=?", ("tester",)).fetchone()[0]
                    effects = json.loads(effects_json)
                    if should_remove:
                        self.assertEqual(effects_json, "[]")
                        self.assertEqual(effects, [])
                        continue
                    self.assertEqual(len(effects), 1)
                    self.assertEqual(effects[0]["name"], "Wzmocnienie")
                    self.assertEqual(effects[0]["modifier_stat"], "sila")
                    self.assertEqual(effects[0]["value"], value)
                    self.assertEqual(effects[0]["duration_ticks"], 5)
                    self.assertEqual(effects[0]["marker"], "candidate")

    def test_legacy_magic_effects_preserve_similar_and_missing_value_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "mud.db"
            migrations_dir = self._copy_legacy_migrations(root)
            repo_v10 = self._build_legacy_repository(db, migrations_dir)
            self._seed_player_with_effects(
                repo_v10,
                "preserve",
                [
                    {"name": "Wzmocnienie", "modifier_stat": "sila", "value": 4, "duration_ticks": 19, "marker": "legacy-1"},
                    {"name": "Opatrunek", "modifier_stat": "kondycja", "value": 5, "duration_ticks": 3, "marker": "keep-1"},
                    {"name": "Wzmocnienie", "modifier_stat": "sila", "value": 5, "duration_ticks": 7, "marker": "keep-2"},
                    {"name": "Wzmocnienie", "modifier_stat": "sila", "duration_ticks": 11, "marker": "keep-3"},
                    {"name": "Odrzut Źródła", "modifier_stat": "sila_woli", "value": -2, "duration_ticks": 10, "marker": "legacy-2"},
                ],
            )

            repo = PlayerRepository(str(db))
            with repo.connection() as con:
                effects_json, save_version = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("preserve",),
                ).fetchone()
            self.assertEqual(save_version, 1)
            effects = json.loads(effects_json)
            self.assertEqual([effect["name"] for effect in effects], ["Opatrunek", "Wzmocnienie", "Wzmocnienie"])
            self.assertEqual(effects[0], {"name": "Opatrunek", "modifier_stat": "kondycja", "value": 5, "duration_ticks": 3, "marker": "keep-1"})
            self.assertEqual(effects[1], {"name": "Wzmocnienie", "modifier_stat": "sila", "value": 5, "duration_ticks": 7, "marker": "keep-2"})
            self.assertEqual(effects[2]["name"], "Wzmocnienie")
            self.assertEqual(effects[2]["modifier_stat"], "sila")
            self.assertEqual(effects[2]["duration_ticks"], 11)
            self.assertEqual(effects[2]["marker"], "keep-3")
            self.assertNotIn("value", effects[2])

            repo_again = PlayerRepository(str(db))
            with repo_again.connection() as con:
                effects_json_again, save_version_again = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("preserve",),
                ).fetchone()
            self.assertEqual(save_version_again, 1)
            self.assertEqual(json.loads(effects_json_again), effects)

    def test_invalid_top_level_effects_json_is_loaded_as_empty_effects_with_warning(self) -> None:
        cases = [
            ("corrupted", "not-json", r"^Nieprawidłowe effects_json w zapisie postaci corrupted; użyto pustej listy efektów\.$"),
            ("empty", "", r"^Nieprawidłowe effects_json w zapisie postaci empty; użyto pustej listy efektów\.$"),
            ("object", "{}", r"^Nieprawidłowe effects_json w zapisie postaci object; użyto pustej listy efektów\.$"),
        ]
        for username, raw_effects_json, pattern in cases:
            with self.subTest(username=username, raw_effects_json=raw_effects_json):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    db = root / "mud.db"
                    migrations_dir = self._copy_legacy_migrations(root)
                    repo_v10 = self._build_legacy_repository(db, migrations_dir)
                    self._seed_player_with_effects(
                        repo_v10,
                        username,
                        [
                            {"name": "Opatrunek", "modifier_stat": "kondycja", "value": 5, "duration_ticks": 3},
                        ],
                    )
                    with repo_v10.connection() as con:
                        con.execute("UPDATE players SET effects_json=? WHERE username=?", (raw_effects_json, username))

                    repo = PlayerRepository(str(db))
                    with pytest.warns(UserWarning, match=pattern) as record:
                        loaded = repo.load(username)
                    self.assertEqual(len(record), 1)
                    self.assertEqual(loaded.active_effects, [])
                    with repo.connection() as con:
                        stored_effects_json, save_version = con.execute(
                            "SELECT effects_json, save_version FROM players WHERE username=?",
                            (username,),
                        ).fetchone()
                    self.assertEqual(stored_effects_json, raw_effects_json)
                    self.assertEqual(save_version, 1)

                    repo.save(loaded)
                    with repo.connection() as con:
                        saved_effects_json, saved_version = con.execute(
                            "SELECT effects_json, save_version FROM players WHERE username=?",
                            (username,),
                        ).fetchone()
                    self.assertEqual(saved_effects_json, "[]")
                    self.assertEqual(saved_version, 2)

                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        loaded_again = repo.load(username)
                    self.assertEqual(len(caught), 0)
                    self.assertEqual(loaded_again.active_effects, [])

    def test_null_effects_json_is_loaded_as_empty_effects_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "mud.db"
            repo = self._build_null_effects_repository(db, "nullable")
            with pytest.warns(UserWarning, match=r"^Nieprawidłowe effects_json w zapisie postaci nullable; użyto pustej listy efektów\.$") as record:
                loaded = repo.load("nullable")
            self.assertEqual(len(record), 1)
            self.assertEqual(loaded.active_effects, [])
            with repo.connection() as con:
                stored_effects_json, save_version = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("nullable",),
                ).fetchone()
            self.assertIsNone(stored_effects_json)
            self.assertEqual(save_version, 1)

            repo.save(loaded)
            with repo.connection() as con:
                saved_effects_json, saved_version = con.execute(
                    "SELECT effects_json, save_version FROM players WHERE username=?",
                    ("nullable",),
                ).fetchone()
            self.assertEqual(saved_effects_json, "[]")
            self.assertEqual(saved_version, 2)

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                loaded_again = repo.load("nullable")
            self.assertEqual(len(caught), 0)
            self.assertEqual(loaded_again.active_effects, [])

    def test_malformed_active_effects_are_skipped_with_single_warning(self) -> None:
        cases = [
            ("null_elem", '[null]', [], 1),
            ("empty_obj", '[{}]', [], 1),
            ("missing_name", '[{"name": "Test"}]', [], 1),
            (
                "bad_value",
                '[{"name": "Test", "modifier_stat": "sila", "value": "abc", "duration_ticks": 1}]',
                [],
                1,
            ),
            (
                "bad_duration",
                '[{"name": "Test", "modifier_stat": "sila", "value": 4, "duration_ticks": "x"}]',
                [],
                1,
            ),
            (
                "overflow",
                '[{"name": "Test", "modifier_stat": "sila", "value": 1e1000, "duration_ticks": 1}]',
                [],
                1,
            ),
            (
                "mixed",
                '[{"name": "First", "modifier_stat": "kondycja", "value": 3, "duration_ticks": 2, "marker": "a"},'
                '{"name": "Broken"},'
                'null,'
                '{"name": "Second", "modifier_stat": "sila", "value": 5, "duration_ticks": 7, "marker": "b"},'
                '{"name": "Oops", "modifier_stat": "sila", "value": "x", "duration_ticks": 9}]',
                [
                    {"name": "First", "modifier_stat": "kondycja", "value": 3, "duration_ticks": 2},
                    {"name": "Second", "modifier_stat": "sila", "value": 5, "duration_ticks": 7},
                ],
                3,
            ),
        ]
        for username, raw_effects_json, expected_effects, skipped in cases:
            with self.subTest(username=username):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    db = root / "mud.db"
                    migrations_dir = self._copy_legacy_migrations(root)
                    repo_v10 = self._build_legacy_repository(db, migrations_dir)
                    self._seed_player_with_effects(
                        repo_v10,
                        username,
                        [{"name": "Opatrunek", "modifier_stat": "kondycja", "value": 5, "duration_ticks": 3}],
                    )
                    with repo_v10.connection() as con:
                        con.execute("UPDATE players SET effects_json=? WHERE username=?", (raw_effects_json, username))

                    repo = PlayerRepository(str(db))
                    with pytest.warns(
                        UserWarning,
                        match=rf"^Nieprawidłowe elementy effects_json w zapisie postaci {username}; pominięto {skipped} element\(ów\)\.$",
                    ) as record:
                        loaded = repo.load(username)
                    self.assertEqual(len(record), 1)
                    self.assertEqual([effect.to_dict() for effect in loaded.active_effects], expected_effects)
                    with repo.connection() as con:
                        stored_effects_json, save_version = con.execute(
                            "SELECT effects_json, save_version FROM players WHERE username=?",
                            (username,),
                        ).fetchone()
                    self.assertEqual(stored_effects_json, raw_effects_json)
                    self.assertEqual(save_version, 1)

                    repo.save(loaded)
                    with repo.connection() as con:
                        saved_effects_json, saved_version = con.execute(
                            "SELECT effects_json, save_version FROM players WHERE username=?",
                            (username,),
                        ).fetchone()
                    self.assertEqual(json.loads(saved_effects_json), expected_effects)
                    self.assertEqual(saved_version, 2)

                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        loaded_again = repo.load(username)
                    self.assertEqual(len(caught), 0)
                    self.assertEqual([effect.to_dict() for effect in loaded_again.active_effects], expected_effects)

    def test_migration_runner_rejects_invalid_file_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            migrations = Path(tmp)
            (migrations / "bad.sql").write_text("SELECT 1;", encoding="utf-8")
            runner = MigrationRunner(migrations)
            with self.assertRaises(RuntimeError):
                runner.discover()


if __name__ == "__main__":
    unittest.main()
