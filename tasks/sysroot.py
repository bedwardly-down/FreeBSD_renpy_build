from renpybuild.context import Context
from renpybuild.task import task

import os

freebsd = "14.0.0"


@task(platforms="freebsd")
def unpack_sysroot(c: Context):
    c.clean()

    c.var("freebsd", freebsd)
    c.run("mkdir -p freebsd-{{freebsd}}-base")
    c.run("tar xJf {{ tmp }}/tars/freebsd-amd64-{{freebsd}}-base.tar.xz -C freebsd-{{freebsd}}-base")

# this is here to make setting sysroot easier; most of this will rely on it until the sysroot is finalized
@task(platforms="freebsd")
def set_sysroot(c: Context):
    c.var("freebsd", freebsd)
    c.var("sysroot", str(c.path("freebsd-{{freebsd}}-base")))
    return c

# we're building the sysroot jail here with the required libraries for cross-compiling
@task(platforms="freebsd")
def prepare_sysroot(c: Context):
    set_sysroot(c)

    # set sysroot to pull the latest packages; quarterly typically isn't new enough
    c.run("mkdir -p {{ sysroot }}/usr/local/etc/pkg/repos")
    c.copy("{{ sysroot }}/etc/pkg/FreeBSD.conf", "{{ sysroot }}/usr/local/etc/pkg/repos/FreeBSD.conf")

    # set up internal network stuff so pkg works
    c.copy("/etc/resolv.conf", "{{ sysroot }}/etc/resolv.conf")
    c.copy("/etc/localtime", "{{ sysroot }}/etc/localtime")
    c.run("""
        sysrc -f {{ sysroot }}/etc/rc.conf hostname="base"
    """)

    c.run("""
        sed -i.orig 's/quarterly/latest/' {{ sysroot }}/usr/local/etc/pkg/repos/FreeBSD.conf
    """)

    # set the base as owned by root:wheel so that pkg will work correctly
    c.run("sudo chown -R root:wheel {{ sysroot }}")

    # mount required mount points for pkg to work; these only need to exist here
    c.run("sudo mount -t devfs devfs {{ sysroot }}/dev")
    c.run("sudo mount -t procfs procfs {{ sysroot }}/proc")


@task(platforms="freebsd")
def install_sysroot_tools(c: Context):
    set_sysroot(c)

    c.run("""
        sudo chroot {{ sysroot }} /bin/sh -c '
            pkg install -y gcc13 bison \
                flex libxml2 llvm15 gmp mpfr mpc iconv
        '
    """)

    #c.run("""sudo {{source}}/make_links_relative.py {{sysroot}}""")

@task(platforms="freebsd")
def permissions(c: Context):
    import os

    set_sysroot(c)

    c.var("uid", str(os.getuid()))
    c.var("gid", str(os.getgid()))
    c.run("""sudo chown -R {{uid}}:{{gid}} {{sysroot}}""")
    

    c.run("sudo umount {{ sysroot }}/dev")
    c.run("sudo umount {{ sysroot }}/proc")

#@task(platforms="freebsd")
#def fix_pkgconf_prefix(c: Context):
#    """
#    Replace prefix for .pc file in sysroot, so pkgconfig can pass right
#    SYSROOT prefix to cflags. Set env PKG_CONFIG_SYSROOT_DIR isn't safe
#    because it will prepend prefix to libraries outside of SYSROOT, see
#    https://github.com/pkgconf/pkgconf/issues/213 and https://github.co
#    m/pkgconf/pkgconf/pull/280.
#    """
#
#    c.run("""
#          bash -c "grep -rl {{sysroot}} {{sysroot}}/usr/local/lib/{{architecture_name}}/pkgconfig > /dev/null || sed -i.orig 's#/usr#{{sysroot}}/usr/local/#g' $(grep -rl /usr/local {{sysroot}}/usr/local/lib/{{architecture_name}}/pkgconfig) $(grep -rl /usr/local {{sysroot}}/usr/local/share/pkgconfig)"
#          """)

@task(platforms="freebsd")
def update_wayland_headers(c: Context):
    """
    This adds newer wayland headers to the systems we support. This
    is safe because wayland is dynamically loaded, and we don't use
    any of the newer features.
    """

    c.copytree("{{source}}/wayland-headers/", "{{ sysroot }}/usr/local/include/wayland")

@task(platforms="freebsd")
def update_wayland_pkgconfig(c: Context):

    c.copytree("{{source}}/wayland-pc-files/", "{{ sysroot }}/usr/local/lib/wayland/")

@task(platforms="freebsd")
def install_sysroot(c: Context):
    set_sysroot(c)

    # make sysroot one that the build system can use
    c.var("platform", c.platform)
    c.var("arch", c.arch)
    c.var("main_sysroot", "{{ tmp }}/sysroot.{{ platform }}-{{ arch }}")

    # remove the old sysroot before replacing with new one
    if c.path("{{ main_sysroot }}").exists():
        c.rmtree("{{ main_sysroot }}")
    # use this to preserve symlinks
    c.run("mv -v {{ sysroot }} {{ main_sysroot }}")

