from renpybuild.context import Context
from renpybuild.task import task

import os
import requests

@task(platforms="freebsd")
def download_freebsd_amd64_base(c: Context):

    url = "https://ftp.freebsd.org/pub/FreeBSD/releases/amd64/14.0-RELEASE/base.txz"
    dest = c.path("{{ tmp }}/tars/freebsd-amd64-14.0.0-base.tar.xz")

    if os.path.exists(dest) or c.arch != "x86_64": 
        return

    dest.parent.mkdir(parents=True, exist_ok=True)

    print("Downloading freebsd amd64 base")
   
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest.with_suffix(".tmp"), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                f.write(chunk)

    dest.with_suffix(".tmp").rename(dest)

@task(platforms="freebsd")
def download_freebsd_i386_base(c: Context):

    url = "https://ftp.freebsd.org/pub/FreeBSD/releases/i386/14.0-RELEASE/base.txz"
    dest = c.path("{{ tmp }}/tars/freebsd-i386-14.0.0-base.tar.xz")

    if os.path.exists(dest) or c.arch != "i686":
        return

    dest.parent.mkdir(parents=True, exist_ok=True)

    print("Downloading freebsd i386 base")
   
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest.with_suffix(".tmp"), "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                f.write(chunk)

    dest.with_suffix(".tmp").rename(dest)
