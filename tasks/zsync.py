from renpybuild.context import Context
from renpybuild.task import task

version = "0.6.2"


@task(kind="python")
def unpack(c: Context):
    c.clean()

    c.var("version", version)
    c.run("tar xjf {{source}}/zsync-{{version}}.tar.bz2")

    c.run("""cp /usr/share/misc/config.sub zsync-{{version}}/autotools""")

@task(kind="python", platforms="freebsd")
def build_freebsd(c: Context):

    c.var("version", version)
    c.chdir("zsync-{{ version }}")

    c.patch("zsync-no-isastty.diff", p=1)
    c.patch("zsync-compress-5.diff", p=0)

    c.run("""{{configure}} {{ cross_config }} --prefix="{{ install }}" """)
    c.run("""{{ make }}""")

    c.run("install -d {{ dlpa }}")
    c.run("install zsync zsyncmake {{ dlpa }}")
