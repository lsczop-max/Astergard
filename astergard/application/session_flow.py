from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from astergard.application.bootstrap import GameServices
from astergard.characters.creation import (
    CharacterCreationError,
    CharacterCreationProfile,
    beard_prompt_text,
    build_appearance_summary,
    build_appearance_prompt_text,
    birth_region_prompt_text,
    childhood_prompt_text,
    creation_closing_text,
    creation_opening_text,
    eyes_prompt_text,
    gait_prompt_text,
    hair_prompt_text,
    height_prompt_text,
    origin_prompt_text,
    resolve_beard,
    resolve_build,
    resolve_birth_region,
    resolve_eyes,
    resolve_gait,
    resolve_origin,
    resolve_hair,
    resolve_childhood,
    resolve_height,
    resolve_scars,
    resolve_tattoos,
    scars_prompt_text,
    tattoos_prompt_text,
    validate_age,
    validate_text,
)
from astergard.characters.professions import (
    ProfessionError,
    build_selection,
    profession_menu_text,
)
from astergard.characters.models import Character
from astergard.commands.parser import CommandParser
from astergard.gmcp import core_hello_packet, room_info_packet
from astergard.server.context import GameContext
from astergard.utils import send_gmcp, send_gmcp_negotiation, send_prompt, send_text


@dataclass(slots=True)
class LoginResult:
    character: Character | None
    close_connection: bool = False


class SessionFlow:
    """Owns the login and command loop for one connected client."""

    def __init__(
        self,
        services: GameServices,
        context_factory: Any,
        prompt_renderer: Any,
    ) -> None:
        self.services = services
        self.context_factory = context_factory
        self.prompt_renderer = prompt_renderer
        self.map_payload_enabled = bool(getattr(self.services.minimap_service, "enabled", False))
        self._gmcp_announced_writers: set[int] = set()

    async def _read_line(self, reader: asyncio.StreamReader) -> str:
        return (await reader.readline()).decode("utf-8").strip()

    def _map_update_enabled(self) -> bool:
        return self.map_payload_enabled

    def _writer_key(self, writer: asyncio.StreamWriter) -> int:
        return id(writer)

    async def _ensure_gmcp_ready(self, writer: asyncio.StreamWriter) -> None:
        key = self._writer_key(writer)
        if key in self._gmcp_announced_writers:
            return
        await send_gmcp_negotiation(writer)
        await send_gmcp(writer, core_hello_packet())
        self._gmcp_announced_writers.add(key)

    async def _send_room_info(self, writer: asyncio.StreamWriter, context: GameContext) -> None:
        location = context.world.get_location(context.character.room_id)
        if location is None:
            return
        await self._ensure_gmcp_ready(writer)
        await send_gmcp(writer, room_info_packet(location, context.world))

    async def _send_full_map_debug(
        self,
        writer: asyncio.StreamWriter,
        context: GameContext,
    ) -> None:
        if not self._map_update_enabled():
            return
        payload = self.services.minimap_service.build_payload(
            context.character,
            context.world,
        )
        await send_text(
            writer,
            self.services.minimap_service.serialize_payload(payload),
        )

    async def _prompt_validated(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        prompt: str,
        validator,
        intro: str | None = None,
    ) -> Any:
        if intro:
            await send_text(writer, intro)
        while True:
            await send_prompt(writer, prompt)
            value = await self._read_line(reader)
            try:
                return validator(value)
            except (CharacterCreationError, ProfessionError) as exc:
                await send_text(writer, f"<red>{exc}</red>")

    async def _collect_creation_profile(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> CharacterCreationProfile:
        await send_text(writer, creation_opening_text())
        name = await self._prompt_validated(
            reader,
            writer,
            "— Jak cię zwać? ",
            lambda value: validate_text("Imię", value, min_length=2, max_length=32),
            "Karczmarz opiera łokcie o stół. ",
        )
        gender_description = await self._prompt_validated(
            reader,
            writer,
            "— Jak mam cię opisać w księdze? ",
            lambda value: validate_text(
                "Opis płci",
                value,
                min_length=2,
                max_length=80,
            ),
            "Kronikarz zanurza pióro w atramencie. ",
        )
        age = await self._prompt_validated(
            reader,
            writer,
            "— Ile masz lat? ",
            validate_age,
            "Karczmarz kiwa głową, jakby znał już odpowiedź, ale czeka na twoje słowo. ",
        )
        origin = await self._prompt_validated(
            reader,
            writer,
            "— Skąd przybywasz? ",
            lambda value: resolve_origin(value).key,
            origin_prompt_text(),
        )
        childhood = await self._prompt_validated(
            reader,
            writer,
            "— Gdzie dorastałeś? ",
            lambda value: resolve_childhood(value).key,
            childhood_prompt_text(),
        )
        birth_region = await self._prompt_validated(
            reader,
            writer,
            "— W jakim regionie stawiałeś pierwsze kroki? ",
            lambda value: resolve_birth_region(value).label,
            birth_region_prompt_text(),
        )
        main_profession = await self._prompt_validated(
            reader,
            writer,
            "— Czym zajmowałeś się dotąd? ",
            lambda value: build_selection(value).main_profession,
            profession_menu_text(),
        )
        secondary_profession = await self._prompt_validated(
            reader,
            writer,
            "— Czy nauczyłeś się jeszcze czegoś przy okazji? Jeśli nie, wpisz brak. ",
            lambda value: build_selection(main_profession, value).secondary_profession,
            profession_menu_text(),
        )
        build = await self._prompt_validated(
            reader,
            writer,
            "— Jakiej jesteś budowy? ",
            lambda value: resolve_build(value).label,
            build_appearance_prompt_text(),
        )
        height = await self._prompt_validated(
            reader,
            writer,
            "— Jakiego jesteś wzrostu? ",
            lambda value: resolve_height(value).label,
            height_prompt_text(),
        )
        hair = await self._prompt_validated(
            reader,
            writer,
            "— Jak wyglądają twoje włosy? ",
            lambda value: resolve_hair(value).label,
            hair_prompt_text(),
        )
        beard = await self._prompt_validated(
            reader,
            writer,
            "— Nosisz brodę? Jeśli nie, wpisz brak. ",
            lambda value: resolve_beard(value).label,
            beard_prompt_text(),
        )
        scars = await self._prompt_validated(
            reader,
            writer,
            "— Masz blizny? Jeśli nie, wpisz brak. ",
            lambda value: resolve_scars(value).label,
            scars_prompt_text(),
        )
        eyes = await self._prompt_validated(
            reader,
            writer,
            "— Jakiego koloru są twoje oczy? ",
            lambda value: resolve_eyes(value).label,
            eyes_prompt_text(),
        )
        tattoos = await self._prompt_validated(
            reader,
            writer,
            "— Masz tatuaże? Jeśli nie, wpisz brak. ",
            lambda value: resolve_tattoos(value).label,
            tattoos_prompt_text(),
        )
        gait = await self._prompt_validated(
            reader,
            writer,
            "— Jak się poruszasz? ",
            lambda value: resolve_gait(value).label,
            gait_prompt_text(),
        )
        appearance = build_appearance_summary(
            name=name,
            gender_description=gender_description,
            build=build,
            height=height,
            hair=hair,
            beard=beard,
            scars=scars,
            eyes=eyes,
            tattoos=tattoos,
            gait=gait,
        )
        return CharacterCreationProfile.build(
            name=name,
            gender_description=gender_description,
            age=age,
            origin=origin,
            childhood=childhood,
            birth_region=birth_region,
            main_profession=main_profession,
            secondary_profession=secondary_profession or None,
            appearance=appearance,
        )

    async def login(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> LoginResult:
        await send_text(writer, "<gold>Astergard MUD</gold>\nKarczmarz podnosi wzrok znad kufla. Jak się przedstawiasz? ")
        username = await self._read_line(reader)
        if not username:
            return LoginResult(None, close_connection=True)

        if self.services.repo.player_exists(username):
            await send_text(writer, "— Najpierw potrzebuję twojego hasła. ")
            password = await self._read_line(reader)
            if not self.services.repo.verify(username, password):
                await send_text(writer, "<red>Błędne hasło.</red>")
                return LoginResult(None, close_connection=True)
            character = self.services.repo.load(username)
            character.visit_current_room()
            return LoginResult(character)

        await send_text(writer, "— Jeśli to twój pierwszy raz, podaj hasło do księgi podróżnych. ")
        password = await self._read_line(reader)
        profile = await self._collect_creation_profile(reader, writer)
        self.services.repo.register(username, password, profile)
        character = self.services.repo.load(username)
        character.visit_current_room()
        await send_text(writer, creation_closing_text())
        return LoginResult(character)

    async def send_initial_view(
        self,
        writer: asyncio.StreamWriter,
        context: GameContext,
    ) -> None:
        context.character.visit_current_room()
        await self._ensure_gmcp_ready(writer)
        await send_text(
            writer,
            await self.services.dispatcher.commands["look"](context, None, 1),
        )
        await self._send_room_info(writer, context)
        await self._send_full_map_debug(writer, context)
        await send_prompt(writer, self.prompt_renderer(context.character))

    async def command_loop(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        context: GameContext,
    ) -> None:
        character = context.character
        while not reader.at_eof() and character.is_alive:
            raw = (await reader.readline()).decode("utf-8").strip()
            if not raw:
                await send_prompt(writer, self.prompt_renderer(character))
                continue
            before_room_id = character.room_id
            parsed = CommandParser.parse(raw)
            spec = (
                self.services.dispatcher.registry.get(parsed.command)
                if parsed.command
                else None
            )
            needs_full_map = spec is not None and spec.name == "debug_map"
            needs_minimap_update = spec is not None and spec.name in {"look", "move"}
            output = await self.services.dispatcher.execute_line(context, raw)
            if output:
                await send_text(writer, output)
            if character.room_id != before_room_id:
                await self._send_room_info(writer, context)
            if needs_full_map:
                await self._send_full_map_debug(writer, context)
            elif needs_minimap_update:
                await self._send_minimap_update(writer, context)
            await send_prompt(writer, self.prompt_renderer(character))

    async def _send_minimap_update(
        self,
        writer: asyncio.StreamWriter,
        context: GameContext,
    ) -> None:
        if not self._map_update_enabled():
            return
        payload = self.services.minimap_service.build_update_payload(
            context.character,
            context.world,
        )
        await send_text(
            writer,
            self.services.minimap_service.serialize_payload(payload),
        )
