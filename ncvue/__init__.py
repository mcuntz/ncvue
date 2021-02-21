#!/usr/bin/env python
"""
Purpose
=======

ncvue is a minimal GUI for a quick view of netcdf files.
It is aiming to be a drop-in replacement for ncview and panoply,
being slightly more general than ncview targeting maps but providing
animations, zooming and panning capabilities unlike panoply.

:copyright: Copyright 2020 Matthias Cuntz, see AUTHORS.rst for details.
:license: MIT License, see LICENSE for details.
"""
from __future__ import division, absolute_import, print_function

from .version import __version__, __author__

# helper functions
# general helper function
from .ncvutils   import DIMMETHODS, SEPCHAR
from .ncvutils   import add_cyclic_point, clone_ncvmain, get_slice
from .ncvutils   import list_intersection, set_axis_label, set_miss
from .ncvutils   import spinbox_values, vardim2var, zip_dim_name_length

# common methods of all panels
from .ncvmethods import analyse_netcdf, get_miss, get_slice_miss
from .ncvmethods import set_dim_lat, set_dim_lon, set_dim_var
from .ncvmethods import set_dim_x, set_dim_y, set_dim_y2, set_dim_z

# adding widgets with labels, etc.
from .ncvwidgets import Tooltip
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_menu, add_scale, add_spinbox, add_tooltip

# scatter/line panel
from .ncvscatter import ncvScatter
# contour panel
from .ncvcontour import ncvContour
# map panel
from .ncvmap     import ncvMap
# main window with panels
from .ncvmain    import ncvMain

# main calling program
from .ncvue import ncvue
