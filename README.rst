Ren'Py Build
============

The purpose of the Ren'Py build system is to provide a single system that
can build the binary components of Ren'Py and all its dependencies, in
the same manner that is used to make official Ren'Py releases.

Requirements
-------------

**This entire process will globally change your system.**  It will install packages 
from the FreeBSD latest branch repository and will directly copy over and modify those 
copies of major system files. Have a solid backup system in place before running this 
if you're uncomfortable. 

Ren'Py Build requires a computer running FreeBSD 14.0+ (may support older 
releases for my fork but not sure yet due to not having the resources for 
fully testing them. While it can run on a desktop computer (I'm personally 
using an older laptop for writing and testing as we speak, portions of the 
build process must ran as root, and there are security implications to consider
there. My personal recommendation is to dedicate a bit of time to understand how
the system works, create a virtual machine (or on a backup system that's not your
daily driver, and install the latest patched version of FreeBSD-14.0 (or equivalent
minor version release) on it, and run from there.

Due to this primarily being used for building binary components for FreeBSD, the 
system requirements will vary based on how many different releases will be supported
and when custom builds will be needed for specific games or engine requirements on the
game developer's end of things. Setting up Ren'Py Build requires some FreeBSD/Linux 
knowledge to complete. In my personal opinion, it's not something most developers would 
need to directly use (the binaries will be provided for distribution for multiple Ren'py 
releases as new versions come out) but will remain open source and available.

I recommend dedicating a user to Ren'Py Build. In this example, I name the
user ``rb``, with a home directory of ``/home/rb``. Once that's done, you
will want to modify your computer so that user can use the ``sudo`` command
without a password. It's important that the username you chose does not have
a space in it.

That means first manually sudo-ing to root with the ``sudo -s`` command and
your user's password. Run the ``visudo`` command, and add the following line
to the bottom of the file:

    rb ALL = (ALL) NOPASSWD : ALL

Be sure to leave a blank line after it, then save the file with ctrl+X, and
use ``exit`` to get back to the non-root user. Note that this will allow
anyone who can log in as rb to become the superuser of this system.


Preparing
---------

To get ready to build, log in as the rb user, and then run the following
commands to instal git and clone renpy-build::

    sudo pkg install -y git
    git clone https://github.com/bedwardly-down/FreeBSD_renpy_build

Change into the renpy-build directory, install bash and run prepare.sh::

    cd ~/renpy-build
    sudo pkg install -y bash
    bash prepare.sh

This will first install all the packages required to build Ren'Py, and
then it will clone Ren'Py and pygame_sdl2. It will also create a python
virtual environment with the tools in it. If this completes successfully,
you are ready to build.

Third-Party Proprietary Downloads
---------------------------------

At this time, there is only one third-party proprietary that would need
to be downloaded and manually installed for the process to work. That 
would be the latest Live2D Cubism release (at the time of this writing 
is version Native5-R1. Grab it here https://www.live2d.com/en/download/cubism-sdk/ .
There currently is no way to build without it but it doesn't natively work on
FreeBSD. The header is the main required file.

You'll download it and place it in the `tmp/tars` folder (if it doesn't exist, create it)
and that's all that's needed.

Building
---------

You'll need to be in the renpy-build directory to build. If you're not, run::

    cd ~/renpy-build

From the renpy-build directory, activate the virtualenv with the command::

    source tmp/virtualenv.py3/bin/activate

It should then be possible to build using the command::

    ./build.py

The build command can take some options:

`--python <version>`
    The python version to build. Can be "3" or "2", defaults to 3.

`--platform <name>`
    The platform to build for. Only FreeBSD is targeted at this time, so this option
    is very optional.

`--arch <name>`
    The architecture to build for. Due to FreeBSD dropping support for 32-bit, arm and 
    several other architectures within the next few major releases, I will only be 
    currently supporting just 64-bit builds, so this is another completely optional 
    option. ::

        # Python 2

        Platform("freebsd", "x86_64", "2")

        # Python 3

        Platform("freebsd", "x86_64", "3")

    `--experimental`
        This builds platforms marked as experimental.

A second build should be faster than the first, as it will only rebuild
Ren'Py, pygame_sdl2, and other components that are likely to frequently
change.

Updating
---------

It's possible to change renpy or pygame_sdl2 to be symlinks to your own
clones of those projects after the prepare step is complete. Updating
renpy-build itself may require deleting the tmp/ directory and a complete
rebuild, though simple changes may not require that. You may also need to
run prepare.sh again.

Note
----

This port is not officially affiliated with or supported by the original 
Ren'py developer and will be receiving possibly heavy alterations from the 
original version (such as upgrading the build components to releases that FreeBSD 
recommends upstream, deprecating and replacing old patches, and altering the build
system scripts themselves). If you use this software, expect frequent changes from
time to time but it will remain mostly as stable as possible.
