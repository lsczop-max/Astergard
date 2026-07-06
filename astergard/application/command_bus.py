from __future__ import annotations

from dataclasses import dataclass

from astergard.commands.dispatcher import CommandDispatcher, CommandFunc
from astergard.commands.engine import CommandArgumentSpec, CommandMetadata, PermissionLevel


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    canonical_name: str
    aliases: list[str]
    handler: CommandFunc
    description: str
    usage: str
    group: str
    cooldown_seconds: float = 0.0
    argument_required: bool = False
    argument_name: str = "argument"
    permission: PermissionLevel = PermissionLevel.PLAYER

    def metadata(self) -> CommandMetadata:
        return CommandMetadata(
            canonical_name=self.canonical_name,
            description=self.description,
            usage=self.usage,
            group=self.group,
            cooldown_seconds=self.cooldown_seconds,
            argument=CommandArgumentSpec(required=self.argument_required, name=self.argument_name),
            permission=self.permission,
        )


@dataclass(slots=True)
class CommandBus:
    """Binds player-facing aliases to command definitions with metadata."""

    definitions: list[CommandDefinition]
    direction_names: list[str]

    @property
    def handlers(self) -> dict[str, CommandFunc]:
        return {definition.canonical_name: definition.handler for definition in self.definitions}

    @property
    def aliases(self) -> dict[str, list[str]]:
        return {definition.canonical_name: definition.aliases for definition in self.definitions}

    def install(self, dispatcher: CommandDispatcher) -> None:
        move_definition = next(defn for defn in self.definitions if defn.canonical_name == "move")
        for direction in self.direction_names:
            dispatcher.register(
                direction,
                move_definition.handler,
                CommandMetadata(
                    canonical_name="move",
                    description="Przemieszcza postać we wskazanym kierunku.",
                    usage=direction,
                    group="Eksploracja",
                    cooldown_seconds=0.2,
                ),
                aliases=[direction],
            )
        for definition in self.definitions:
            if definition.canonical_name == "move":
                continue
            dispatcher.register(
                definition.aliases[0],
                definition.handler,
                definition.metadata(),
                aliases=definition.aliases,
            )
