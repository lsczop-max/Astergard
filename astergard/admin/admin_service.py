from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from astergard.admin.audit_logger import AdminAuditLogger
from astergard.admin.permissions import AdminRole, has_role, role_for_actor
from astergard.characters.models import Character
from astergard.items.models import Item


@dataclass(frozen=True, slots=True)
class AdminCommandResult:
    ok: bool
    message: str


class AdminService:
    """Application service for GM/admin actions.

    All mutations are funneled here so command handlers remain thin adapters and
    every successful action is auditable.
    """

    destructive_actions = {"shutdown", "kill", "restore", "despawnnpc", "destroyitem"}

    def __init__(self, audit: AdminAuditLogger) -> None:
        self.audit = audit

    def ensure(self, actor: Character, required: AdminRole) -> AdminCommandResult | None:
        if not has_role(actor, required):
            return AdminCommandResult(False, "Nie masz uprawnień do tej komendy.")
        return None

    def inspect(self, ctx: Any, target_name: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        target = self._find_player(ctx, target_name) if target_name else ctx.character
        if target is None:
            return AdminCommandResult(False, "Nie znaleziono gracza.")
        self.audit.record(ctx.character.username, "inspect", target=target.username)
        return AdminCommandResult(
            True,
            "\n".join(
                [
                    f"Gracz: {target.username}",
                    f"Lokacja: {target.room_id}",
                    f"Kondycja: {target.stats.kondycja}/{target.stats.max_kondycja}",
                    f"Złoto: {target.gold}",
                    f"Stan: {target.state}",
                    f"Rola admin: {role_for_actor(target).name}",
                ]
            ),
        )

    def teleport(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        parts = (arg or "").split()
        if len(parts) != 2:
            return AdminCommandResult(False, "Użycie: teleport <gracz> <lokacja>")
        target = self._find_player(ctx, parts[0])
        if target is None:
            return AdminCommandResult(False, "Nie znaleziono gracza.")
        try:
            room_id = int(parts[1])
        except ValueError:
            return AdminCommandResult(False, "ID lokacji musi być liczbą.")
        if ctx.admin.world.get_location(room_id) is None:
            return AdminCommandResult(False, "Nie ma takiej lokacji.")
        old_room = target.room_id
        target.room_id = room_id
        self.audit.record(ctx.character.username, "teleport", target=target.username, from_room=old_room, to_room=room_id)
        return AdminCommandResult(True, f"Teleportowano {target.username} do lokacji {room_id}.")

    def goto(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        try:
            room_id = int((arg or "").strip())
        except ValueError:
            return AdminCommandResult(False, "Użycie: goto <lokacja>")
        if ctx.admin.world.get_location(room_id) is None:
            return AdminCommandResult(False, "Nie ma takiej lokacji.")
        old_room = ctx.character.room_id
        ctx.character.room_id = room_id
        self.audit.record(ctx.character.username, "goto", from_room=old_room, to_room=room_id)
        return AdminCommandResult(True, f"Przeniesiono cię do lokacji {room_id}.")

    def summon(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        target = self._find_player(ctx, (arg or "").strip())
        if target is None:
            return AdminCommandResult(False, "Nie znaleziono gracza.")
        old_room = target.room_id
        target.room_id = ctx.character.room_id
        self.audit.record(ctx.character.username, "summon", target=target.username, from_room=old_room, to_room=target.room_id)
        return AdminCommandResult(True, f"Przyzwano {target.username}.")

    def heal(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        target = self._find_player(ctx, (arg or "").strip()) or ctx.character
        target.stats.kondycja = target.stats.max_kondycja
        target.wounds = {part: 0 for part in target.wounds}
        if not target.is_alive:
            target.state = "alive"
            target.sync_flags_from_state()
        self.audit.record(ctx.character.username, "heal", target=target.username)
        return AdminCommandResult(True, f"Uleczono {target.username}.")

    def kill(self, ctx: Any, arg: str | None, confirmed: bool = False) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.ADMIN)
        if denied:
            return denied
        target = self._find_player(ctx, (arg or "").strip())
        if target is None:
            return AdminCommandResult(False, "Nie znaleziono gracza.")
        if not confirmed:
            return AdminCommandResult(False, "Komenda destrukcyjna. Użyj: kill <gracz> confirm")
        target.die()
        self.audit.record(ctx.character.username, "kill", target=target.username)
        return AdminCommandResult(True, f"Zabito {target.username}.")

    def give(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        parts = (arg or "").split(maxsplit=1)
        if len(parts) != 2:
            return AdminCommandResult(False, "Użycie: give <gracz> <item>")
        target = self._find_player(ctx, parts[0])
        if target is None:
            return AdminCommandResult(False, "Nie znaleziono gracza.")
        item_name = parts[1].strip()
        item = self._item_from_name(item_name)
        target.inventory.append(item)
        self.audit.record(ctx.character.username, "give", target=target.username, item=item.name)
        return AdminCommandResult(True, f"Dodano {item.name} do ekwipunku {target.username}.")

    def setstat(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.ADMIN)
        if denied:
            return denied
        parts = (arg or "").split()
        if len(parts) != 3:
            return AdminCommandResult(False, "Użycie: setstat <gracz> <stat> <wartość>")
        target = self._find_player(ctx, parts[0])
        if target is None:
            return AdminCommandResult(False, "Nie znaleziono gracza.")
        stat = parts[1]
        if not hasattr(target.stats, stat):
            return AdminCommandResult(False, "Nie ma takiej cechy.")
        try:
            value = int(parts[2])
        except ValueError:
            return AdminCommandResult(False, "Wartość musi być liczbą.")
        setattr(target.stats, stat, value)
        self.audit.record(ctx.character.username, "setstat", target=target.username, stat=stat, value=value)
        return AdminCommandResult(True, f"Ustawiono {stat}={value} dla {target.username}.")

    def spawnnpc(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.GM)
        if denied:
            return denied
        parts = (arg or "").split()
        if not parts:
            return AdminCommandResult(False, "Użycie: spawnnpc <vnum> [lokacja]")
        vnum = parts[0]
        room_id = ctx.character.room_id
        if len(parts) > 1:
            try:
                room_id = int(parts[1])
            except ValueError:
                return AdminCommandResult(False, "ID lokacji musi być liczbą.")
        npc = ctx.admin.npcs.spawn(vnum, room_id)
        if npc is None:
            return AdminCommandResult(False, "Nie udało się zespawnować NPC.")
        self.audit.record(ctx.character.username, "spawnnpc", vnum=vnum, room_id=room_id, npc_id=npc.id)
        return AdminCommandResult(True, f"Zespawnowano NPC: {npc.name} ({npc.id}).")

    def saveworld(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.ADMIN)
        if denied:
            return denied
        result = ctx.admin.save_load.save_world("admin_saveworld")
        self.audit.record(ctx.character.username, "saveworld", success=result.ok)
        message = "World saved." if result.ok else "; ".join(result.errors)
        return AdminCommandResult(result.ok, message)

    def checkpoint(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.ADMIN)
        if denied:
            return denied
        try:
            path = ctx.admin.save_load.create_checkpoint("admin_checkpoint")
        except Exception as exc:
            self.audit.record(ctx.character.username, "checkpoint", success=False, error=str(exc))
            return AdminCommandResult(False, f"Checkpoint nieudany: {exc}")
        self.audit.record(ctx.character.username, "checkpoint", success=True, path=str(path))
        return AdminCommandResult(True, f"Checkpoint utworzony: {path}")

    def restore(self, ctx: Any, arg: str | None, confirmed: bool = False) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.OWNER)
        if denied:
            return denied
        if not confirmed:
            return AdminCommandResult(False, "Komenda destrukcyjna. Użyj: restore <ścieżka> confirm")
        source = (arg or "").strip()
        if not source:
            return AdminCommandResult(False, "Użycie: restore <ścieżka> confirm")
        try:
            ctx.admin.repo.restore_backup(Path(source))
        except Exception as exc:
            return AdminCommandResult(False, f"Restore nieudany: {exc}")
        self.audit.record(ctx.character.username, "restore", source=source)
        return AdminCommandResult(True, "Przywrócono backup bazy.")

    def worldstats(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        world = ctx.admin.world
        npcs = ctx.admin.npcs
        self.audit.record(ctx.character.username, "worldstats")
        return AdminCommandResult(
            True,
            "\n".join(
                [
                    f"Lokacje: {len(world.locations)}",
                    f"NPC: {len(npcs.npcs)}",
                    f"Respawn queue: {len(world.respawn_queue)}",
                    f"Aktywni gracze: {len(ctx.admin.all_players())}",
                ]
            ),
        )

    def auditlog(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.ADMIN)
        if denied:
            return denied
        try:
            limit = int(arg or "10")
        except ValueError:
            limit = 10
        entries = self.audit.recent(limit)
        if not entries:
            return AdminCommandResult(True, "Audit log jest pusty.")
        lines = [f"{entry.created_at} {entry.actor} {entry.action} {entry.payload}" for entry in entries]
        return AdminCommandResult(True, "\n".join(lines))

    def scheduler(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        scheduler = ctx.admin.scheduler
        self.audit.record(ctx.character.username, "scheduler")
        return AdminCommandResult(True, f"Zadania schedulera: {len(getattr(scheduler, '_tasks', []))}")

    def listsessions(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        players = ctx.admin.all_players()
        self.audit.record(ctx.character.username, "listsessions")
        if not players:
            return AdminCommandResult(True, "Brak aktywnych sesji.")
        return AdminCommandResult(True, "\n".join(f"{p.username} @ {p.room_id}" for p in players))


    def metrics(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        self.audit.record(ctx.character.username, "metrics")
        return AdminCommandResult(True, ctx.admin.observability.render_metrics())

    def events(self, ctx: Any, arg: str | None) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        try:
            limit = int(arg or "20")
        except ValueError:
            limit = 20
        self.audit.record(ctx.character.username, "events", limit=limit)
        return AdminCommandResult(True, ctx.admin.observability.render_events(limit))

    def lag(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        self.audit.record(ctx.character.username, "lag")
        return AdminCommandResult(True, ctx.admin.observability.render_lag())

    def diagnostics(self, ctx: Any) -> AdminCommandResult:
        denied = self.ensure(ctx.character, AdminRole.HELPER)
        if denied:
            return denied
        self.audit.record(ctx.character.username, "diagnostics")
        return AdminCommandResult(True, ctx.admin.observability.render_diagnostics())

    def _find_player(self, ctx: Any, username: str | None) -> Character | None:
        if not username:
            return None
        needle = username.strip().lower()
        return next((player for player in ctx.admin.all_players() if player.username.lower() == needle), None)

    def _item_from_name(self, name: str) -> Item:
        normalized = name.strip().lower()
        if normalized in {"miecz", "prosty miecz", "simple_sword"}:
            return Item("prosty miecz", "Adminowski miecz testowy.", 1.8, 25, "simple_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4)
        if normalized in {"tarcza", "drewniana tarcza", "wooden_shield"}:
            return Item("drewniana tarcza", "Adminowska tarcza testowa.", 2.5, 15, "wooden_shield", "shield", "lewa_reka", protection=1, shield_block=3)
        return Item(name.strip() or "przedmiot testowy", "Przedmiot utworzony przez GM.", 1.0, 1, normalized or "gm_item")
