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
def link_freebsd(c: Context):

    c.env("LDFLAGS", "{{ LDFLAGS }} -L/usr/local/lib")
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


def fix_pe(c: Context, fn):
    """
    Sets the PE file characteristics to mark the relocations as stripped.
    """

    import sys
    print(sys.executable, sys.path)

    fn = str(c.path(fn))

    with open(c.path("fix_pe.py"), "w") as f:

        f.write("""\
import sys
print(sys.executable, sys.path)

import pefile
import sys

fn = sys.argv[1]

pe = pefile.PE(fn)
pe.FILE_HEADER.Characteristics = pe.FILE_HEADER.Characteristics | pefile.IMAGE_CHARACTERISTICS["IMAGE_FILE_RELOCS_STRIPPED"]
pe.OPTIONAL_HEADER.CheckSum = pe.generate_checksum()
pe.write(fn)
""")

    c.run("""{{ hostpython }} fix_pe.py """ + fn)

