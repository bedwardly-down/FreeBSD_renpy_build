#!/usr/bin/env python3

import sys
import argparse
import shutil
from pathlib import Path

sys.path.insert(1, str(Path(__file__).parent / 'deps'))

import renpybuild.task
from renpybuild.context import Context

import tasks as _

known_platforms = [ ]

# Platform Registry ############################################################


class Platform:

    def __init__(self, platform, arch, python, experimental=False):
        self.platform = platform
        self.arch = arch
        self.python = python
        self.experimental = experimental

        known_platforms.append(self)


# Python 2

Platform("freebsd", "x86_64", "2")

# Python 3

Platform("freebsd", "x86_64", "3")

def build(args):
    platforms = set(i.strip() for i in args.platforms.split(",") if i)
    archs = set(i.strip() for i in args.archs.split(",") if i)
    pythons = set(i.strip() for i in args.pythons.split(",") if i)

    # Check that the platforms, archs, and pythons are known.

    for i in platforms:
        if i not in { j.platform for j in known_platforms }:
            print("Platform", i, "is not known.", file=sys.stderr)
            sys.exit(1)

    for i in archs:
        if i not in { j.arch for j in known_platforms }:
            print("Architecture", i, "is not known.", file=sys.stderr)
            sys.exit(1)

    for i in pythons:
        if i not in { j.python for j in known_platforms }:
            print("Python", i, "is not known.", file=sys.stderr)
            sys.exit(1)

    # Actually build everything.

    for task in renpybuild.task.tasks:
        for p in known_platforms:

            if platforms and (p.platform not in platforms):
                continue

            if archs and (p.arch not in archs):
                continue

            if pythons and (p.python not in pythons):
                continue

            platform = p.platform
            arch = p.arch
            python = p.python

            context = Context(
                p.platform,
                p.arch,
                p.python,
                root,
                args)

            task.run(context)

    print("")
    print("Build finished successfully.")


def remove_complete(args):

    tmp = root / "tmp"
    complete = tmp / "complete"

    if not complete.is_dir():
        return

    for fn in complete.iterdir():
        name = fn.name.split(".")[0]
        taskname = name.rpartition("-")[2]

        if (name in args.tasks) or (taskname in args.tasks):
            fn.unlink()


def rebuild(args):

    remove_complete(args)
    build(args)


def clean(args):

    def rmtree(p : Path):
        if p.exists():
            shutil.rmtree(p)

    def unlink(p : Path):
        if p.exists():
            p.unlink()

    tmp = root / "tmp"

    rmtree(tmp / "build")
    rmtree(tmp / "complete")
    rmtree(tmp / "host")
    rmtree(tmp / "source")

    for i in tmp.glob("install.*"):
        rmtree(i)

    def rmgen(d):
        rmtree(d / "gen")
        rmtree(d / "gen-static")
        rmtree(d / "gen3")
        rmtree(d / "gen3-static")

    rmgen(root / "renpy" / "module")
    rmgen(root / "pygame_sdl2")

    def rmtrio(name : str):
        """
        Deletes groups of directories and symlinks, like web, renios, and rapt.
        """

        unlink(root / "renpy" / name)
        rmtree(root / "renpy" / (name + "2"))
        rmtree(root / "renpy" / (name + "3"))

    rmtrio("web")
    rmtrio("renios")
    rmtrio("rapt")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--platforms", "--platform", default="")
    ap.add_argument("--archs", "--arch", default="")
    ap.add_argument("--pythons", "--python", default="3")

    ap.add_argument("--nostrip", action="store_true", default=False)
    ap.add_argument("--sdl", action="store_true", default=False, help="Do not clean SDL on rebuild.")

    ap.add_argument("--experimental", action="store_true", default=False)

    ap.set_defaults(function=build)

    subparsers = ap.add_subparsers()

    sp = subparsers.add_parser("build")
    sp.set_defaults(function=build)

    sp = subparsers.add_parser("rebuild")
    sp.add_argument("tasks", nargs='+')
    sp.set_defaults(function=rebuild)

    sp = subparsers.add_parser("clean")
    sp.set_defaults(function=clean)

    global root

    args = ap.parse_args()

    if not args.experimental:
        known_platforms[:] = [ i for i in known_platforms if not i.experimental ]

    root = Path(__file__).parent.resolve()


    args.function(args)


if __name__ == "__main__":
    import os

    if os.environ.get('PYTHONHASHSEED') is None:
        os.environ['PYTHONHASHSEED'] = "0"
        os.execv(sys.executable, sys.orig_argv)
        # script will now re-execute with new hash seed

    main()
