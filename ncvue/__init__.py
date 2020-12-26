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

# helper functions
# open new window with panels
from .ncvclone   import clone_ncvmain
# contour panel
from .ncvcontour import ncvContour
# main window with panels
from .ncvmain    import ncvMain
# common methods of all panels
from .ncvmethods import get_miss
from .ncvmethods import get_slice_x, get_slice_y, get_slice_y2, get_slice_z
from .ncvmethods import set_dim_x, set_dim_y, set_dim_y2, set_dim_z
# scatter/line panel
from .ncvscatter import ncvScatter
# general helper function
from .ncvutils   import set_miss, spinbox_values, zip_dim_name_length
# adding widgets with labels, etc.
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_spinbox

# main calling program
from .ncvue import ncvue