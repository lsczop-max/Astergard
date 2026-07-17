local movement = {}
local core = nil
local bindings = {
  ["Numpad8"] = "polnoc",
  ["Numpad2"] = "poludnie",
  ["Numpad4"] = "zachod",
  ["Numpad6"] = "wschod",
  ["Numpad7"] = "polnocny-zachod",
  ["Numpad9"] = "polnocny-wschod",
  ["Numpad1"] = "poludniowy-zachod",
  ["Numpad3"] = "poludniowy-wschod",
  ["Numpad5"] = "rozejrzyj sie",
  ["NumpadMultiply"] = "gora",
  ["NumpadDivide"] = "dol",
}

local function send_command(command)
  if type(send) == "function" then
    send(command)
  elseif type(core) == "table" then
    core.log("Brak funkcji send() dla komendy: " .. tostring(command))
  end
end

local function bind_key(key, command)
  if type(setKey) == "function" then
    pcall(setKey, key, command)
    return true
  end
  return false
end

local function unbind_key(key)
  if type(deleteKey) == "function" then
    pcall(deleteKey, key)
    return true
  end
  if type(delKey) == "function" then
    pcall(delKey, key)
    return true
  end
  return false
end

function movement.init(core_ref)
  core = core_ref
  return movement
end

function movement.enable()
  ast.config.numpad_enabled = true
  core.save_config()
  for key, command in pairs(bindings) do
    bind_key(key, command)
  end
  core.log("Numpad włączony.")
end

function movement.disable()
  ast.config.numpad_enabled = false
  core.save_config()
  for key, _ in pairs(bindings) do
    unbind_key(key)
  end
  core.log("Numpad wyłączony.")
end

function movement.test()
  local lines = {}
  for key, command in pairs(bindings) do
    lines[#lines + 1] = key .. " -> " .. command
  end
  table.sort(lines)
  core.log(table.concat(lines, " | "))
end

function movement.special_exit()
  local room = gmcp and gmcp.Room and gmcp.Room.Info or nil
  local exits = room and room.special_exits or nil
  if type(exits) == "table" and exits[1] and exits[1].direction then
    send_command(tostring(exits[1].direction))
    return
  end
  core.log("Brak specjalnego przejścia w tej lokacji.")
end

function movement.bind_commands()
  core.register_alias("^/ast_numpad_on$", function()
    movement.enable()
  end)
  core.register_alias("^/ast_numpad_off$", function()
    movement.disable()
  end)
  core.register_alias("^/ast_numpad_test$", function()
    movement.test()
  end)
end

return movement
