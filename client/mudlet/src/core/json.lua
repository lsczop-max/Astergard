local existing = rawget(_G, "json")
if type(existing) == "table" and type(existing.encode) == "function" and type(existing.decode) == "function" then
  return existing
end

local json = {}

local function escape_string(value)
  value = value:gsub("\\", "\\\\")
  value = value:gsub("\"", "\\\"")
  value = value:gsub("\b", "\\b")
  value = value:gsub("\f", "\\f")
  value = value:gsub("\n", "\\n")
  value = value:gsub("\r", "\\r")
  value = value:gsub("\t", "\\t")
  return value
end

local function is_array(value)
  local count = 0
  for key, _ in pairs(value) do
    if type(key) ~= "number" then
      return false
    end
    count = count + 1
  end
  for index = 1, count do
    if value[index] == nil then
      return false
    end
  end
  return true
end

function json.encode(value)
  local kind = type(value)
  if kind == "nil" then
    return "null"
  end
  if kind == "number" then
    return tostring(value)
  end
  if kind == "boolean" then
    return value and "true" or "false"
  end
  if kind == "string" then
    return "\"" .. escape_string(value) .. "\""
  end
  if kind ~= "table" then
    error("Nieobsługiwany typ JSON: " .. kind)
  end
  if is_array(value) then
    local items = {}
    for index = 1, #value do
      items[#items + 1] = json.encode(value[index])
    end
    return "[" .. table.concat(items, ",") .. "]"
  end
  local items = {}
  for key, item in pairs(value) do
    items[#items + 1] = json.encode(tostring(key)) .. ":" .. json.encode(item)
  end
  table.sort(items)
  return "{" .. table.concat(items, ",") .. "}"
end

local function decode_error(message, index)
  error(message .. " przy pozycji " .. tostring(index))
end

local function decode_value(text, index)
  local length = #text
  local function skip_ws(position)
    while position <= length do
      local char = text:sub(position, position)
      if char ~= " " and char ~= "\t" and char ~= "\r" and char ~= "\n" then
        return position
      end
      position = position + 1
    end
    return position
  end

  local function parse_string(position)
    local buffer = {}
    position = position + 1
    while position <= length do
      local char = text:sub(position, position)
      if char == "\"" then
        return table.concat(buffer), position + 1
      end
      if char == "\\" then
        local next_char = text:sub(position + 1, position + 1)
        if next_char == "n" then
          buffer[#buffer + 1] = "\n"
        elseif next_char == "r" then
          buffer[#buffer + 1] = "\r"
        elseif next_char == "t" then
          buffer[#buffer + 1] = "\t"
        elseif next_char == "b" then
          buffer[#buffer + 1] = "\b"
        elseif next_char == "f" then
          buffer[#buffer + 1] = "\f"
        else
          buffer[#buffer + 1] = next_char
        end
        position = position + 2
      else
        buffer[#buffer + 1] = char
        position = position + 1
      end
    end
    decode_error("Niezamknięty string JSON", position)
  end

  local function parse_number(position)
    local start = position
    while position <= length do
      local char = text:sub(position, position)
      if not char:match("[%d%+%-%.eE]") then
        break
      end
      position = position + 1
    end
    local number = tonumber(text:sub(start, position - 1))
    if number == nil then
      decode_error("Niepoprawna liczba JSON", start)
    end
    return number, position
  end

  local function parse_literal(position, literal, value)
    if text:sub(position, position + #literal - 1) ~= literal then
      decode_error("Niepoprawny literal JSON", position)
    end
    return value, position + #literal
  end

  local function parse_array(position)
    local result = {}
    position = skip_ws(position + 1)
    if text:sub(position, position) == "]" then
      return result, position + 1
    end
    while true do
      local item
      item, position = decode_value(text, position)
      result[#result + 1] = item
      position = skip_ws(position)
      local char = text:sub(position, position)
      if char == "]" then
        return result, position + 1
      end
      if char ~= "," then
        decode_error("Oczekiwano przecinka w tablicy JSON", position)
      end
      position = skip_ws(position + 1)
    end
  end

  local function parse_object(position)
    local result = {}
    position = skip_ws(position + 1)
    if text:sub(position, position) == "}" then
      return result, position + 1
    end
    while true do
      if text:sub(position, position) ~= "\"" then
        decode_error("Oczekiwano klucza tekstowego JSON", position)
      end
      local key
      key, position = parse_string(position)
      position = skip_ws(position)
      if text:sub(position, position) ~= ":" then
        decode_error("Oczekiwano dwukropka JSON", position)
      end
      position = skip_ws(position + 1)
      local value
      value, position = decode_value(text, position)
      result[key] = value
      position = skip_ws(position)
      local char = text:sub(position, position)
      if char == "}" then
        return result, position + 1
      end
      if char ~= "," then
        decode_error("Oczekiwano przecinka w obiekcie JSON", position)
      end
      position = skip_ws(position + 1)
    end
  end

  index = skip_ws(index)
  local char = text:sub(index, index)
  if char == "\"" then
    return parse_string(index)
  end
  if char == "{" then
    return parse_object(index)
  end
  if char == "[" then
    return parse_array(index)
  end
  if char == "t" then
    return parse_literal(index, "true", true)
  end
  if char == "f" then
    return parse_literal(index, "false", false)
  end
  if char == "n" then
    return parse_literal(index, "null", nil)
  end
  if char:match("[%d%-]") then
    return parse_number(index)
  end
  decode_error("Nieoczekiwany token JSON", index)
end

function json.decode(text)
  local value, index = decode_value(text, 1)
  while index <= #text do
    local char = text:sub(index, index)
    if char ~= " " and char ~= "\t" and char ~= "\r" and char ~= "\n" then
      decode_error("Nadmiarowe dane JSON", index)
    end
    index = index + 1
  end
  return value
end

return json
