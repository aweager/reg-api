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

function M.setup()
    local dir = vim.fn.stdpath("run") .. "/nvim/reg/" .. vim.fn.getpid()
    -- TODO use uv
    os.execute("mkdir -p '" .. dir .. "'")
    vim.uv.fs_mkdir(dir, tonumber("0700", 8))

    local close_func =
        require("reg.ipc").start_server("/Users/alexandereager/socket", dispatch_request)

    if close_func then
        vim.api.nvim_create_autocmd("VimLeave", {
            group = vim.api.nvim_create_augroup("RegApi", {}),
            callback = function()
                close_func()
                -- TODO use uv
                os.execute("rmdir '" .. state_dir .. "'")
            end,
        })
    end
end

return M
