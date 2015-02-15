#!/usr/bin/python3

import sys
import os

if sys.version > '3': # python3
    import subprocess as commands
    from functools import reduce
else:
    import commands
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib, get_python_version

lunatic = dict(
    name="lunatic-python",
    version="2.0",
    description="Two-way bridge between Python and Lua",
    author="Gustavo Niemeyer",
    author_email="gustavo@niemeyer.net",
    url="http://labix.org/lunatic-python",
    license="LGPL",
    long_description="""\
Lunatic Python is a two-way bridge between Python and Lua, allowing these
languages to intercommunicate. Being two-way means that it allows Lua inside
Python, Python inside Lua, Lua inside Python inside Lua, Python inside Lua
inside Python, and so on.
""")


if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

# You may have to change these
LUAJITVERSION = "5.1"
LUAJITLIBS = ["luajit" + LUAJITVERSION, "luajit-" + LUAJITVERSION, "luajit"]

LUAVERSION = "5.2"
LUALIBS = ["lua-" + LUAVERSION, "lua" + LUAVERSION, "lua"]

PYTHONVERSION = get_python_version()
PYLIBS = ["python-" + PYTHONVERSION, "python" + PYTHONVERSION, "python"]


def pkgconfig(*packages):
    # map pkg-config output to kwargs for distutils.core.Extension
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}

    for package in packages:
        (pcstatus, pcoutput) = commands.getstatusoutput(
            "pkg-config --libs --cflags %s" % package)
        if pcstatus == 0:
            break
    else:
        sys.exit("pkg-config failed for %s; "
                 "most recent output was:\n%s" %
                 (", ".join(packages), pcoutput))

    kwargs = {}
    for token in pcoutput.split():
        if token[:2] in flag_map:
            kwargs.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else:                           # throw others to extra_link_args
            kwargs.setdefault('extra_link_args', []).append(token)

    for k, v in kwargs.items():     # remove duplicated
        kwargs[k] = list(set(v))

    return kwargs

def merge(*dicts):
    def dict_extend(a, b):
        for k, v in b.items():
            a.setdefault(k, []).extend(v)
        return a
    return reduce(dict_extend, dicts, {})


py_pkgconfig = pkgconfig(*PYLIBS)
lua_pkgconfig = pkgconfig(*LUALIBS)
luajit_pkgconfig = pkgconfig(*LUAJITLIBS)


lunatic.update({
    'ext_modules': [
        Extension("lua",
                  ["src/pythoninlua.c", "src/luainpython.c"],
                  define_macros=[
                      ('LUA_MODULE', 'lua'),
                  ], **merge(lua_pkgconfig, py_pkgconfig)),
        Extension("luajit",
                  ["src/pythoninlua.c", "src/luainpython.c"],
                  define_macros=[
                      ('LUA_MODULE', 'luajit'),
                  ], **merge(luajit_pkgconfig, py_pkgconfig)),
        ],
})

setup(**lunatic)
