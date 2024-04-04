import os
import re
import shlex
import subprocess
import sys
import sysconfig

import jinja2

# This caches the results of emsdk_environment.
emsdk_cache : dict[str, str] = { }

def emsdk_environment(c):
    """
    Loads the emsdk environment into `c`.
    """

    emsdk = c.path("{{ cross }}/emsdk")

    if not emsdk.exists():
        return

    if not emsdk_cache:

        env = dict(os.environ)
        env["EMSDK_BASH"] = "1"
        env["EMSDK_QUIET"] = "1"

        bash = subprocess.check_output([ str(emsdk), "construct_env" ], env=env, text=True)

        for l in bash.split("\n"):
            m = re.match(r'export (\w+)=\"(.*?)\";?$', l)
            if m:
                emsdk_cache[m.group(1)] = m.group(2)

    for k, v in emsdk_cache.items():
        c.env(k, v)


def llvm(c, bin="", prefix="", suffix="15", clang_args="", use_ld=True):

    if bin and not bin.endswith("/"):
        bin += "/"

    c.var("llvm_bin", bin)
    c.var("llvm_prefix", prefix)
    c.var("llvm_suffix", suffix)

    ld = c.expand("{{llvm_bin}}lld{{llvm_suffix}}")

    if use_ld:
        clang_args = "-fuse-ld=lld -Wno-unused-command-line-argument " + clang_args

    c.var("cxx_clang_args", "")

    c.var("clang_args", clang_args)

    c.env("CC", "ccache {{llvm_bin}}{{llvm_prefix}}clang{{llvm_suffix}} {{ clang_args }} -std=gnu17")
    c.env("CXX", "ccache {{llvm_bin}}{{llvm_prefix}}clang++{{llvm_suffix}} {{ clang_args }} -std=gnu++17 {{ cxx_clang_args }}")
    c.env("CPP", "ccache {{llvm_bin}}{{llvm_prefix}}clang{{llvm_suffix}} {{ clang_args }} -E")

    c.env("LD", "ccache " + ld)
    c.env("AR", "ccache {{llvm_bin}}llvm-ar{{llvm_suffix}}")
    c.env("RANLIB", "ccache {{llvm_bin}}llvm-ranlib{{llvm_suffix}}")
    c.env("STRIP", "ccache {{llvm_bin}}llvm-strip{{llvm_suffix}}")
    c.env("NM", "ccache {{llvm_bin}}llvm-nm{{llvm_suffix}}")
    c.env("READELF", "ccache {{llvm_bin}}llvm-readelf{{llvm_suffix}}")

    c.env("WINDRES", "{{llvm_bin}}{{llvm_prefix}}windres{{llvm_suffix}}")

def build_environment(c):
    """
    Sets up the build environment inside the context.
    """
    cpuccount = os.cpu_count()

    if cpuccount is None:
        cpuccount = 4

    if cpuccount > 12:
        cpuccount -= 4

    # FreeBSD primarily uses gmake for make actions; this is to fix that
    # FreeBSD wasn't initialized in the context yet; workaround with sys module
    if sys.platform.startswith('freebsd'):
        c.var("make_exec", "gmake")
    else:
        c.var("make_exec", "make")
    
    c.var("make", "nice {{make_exec}} -j " + str(cpuccount))
    c.var("configure", "./configure")
    c.var("cmake", "cmake")

    c.var("sysroot", c.tmp / f"sysroot.{c.platform}-{c.arch}")
    c.var("build_platform", sysconfig.get_config_var("HOST_GNU_TYPE"))

    c.env("CPPFLAGS", "-I{{ install }}/include")
    c.env("CFLAGS", "-O3 -I{{ install }}/include")
    c.env("LDFLAGS", "-O3 -L{{install}}/lib")

    c.env("PATH", "{{ host }}/bin:{{ PATH }}")

    # will update this once I have multi-release support added
    c.var("host_platform", "x86_64-pc-freebsd14.0")
    c.var("architecture_name", "x86_64-pc-freebsd14.0")

    c.var("sdl_host_platform", "{{ host_platform }}")

    c.var("ffi_host_platform", "{{ host_platform }}")

    if c.kind == "host" or c.kind == "host-python" or c.kind == "cross":
        llvm(c)

        c.env("LDFLAGS", "{{ LDFLAGS }} -L{{install}}/lib")
        c.env("PKG_CONFIG_PATH", "{{ install }}/lib/pkgconfig")

        # c.var("cmake_system_name", "Linux")
        # c.var("cmake_system_processor", "x86_64")
        c.var("cmake_args", "-DCMAKE_FIND_ROOT_PATH={{ install }}")

    elif (c.platform == "freebsd") and (c.arch == "x86_64"):

        llvm(c, clang_args="-target {{ host_platform }} --sysroot {{ sysroot }} -fPIC -pthread")
        c.env("LDFLAGS", "{{ LDFLAGS }} -L{{install}}/lib")
        c.env("PKG_CONFIG_LIBDIR", "{{ install }}/lib/pkgconfig:{{ sysroot }}/usr/local/lib/{{ architecture_name }}/pkgconfig:{{ sysroot }}/usr/local/share/pkgconfig")
        # c.env("PKG_CONFIG_SYSROOT_DIR", "{{ sysroot }}")

        c.var("cmake_system_name", "FreeBSD")
        c.var("cmake_system_processor", "x86_64")
        c.var("cmake_args", "-DCMAKE_FIND_ROOT_PATH='{{ install }};{{ sysroot }}' -DCMAKE_SYSROOT={{ sysroot }}")

    else:
        c.env("PKG_CONFIG_LIBDIR", "{{ install }}/lib/pkgconfig:{{ PKG_CONFIG_LIBDIR }}")
        c.var("cmake_args", "{{cmake_args}} -DCMAKE_SYSTEM_NAME={{ cmake_system_name }} -DCMAKE_SYSTEM_PROCESSOR={{ cmake_system_processor }} -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER -DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY -DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY")

    c.env("PKG_CONFIG", "pkg-config --static")

    c.env("CFLAGS", "{{ CFLAGS }} -DRENPY_BUILD")
    c.env("CXXFLAGS", "{{ CFLAGS }}")

    c.var("cmake", "{{cmake}} {{ cmake_args }} -DCMAKE_PROJECT_INCLUDE_BEFORE={{root}}/tools/cmake_build_variables.cmake -DCMAKE_BUILD_TYPE=Release")

    # Used by zlib.
    if c.kind != "host":
        c.var("cross_config", "--host={{ host_platform }} --build={{ build_platform }}")
        c.var("sdl_cross_config", "--host={{ sdl_host_platform }} --build={{ build_platform }}")
        c.var("ffi_cross_config", "--host={{ ffi_host_platform }} --build={{ build_platform }}")


def run(command, context, verbose=False, quiet=False):
    args = shlex.split(command)

    if verbose:
        print(" ".join(shlex.quote(i) for i in args))

    if not quiet:
        p = subprocess.run(args, cwd=context.cwd, env=context.environ)
    else:
        with open("/dev/null", "w") as f:
            p = subprocess.run(args, cwd=context.cwd, env=context.environ, stdout=f, stderr=f)

    if p.returncode != 0:
        print(f"{context.task_name}: process failed with {p.returncode}.")
        print("args:", " ".join(repr(i) for i in args))
        import traceback
        traceback.print_stack()
        sys.exit(1)

class RunCommand(object):

    def __init__(self, command, context):
        command = context.expand(command)
        self.command = shlex.split(command)

        self.cwd = context.cwd
        self.environ = context.environ.copy()

        self.p = subprocess.Popen(self.command, cwd=self.cwd, env=self.environ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")

    def wait(self):
        self.code = self.p.wait()
        self.output = self.p.stdout.read() # type: ignore

    def report(self):
        print ("-" * 78)

        for i in self.command:
            if " " in i:
                print(repr(i), end=" ")
            else:
                print(i, end=" ")

        print()
        print()
        print(self.output)

        if self.code != 0:
            print()
            print(f"Process failed with {self.code}.")

class RunGroup(object):

    def __init__(self, context):
        self.context = context
        self.tasks = [ ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return

        for i in self.tasks:
            i.wait()

        good = [ i for i in self.tasks if i.code == 0 ]
        bad = [ i for i in self.tasks if i.code != 0 ]

        for i in good:
            i.report()

        for i in bad:
            i.report()

        if bad:
            print()
            print("{} tasks failed.".format(len(bad)))
            sys.exit(1)

    def run(self, command):
        self.tasks.append(RunCommand(command, self.context))
