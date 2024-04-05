from renpybuild.context import Context
from renpybuild.task import task

# 1.5.3 is the last version that supported ./configure.
version = "1.5.3"


@task()
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xzf {{source}}/libjpeg-turbo-{{version}}.tar.gz")


@task()
def build(c: Context):
    c.var("version", version)
    c.chdir("libjpeg-turbo-{{version}}")

    c.run("""{{configure}} {{ cross_config }} --disable-shared --prefix="{{ install }}" """)

    c.run("""{{ make }}""")
    c.run("""{{ make_exec }} install """)
