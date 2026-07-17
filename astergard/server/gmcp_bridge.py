from __future__ import annotations

from astergard.gmcp import room_info_packet


def writer_for_character(server, character):
    for writer, current in server.clients.items():
        if current is character:
            return writer
    return None


def send_room_info_for_character(server, character) -> None:
    writer = writer_for_character(server, character)
    if writer is None:
        return
    location = server.world.get_location(character.room_id)
    if location is None:
        return
    try:
        writer.write(room_info_packet(location, server.world))
    except Exception:
        return
