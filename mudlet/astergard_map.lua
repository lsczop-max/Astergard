AstergardMap = AstergardMap or {}
AstergardMap.console = AstergardMap.console or "AstergardMapConsole"
AstergardMap.rooms = AstergardMap.rooms or {}
AstergardMap.current_room_id = AstergardMap.current_room_id or nil
AstergardMap.current_zone = AstergardMap.current_zone or ""
AstergardMap.current_room_name = AstergardMap.current_room_name or ""
AstergardMap.last_payload = AstergardMap.last_payload or nil
AstergardMap.showFullMap = AstergardMap.showFullMap or false
AstergardMap.localDepth = AstergardMap.localDepth or 1

local function sorted_keys(data)
  local keys = {}
  for key in pairs(data or {}) do
    table.insert(keys, key)
  end
  table.sort(keys, function(left, right)
    return tostring(left) < tostring(right)
  end)
  return keys
end

local function get_json_decoder()
  if json and type(json.decode) == "function" then
    return json.decode
  end
  local ok, lib = pcall(require, "json")
  if ok and lib and type(lib.decode) == "function" then
    return lib.decode
  end
  return nil
end

local function room_by_id(room_id)
  return AstergardMap.rooms[tostring(room_id)]
end

local function room_label(room)
  if not room then
    return "? [unknown]"
  end
  local room_id = tostring(room.room_id or "?")
  local name = tostring(room.name or "?")
  local zone = tostring(room.zone or "?")
  return string.format("%s %s [%s]", room_id, name, zone)
end

local function line(text)
  if type(cecho) == "function" then
    cecho(AstergardMap.console, text .. "\n")
  elseif type(echo) == "function" then
    echo(text .. "\n")
  end
end

local function render_room_line(room_id, room, current_id)
  local marker = room_id == current_id and "@" or "o"
  return string.format("%s %s", marker, room_label(room))
end

local function render_current_view()
  local current = room_by_id(AstergardMap.current_room_id)
  line("<gold>Astergard Map</gold>")
  line(string.format(
    "<grey>room=%s zone=%s mode=%s</grey>",
    tostring(AstergardMap.current_room_id or "?"),
    tostring(AstergardMap.current_zone or ""),
    AstergardMap.showFullMap and "full" or "local"
  ))
  line(render_room_line(AstergardMap.current_room_id, current, AstergardMap.current_room_id))
  line("  |")
  line("  +-- exits")
  if not current or not current.exits then
    line("  ? brak wyjsc")
    return
  end
  local directions = sorted_keys(current.exits)
  if #directions == 0 then
    line("  ? brak wyjsc")
    return
  end
  for _, direction in ipairs(directions) do
    local target_id = current.exits[direction]
    local target_room = room_by_id(target_id)
    line(string.format("  |-- %s -> %s", direction, render_room_line(target_id, target_room, AstergardMap.current_room_id)))
  end
end

local function render_full_view()
  local zones = {}
  for _, room in pairs(AstergardMap.rooms) do
    local zone = tostring(room.zone or "?")
    zones[zone] = zones[zone] or {}
    table.insert(zones[zone], room)
  end
  local zone_names = sorted_keys(zones)
  for _, zone_name in ipairs(zone_names) do
    line("")
    line(string.format("<indigo>%s</indigo>", zone_name))
    table.sort(zones[zone_name], function(left, right)
      return tonumber(left.room_id or 0) < tonumber(right.room_id or 0)
    end)
    for _, room in ipairs(zones[zone_name]) do
      line(render_room_line(room.room_id, room, AstergardMap.current_room_id))
    end
  end
end

function AstergardMap.init()
  local screen_width, screen_height = 1200, 800
  if type(getMainWindowSize) == "function" then
    local ok, width, height = pcall(getMainWindowSize)
    if ok and tonumber(width) and tonumber(height) then
      screen_width = tonumber(width) or screen_width
      screen_height = tonumber(height) or screen_height
    end
  end
  local width = math.max(40, math.floor(screen_width * 0.30))
  local height = math.max(20, math.floor(screen_height * 0.40))
  local x = math.max(0, screen_width - width - 20)
  local y = 10
  if type(createMiniConsole) == "function" then
    pcall(createMiniConsole, AstergardMap.console, x, y, width, height)
  end
  if type(moveWindow) == "function" then
    pcall(moveWindow, AstergardMap.console, x, y)
  end
  if type(resizeWindow) == "function" then
    pcall(resizeWindow, AstergardMap.console, width, height)
  end
  if type(showWindow) == "function" then
    pcall(showWindow, AstergardMap.console)
  end
  if type(setMiniConsoleFontSize) == "function" then
    pcall(setMiniConsoleFontSize, AstergardMap.console, 9)
  end
  AstergardMap.render()
end

function AstergardMap.clear()
  if type(clearWindow) == "function" then
    pcall(clearWindow, AstergardMap.console)
  end
end

function AstergardMap.update(payload)
  local decoded = payload
  if type(payload) == "string" then
    local decoder = get_json_decoder()
    if not decoder then
      line("<red>AstergardMap: JSON decoder not available.</red>")
      return
    end
    local ok, data = pcall(decoder, payload)
    if not ok then
      line("<red>AstergardMap: invalid JSON payload.</red>")
      return
    end
    decoded = data
  end
  if type(decoded) ~= "table" then
    return
  end
  AstergardMap.last_payload = decoded
  AstergardMap.rooms = decoded.rooms or {}
  AstergardMap.current_room_id = decoded.current_room_id
  AstergardMap.current_zone = decoded.current_zone or ""
  AstergardMap.current_room_name = decoded.current_room_name or ""
  AstergardMap.render()
end

function AstergardMap.render()
  if not AstergardMap.rooms then
    AstergardMap.rooms = {}
  end
  AstergardMap.clear()
  if next(AstergardMap.rooms) == nil then
    line("<gold>Astergard Map</gold>")
    line("<grey>Brak danych mapy.</grey>")
    return
  end
  if AstergardMap.showFullMap then
    line("<gold>Astergard Map</gold>")
    line(string.format(
      "<grey>room=%s zone=%s mode=full</grey>",
      tostring(AstergardMap.current_room_id or "?"),
      tostring(AstergardMap.current_zone or "")
    ))
    render_full_view()
  else
    render_current_view()
  end
end

function AstergardMap.toggle()
  AstergardMap.showFullMap = not AstergardMap.showFullMap
  AstergardMap.render()
end

function AstergardMap.showCurrentRoom()
  AstergardMap.showFullMap = false
  AstergardMap.render()
end

function AstergardMap.showFull()
  AstergardMap.showFullMap = true
  AstergardMap.render()
end

-- Trigger action:
-- AstergardMap.update(matches[2])
--
-- Trigger pattern:
-- <MAP_JSON>(.*)</MAP_JSON>
