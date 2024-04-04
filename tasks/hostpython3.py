from renpybuild.context import Context
from renpybuild.task import task
import sys
import os

version = "3.9.10"

@task(kind="host", pythons="3")
def unpack_hostpython(c: Context):
    c.clean()
    c.var("version", version)

    c.run("tar xzf {{source}}/Python-{{version}}.tgz")


@task(kind="host", pythons="3")
def build_host(c: Context):
    c.var("version", version)
    c.var("pyver", "3.9")

    c.chdir("Python-{{ version }}")
    
    c.run("""{{configure}} --prefix="{{ host }}" """)
    c.generate("{{ source }}/Python-{{ version }}-Setup.local", "Modules/Setup.local")

    # create the install folder to solve build error
    c.run("mkdir -p {{ host }}/lib/python{{ pyver }}")

    c.run("""{{ make_exec }} install""")

    # will update once I get multi-release support setup
    c.var("ending", "freebsd14.0")

    c.rmtree("{{ host }}/lib/python{{ pyver }}/config-{{ pyver }}-x86_64-{{ ending }}/Tools/")
    c.run("install -d {{ host }}/lib/python{{ pyver }}/config-{{ pyver }}-x86_64-{{ ending }}/Tools/")
    c.run("cp -a Tools/scripts {{ host }}/lib/python{{ pyver }}/config-{{ pyver }}-x86_64-{{ ending }}/Tools/scripts")
