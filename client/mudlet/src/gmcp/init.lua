local gmcp_client = {}
local core = nil
local mapper = nil
local gui = nil
local state = {
  connected = false,
  last_room = nil,
}

local function current_room_data()
  if type(rawget) == "function" then
    local packet = rawget(_G, "gmcp")
    if type(packet) == "table" and type(packet.Room) == "table" and type(packet.Room.Info) == "table" then
      return packet.Room.Info
    end
  end
  return nil
end

local function apply_room_info(room)
  if type(room) ~= "table" then
    return
  end
  state.connected = true
  state.last_room = room
  if mapper then
    mapper.sync_room({
      num = tonumber(room.num) or tonumber(room.room_id) or tonumber(room.id) or 0,
      name = room.name or "Nieznana lokacja",
      area = room.area or "",
      area_label = room.area_label or room.area or "",
      coords = room.coords or { x = 0, y = 0, z = 0 },
      exits = room.exits or {},
    })
  end
  if gui then
    gui.update()
  end
end

function gmcp_client.init(core_ref, mapper_ref, gui_ref)
  core = core_ref
  mapper = mapper_ref
  gui = gui_ref
  ast.gmcp = gmcp_client
  gmcp_client.state = state
  return gmcp_client
end

function gmcp_client.register()
  if type(registerAnonymousEventHandler) == "function" then
    registerAnonymousEventHandler("gmcp.Core.Hello", function()
      state.connected = true
      if gui then
        gui.update()
      end
    end)
    registerAnonymousEventHandler("gmcp.Room.Info", function()
      apply_room_info(current_room_data())
    end)
  end
end

function gmcp_client.room_info(room)
  apply_room_info(room)
end

function gmcp_client.status()
  return state.connected and "połączony" or "brak"
end

return gmcp_client
