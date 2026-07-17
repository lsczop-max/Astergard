local updater = {}
local core = nil
local manifest_url = "https://raw.githubusercontent.com/lsczop-max/Astergard/develop/client/mudlet/manifest.json"

local function manifest_path()
  return core.path(core.root_dir(), "manifest.json")
end

local function local_manifest()
  return core.load_json_file(manifest_path())
end

local function remote_manifest_target()
  return core.path(core.root_dir(), "tmp", "remote_manifest.json")
end

local function download_and_retry(url, path, callback)
  if type(downloadFile) ~= "function" then
    core.log("Brak downloadFile() w Mudlecie.")
    return false
  end
  core.download(url, path)
  if type(tempTimer) == "function" and type(callback) == "function" then
    tempTimer(2, function()
      callback(path)
    end)
  end
  return true
end

local function version_text()
  return string.format("Pakiet %s, mapa %s, Mudlet %s", tostring(ast.version), tostring(ast.map_version), tostring(core.current_mudlet_version()))
end

function updater.init(core_ref)
  core = core_ref
  return updater
end

function updater.current_manifest()
  return local_manifest()
end

function updater.check_against(manifest)
  if type(manifest) ~= "table" then
    return false, "Brak manifestu."
  end
  local package_version = tostring(manifest.version or "0.0.0")
  local map_version = tostring(manifest.map_version or "0.0.0")
  local package_outdated = core.compare_versions(tostring(ast.version), package_version) < 0
  local map_outdated = core.compare_versions(tostring(ast.map_version), map_version) < 0
  if package_outdated or map_outdated then
    return true, string.format("Dostępna aktualizacja: pakiet %s, mapa %s.", package_version, map_version)
  end
  return false, "Pakiet jest aktualny."
end

function updater.check()
  local manifest = local_manifest()
  if not manifest then
    core.log("Brak lokalnego manifestu do porównania.")
    return false
  end
  local outdated, message = updater.check_against(manifest)
  core.log(message)
  return outdated
end

function updater.check_async()
  download_and_retry(manifest_url, remote_manifest_target(), function(path)
    local manifest = core.load_json_file(path)
    if not manifest then
      core.log("Nie udało się pobrać manifestu aktualizacji.")
      return
    end
    local outdated, message = updater.check_against(manifest)
    core.log(message)
    if outdated then
      core.log("Użyj /ast_aktualizuj, aby pobrać nowe pliki.")
    end
  end)
end

function updater.apply()
  local manifest = local_manifest()
  if not manifest then
    core.log("Nie można zaktualizować bez manifestu.")
    return false
  end
  local base_url = tostring(manifest.client_root_url or "")
  if base_url == "" then
    core.log("Manifest nie zawiera client_root_url.")
    return false
  end
  for _, rel in ipairs(manifest.files or {}) do
    download_and_retry(base_url .. "/" .. rel, core.path(core.root_dir(), rel))
  end
  download_and_retry(tostring(manifest.map_url or ""), core.path(core.root_dir(), "maps", "astergard_map.json"))
  core.log("Aktualizacja pobrana. Uruchom ponownie profil Mudleta.")
  return true
end

function updater.register_commands()
  core.register_alias("^/ast_sprawdz_aktualizacje$", function()
    updater.check_async()
  end)
  core.register_alias("^/ast_aktualizuj$", function()
    updater.apply()
  end)
  core.register_alias("^/ast_wersja$", function()
    core.log(version_text())
  end)
end

return updater
