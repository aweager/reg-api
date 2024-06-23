local M = {}

local dispatch = require("reg.dispatch")

local function dispatch_request(request)
    local newline_ind = string.find(request, "\n", 1, true)
    if not newline_ind then
        return 2
    end

    local verb = string.sub(request, 1, newline_ind - 1)
    if not dispatch[verb] then
        return 2
    end

    return dispatch[verb](string.sub(request, newline_ind + 1))
end

local function prep_files()
    local pid = vim.fn.getpid()
    M.rundir = vim.fn.stdpath("run") .. "/nvim/reg/"
    M.logdir = vim.fn.stdpath("log") .. "/reg/"

    -- TODO use uv
    os.execute("mkdir -p '" .. M.rundir .. "'")
    os.execute("mkdir -p '" .. M.logdir .. "'")

    M.reg_socket = M.rundir .. "/" .. pid .. ".reg.sock"
    M.ipc_socket = M.rundir .. "/" .. pid .. ".ipc.sock"
    M.coproc_log = M.logdir .. "/" .. pid .. ".server.log"
end

function M.setup()
    prep_files()

    local ipc_close = require("reg.ipc").start_server(M.ipc_socket, dispatch_request)
    if not ipc_close then
        return
    end

    local coproc_close =
        require("reg.coproc").start_coproc(M.reg_socket, M.ipc_socket, M.coproc_log)
    if not coproc_close then
        ipc_close()
        return
    end

    local augroup = vim.api.nvim_create_augroup("RegApi", {})

    vim.api.nvim_create_autocmd("VimLeave", {
        group = augroup,
        callback = function()
            coproc_close()
            ipc_close()
        end,
    })

    vim.api.nvim_create_autocmd("TextYankPost", {
        group = augroup,
        callback = function()
            local regname = string.lower(vim.v.event.regname)
            if regname == "" then
                regname = "unnamed"
            elseif regname:match("%W") then
                -- not alphanumeric, so it's a special register that we don't sync
                return
            end

            vim.uv.spawn("reg", {
                args = { "publish", string.lower(vim.v.event.regname) },
            })
        end,
    })
end

return M
