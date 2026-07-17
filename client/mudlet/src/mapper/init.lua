local mapper = {}
local core = nil
local map_data = nil
local room_index = {}
local current_room = nil

local function map_path()
  return core.path(core.root_dir(), "maps", "astergard_map.json")
end

local function ensure_room(room)
  if type(addRoom) == "function" then
    pcall(addRoom, room.num)
  end
  if type(setRoomName) == "function" then
    pcall(setRoomName, room.num, room.name or tostring(room.num))
  end
  if type(setRoomArea) == "function" then
    pcall(setRoomArea, room.num, room.area_label or room.area or "Astergard")
  end
  if type(setRoomCoordinates) == "function" and room.coords then
    pcall(setRoomCoordinates, room.num, room.coords.x or 0, room.coords.y or 0, room.coords.z or 0)
  end
  room_index[room.num] = room
end

local function connect_room(room)
  if type(setExit) ~= "function" then
    return
  end
  for direction, target in pairs(room.exits or {}) do
    pcall(setExit, room.num, target, direction)
  end
end

function mapper.init(core_ref)
  core = core_ref
  return mapper
end

function mapper.load_map_data()
  map_data = core.load_json_file(map_path())
  return map_data
end

function mapper.import_map()
  local data = mapper.load_map_data()
  if not data then
    core.log("Brak mapy JSON do importu.")
    return false
  end
  room_index = {}
  for _, room in ipairs(data.rooms or {}) do
    ensure_room(room)
    connect_room(room)
  end
  return true
end

function mapper.sync_room(room)
  if not room then
    return
  end
  current_room = room.num or current_room
  ensure_room(room)
  if ast.config.auto_center_map and type(centerview) == "function" then
    pcall(centerview, room.num)
  end
end

function mapper.update_room(room)
  mapper.sync_room(room)
end

function mapper.center_on_player()
  if current_room and type(centerview) == "function" then
    pcall(centerview, current_room)
  end
end

function mapper.info()
  local total = 0
  if map_data and type(map_data.rooms) == "table" then
    total = #map_data.rooms
  end
  return string.format("Mapa Astergardu: %d pokoi, aktualny pokój: %s", total, tostring(current_room or "?"))
end

function mapper.reload()
  return mapper.import_map()
end

function mapper.register_commands()
  core.register_alias("^/ast_mapa$", function()
    core.log(mapper.info())
  end)
  core.register_alias("^/ast_mapa_centruj$", function()
    mapper.center_on_player()
    core.log("Wycentrowano mapę.")
  end)
  core.register_alias("^/ast_mapa_info$", function()
    core.log(mapper.info())
  end)
  core.register_alias("^/ast_mapa_przeladuj$", function()
    mapper.reload()
    core.log("Mapa została przeładowana.")
  end)
end

return mapper
