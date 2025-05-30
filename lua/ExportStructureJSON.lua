-- ReaScript: Export Regions and Markers to a single JSON file
-- Output: structure.json in the project folder

function export_structure_json()
    local project_path = reaper.GetProjectPath("")
    local output_file = project_path .. "/structure.json"

    local num_total = reaper.CountProjectMarkers(0)
    local regions = {}
    local markers = {}

    -- Hämta alla markers och regions
    for i = 0, num_total - 1 do
        local retval, isrgn, pos, rgnend, name, idx = reaper.EnumProjectMarkers(i)
        if isrgn then
            table.insert(regions, {
                title = name,
                start = pos,
                endt = rgnend,
                sections = {}
            })
        else
            table.insert(markers, {
                label = name,
                time = pos
            })
        end
    end

    -- Sortera regions i tidsordning
    table.sort(regions, function(a, b) return a.start < b.start end)

    -- Koppla markers till rätt region (baserat på tidsintervall)
    for _, region in ipairs(regions) do
        for _, marker in ipairs(markers) do
            if marker.time >= region.start and marker.time < region.endt then
                table.insert(region.sections, {
                    label = marker.label,
                    time = marker.time
                })
            end
        end
    end

    -- Helper: escapa tecken
    local function escape(str)
        return str:gsub('\\', '\\\\'):gsub('"', '\\"')
    end

    -- Manuell JSON-generering
    local function to_json(tbl)
        local out = {}
        table.insert(out, "[")
        for i, region in ipairs(tbl) do
            table.insert(out, string.format(
                '{"title":"%s","start":%.3f,"end":%.3f,"sections":[',
                escape(region.title), region.start, region.endt
            ))
            for j, section in ipairs(region.sections) do
                table.insert(out, string.format(
                    '{"label":"%s","time":%.3f}',
                    escape(section.label), section.time
                ))
                if j < #region.sections then table.insert(out, ",") end
            end
            table.insert(out, "]}")
            if i < #tbl then table.insert(out, ",") end
        end
        table.insert(out, "]")
        return table.concat(out)
    end

    -- Skriv till fil
    local json = to_json(regions)
    local file = io.open(output_file, "w")
    if file then
        file:write(json)
        file:close()
        reaper.ShowMessageBox("Exported to structure.json", "Success", 0)
    else
        reaper.ShowMessageBox("Failed to write structure.json", "Error", 0)
    end
end

-- Kör script
reaper.Undo_BeginBlock()
export_structure_json()
reaper.Undo_EndBlock("Export structure to JSON", -1)
