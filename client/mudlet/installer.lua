local ROOT = (type(getMudletHomeDir) == "function" and getMudletHomeDir() or ".") .. "/Astergard"
local MANIFEST_URL = "https://raw.githubusercontent.com/lsczop-max/Astergard/develop/client/mudlet/manifest.json"

local function echo_line(message)
  if type(cecho) == "function" then
    cecho(message .. "\n")
  elseif type(echo) == "function" then
    echo(message .. "\n")
  else
    print(message)
  end
end

local function ensure_dir(path)
  if type(lfs) == "table" and type(lfs.mkdir) == "function" then
    local current = path:sub(1, 1) == "/" and "/" or ""
    for part in path:gmatch("[^/]+") do
      if current == "" then
        current = part
      elseif current == "/" then
        current = current .. part
      else
        current = current .. "/" .. part
      end
      lfs.mkdir(current)
    end
  end
end

local function read_all(path)
  local handle = io.open(path, "r")
  if not handle then
    return nil
  end
  local content = handle:read("*a")
  handle:close()
  return content
end

local function write_all(path, content)
  local handle = assert(io.open(path, "w"))
  handle:write(content)
  handle:close()
end

local function decode_json(text)
  if type(json) == "table" and type(json.decode) == "function" then
    return json.decode(text)
  end
  local ok, lib = pcall(require, "json")
  if ok and lib and type(lib.decode) == "function" then
    return lib.decode(text)
  end
  error("Brak dekodera JSON w Mudlecie.")
end

local function download_and_store(url, path)
  if type(downloadFile) ~= "function" then
    error("Mudlet nie udostępnia downloadFile().")
  end
  ensure_dir(path:match("^(.*)/[^/]+$") or ROOT)
  downloadFile(url, path)
end

local function load_manifest(path)
  local content = read_all(path)
  if not content then
    return nil, "Brak manifestu."
  end
  local ok, manifest = pcall(decode_json, content)
  if not ok then
    return nil, manifest
  end
  return manifest
end

local function install_files(manifest)
  local base_url = manifest.client_root_url
  if type(base_url) ~= "string" or base_url == "" then
    error("Manifest nie zawiera client_root_url.")
  end
  for _, rel in ipairs(manifest.files or {}) do
    local target = ROOT .. "/" .. rel
    local url = base_url .. "/" .. rel
    echo_line("Pobieram: " .. rel)
    download_and_store(url, target)
  end
  download_and_store(manifest.map_url, ROOT .. "/maps/astergard_map.json")
  download_and_store(tostring(manifest.package_url or ""), ROOT .. "/releases/Astergard.mpackage")
end

local function bootstrap()
  ensure_dir(ROOT)
  local manifest_path = ROOT .. "/manifest.json"
  download_and_store(MANIFEST_URL, manifest_path)
  if type(tempTimer) == "function" then
    tempTimer(2, function()
      local manifest, err = load_manifest(manifest_path)
      if not manifest then
        echo_line("Nie udało się odczytać manifestu: " .. tostring(err))
        return
      end
      install_files(manifest)
      if type(installPackage) == "function" then
        pcall(installPackage, ROOT .. "/releases/Astergard.mpackage")
      end
      if type(tempTimer) == "function" then
        tempTimer(2, function()
          echo_line("Instalacja zakończona. Pakiet powinien ładować się automatycznie przy starcie profilu.")
          dofile(ROOT .. "/main.lua")
        end)
      else
        dofile(ROOT .. "/main.lua")
      end
    end)
  else
    local manifest, err = load_manifest(manifest_path)
    if not manifest then
      error("Nie udało się odczytać manifestu: " .. tostring(err))
    end
    install_files(manifest)
    if type(installPackage) == "function" then
      pcall(installPackage, ROOT .. "/releases/Astergard.mpackage")
    end
    dofile(ROOT .. "/main.lua")
  end
end

bootstrap()
