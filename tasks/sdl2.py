from renpybuild.context import Context
from renpybuild.task import task, annotator
import shutil

version = "2.0.20"


@annotator
def annotate(c: Context):
    if c.name != "sdl2":
        c.include("{{ install }}/include/SDL2")


@task()
def unpack(c: Context):

    if not c.args.sdl:

        c.clean()

        c.var("version", version)
        c.run("tar xzf {{source}}/SDL2-{{version}}.tar.gz")

        c.chdir("SDL2-{{version}}")
        c.patchdir("SDL2-{{version}}")

        c.run("""./autogen.sh""")


@task()
def build(c: Context):
    c.var("version", version)
    c.chdir("SDL2-{{version}}")

    c.env("ac_cv_header_libunwind_h", "no")

    if not c.args.sdl:

        c.run("""
        {{configure}} {{ sdl_cross_config }}
        --disable-shared
        --prefix="{{ install }}"

        --disable-render-metal
        --disable-jack
        --disable-pipewire

        --disable-video-kmsdrm

        --disable-video-x11
        --disable-video-wayland
    """)

    c.run("""{{ make }}""")
    c.run("""make install""")
