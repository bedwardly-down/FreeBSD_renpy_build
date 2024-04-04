from renpybuild.context import Context
from renpybuild.task import task, annotator

version = "2.7.18"


@annotator
def annotate(c: Context):
    if c.python == "2":
        c.var("pythonver", "python2.7")
        c.include("{{ install }}/include/{{ pythonver }}")


@task(kind="python", pythons="2")
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/Python-{{version}}.tgz")


@task(kind="python", pythons="2", platforms="freebsd")
def patch_posix(c: Context):
    c.var("version", version)

    c.chdir("Python-{{ version }}")
    c.patch("python2-no-multiarch.diff")
    c.patch("python2-cross-darwin.diff")
    c.patch("python2-utf8.diff")
    c.patch("python-c-locale-utf8.diff")


@task(kind="python", pythons="2", platforms="freebsd")
def build_posix(c: Context):
    c.var("version", version)

    c.chdir("Python-{{ version }}")

    with open(c.path("config.site"), "w") as f:
        f.write("ac_cv_file__dev_ptmx=no\n")
        f.write("ac_cv_file__dev_ptc=no\n")

    c.env("CONFIG_SITE", "config.site")

    c.env("CFLAGS", "{{ CFLAGS }} -DXML_POOR_ENTROPY=1 -DUSE_PYEXPAT_CAPI -DHAVE_EXPAT_CONFIG_H ")

    # Using separate sysroot jails instead of a full cross-compiler for this, so had to adjust these to get compilation to complete
    c.env("MACHDEP", "freebsd")

    # Will update once multi-release support is added
    c.env("_PYTHON_SYSCONFIGDATA_NAME", "_sysconfigdata__freebsd14_")
    c.var("cross_config", "")

    c.run("""{{configure}} {{ cross_config }} --prefix="{{ install }}" --with-system-ffi --enable-ipv6""")

    c.generate("{{ source }}/Python-{{ version }}-Setup.local", "Modules/Setup.local")

    c.run("""{{ make }}""")
    c.run("""{{ make_exec }} install""")

    c.copy("{{ host }}/bin/python2", "{{ install }}/bin/hostpython2")


@task(kind="python", pythons="2")
def pip(c: Context):
    c.run("{{ install }}/bin/hostpython2 -s -m ensurepip")
    c.run("""{{ install }}/bin/hostpython2 -s -m pip install --upgrade
        future==0.18.3
        six==1.12.0
        rsa==3.4.2
        pyasn1==0.4.2
        ecdsa==0.18.0
        urllib3==1.22
        certifi
        idna==2.6
        requests==2.20.0
        pefile==2019.4.18
        typing==3.10.0.0
        """)
