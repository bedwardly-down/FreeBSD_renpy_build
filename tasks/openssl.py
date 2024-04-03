from renpybuild.context import Context
from renpybuild.task import task

version = "1.1.1s"


@task()
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/openssl-{{version}}.tar.gz")


@task()
def build(c: Context):
    c.var("version", version)
    c.chdir("openssl-{{version}}")

    c.run("""./Configure cc no-shared no-asm no-engine threads -lpthread --prefix="{{ install }}" """)

    c.run("""{{ make }}""")
    c.run("""make install_sw""")
