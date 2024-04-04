from renpybuild.context import Context
from renpybuild.task import task, annotator

version = "3.9.10"

@annotator
def annotate(c: Context):
    if c.python == "3":

        c.var("pythonver", "python3.9")
        c.var("pycver", "39")

        c.include("{{ install }}/include/{{ pythonver }}")


@task(kind="python", pythons="3", platforms="linux,mac,android,ios")
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/Python-{{version}}.tgz")

@task(kind="python", pythons="3", platforms="freebsd")
def unpack_freebsd(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/Python-{{version}}.tgz")

@task(kind="python", pythons="3", platforms="freebsd")
def patch_posix_freebsd(c: Context):
    c.var("version", version)

    c.chdir("Python-{{ version }}")
    c.patch("Python-{{ version }}/no-multiarch.diff")
    c.patch("Python-{{ version }}/fix-ssl-dont-use-enum_certificates.diff")

    c.run(""" autoreconf -vfi """)

def common(c: Context):
    c.var("version", version)
    c.env("CONFIG_SITE", "config.site")
    c.env("PYTHON_FOR_BUILD", "{{ host }}/bin/python3")

    c.chdir("Python-{{ version }}")
    with open(c.path("config.site"), "w") as f:
        f.write("ac_cv_file__dev_ptmx=no\n")
        f.write("ac_cv_file__dev_ptc=no\n")


@task(kind="python", pythons="3", platforms="linux,mac,freebsd")
def build_posix(c: Context):

    common(c)

    # Using separate sysroot jails instead of a full cross-compiler for this, so had to adjust these to get compilation to complete
    c.var("platform", c.platform)
    c.var("arch", c.arch)
    c.env("MACHDEP", "freebsd")
    c.env("_PYTHON_SYSCONFIGDATA_NAME", "_sysconfigdata__freebsd14_")
    c.var("cross_config", "")

    c.run("""{{configure}} {{ cross_config }} --prefix="{{ install }}" --with-system-ffi --enable-ipv6""")
    c.generate("{{ source }}/Python-{{ version }}-Setup.local", "Modules/Setup.local")

    # nuke nismodule.c to prevent build failure; this is deprecated and not needed for this build
    c.run("cp /dev/null Modules/nismodule.c")

    c.run("""{{ make }}""")
    c.run("""{{ make_exec }} install""")
    c.copy("{{ host }}/bin/python3", "{{ install }}/bin/hostpython3")

@task(kind="python", pythons="3", platforms="all")
def pip(c: Context):
    c.run("{{ install }}/bin/hostpython3 -s -m ensurepip")
    c.run("""{{ install }}/bin/hostpython3 -s -m pip install --no-compile --upgrade
        future==0.18.3
        six==1.12.0
        rsa==3.4.2
        pyasn1==0.4.2
        ecdsa==0.18.0
        urllib3==2.0.4
        charset-normalizer==3.2.0
        certifi
        idna==3.4
        requests==2.31.0
        pefile==2021.9.3
        chardet==5.1.0
        websockets==12.0
        """)
