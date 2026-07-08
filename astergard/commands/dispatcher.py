from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from time import perf_counter

from astergard.commands.engine import (
    CommandMetadata,
    CommandRegistry,
    CooldownTracker,
    actor_identifier,
    has_permission,
    render_help,
)
from astergard.commands.parser import CommandParser
from astergard.utils import colorize

CommandFunc = Callable[[Any, str | None, int], Awaitable[str]]


class CommandDispatcher:
    def __init__(self) -> None:
        self.commands: dict[str, CommandFunc] = {}
        self.registry = CommandRegistry()
        self.cooldowns = CooldownTracker()
        self.register(
            "pomoc",
            self._cmd_help,
            CommandMetadata(
                canonical_name="help",
                description="Wyświetla pomoc albo szczegóły wskazanej komendy.",
                usage="pomoc [komenda]",
                group="System",
            ),
            aliases=["pomoc", "help"],
        )

    def register(
        self,
        name: str,
        func: CommandFunc,
        metadata: CommandMetadata | None = None,
        aliases: list[str] | None = None,
    ) -> None:
        command_aliases = aliases or [name]
        command_metadata = metadata or CommandMetadata(
            canonical_name=name,
            description="Komenda gry.",
            usage=name,
        )
        self.registry.register(command_aliases, func, command_metadata)
        for alias in command_aliases:
            self.commands[alias] = func

    async def _cmd_help(self, context: Any, arg: str | None, index: int) -> str:
        return render_help(self.registry, arg, context)

    async def execute_line(self, context: Any, raw_line: str) -> str:
        parsed = CommandParser.parse(raw_line)
        if not parsed.command:
            return ""
        if hasattr(context, "current_command"):
            setattr(context, "current_command", parsed.command)
        elif hasattr(context, "exploration"):
            context.exploration().current_command = parsed.command

        observability = getattr(context, "observability", None)
        actor_id = actor_identifier(context)
        start = perf_counter()
        command_name = parsed.command
        ok = False
        error: str | None = None
        try:
            spec = self.registry.get(parsed.command)
            if spec is None:
                error = "unknown_command"
                return "Nie rozumiem takiego polecenia."
            command_name = spec.name
            if not has_permission(context, spec.metadata.permission):
                error = "permission_denied"
                return "Nie masz uprawnień do tego polecenia."
            if spec.metadata.argument.required and not parsed.argument:
                error = "missing_argument"
                return f"Brakuje argumentu: {spec.metadata.argument.name}. Spróbuj: {spec.metadata.usage}"

            remaining = self.cooldowns.remaining(actor_id, spec.name, spec.metadata.cooldown_seconds)
            if remaining > 0:
                error = "cooldown"
                return f"Jeszcze nie możesz użyć tej komendy. Poczekaj {remaining:.1f} s."

            output = await spec.handler(context, parsed.argument, parsed.index)
            self.cooldowns.mark_used(actor_id, spec.name)
            ok = True
            return colorize(output)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            return colorize(f"<red>Coś poszło nie tak podczas wykonywania komendy: {exc}</red>")
        finally:
            if observability is not None:
                observability.record_command(
                    command_name,
                    actor_id,
                    (perf_counter() - start) * 1000.0,
                    ok,
                    error,
                )
