#!/usr/bin/env python
"""
Purpose
=======

ncvue is a minimal GUI for a quick view of netcdf files.
It is aiming to be a drop-in replacement for ncview,
being slightly more general than ncview, which targets maps.

:copyright: Copyright 2020 Matthias Cuntz, see AUTHORS.md for details.
:license: MIT License, see LICENSE for details.

Subpackages
===========
.. autosummary::
    version
"""
from __future__ import division, absolute_import, print_function

from .version import __version__, __author__

# Function wrappers to be used with partial from functools
from .ncvuew import ncvue
