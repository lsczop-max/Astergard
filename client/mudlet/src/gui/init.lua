local gui = {}
local core = nil
local mapper = nil
local window_name = "astergard_status"
local visible = false

local function label_text()
  local room_id = tostring((gmcp and gmcp.Room and gmcp.Room.Info and gmcp.Room.Info.num) or "?")
  local room_name = tostring((gmcp and gmcp.Room and gmcp.Room.Info and gmcp.Room.Info.name) or "Brak danych")
  local area = tostring((gmcp and gmcp.Room and gmcp.Room.Info and (gmcp.Room.Info.area_label or gmcp.Room.Info.area)) or "Brak danych")
  local gmcp_state = tostring((ast and ast.gmcp and ast.gmcp.state and ast.gmcp.state.connected) and "połączony" or "brak")
  return string.format(
    "<b>Astergard</b><br/>%s<br/>%s<br/>#%s<br/>GMCP: %s<br/>Pakiet: %s<br/>Mapa: %s",
    room_name,
    area,
    room_id,
    gmcp_state,
    tostring(ast.version or "?"),
    tostring(ast.map_version or "?")
  )
end

function gui.init(core_ref, mapper_ref)
  core = core_ref
  mapper = mapper_ref
  return gui
end

function gui.ensure()
  if type(createLabel) ~= "function" then
    return false
  end
  if type(getLabelWidth) == "function" then
    local ok = pcall(getLabelWidth, window_name)
    if ok then
      return true
    end
  end
  pcall(createLabel, window_name, 20, 20, 260, 120, 1)
  if type(setLabelStyleSheet) == "function" then
    pcall(setLabelStyleSheet, window_name, "background-color: rgba(20,20,20,170); color: #f0e6d2; padding: 6px;")
  end
  if type(moveWindow) == "function" then
    pcall(moveWindow, window_name, 20, 20)
  end
  return true
end

function gui.refresh()
  if not ast.config.gui_enabled then
    return
  end
  if not gui.ensure() then
    return
  end
  if type(setLabelText) == "function" then
    pcall(setLabelText, window_name, label_text())
  end
  if type(showWindow) == "function" then
    pcall(showWindow, window_name)
  end
  visible = true
end

function gui.enable()
  ast.config.gui_enabled = true
  core.save_config()
  gui.refresh()
end

function gui.disable()
  ast.config.gui_enabled = false
  core.save_config()
  if type(hideWindow) == "function" then
    pcall(hideWindow, window_name)
  end
  visible = false
end

function gui.update()
  if visible then
    gui.refresh()
  end
end

function gui.register_commands()
  core.register_alias("^/ast_gui_on$", function()
    gui.enable()
    core.log("Panel GUI włączony.")
  end)
  core.register_alias("^/ast_gui_off$", function()
    gui.disable()
    core.log("Panel GUI wyłączony.")
  end)
end

return gui
