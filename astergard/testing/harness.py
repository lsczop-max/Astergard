from __future__ import annotations
from typing import cast

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from astergard.characters.models import Character
from astergard.server.game import GameServer
from astergard.testing.fakes import FakeWriter


@dataclass(slots=True)
class CommandTranscript:
    character: Character
    command: str
    output: str


@dataclass
class TestGameHarness:
    """Integration harness for command and engine tests.

    The harness builds a real GameServer against a temporary SQLite database,
    registers in-memory fake clients, and executes commands through the real
    dispatcher/context assembly path. It is intentionally closer to the running
    game than unit mocks, but still deterministic and fast.
    """

    __test__ = False

    db_path: str | None = None
    server: GameServer | None = None
    _temp_dir: tempfile.TemporaryDirectory[str] | None = None
    writers: dict[str, FakeWriter] = field(default_factory=dict)

    def start(self) -> "TestGameHarness":
        if self.db_path is None:
            self._temp_dir = tempfile.TemporaryDirectory()
            self.db_path = str(Path(self._temp_dir.name) / "test_mud.db")
        self.server = GameServer(self.db_path)
        return self

    def close(self) -> None:
        if self.server is not None:
            self.server.lifecycle.flush_all("test_harness_close")
            self.server = None
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None

    def __enter__(self) -> "TestGameHarness":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def require_server(self) -> GameServer:
        if self.server is None:
            raise RuntimeError("TestGameHarness.start() was not called.")
        return self.server

    def create_character(self, username: str = "tester", room_id: int = 0) -> Character:
        server = self.require_server()
        if not server.repo.player_exists(username):
            server.repo.register(username, "test-password")
        character = server.repo.load(username)
        character.room_id = room_id
        writer = FakeWriter()
        self.writers[username] = writer
        server.clients[cast(object, writer)] = character  # type: ignore[index]
        return character

    def context_for(self, character: Character):
        return self.require_server().make_context(character)

    async def execute(self, character: Character, command: str) -> CommandTranscript:
        server = self.require_server()
        output = await server.dispatcher.execute_line(server.make_context(character), command)
        return CommandTranscript(character=character, command=command, output=output)

    async def execute_many(self, character: Character, commands: list[str]) -> list[CommandTranscript]:
        transcripts: list[CommandTranscript] = []
        for command in commands:
            transcripts.append(await self.execute(character, command))
        return transcripts

    def save_and_reload_character(self, character: Character) -> Character:
        server = self.require_server()
        server.services.save_load.save_character(character, "test_harness_reload")
        return server.repo.load(character.username)

    def tick_once(self) -> None:
        server = self.require_server()
        server.heartbeat.tick_once()
