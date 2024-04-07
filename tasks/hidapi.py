from renpybuild.context import Context
from renpybuild.task import task

@task(kind="host", platforms="all")
def download(c : Context):

    if c.path("{{ tmp }}/source/hidapi").exists():
        c.chdir("{{ tmp }}/source/hidapi")
        c.run("git checkout master")
        c.run("git pull")
        return

    c.clean("{{ tmp }}/source/hidapi")
    c.chdir("{{ tmp }}/source")

    c.run("git clone https://github.com/libusb/hidapi.git")
    c.chdir("{{ tmp }}/source/hidapi")

@task(platforms="all")
def build(c : Context):
    c.clean()

    c.run("""
        {{ cmake }}
        -DCMAKE_INSTALL_PREFIX={{install}}
        {{ tmp }}/source/hidapi
        """)

    try:
        c.run("{{ make }}")
    except:
        c.run("{{ make }} VERBOSE=1")

    c.run("{{ make_exec }} install")
