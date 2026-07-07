from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from astergard.application.bootstrap import GameServices
from astergard.characters.creation import (
    CharacterCreationError,
    CharacterCreationProfile,
    origin_menu_text,
    resolve_origin,
    validate_age,
    validate_text,
)
from astergard.characters.professions import ProfessionError, build_selection, profession_menu_text
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

    async def _read_line(self, reader: asyncio.StreamReader) -> str:
        return (await reader.readline()).decode().strip()

    async def _prompt_validated(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        prompt: str,
        validator,
    ) -> Any:
        while True:
            await send_to_client(writer, prompt)
            value = await self._read_line(reader)
            try:
                return validator(value)
            except (CharacterCreationError, ProfessionError) as exc:
                await send_to_client(writer, f"<red>{exc}</red>")

    async def _collect_creation_profile(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> CharacterCreationProfile:
        await send_to_client(
            writer,
            "Tworzysz nową postać.\n"
            "Pochodzenie wpływa na reputację początkową i ekwipunek.\n"
            "Profesje wpływają na startowe umiejętności, ekwipunek i styl gry.\n"
            f"{origin_menu_text()}",
        )
        name = await self._prompt_validated(reader, writer, "Imię postaci: ", lambda value: validate_text("Imię", value, min_length=2, max_length=32))
        gender_description = await self._prompt_validated(
            reader,
            writer,
            "Jak opisać płeć / sposób opisu postaci? ",
            lambda value: validate_text("Opis płci", value, min_length=2, max_length=80),
        )
        age = await self._prompt_validated(reader, writer, "Wiek postaci: ", validate_age)
        origin = await self._prompt_validated(
            reader,
            writer,
            "Pochodzenie (numer albo nazwa): ",
            lambda value: resolve_origin(value).key,
        )
        birth_region = await self._prompt_validated(
            reader,
            writer,
            "Region urodzenia: ",
            lambda value: validate_text("Region urodzenia", value, min_length=2, max_length=80),
        )
        culture = await self._prompt_validated(
            reader,
            writer,
            "Kultura: ",
            lambda value: validate_text("Kultura", value, min_length=2, max_length=80),
        )
        religion = await self._prompt_validated(
            reader,
            writer,
            "Religia / wyznanie: ",
            lambda value: validate_text("Religia", value, min_length=2, max_length=80),
        )
        await send_to_client(writer, profession_menu_text())
        main_profession = await self._prompt_validated(
            reader,
            writer,
            "Wybierz profesję główną: ",
            lambda value: build_selection(value).main_profession,
        )
        secondary_profession = await self._prompt_validated(
            reader,
            writer,
            "Wybierz profesję dodatkową (0/brak jeśli nie chcesz): ",
            lambda value: build_selection(main_profession, value).secondary_profession,
        )
        appearance = await self._prompt_validated(
            reader,
            writer,
            "Wygląd: ",
            lambda value: validate_text("Wygląd", value, min_length=2, max_length=200),
        )
        history = await self._prompt_validated(
            reader,
            writer,
            "Krótka historia: ",
            lambda value: validate_text("Historia", value, min_length=10, max_length=600),
        )
        return CharacterCreationProfile.build(
            name=name,
            gender_description=gender_description,
            age=age,
            origin=origin,
            birth_region=birth_region,
            culture=culture,
            religion=religion,
            main_profession=main_profession,
            secondary_profession=secondary_profession or None,
            appearance=appearance,
            history=history,
        )

    async def login(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> LoginResult:
        await send_to_client(writer, "<gold>Astergard MUD</gold>\nPodaj swoje imię: ")
        username = await self._read_line(reader)
        if not username:
            return LoginResult(None, close_connection=True)

        if self.services.repo.player_exists(username):
            await send_to_client(writer, "Podaj hasło: ")
            password = await self._read_line(reader)
            if not self.services.repo.verify(username, password):
                await send_to_client(writer, "<red>Błędne hasło.</red>")
                return LoginResult(None, close_connection=True)
            return LoginResult(self.services.repo.load(username))

        await send_to_client(writer, "Nowa postać. Podaj hasło: ")
        password = await self._read_line(reader)
        profile = await self._collect_creation_profile(reader, writer)
        self.services.repo.register(username, password, profile)
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
