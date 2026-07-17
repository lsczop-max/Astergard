local ROOT = (type(getMudletHomeDir) == "function" and getMudletHomeDir() or ".") .. "/Astergard"

ast = ast or {}
ast.root = ROOT

local core = dofile(ROOT .. "/src/core/init.lua")
local mapper = dofile(ROOT .. "/src/mapper/init.lua")
local gui = dofile(ROOT .. "/src/gui/init.lua")
local movement = dofile(ROOT .. "/src/movement/init.lua")
local gmcp = dofile(ROOT .. "/src/gmcp/init.lua")
local updater = dofile(ROOT .. "/src/updater/init.lua")

ast.core = core
ast.mapper = mapper
ast.gui = gui
ast.movement = movement
ast.gmcp = gmcp
ast.updater = updater

mapper.init(core)
gui.init(core, mapper)
movement.init(core)
gmcp.init(core, mapper, gui)
updater.init(core)

mapper.register_commands()
gui.register_commands()
movement.bind_commands()
gmcp.register()
updater.register_commands()

if ast.config.gui_enabled then
  gui.enable()
else
  gui.disable()
end

if ast.config.numpad_enabled then
  movement.enable()
else
  movement.disable()
end

mapper.import_map()
gui.refresh()

if ast.config.check_updates_on_start then
  updater.check_async()
end

core.log("Klient Mudlet Astergard został uruchomiony.")
return ast
