local ROOT = (type(getMudletHomeDir) == "function" and getMudletHomeDir() or ".") .. "/Astergard"

if type(dofile) == "function" then
  dofile(ROOT .. "/src/bootstrap.lua")
end
