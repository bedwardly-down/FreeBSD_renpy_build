from renpybuild.context import Context
from renpybuild.task import task

version = "2.6.2"


@task(platforms="all")
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/SDL2_image-{{version}}.tar.gz")
    c.chdir("SDL2_image-{{version}}")

    c.patch("sdl2_image-avif-error.diff")


@task(platforms="all")
def build(c: Context):
    c.var("version", version)
    c.chdir("SDL2_image-{{version}}")

    c.var("config_dir", "/usr/local/share/libtool/build-aux")
    c.run("""cp {{ config_dir }}/config.sub config.sub""")

    # c.run("""./autogen.sh""")
    c.run("autoreconf -f")

    c.env("LIBAVIF_LIBS", "-lavif -laom -lyuv")

    c.run("""{{configure}} {{ cross_config }} --prefix="{{ install }}"
    --with-gnu-ld
    --disable-shared

    --disable-imageio
    --disable-stb-image

    --enable-avif
    --disable-avif-shared
    --disable-jpg-shared
    --disable-jxl
    --disable-jxl-shared
    --disable-lbm
    --disable-pcx
    --disable-png-shared
    --disable-tif
    --disable-xcf
    --disable-webp-shared
    --disable-qoi
    """)

    libtool = c.path("libtool")
    text = libtool.read_text()

    text = text.replace("cygpath -w -p", "echo")
    text = text.replace("cygpath -w", "echo")

    libtool.write_text(text)

    c.run("""{{ make }}""")
    c.run("""{{ make_exec }} install""")
