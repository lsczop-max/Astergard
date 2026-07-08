# Astergard Mudlet Map

## Install

1. Open your Mudlet profile.
2. Create a new script and paste [`mudlet/astergard_map.lua`](./astergard_map.lua).
3. Run `AstergardMap.init()` once after profile load.
4. Add a trigger with:
   - Pattern: `<MAP_JSON>(.*)</MAP_JSON>`
   - Action: `AstergardMap.onTrigger(matches[2])`
5. Optional:
   - `AstergardMap.showFullMap = true` for the full debug list.
   - `AstergardMap.toggle()` to switch between local and full views.

## Notes

- The map is debug-only and currently renders the whole world payload when the server enables it.
- The window is created in the upper-right corner as a Mudlet miniConsole.
- `@` marks the current room, `o` marks other rooms, `?` is reserved for future fog / unknown placeholders.

## Example payload

```json
{
  "type": "map_update",
  "current_room_id": 60,
  "current_room_name": "...",
  "current_zone": "Podgrodzie",
  "rooms": {
    "60": {
      "room_id": 60,
      "name": "...",
      "zone": "Podgrodzie",
      "exits": {
        "poludnie": 61,
        "wschod": 135
      }
    }
  }
}
```
