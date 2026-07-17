local core = {}
ast = ast or {}
ast.core = core

core.package_name = "Astergard"
core.version = "0.1.0"
core.map_version = "0.1.0"
core.minimum_mudlet_version = "4.12.0"
core.json = dofile((type(getMudletHomeDir) == "function" and getMudletHomeDir() or ".") .. "/Astergard/src/core/json.lua")
ast.json = core.json
ast.version = core.version
ast.map_version = core.map_version
ast.package_name = core.package_name

ast.config = ast.config or {}

local defaults = {
  gui_enabled = true,
  numpad_enabled = true,
  auto_center_map = true,
  diagnostics = true,
  check_updates_on_start = true,
}

local function home_dir()
  if type(getMudletHomeDir) == "function" then
    return getMudletHomeDir()
  end
  return "."
end

function core.root_dir()
  return home_dir() .. "/Astergard"
end

function core.path(...)
  local parts = { ... }
  return table.concat(parts, "/")
end

function core.ensure_dir(path)
  local lfs_lib = rawget(_G, "lfs")
  if type(lfs_lib) ~= "table" or type(lfs_lib.mkdir) ~= "function" then
    return path
  end
  local current = path:sub(1, 1) == "/" and "/" or ""
  for part in tostring(path):gmatch("[^/]+") do
    if current == "" then
      current = part
    elseif current == "/" then
      current = current .. part
    else
      current = current .. "/" .. part
    end
    lfs_lib.mkdir(current)
  end
  return path
end

function core.read_file(path)
  local handle = io.open(path, "r")
  if not handle then
    return nil
  end
  local content = handle:read("*a")
  handle:close()
  return content
end

function core.write_file(path, content)
  core.ensure_dir((path:match("^(.*)/[^/]+$")) or ".")
  local handle = assert(io.open(path, "w"))
  handle:write(content)
  handle:close()
end

function core.load_json_file(path)
  local content = core.read_file(path)
  if not content then
    return nil
  end
  return core.json.decode(content)
end

function core.save_json_file(path, data)
  core.write_file(path, core.json.encode(data))
end

function core.compare_versions(left, right)
  local function parse(value)
    local pieces = {}
    for chunk in tostring(value):gmatch("%d+") do
      pieces[#pieces + 1] = tonumber(chunk) or 0
      if #pieces == 3 then
        break
      end
    end
    while #pieces < 3 do
      pieces[#pieces + 1] = 0
    end
    return pieces
  end

  local left_parts = parse(left)
  local right_parts = parse(right)
  for index = 1, 3 do
    if left_parts[index] ~= right_parts[index] then
      return left_parts[index] > right_parts[index] and 1 or -1
    end
  end
  return 0
end

function core.current_mudlet_version()
  if type(getMudletVersion) == "function" then
    return tostring(getMudletVersion())
  end
  if type(mudlet_version) == "string" then
    return mudlet_version
  end
  return "0.0.0"
end

function core.is_supported()
  return core.compare_versions(core.current_mudlet_version(), core.minimum_mudlet_version) >= 0
end

function core.log(message)
  local text = "[Astergard] " .. tostring(message)
  if type(cecho) == "function" then
    cecho(text .. "\n")
  elseif type(echo) == "function" then
    echo(text .. "\n")
  else
    print(text)
  end
end

function core.download(url, path)
  if type(downloadFile) ~= "function" then
    error("Mudlet nie udostępnia downloadFile().")
  end
  core.ensure_dir((path:match("^(.*)/[^/]+$")) or ".")
  return downloadFile(url, path)
end

function core.load_config()
  local path = core.path(core.root_dir(), "config.json")
  local loaded = core.load_json_file(path)
  ast.config = loaded or {}
  for key, value in pairs(defaults) do
    if ast.config[key] == nil then
      ast.config[key] = value
    end
  end
  return ast.config
end

function core.save_config()
  local path = core.path(core.root_dir(), "config.json")
  core.save_json_file(path, ast.config)
end

function core.register_alias(pattern, callback)
  if type(tempAlias) == "function" then
    tempAlias(pattern, callback)
    return true
  end
  return false
end

function core.register_hotkey(key, command)
  if type(setKey) == "function" then
    pcall(setKey, key, command)
    return true
  end
  return false
end

function core.unregister_hotkey(key)
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

function core.safe_call(callback, ...)
  if type(callback) ~= "function" then
    return nil
  end
  local ok, result = pcall(callback, ...)
  if ok then
    return result
  end
  core.log("Błąd klienta: " .. tostring(result))
  return nil
end

core.load_config()
return core
