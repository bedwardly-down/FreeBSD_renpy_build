from renpybuild.context import Context
from renpybuild.task import task
import os

version = "3.4.6"


@task()
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/libffi-{{version}}.tar.gz")


@task()
def build(c: Context):
    c.var("version", version)
    c.chdir("libffi-{{version}}")

    c.run("""{{configure}} {{ ffi_cross_config }} --disable-shared --enable-portable-binary --prefix="{{ install }}" """)
    c.run("""{{ make }}""")
    c.run("""{{ make_exec }} install """)

    # create the host's lib folder to solve build error
    c.var("lib_dir", "{{ host }}/lib")
    if not os.path.exists("{{ lib_dir }}"):
        c.run("mkdir -p {{ lib_dir }}")
    # create the host's include folder to solve build error
    c.var("include_dir", "{{ host }}/include")
    if not os.path.exists("{{ include_dir_dir }}"):
        c.run("mkdir -p {{ include_dir }}")

    # copy ffi.h for Freebsd hostpythons to compile properly
    c.run("ln -s {{ install }}/include/ffi.h {{ include_dir }}/ffi.h")
    c.run("ln -s {{ install }}/include/ffitarget.h {{ include_dir }}/ffitarget.h")
    c.run("ln -s {{ install }}/lib/libffi.a {{ lib_dir }}/libffi.a")
