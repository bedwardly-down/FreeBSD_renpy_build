from renpybuild.context import Context
from renpybuild.task import task, annotator

version = "5-r.1"

@annotator
def annotate(c: Context):
    c.include("{{ install }}/cubism/Core/include")
    c.env("CUBISM", "{{ install }}/cubism")


@task(platforms="all")
def build(c: Context):
    c.clean()

    c.var("version", version)
    c.var("cubism_zip", "CubismSdkForNative-{{version}}.zip")
    c.var("cubism_dir", "CubismSdkForNative-{{version}}")

    c.var("live2d", c.path("{{ root }}/live2d"))

    if not c.path("{{ tmp }}/tars/{{ cubism_zip }}").exists():
        return

    c.run("unzip -q {{ tmp }}/tars/{{ cubism_zip }}")

    c.rmtree("{{ install }}/cubism")
    c.run("mv {{cubism_dir}} {{ install }}/cubism")
