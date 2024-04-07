from renpybuild.context import Context
from renpybuild.task import task

version = "1.0.27"


@task()
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xjf {{source}}/libusb-{{version}}.tar.bz2")

@task()
def build(c: Context):
    c.var("version", version)
    c.chdir("libusb-{{version}}")

    c.run("""{{configure}} --prefix="{{ install }}" """)
    c.run("""{{ make }}""")
    c.run("""{{ make_exec }} install """)
