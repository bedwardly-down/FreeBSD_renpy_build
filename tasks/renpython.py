from renpybuild.context import Context
from renpybuild.task import task
import os
import time

@task(kind="python", always=True)
def clean(c: Context):
    c.clean()


@task(kind="python", always=True)
def build(c: Context):

    c.run("""
    {{ CC }} {{ CFLAGS }}

    -DPLATFORM=\\"{{ c.platform }}\\"
    -DARCH=\\"{{ c.arch }}\\"
    -DPYTHONVER=\\"{{ pythonver }}\\"
    -DPYCVER=\\"{{ pycver }}\\"
    -D{{ c.platform|upper }}

    -c -o librenpython.o
    {{ runtime }}/librenpython{{ c.python }}.c
    """)

@task(kind="python", always=True, platforms="freebsd")
def link(c: Context):

    c.run("""
    {{ CXX }} {{ LDFLAGS }}
    -shared
    -static-libstdc++
    -Wl,-Bsymbolic

    -o librenpython.so
    librenpython.o

    -lrenpy
    -l{{ pythonver }}

    -lavformat
    -lavcodec
    -lswscale
    -lswresample
    -lavutil

    -lSDL2_image
    -lSDL2
    -lGL
    -lavif
    -laom
    -lyuv
    -ljpeg
    -lpng
    -lwebp
    -lsharpyuv
    -lfribidi
    -lharfbuzz
    -lbrotlidec
    -lfreetype
    -lffi
    -ldl
    -lssl
    -lcrypto
    -llzma
    -lbz2
    -lutil
    -lz
    -lpthread
    -lm
    """)

    c.run("""
    {{ CC }} {{ CDFLAGS }} {{ LDFLAGS }}
    -o python
    {{ runtime }}/renpython{{ c.python }}_posix.c

    librenpython.so
    -Wl,-rpath -Wl,$ORIGIN
    """)

    c.run("""
    {{ CC }} {{ CDFLAGS }} {{ LDFLAGS }}
    -o renpy
    {{ runtime }}/launcher{{ c.python }}_posix.c

    librenpython.so
    -Wl,-rpath -Wl,$ORIGIN
    """)

    if not c.args.nostrip:
        c.run("""{{ STRIP }} --strip-unneeded librenpython.so python renpy""")

    c.run("""install -d {{ dlpa }}""")
    c.run("""install librenpython.so {{ dlpa }}""")
    c.run("""install python {{ dlpa }}/python""")
    c.run("""install python {{ dlpa }}/pythonw""")
    c.run("""install renpy {{ dlpa }}/renpy""")
