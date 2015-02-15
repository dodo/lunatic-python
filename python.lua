local io = require 'io'
local pythons = {'python3', 'python'}
local lua = jit and 'luajit' or 'lua'
local loaded = false
local filename = nil

for _, python in ipairs(pythons) do
	-- call python executable to lua/luajit module to get its absolute filename
	local fd = io.popen(
		string.format(
			"%s -c 'import %s; print(%s.__file__)'",
			python, lua, lua
		)
	)
	if fd then
		for line in fd:lines() do
			if not filename then
				filename = line
			else -- probably an error
				filename = nil
				fd:close()
				break
			end
		end
		if filename then
			break
		end
	end
end

if filename then
	local luaopen_python = package.loadlib(filename, "luaopen_python")
	if luaopen_python then
		-- load python module into global namespace
		loaded = luaopen_python()
	end
end

if not loaded then
	error("unable to find lua-python library")
end

return python
