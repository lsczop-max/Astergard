from __future__ import annotations

from astergard.characters.models import Character
from astergard.database.connections import SQLiteConnectionFactory
from astergard.database.serialization import CharacterStateSerializer


class CharacterStateRepository:
    def __init__(self, connection_factory: SQLiteConnectionFactory, serializer: CharacterStateSerializer | None = None) -> None:
        self.connection_factory = connection_factory
        self.serializer = serializer or CharacterStateSerializer()

    def insert_new(self, username: str, password_hash: str, salt: str, character: Character) -> None:
        payload = self.serializer.to_payload(character)
        with self.connection_factory.connection() as con:
            con.execute(
                """
                INSERT INTO players(
                    username,password_hash,salt,room_id,gold,stats_json,skills_json,wounds_json,
                    reputation_json,global_reputation,local_reputation_json,renown,title,crimes_json,wanted_level,wanted_posts_json,
                    quests_json,completed_json,inventory_json,equipment_json,effects_json,combat_style,creator_json,visited_room_ids_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (username, password_hash, salt, *payload),
            )

    def load(self, username: str) -> Character:
        with self.connection_factory.connection() as con:
            row = con.execute(
                """
                SELECT room_id,gold,stats_json,skills_json,wounds_json,reputation_json,global_reputation,local_reputation_json,
                       renown,title,crimes_json,wanted_level,wanted_posts_json,quests_json,completed_json,inventory_json,equipment_json,effects_json,combat_style,creator_json,visited_room_ids_json
                FROM players WHERE username=?
                """,
                (username,),
            ).fetchone()
        if not row:
            raise KeyError(username)
        return self.serializer.hydrate(username, row)

    def save(self, character: Character) -> None:
        payload = self.serializer.to_payload(character)
        with self.connection_factory.connection() as con:
            con.execute(
                """
                UPDATE players
                SET room_id=?,gold=?,stats_json=?,skills_json=?,wounds_json=?,reputation_json=?,global_reputation=?,local_reputation_json=?,
                    renown=?,title=?,crimes_json=?,wanted_level=?,wanted_posts_json=?,quests_json=?,completed_json=?,inventory_json=?,equipment_json=?,effects_json=?,combat_style=?,creator_json=?,visited_room_ids_json=?,
                    updated_at=CURRENT_TIMESTAMP,save_version=save_version+1
                WHERE username=?
                """,
                (*payload, character.username),
            )

    def save_version(self, username: str) -> int:
        with self.connection_factory.connection() as con:
            row = con.execute("SELECT save_version FROM players WHERE username=?", (username,)).fetchone()
        if not row:
            raise KeyError(username)
        return int(row[0])
