from __future__ import annotations

from astergard.application.session_transport import make_room_info_event


def transport_for_character(server, character):
    for transport, current in server.clients.items():
        if current is character:
            return transport
    return None


async def send_room_info_for_character(server, character) -> None:
    transport = transport_for_character(server, character)
    if transport is None:
        return
    location = server.world.get_location(character.room_id)
    if location is None:
        return
    try:
        await transport.send_event(make_room_info_event(location, server.world))
    except Exception:
        return
