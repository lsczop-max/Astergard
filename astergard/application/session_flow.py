from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from astergard.application.bootstrap import GameServices
from astergard.characters.creation import (
    CharacterCreationError,
    CharacterCreationProfile,
    build_appearance_summary,
    childhood_prompt_text,
    creation_closing_text,
    creation_opening_text,
    resolve_origin,
    resolve_childhood,
    validate_age,
    validate_text,
)
from astergard.characters.professions import (
    ProfessionError,
    build_selection,
)
from astergard.characters.models import Character
from astergard.commands.parser import CommandParser
from astergard.server.context import GameContext
from astergard.utils import send_prompt, send_text


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

    async def _read_line(self, reader: asyncio.StreamReader) -> str:
        return (await reader.readline()).decode("utf-8").strip()

    def _map_update_enabled(self) -> bool:
        return self.map_payload_enabled

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
            "Karczmarz przez chwilę milczy. Potem wskazuje na zewnątrz, jakby znał wszystkie drogi świata. "
            "Wystarczy jedno słowo albo nazwa miejsca: mieszczanin Astergardu, chłop z Podgrodzia, dziecko traktu, uczeń rzemieślnika, były strażnik, rybak znad rzeki albo włóczęga.\n",
        )
        childhood = await self._prompt_validated(
            reader,
            writer,
            "— Gdzie dorastałeś? ",
            lambda value: resolve_childhood(value).key,
            childhood_prompt_text() + "\n",
        )
        birth_region = await self._prompt_validated(
            reader,
            writer,
            "— W jakim regionie stawiałeś pierwsze kroki? ",
            lambda value: validate_text(
                "Region urodzenia",
                value,
                min_length=2,
                max_length=80,
            ),
            "Kronikarz odsuwa kubek i czeka cierpliwie. ",
        )
        culture = await self._prompt_validated(
            reader,
            writer,
            "— Jaką kulturę nosisz w sobie? ",
            lambda value: validate_text("Kultura", value, min_length=2, max_length=80),
            "Karczmarz poprawia rękawy. ",
        )
        religion = await self._prompt_validated(
            reader,
            writer,
            "— Komu składasz modlitwy? ",
            lambda value: validate_text("Religia", value, min_length=2, max_length=80),
            "Kronikarz nie podnosi wzroku znad księgi. ",
        )
        main_profession = await self._prompt_validated(
            reader,
            writer,
            "— Czym zajmowałeś się dotąd? ",
            lambda value: build_selection(value).main_profession,
            "Karczmarz przesuwa w twoją stronę kubek. ",
        )
        secondary_profession = await self._prompt_validated(
            reader,
            writer,
            "— Czy nauczyłeś się jeszcze czegoś przy okazji? Jeśli nie, wpisz brak. ",
            lambda value: build_selection(main_profession, value).secondary_profession,
            "Kronikarz stawia obok świeżą kartkę. ",
        )
        build = await self._prompt_validated(
            reader,
            writer,
            "— Jakiej jesteś budowy? ",
            lambda value: validate_text("Budowa", value, min_length=2, max_length=80),
            "Karczmarz zerka na twoją sylwetkę, nie na twoją historię. ",
        )
        height = await self._prompt_validated(
            reader,
            writer,
            "— Jakiego jesteś wzrostu? ",
            lambda value: validate_text("Wzrost", value, min_length=2, max_length=80),
            "Kronikarz zanurza pióro ponownie. ",
        )
        hair = await self._prompt_validated(
            reader,
            writer,
            "— Jak wyglądają twoje włosy? ",
            lambda value: validate_text("Włosy", value, min_length=2, max_length=120),
            "Karczmarz kiwa głową na znak, że to ważniejsza rzecz, niż się wydaje. ",
        )
        beard = await self._prompt_validated(
            reader,
            writer,
            "— Nosisz brodę? Jeśli nie, wpisz brak. ",
            lambda value: validate_text("Brodę", value, min_length=2, max_length=120),
            "Kronikarz uśmiecha się pod nosem. ",
        )
        scars = await self._prompt_validated(
            reader,
            writer,
            "— Masz blizny? Jeśli nie, wpisz brak. ",
            lambda value: validate_text("Blizny", value, min_length=2, max_length=120),
            "Karczmarz nie naciska. ",
        )
        eyes = await self._prompt_validated(
            reader,
            writer,
            "— Jakiego koloru są twoje oczy? ",
            lambda value: validate_text("Oczy", value, min_length=2, max_length=80),
            "Kronikarz spogląda na ciebie uważniej. ",
        )
        tattoos = await self._prompt_validated(
            reader,
            writer,
            "— Masz tatuaże? Jeśli nie, wpisz brak. ",
            lambda value: validate_text("Tatuaże", value, min_length=2, max_length=120),
            "Karczmarz składa dłonie na blacie. ",
        )
        gait = await self._prompt_validated(
            reader,
            writer,
            "— Jak się poruszasz? ",
            lambda value: validate_text("Chód", value, min_length=2, max_length=120),
            "Kronikarz odsuwa pergamin i czeka na ostatni szczegół. ",
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
            culture=culture,
            religion=religion,
            main_profession=main_profession,
            secondary_profession=secondary_profession or None,
            appearance=appearance,
            history="Zapisano w księdze podróżnych podczas pierwszej nocy w Karczmie pod Żurawiem.",
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
        await send_text(
            writer,
            await self.services.dispatcher.commands["look"](context, None, 1),
        )
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
