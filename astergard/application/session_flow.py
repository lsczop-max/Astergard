from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from astergard.application.bootstrap import GameServices
from astergard.characters.models import Character
from astergard.server.context import GameContext
from astergard.utils import send_to_client


@dataclass(slots=True)
class LoginResult:
    character: Character | None
    close_connection: bool = False


class SessionFlow:
    """Owns the login and command loop for one connected client."""

    def __init__(self, services: GameServices, context_factory: Any, prompt_renderer: Any) -> None:
        self.services = services
        self.context_factory = context_factory
        self.prompt_renderer = prompt_renderer

    async def login(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> LoginResult:
        await send_to_client(writer, "<gold>Astergard MUD</gold>\nPodaj swoje imię: ")
        username = (await reader.readline()).decode().strip()
        if not username:
            return LoginResult(None, close_connection=True)

        if self.services.repo.player_exists(username):
            await send_to_client(writer, "Podaj hasło: ")
            password = (await reader.readline()).decode().strip()
            if not self.services.repo.verify(username, password):
                await send_to_client(writer, "<red>Błędne hasło.</red>")
                return LoginResult(None, close_connection=True)
            return LoginResult(self.services.repo.load(username))

        await send_to_client(writer, "Nowa postać. Podaj hasło: ")
        password = (await reader.readline()).decode().strip()
        self.services.repo.register(username, password)
        return LoginResult(self.services.repo.load(username))

    async def send_initial_view(self, writer: asyncio.StreamWriter, context: GameContext) -> None:
        await send_to_client(
            writer,
            await self.services.dispatcher.commands["look"](context, None, 1),
            self.prompt_renderer(context.character),
        )

    async def command_loop(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, context: GameContext) -> None:
        character = context.character
        while not reader.at_eof() and character.is_alive:
            raw = (await reader.readline()).decode().strip()
            output = await self.services.dispatcher.execute_line(context, raw)
            if output:
                await send_to_client(writer, output, self.prompt_renderer(character))
