from renpybuild.context import Context
from renpybuild.task import task


@task(kind="python")
def clean(c: Context):
    c.clean()


@task(kind="host-python", pythons="2", always=True)
def gen_static2(c: Context):

    c.chdir("{{ renpy }}/module")
    c.env("RENPY_DEPS_INSTALL", "/usr/local::{{ install }}/lib")
    c.env("RENPY_STATIC", "1")
    c.run("{{ hostpython }} setup.py generate")


@task(kind="host-python", platforms="all", pythons="3", always=True)
def gen_static3(c: Context):

    c.chdir("{{ renpy }}/module")
    c.env("RENPY_DEPS_INSTALL", "/usr/local::{{ install }}/lib")
    c.env("RENPY_STATIC", "1")
    c.run("{{ hostpython }} setup.py generate")


@task(kind="python", platforms="all", always=True)
def build(c: Context):

    c.env("CFLAGS", """{{ CFLAGS }} "-I{{ pygame_sdl2 }}" "-I{{ pygame_sdl2 }}/src" "-I{{ renpy }}/module" """)

    if c.python == "3":
        gen = "gen3-static/"
    else:
        gen = "gen-static/"

    modules = [ ]
    sources = [ ]

    def read_setup(dn, suffix=""):

        with open(dn / ("Setup" + suffix)) as f:
            for l in f:
                l = l.partition("#")[0]
                l = l.strip()

                if not l:
                    continue

                parts = l.split()

                if parts[0] == "renpy.compat.dictviews" and c.python != "2":
                    continue

                modules.append(parts[0])

                for i in parts[1:]:
                    if "libhydrogen" not in i:
                        i = i.replace("gen/", gen)
                    sources.append(dn / i)

    read_setup(c.pygame_sdl2)
    read_setup(c.renpy / "module")
    read_setup(c.root / "extensions")

    objects = [ ]

    with c.run_group() as g:

        for source in sources:

            object = str(source.name)[:-2] + ".o"
            objects.append(object)

            c.var("src", source)
            c.var("object", object)
            g.run("{{ CC }} {{ CFLAGS }} -c {{ src }} -o {{ object }}")

        c.generate("{{ runtime }}/librenpy_inittab{{ c.python }}.c", "inittab.c", modules=modules)
        g.run("{{ CC }} {{ CFLAGS }} -c inittab.c -o inittab.o")
        objects.append("inittab.o")

    c.var("objects", " ".join(objects))

    c.run("{{ AR }} r librenpy.a {{ objects }} inittab.o")
    c.run("{{ RANLIB }} librenpy.a")

    c.copy("librenpy.a", "{{ install }}/lib/librenpy.a")
