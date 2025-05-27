-- ExportMarkersOnSave.lua

function ExportMarkers()
  local project_path = reaper.GetProjectPath("")  -- folder of current project
  local file = io.open(project_path .. "/markers.txt", "w")

  if not file then
    reaper.ShowMessageBox("Could not open markers.txt for writing!", "Error", 0)
    return
  end

  local count = reaper.CountProjectMarkers(0)
  for i = 0, count - 1 do
    local retval, isrgn, pos, rgnend, name, markrgnindexnumber = reaper.EnumProjectMarkers(i)
    if not isrgn then
      file:write(string.format("%f|%s\n", pos, name))
    end
  end

  file:close()
end

ExportMarkers()