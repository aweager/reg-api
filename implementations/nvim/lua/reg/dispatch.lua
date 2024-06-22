local M = {}

local function resolve_regname(regname)
    if regname == "unnamed" then
        return ""
    end

    if string.len(regname) ~= 1 then
        return nil
    end

    return regname
end

function M.get(regname)
    regname = resolve_regname(regname)
    if regname == nil then
        return 2
    end

    local lines = vim.fn.getreg(regname, 1, 1)
    if #lines > 0 then
        return table.concat(lines, "\n")
    end

    return 1
end

function M.list()
    local results = {}
    local lines = vim.fn.getreg("", 1, 1)
    if #lines > 0 then
        table.insert(results, "unnamed")
    end

    for c in ("abcdefghijklmnopqrstuvwxyz"):gmatch(".") do
        lines = vim.fn.getreg(c, 1, 1)
        if #lines > 0 then
            table.insert(results, c)
        end
    end

    if #results == 0 then
        return 0
    end

    return table.concat(results, "\n") .. "\n"
end

function M.set(request_body)
    local newline_ind = string.find(request_body, "\n", 1, true)
    if not newline_ind then
        return 2
    end

    local regname = resolve_regname(string.sub(request_body, 1, newline_ind - 1))
    if regname == nil then
        return 2
    end

    vim.fn.setreg(regname, string.sub(request_body, newline_ind + 1))
    return 0
end

function M.delete(regname)
    regname = resolve_regname(regname)
    if regname == nil then
        return 2
    end

    vim.fn.setreg(regname, {})
    return 0
end

function M.set_link_list(links)
    M.links = links
    return 0
end

function M.list_links()
    return M.links
end

M.links = ""
return M
