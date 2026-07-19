from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from astergard.admin.tools import AdminTools
from astergard.admin.audit_logger import AdminAuditLogger
from astergard.admin.admin_service import AdminService
from astergard.combat.manager import CombatManager
from astergard.commands.dispatcher import CommandDispatcher
from astergard.commands.registration import register_commands
from astergard.crafting.services import CraftingService
from astergard.database.repository import PlayerRepository
from astergard.economy.services import EconomyService
from astergard.factions.reputation import FactionManager
from astergard.magic.services import MagicService
from astergard.npcs.manager import NPCManager
from astergard.quests.manager import QuestManager
from astergard.weather.time_weather import TimeAndWeatherManager
from astergard.application.services.inventory_service import InventoryService
from astergard.application.services.exploration_service import ExplorationService
from astergard.application.services.communication_service import CommunicationService
from astergard.application.services.minimap_service import MinimapService
from astergard.application.services.magic_crafting_service import MagicCraftingApplicationService
from astergard.application.services.system_service import SystemCommandService
from astergard.application.services.combat_service import CombatApplicationService
from astergard.application.services.quest_service import QuestApplicationService
from astergard.application.services.economy_application_service import EconomyApplicationService
from astergard.application.services.world_reaction_service import WorldReactionService
from astergard.world.manager import WorldManager
from astergard.engine.events import EventBus
from astergard.engine.scheduler import Scheduler
from astergard.engine.save_load import SaveLoadEngine
from astergard.rules.engine import RuleSet, default_ruleset
from astergard.observability import ObservabilityService


@dataclass(slots=True)
class GameServices:
    rules: RuleSet
    event_bus: EventBus
    scheduler: Scheduler
    repo: PlayerRepository
    world: WorldManager
    npcs: NPCManager
    combat: CombatManager
    factions: FactionManager
    quests: QuestManager
    economy: EconomyService
    crafting: CraftingService
    magic: MagicService
    weather: TimeAndWeatherManager
    admin: AdminTools
    admin_audit: AdminAuditLogger
    admin_service: AdminService
    dispatcher: CommandDispatcher
    inventory_service: InventoryService
    combat_service: CombatApplicationService
    quest_service: QuestApplicationService
    economy_service: EconomyApplicationService
    exploration_service: ExplorationService
    communication_service: CommunicationService
    minimap_service: MinimapService
    magic_crafting_service: MagicCraftingApplicationService
    system_service: SystemCommandService
    save_load: SaveLoadEngine
    observability: ObservabilityService
    server: Any | None = None


class GameBootstrapper:
    """Creates the full game object graph in one explicit place.

    The server layer must not know the construction order of world generation,
    NPC population, command registration, or application services.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def build(self) -> GameServices:
        rules = default_ruleset()
        repo = PlayerRepository(self.db_path)
        world = WorldManager()
        world.generate_world()
        npcs = NPCManager(world, rules.respawn)
        if not repo.world_state.load_into(world, npcs.npcs, npcs.factory):
            npcs.populate()
            repo.world_state.save(world, npcs.npcs)
        combat = CombatManager(rules=rules.combat)
        factions = FactionManager(rules.reputation)
        quests = QuestManager()
        economy = EconomyService(rules.economy)
        event_bus = EventBus()
        scheduler = Scheduler()
        observability = ObservabilityService(event_bus, scheduler)
        admin_audit = AdminAuditLogger(repo, event_bus)
        admin_service = AdminService(admin_audit)
        world_reactions = WorldReactionService(event_bus, factions, npcs, lambda: [])
        world_reactions.subscribe(event_bus)
        services = GameServices(
            rules=rules,
            event_bus=event_bus,
            scheduler=scheduler,
            repo=repo,
            world=world,
            npcs=npcs,
            combat=combat,
            factions=factions,
            quests=quests,
            economy=economy,
            crafting=CraftingService(),
            magic=MagicService(rules.magic),
            weather=TimeAndWeatherManager(),
            admin=AdminTools(world),
            admin_audit=admin_audit,
            admin_service=admin_service,
            dispatcher=CommandDispatcher(),
            inventory_service=InventoryService(),
            combat_service=CombatApplicationService(world, npcs, combat, factions, quests, rules.movement),
            quest_service=QuestApplicationService(quests, factions),
            economy_service=EconomyApplicationService(economy, factions),
            exploration_service=ExplorationService(rules.movement, rules.search),
            communication_service=CommunicationService(),
            minimap_service=MinimapService(),
            magic_crafting_service=MagicCraftingApplicationService(),
            system_service=SystemCommandService(),
            save_load=None,  # type: ignore[arg-type]
            observability=observability,
        )
        services.save_load = SaveLoadEngine(services)
        register_commands(services.dispatcher, services)
        return services
