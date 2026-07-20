from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from astergard.application.bootstrap import GameServices
from astergard.application.session_transport import (
    SessionInput,
    SessionInputKind,
    SessionCapability,
    SessionTransport,
    is_debug_map_allowed,
    make_auth_result_event,
    make_command_result_event,
    make_connection_pong_event,
    make_core_hello_event,
    make_gmcp_negotiation_event,
    make_protocol_error_event,
    make_room_info_event,
    make_session_ready_event,
    next_sequence,
)
from astergard.server.gmcp_bridge import send_room_info_for_character
from astergard.characters.creation import (
    CharacterCreationError,
    CharacterCreationProfile,
    beard_prompt_text,
    build_appearance_prompt_text,
    build_appearance_summary,
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
    resolve_childhood,
    resolve_eyes,
    resolve_gait,
    resolve_hair,
    resolve_height,
    resolve_origin,
    resolve_scars,
    resolve_tattoos,
    scars_prompt_text,
    tattoos_prompt_text,
    validate_age,
    validate_text,
)
from astergard.characters.models import Character
from astergard.characters.professions import ProfessionError, build_selection, profession_menu_text
from astergard.commands.parser import CommandParser
from astergard.protocol.web_v1 import COMMAND_LENGTH_LIMIT
from astergard.server.context import GameContext


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
        self._gmcp_announced_transports: set[int] = set()
        self._sequence_by_transport: dict[int, int] = {}

    def _transport_key(self, transport: SessionTransport) -> int:
        return id(transport)

    def _next_sequence(self, transport: SessionTransport) -> int:
        key = self._transport_key(transport)
        current = self._sequence_by_transport.get(key, 0)
        sequence = next_sequence(current)
        self._sequence_by_transport[key] = sequence
        return sequence

    def _map_update_enabled(self, transport: SessionTransport) -> bool:
        return self.map_payload_enabled and is_debug_map_allowed(transport)

    async def _await_message(self, transport: SessionTransport, expected: SessionInputKind) -> SessionInput:
        while True:
            message = await transport.read_input(expected)
            if message.kind == SessionInputKind.PING:
                await transport.send_event(
                    make_connection_pong_event(
                        message.request_id,
                        sequence=self._next_sequence(transport),
                    )
                )
                continue
            if message.kind == SessionInputKind.DISCONNECT:
                raise EOFError
            if message.kind != expected:
                raise ValueError(f"Unexpected input kind: {message.kind.value}")
            return message

    def _string_payload(
        self,
        message: SessionInput,
        key: str,
        *,
        allow_empty: bool = False,
    ) -> str:
        value = message.payload.get(key)
        if not isinstance(value, str):
            raise ValueError(f"Message {message.kind.value} requires string field {key!r}.")
        if not allow_empty and not value:
            raise ValueError(f"Message {message.kind.value} requires non-empty field {key!r}.")
        if len(value.encode("utf-8")) > COMMAND_LENGTH_LIMIT:
            raise ValueError("Input exceeds the transport limit.")
        return value

    async def _ensure_gmcp_ready(self, transport: SessionTransport) -> None:
        if SessionCapability.GMCP not in transport.capabilities:
            return
        key = self._transport_key(transport)
        if key in self._gmcp_announced_transports:
            return
        await transport.send_event(make_gmcp_negotiation_event())
        await transport.send_event(make_core_hello_event())
        self._gmcp_announced_transports.add(key)

    async def _send_room_info(self, transport: SessionTransport, context: GameContext) -> None:
        location = context.world.get_location(context.character.room_id)
        if location is None:
            return
        await transport.send_event(
            make_room_info_event(
                location,
                context.world,
                sequence=self._next_sequence(transport),
            )
        )

    async def _send_full_map_debug(self, transport: SessionTransport, context: GameContext) -> None:
        if not self._map_update_enabled(transport):
            return
        payload = self.services.minimap_service.build_payload(
            context.character,
            context.world,
        )
        await transport.send_text(self.services.minimap_service.serialize_payload(payload))

    async def _send_minimap_update(self, transport: SessionTransport, context: GameContext) -> None:
        if not self._map_update_enabled(transport):
            return
        payload = self.services.minimap_service.build_update_payload(
            context.character,
            context.world,
        )
        await transport.send_text(self.services.minimap_service.serialize_payload(payload))

    async def _flush_location_changes(self, context: GameContext) -> None:
        server = getattr(self.services, "server", None)
        if server is None:
            return
        for character in context.location_changes.drain():
            await send_room_info_for_character(server, character)

    async def _prompt_validated(
        self,
        transport: SessionTransport,
        prompt: str,
        validator,
        intro: str | None = None,
    ) -> Any:
        if intro:
            await transport.send_text(intro)
        while True:
            await transport.send_prompt(prompt)
            value = await self._await_message(transport, SessionInputKind.RESPONSE)
            try:
                response = self._string_payload(value, "text", allow_empty=True)
                return validator(response)
            except (CharacterCreationError, ProfessionError) as exc:
                await transport.send_text(f"<red>{exc}</red>")

    async def _collect_creation_profile(self, transport: SessionTransport) -> CharacterCreationProfile:
        await transport.send_text(creation_opening_text())
        name = await self._prompt_validated(
            transport,
            "— Jak cię zwać? ",
            lambda value: validate_text("Imię", value, min_length=2, max_length=32),
            "Karczmarz opiera łokcie o stół. ",
        )
        gender_description = await self._prompt_validated(
            transport,
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
            transport,
            "— Ile masz lat? ",
            validate_age,
            "Karczmarz kiwa głową, jakby znał już odpowiedź, ale czeka na twoje słowo. ",
        )
        origin = await self._prompt_validated(
            transport,
            "— Skąd przybywasz? ",
            lambda value: resolve_origin(value).key,
            origin_prompt_text(),
        )
        childhood = await self._prompt_validated(
            transport,
            "— Gdzie dorastałeś? ",
            lambda value: resolve_childhood(value).key,
            childhood_prompt_text(),
        )
        birth_region = await self._prompt_validated(
            transport,
            "— W jakim regionie stawiałeś pierwsze kroki? ",
            lambda value: resolve_birth_region(value).label,
            birth_region_prompt_text(),
        )
        main_profession = await self._prompt_validated(
            transport,
            "— Czym zajmowałeś się dotąd? ",
            lambda value: build_selection(value).main_profession,
            profession_menu_text(),
        )
        secondary_profession = await self._prompt_validated(
            transport,
            "— Czy nauczyłeś się jeszcze czegoś przy okazji? Jeśli nie, wpisz brak. ",
            lambda value: build_selection(main_profession, value).secondary_profession,
            profession_menu_text(),
        )
        build = await self._prompt_validated(
            transport,
            "— Jakiej jesteś budowy? ",
            lambda value: resolve_build(value).label,
            build_appearance_prompt_text(),
        )
        height = await self._prompt_validated(
            transport,
            "— Jakiego jesteś wzrostu? ",
            lambda value: resolve_height(value).label,
            height_prompt_text(),
        )
        hair = await self._prompt_validated(
            transport,
            "— Jak wyglądają twoje włosy? ",
            lambda value: resolve_hair(value).label,
            hair_prompt_text(),
        )
        beard = await self._prompt_validated(
            transport,
            "— Nosisz brodę? Jeśli nie, wpisz brak. ",
            lambda value: resolve_beard(value).label,
            beard_prompt_text(),
        )
        scars = await self._prompt_validated(
            transport,
            "— Masz blizny? Jeśli nie, wpisz brak. ",
            lambda value: resolve_scars(value).label,
            scars_prompt_text(),
        )
        eyes = await self._prompt_validated(
            transport,
            "— Jakiego koloru są twoje oczy? ",
            lambda value: resolve_eyes(value).label,
            eyes_prompt_text(),
        )
        tattoos = await self._prompt_validated(
            transport,
            "— Masz tatuaże? Jeśli nie, wpisz brak. ",
            lambda value: resolve_tattoos(value).label,
            tattoos_prompt_text(),
        )
        gait = await self._prompt_validated(
            transport,
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

    async def _read_login_credentials(self, transport: SessionTransport) -> tuple[str, str, str | None]:
        first = await self._await_message(transport, SessionInputKind.CREDENTIALS)
        username = self._string_payload(first, "username", allow_empty=False)
        request_id = first.request_id
        password = first.payload.get("password")
        if isinstance(password, str) and password:
            if len(password.encode("utf-8")) > COMMAND_LENGTH_LIMIT:
                raise ValueError("Input exceeds the transport limit.")
            return username, password, request_id

        await transport.send_text("— Jeśli to twój pierwszy raz, podaj hasło do księgi podróżnych. ")
        second = await self._await_message(transport, SessionInputKind.CREDENTIALS)
        password = self._string_payload(second, "password", allow_empty=False)
        return username, password, request_id or second.request_id

    async def login(self, transport: SessionTransport) -> LoginResult:
        request_id: str | None = None
        try:
            await self._await_message(transport, SessionInputKind.HELLO)
            await transport.send_text(
                "<gold>Astergard MUD</gold>\nKarczmarz podnosi wzrok znad kufla. Jak się przedstawiasz? "
            )
            username, password, request_id = await self._read_login_credentials(transport)
            if not username:
                return LoginResult(None, close_connection=True)

            if self.services.repo.player_exists(username):
                if not self.services.repo.verify(username, password):
                    await transport.send_text("<red>Błędne hasło.</red>")
                    await transport.send_event(
                        make_auth_result_event(
                            False,
                            username,
                            reason="invalid_credentials",
                            request_id=request_id,
                            sequence=self._next_sequence(transport),
                        )
                    )
                    return LoginResult(None, close_connection=True)
                character = self.services.repo.load(username)
                character.visit_current_room()
                await transport.send_event(
                    make_auth_result_event(
                        True,
                        username,
                        request_id=request_id,
                        sequence=self._next_sequence(transport),
                    )
                )
                return LoginResult(character)

            profile = await self._collect_creation_profile(transport)
            self.services.repo.register(username, password, profile)
            character = self.services.repo.load(username)
            character.visit_current_room()
            await transport.send_text(creation_closing_text())
            await transport.send_event(
                make_auth_result_event(
                    True,
                    username,
                    request_id=request_id,
                    sequence=self._next_sequence(transport),
                )
            )
            return LoginResult(character)
        except EOFError:
            return LoginResult(None, close_connection=True)
        except ValueError:
            await transport.send_event(
                make_protocol_error_event(
                    "input_too_long",
                    "Input exceeds the transport limit.",
                    request_id=request_id,
                    sequence=self._next_sequence(transport),
                )
            )
            return LoginResult(None, close_connection=True)

    async def send_initial_view(self, transport: SessionTransport, context: GameContext) -> None:
        context.character.visit_current_room()
        await self._ensure_gmcp_ready(transport)
        await transport.send_text(
            await self.services.dispatcher.commands["look"](context, None, 1),
        )
        await self._send_room_info(transport, context)
        await self._send_full_map_debug(transport, context)
        await transport.send_prompt(self.prompt_renderer(context.character))
        await transport.send_event(
            make_session_ready_event(
                transport.kind,
                context.character.username,
                sequence=self._next_sequence(transport),
            )
        )

    async def command_loop(self, transport: SessionTransport, context: GameContext) -> None:
        character = context.character
        while character.is_alive:
            message: SessionInput | None = None
            try:
                message = await self._await_message(transport, SessionInputKind.COMMAND)
                raw = self._string_payload(message, "command", allow_empty=True)
                if not raw:
                    await transport.send_prompt(self.prompt_renderer(character))
                    continue
                parsed = CommandParser.parse(raw)
                spec = (
                    self.services.dispatcher.registry.get(parsed.command)
                    if parsed.command
                    else None
                )
                needs_full_map = spec is not None and spec.name == "debug_map"
                needs_minimap_update = spec is not None and spec.name in {"look", "move"}
                before_room_id = character.room_id
                output = await self.services.dispatcher.execute_line(context, raw)
                if character.room_id != before_room_id:
                    context.location_changes.record(character)
                await self._flush_location_changes(context)
                if output:
                    await transport.send_text(output)
                if needs_full_map:
                    await self._send_full_map_debug(transport, context)
                elif needs_minimap_update:
                    await self._send_minimap_update(transport, context)
                await transport.send_event(
                    make_command_result_event(
                        raw,
                        success=True,
                        request_id=message.request_id,
                        sequence=self._next_sequence(transport),
                    )
                )
                await transport.send_prompt(self.prompt_renderer(character))
            except EOFError:
                break
            except ValueError:
                await transport.send_event(
                    make_protocol_error_event(
                        "input_too_long",
                        "Input exceeds the transport limit.",
                        request_id=message.request_id if message is not None else None,
                        sequence=self._next_sequence(transport),
                    )
                )
                break
