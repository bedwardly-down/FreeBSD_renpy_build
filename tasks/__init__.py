from renpybuild.context import Context
# The tasks to run, in order.

from . import cython

from . import env_sh

from . import toolchain
from . import sysroot

from . import nasm

from . import zlib
from . import bzip2
from . import xz
from . import brotli # keep this Ren'Py upstream version until this gets fully resolved altogether: https://github.com/urllib3/urllib3/pull/3136 (not an issue but URLLIB is a dependency and Brotli 1.1.0 will break Python 2.7 support

from . import openssl # keep an eye on this; upgraded from 1.1.1s to 3.2.0 without too many issues
from . import libffi

from . import libpng
from . import libjpeg_turbo # will need to micro upgrade this and do heavy testing if I do upgrade it; This can be one of the last upgrades
from . import libwebp

from . import libyuv
from . import aom
from . import libavif

from . import hostpython3
from . import hostpython2
from . import python2
from . import python3

from . import live2d

from . import sdl2 # this is gonna be a nightmare to upgrade
from . import sdl2_image

from . import ffmpeg

from . import fribidi
from . import freetype
from . import harfbuzz
from . import freetypehb

from . import zsync

from . import steam

from . import pygame_sdl2
from . import librenpy
from . import pythonlib
from . import renpython

from . import renpysh
