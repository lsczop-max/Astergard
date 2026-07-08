from __future__ import annotations

from astergard.application.command_bus import CommandBus, CommandDefinition
from astergard.admin.gm_commands import build_admin_handlers
from astergard.commands.character_sheet import build_character_sheet_handlers
from astergard.commands.combat import build_combat_handlers
from astergard.commands.communication import build_communication_handlers
from astergard.commands.dispatcher import CommandDispatcher
from astergard.commands.economy import build_economy_handlers
from astergard.commands.exploration import DIRECTIONS, build_exploration_handlers
from astergard.commands.inventory import build_inventory_handlers
from astergard.commands.magic_crafting import build_magic_crafting_handlers
from astergard.commands.social_systems import build_social_handlers
from astergard.commands.system import build_system_handlers
from astergard.commands.engine import PermissionLevel

CommandDefinitionTuple = tuple[str, list[str], str, str, float, bool, str] | tuple[str, list[str], str, str, float, bool, str, PermissionLevel]

COMMAND_DEFINITIONS: dict[str, CommandDefinitionTuple] = {
    "look": ("Eksploracja", ["look", "l", "ob", "sp", "spojrz", "spójrz", "obejrzyj", "ogladnij", "oglądnij", "popatrz", "patrz", "zerknij", "zobacz"], "Opisuje obecną lokację albo wskazany cel.", "spojrz [cel]", 0.0, False, "cel"),
    "move": ("Eksploracja", ["wejdz", "zejdz", "wroc", "dalej", "do srodka", "na zewnatrz", "na polnoc", "na poludnie", "na wschod", "na zachod", "na gore", "na dol", "w gore", "w dol"], "Przemieszcza postać.", "polnoc", 0.2, False, "kierunek"),
    "search": ("Eksploracja", ["szukaj", "przeszukaj", "szperaj"], "Przeszukuje lokację kosztem kondycji.", "szukaj", 2.0, False, ""),
    "sense": ("Eksploracja", ["zbadaj", "nasluchuj", "nasluchaj", "powachaj", "dotknij", "usiadz", "odpocznij", "rozejrzyj", "rozejrzyj sie", "obserwuj"], "Pozwala wyczuć miejsce bez mechanicznego wyliczania opcji.", "zbadaj [cel]", 0.0, False, "cel"),
    "say": ("Komunikacja", ["powiedz", "mow", "mów", "pow", "say"], "Mówi do graczy w tej samej lokacji.", "powiedz <tekst>", 0.5, True, "tekst"),
    "emote": ("Komunikacja", ["em", "emocja", "emote"], "Opisuje gest lub emocję postaci.", "em <opis>", 0.5, True, "opis"),
    "shout": ("Komunikacja", ["krzycz", "wrzasnij", "wrzaśnij", "shout"], "Krzyczy do graczy w strefie.", "krzycz <tekst>", 3.0, True, "tekst"),
    "score": ("Postać", ["cechy", "stan", "score"], "Pokazuje stan i cechy postaci.", "cechy", 0.0, False, ""),
    "profile": ("Postać", ["profil", "profile"], "Pokazuje pełny profil postaci.", "profil", 0.0, False, ""),
    "postac": ("Postać", ["postać", "postac", "wyposazenie", "wyposażenie"], "Pokazuje aktualnie noszone wyposażenie w naturalnej formie.", "postać", 0.0, False, ""),
    "skills": ("Postać", ["umiejetnosci", "umiejętności", "um", "umki"], "Pokazuje poziomy umiejętności.", "umiejetnosci", 0.0, False, ""),
    "style": ("Walka", ["styl", "postawa"], "Ustawia albo pokazuje styl walki.", "styl [nazwa]", 0.0, False, "nazwa"),
    "reputation": ("Postać", ["reputacja"], "Pokazuje reputację u frakcji.", "reputacja", 0.0, False, ""),
    "inventory": ("Ekwipunek", ["ekwipunek", "ekw", "plecak", "torba", "sakwa", "worek", "pojemnik", "inv", "inventory", "i"], "Pokazuje ekwipunek i wyposażenie.", "ekwipunek", 0.0, False, ""),
    "get": ("Ekwipunek", ["wez", "weź", "w", "podnies", "podnieś", "podn", "zabierz"], "Podnosi przedmiot z ziemi albo wyjmuje go z pojemnika, jeśli użyjesz składni z <pojemnik>.", "wez <przedmiot>", 0.5, True, "przedmiot"),
    "take_from": ("Ekwipunek", ["wyjmij", "wyciagnij", "wyciągnij"], "Wyjmuje przedmiot z pojemnika.", "wyjmij <przedmiot> z <pojemnik>", 0.5, True, "przedmiot z pojemnik"),
    "drop": ("Ekwipunek", ["upusc", "upuść", "zostaw", "wyrzuc", "wyrzuć", "odloz", "odłóż"], "Upuszcza przedmiot.", "upusc <przedmiot>", 0.5, True, "przedmiot"),
    "wear": ("Ekwipunek", ["zaloz", "załóż", "ubierz", "naloz", "nałóż", "dobadz", "dobądź", "dobyj"], "Zakłada lub dobywa przedmiot.", "zaloz <przedmiot>", 0.5, True, "przedmiot"),
    "remove": ("Ekwipunek", ["zdejmij", "sciagnij", "ściągnij", "schowaj"], "Zdejmuje wyposażony przedmiot.", "zdejmij <przedmiot>", 0.5, True, "przedmiot"),
    "consume": ("Ekwipunek", ["zjedz", "wypij", "uzyj", "użyj", "skonsumuj"], "Używa przedmiotu konsumpcyjnego.", "uzyj <przedmiot>", 0.5, True, "przedmiot"),
    "put": ("Ekwipunek", ["wloz", "włóż", "wlóż", "wsadz", "wsadź", "schowajdo"], "Wkłada przedmiot do pojemnika.", "wloz <przedmiot> do <pojemnik>", 0.5, True, "przedmiot do pojemnika"),
    "transfer": ("Ekwipunek", ["przeloz", "przełóż", "przenies", "przenieś"], "Przekłada przedmiot między pojemnikami.", "przeloz <przedmiot> z <pojemnika> do <pojemnika>", 0.5, True, "przedmiot z pojemnika do pojemnika"),
    "give_item": ("NPC", ["daj", "oddaj", "przekaz", "przekaż", "przynies"], "Daje przedmiot postaci w lokacji.", "daj <przedmiot> <osobie>", 0.5, True, "przedmiot osoba"),
    "kill": ("Walka", ["zabij", "z", "atakuj", "zaatakuj", "bij"], "Atakuje NPC w lokacji.", "atakuj <cel>", 1.0, True, "cel"),
    "flee": ("Walka", ["ucieczka", "uciekaj", "uciek", "flee"], "Próbuje uciec z walki.", "ucieczka", 2.0, False, ""),
    "talk": ("NPC", ["rozmawiaj", "porozmawiaj", "gadaj"], "Rozmawia z NPC.", "rozmawiaj <npc> [o temat]", 0.5, True, "npc"),
    "quests": ("Questy", ["zadania", "questy", "dziennik", "misje"], "Pokazuje dziennik zadań.", "zadania", 0.0, False, ""),
    "offer": ("Ekonomia", ["oferta", "lista", "towary"], "Pokazuje ofertę kupca.", "oferta", 0.0, False, ""),
    "buy": ("Ekonomia", ["kup", "kupno", "nabyj"], "Kupuje przedmiot od kupca.", "kup <id/nazwa>", 0.5, True, "przedmiot"),
    "sell": ("Ekonomia", ["sprzedaj", "sprzed", "zbyj"], "Sprzedaje przedmiot kupcowi.", "sprzedaj <przedmiot>", 0.5, True, "przedmiot"),
    "cast": ("Magia", ["czaruj", "rzuc", "rzuć", "inkantuj"], "Rzuca czar.", "czaruj <czar>", 1.0, True, "czar"),
    "craft": ("Crafting", ["craft", "stworz", "stwórz", "wykonaj", "zrob", "zrób", "wykuj"], "Tworzy przedmiot według receptury.", "craft <receptura>", 1.0, True, "receptura"),
    "ranking": ("System", ["ranking"], "Pokazuje ranking graczy.", "ranking [kategoria]", 5.0, False, "kategoria"),
    "save": ("System", ["zapisz", "save"], "Zapisuje postać.", "zapisz", 3.0, False, ""),
    "quit": ("System", ["quit", "exit", "wyjdz", "wyjdź", "koniec"], "Kończy sesję gry.", "quit", 0.0, False, ""),
    "debug_map": ("Diagnostyka", ["debug_map", "debug"], "Wyświetla debug payload mapy dla klienta Mudlet.", "debug_map", 0.0, False, "", PermissionLevel.HELPER),
    "inspect": ("Administracja", ["inspect"], "Pokazuje stan gracza.", "inspect [gracz]", 0.0, False, "gracz", PermissionLevel.GM),
    "teleport": ("Administracja", ["teleport"], "Przenosi wskazanego gracza do lokacji.", "teleport <gracz> <lokacja>", 0.0, True, "gracz lokacja", PermissionLevel.GM),
    "goto": ("Administracja", ["goto"], "Przenosi administratora do lokacji.", "goto <lokacja>", 0.0, True, "lokacja", PermissionLevel.GM),
    "summon": ("Administracja", ["summon"], "Przywołuje gracza do administratora.", "summon <gracz>", 0.0, True, "gracz", PermissionLevel.GM),
    "heal": ("Administracja", ["heal"], "Leczy gracza albo administratora.", "heal [gracz]", 0.0, False, "gracz", PermissionLevel.GM),
    "adminkill": ("Administracja", ["adminkill"], "Zabija gracza po potwierdzeniu.", "adminkill <gracz> confirm", 0.0, True, "gracz", PermissionLevel.ADMIN),
    "give": ("Administracja", ["give"], "Dodaje przedmiot do ekwipunku gracza.", "give <gracz> <item>", 0.0, True, "gracz item", PermissionLevel.GM),
    "setstat": ("Administracja", ["setstat"], "Ustawia cechę gracza.", "setstat <gracz> <stat> <wartość>", 0.0, True, "gracz stat wartość", PermissionLevel.ADMIN),
    "spawnnpc": ("Administracja", ["spawnnpc"], "Spawnuje NPC.", "spawnnpc <vnum> [lokacja]", 0.0, True, "vnum", PermissionLevel.GM),
    "saveworld": ("Administracja", ["saveworld"], "Zapisuje snapshot świata.", "saveworld", 0.0, False, "", PermissionLevel.ADMIN),
    "checkpoint": ("Administracja", ["checkpoint"], "Tworzy checkpoint zapisu.", "checkpoint", 0.0, False, "", PermissionLevel.ADMIN),
    "restore": ("Administracja", ["restore"], "Przywraca backup po potwierdzeniu.", "restore <ścieżka> confirm", 0.0, True, "ścieżka", PermissionLevel.OWNER),
    "worldstats": ("Administracja", ["worldstats"], "Pokazuje statystyki świata.", "worldstats", 0.0, False, "", PermissionLevel.HELPER),
    "auditlog": ("Administracja", ["auditlog"], "Pokazuje ostatnie akcje administracyjne.", "auditlog [limit]", 0.0, False, "limit", PermissionLevel.ADMIN),
    "scheduler": ("Administracja", ["scheduler"], "Pokazuje stan schedulera.", "scheduler", 0.0, False, "", PermissionLevel.HELPER),
    "listsessions": ("Administracja", ["listsessions"], "Pokazuje aktywne sesje.", "listsessions", 0.0, False, "", PermissionLevel.HELPER),
    "metrics": ("Diagnostyka", ["metrics", "metryki"], "Pokazuje metryki silnika.", "metrics", 0.0, False, "", PermissionLevel.HELPER),
    "events": ("Diagnostyka", ["events", "eventy"], "Pokazuje liczniki eventów domenowych.", "events [limit]", 0.0, False, "limit", PermissionLevel.HELPER),
    "lag": ("Diagnostyka", ["lag"], "Pokazuje diagnostykę ticków i opóźnień.", "lag", 0.0, False, "", PermissionLevel.HELPER),
    "diagnostics": ("Diagnostyka", ["diagnostics", "diag"], "Pokazuje pełny raport diagnostyczny.", "diagnostics", 0.0, False, "", PermissionLevel.HELPER),
}


def build_command_bus(services) -> CommandBus:
    handlers = {}
    handlers.update(build_character_sheet_handlers())
    handlers.update(build_combat_handlers(services.combat_service))
    handlers.update(build_communication_handlers(services.communication_service))
    handlers.update(build_economy_handlers(services.economy_service))
    handlers.update(build_exploration_handlers(services.exploration_service))
    handlers.update(build_inventory_handlers(services.inventory_service))
    handlers.update(build_magic_crafting_handlers(services.magic_crafting_service))
    handlers.update(build_social_handlers(services.quest_service))
    handlers.update(build_system_handlers(services.system_service, services.minimap_service))
    handlers.update(build_admin_handlers(services.admin_service))
    definitions = []
    for canonical_name, definition_data in COMMAND_DEFINITIONS.items():
        if len(definition_data) == 7:
            group, aliases, description, usage, cooldown, required, argument_name = definition_data
            permission = PermissionLevel.PLAYER
        else:
            group, aliases, description, usage, cooldown, required, argument_name, permission = definition_data
        definitions.append(
            CommandDefinition(
                canonical_name=canonical_name,
                aliases=list(aliases),
                handler=handlers[canonical_name],
                description=description,
                usage=usage,
                group=group,
                cooldown_seconds=cooldown,
                argument_required=required,
                argument_name=argument_name,
                permission=permission,
            )
        )
    return CommandBus(definitions=definitions, direction_names=list(DIRECTIONS))


def register_commands(dispatcher: CommandDispatcher, services) -> None:
    build_command_bus(services).install(dispatcher)
