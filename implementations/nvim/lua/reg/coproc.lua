local M = {}

local function plugin_dir()
    local this_file = debug.getinfo(2, "S").source:sub(2):match("(.*/)")
    return this_file .. "/../.."
end

local dispatch = require("reg.dispatch")

function M.start_coproc(reg_socket, ipc_socket, log_file)
    M.parent_reg_socket = vim.env.REG_SOCKET or ""
    vim.env.REG_SOCKET = reg_socket

    local bin = plugin_dir()
    local out = vim.uv.new_pipe(false)
    local data = ""
    out:read_start(function(err, chunk)
        if err then
            vim.print("Error starting reg server: " .. err)
            out:read_stop()
            out:close()
        elseif chunk then
            data = data .. chunk
        else
            out:read_stop()
            out:close()
            vim.schedule(function()
                -- TODO: this never seems to execute?
                M.pid = tonumber(data)
                M.socket = reg_socket
            end)
        end
    end)

    local handle
    handle = vim.uv.spawn(bin .. "/start-nvim-reg", {
        args = {
            ipc_socket,
            log_file,
            M.parent_reg_socket,
        },
        stdio = { nil, out, nil },
        function(code, signal)
            assert(handle):close()
        end,
    })

    return function()
        vim.uv.fs_unlink(log_file)
        vim.uv.spawn(bin .. "/term-nvim-reg", {
            args = { dispatch.links },
            detached = true,
        })
    end
end

return M
