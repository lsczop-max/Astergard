if type(cecho) == "function" then
  cecho("<green>Astergard smoke test loaded.</green>\n")
elseif type(echo) == "function" then
  echo("Astergard smoke test loaded.\n")
else
  print("Astergard smoke test loaded.")
end
