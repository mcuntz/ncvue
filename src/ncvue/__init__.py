#!/usr/bin/env python
"""
Purpose
-------

ncvue is a minimal GUI for a quick view of netcdf files.
It is aiming to be a drop-in replacement for ncview and panoply,
being slightly more general than ncview targeting maps but providing
animations, zooming and panning capabilities unlike panoply.

:copyright: Copyright 2020- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

Subpackages
-----------
.. autosummary::
   ncvcontour
   ncvmain
   ncvmap
   ncvmethods
   ncvscatter
   ncvscreen
   ncvue
   ncvutils
   ncvwidgets

History
   * Written Nov 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * v1.0, initial PyPI commit, Nov 2020, Matthias Cuntz
   * v1.1, modularised, having utilities and panels in individual files,
     Dec 2020, Matthias Cuntz
   * v1.2, Make lists of spinbox labels and values, outsource common methods,
     Dec 2020, Matthias Cuntz
   * v1.3, fix colorbar and gridlines in contour, invert x in scatter,
     Dec 2020, Matthias Cuntz
   * v1.4, Read only slice from disk, respect unlimited dimension,
     visual colorbar chooser, Dec 2020, Matthias Cuntz
   * v2.0, Added map panel, Jan 2021, Matthias Cuntz
   * v3.0, First version to be tested elsewhere, documentation on Github
     Pages, allow spaces in variable names, bug fixes,
     Jan 2021, Matthias Cuntz
   * v3.1, Include png files in ncvue/images in PyPI wheel,
     Jan 2021, Matthias Cuntz
   * v3.2, Open netcdf files from within ncvue, Jan 2021, Matthias Cuntz
   * v3.3, Standalone apps for macOS and Windows, Feb 2021, Matthias Cuntz
   * v3.3.1, Better installation instructions, Feb 2021, Matthias Cuntz
   * v3.4, Print values, draw grid lines in contour, May 2021, Matthias Cuntz
   * v3.5, Uses different themes on different OS, Jun 2021, Matthias Cuntz
   * v3.5.1, Explicitly set labelling of second y-axis to the right,
     Jun 2021, Matthias Cuntz
   * v3.6, standalone with cx_Freeze, separate units with space,
     Jun 2021, Matthias Cuntz
   * v3.7, new themes from rdbende on Linux and Windows,
     Sep 2021, Matthias Cuntz
   * v3.8, Better detection of lon/lat and working without them,
     Oct 2021, Matthias Cuntz
   * v4.0, pyproject.toml, src layout, and Github actions,
     Oct 2021, Matthias Cuntz
   * v4.1, final add_cyclic and has_cyclic as committed to cartopy,
     Nov 2021, Matthias Cuntz
   * v4.1.2, ncvue is gui_script entry_point, Jun 2022, Matthias Cuntz
   * v4.2, allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * v4.3, allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * v4.4, Add borders, rivers, and lakes checkbuttons in map,
     Feb 2024, Matthias Cuntz
   * v4.4.1 Move themes and images back to src/ncvue, Feb 2024, Matthias Cuntz
   * v4.4.2 Use matplotlib.colormaps[name], Jul 2024, Matthias Cuntz
   * v4.4.3 Use draw_idle for faster animation, Jul 2024, Matthias Cuntz
   * v5.0 Use CustomTkinter if installed, Nov 2024, Matthias Cuntz
   * v5.1 make notarized standalone versions, Dec 2024, Matthias Cuntz
   * v6.0 Include xarray to read input files, Mar 2025, Matthias Cuntz
   * v6.1 macOS and Windows installers, Mar 2025, Matthias Cuntz
   * v6.2 Use screen size to determine window sizes, Nov 2025, Matthias Cuntz

"""
# helper functions
# copy from idle
from .tooltip import TooltipBase, OnHoverTooltipBase, Hovertip
# general helper function
from .ncvutils import DIMMETHODS
from .ncvutils import add_cyclic, has_cyclic, clone_ncvmain
from .ncvutils import format_coord_contour, format_coord_map
from .ncvutils import format_coord_scatter, get_slice
from .ncvutils import get_standard_name, get_units
from .ncvutils import list_intersection, selvar, set_axis_label, set_miss
from .ncvutils import spinbox_values, vardim2var
from .ncvutils import xzip_dim_name_length, zip_dim_name_length
# general helper function
from .ncvscreen import ncvScreen
#
# common methods of all panels
from .ncvmethods import analyse_netcdf, get_miss, get_slice_miss
from .ncvmethods import set_dim_lat, set_dim_lon, set_dim_var
from .ncvmethods import set_dim_x, set_dim_y, set_dim_y2, set_dim_z
#
# adding widgets with labels, etc.
from .ncvwidgets import Tooltip
from .ncvwidgets import add_button, add_checkbutton, add_combobox, add_entry
from .ncvwidgets import add_imagemenu, add_label, add_menu, add_scale
from .ncvwidgets import add_spinbox, add_tooltip
#
# scatter/line panel
from .ncvscatter import ncvScatter
# contour panel
from .ncvcontour import ncvContour
# map panel
from .ncvmap import ncvMap
# main window with panels
from .ncvmain import ncvMain
#
# main calling program
from .ncvue import ncvue
#
# version, author
try:
    from ._version import __version__
except ImportError:  # pragma: nocover
    # package is not installed
    __version__ = '0.0.0.dev0'
__author__  = 'Matthias Cuntz'


__all__ = ['TooltipBase', 'OnHoverTooltipBase', 'Hovertip',
           'DIMMETHODS',
           'add_cyclic', 'has_cyclic', 'clone_ncvmain',
           'format_coord_contour', 'format_coord_map',
           'format_coord_scatter', 'get_slice',
           'get_standard_name', 'get_units',
           'list_intersection', 'selvar', 'set_axis_label', 'set_miss',
           'spinbox_values', 'vardim2var',
           'xzip_dim_name_length', 'zip_dim_name_length',
           'ncvScreen',
           'analyse_netcdf', 'get_miss', 'get_slice_miss',
           'set_dim_lat', 'set_dim_lon', 'set_dim_var',
           'set_dim_x', 'set_dim_y', 'set_dim_y2', 'set_dim_z',
           'Tooltip',
           'add_button', 'add_checkbutton', 'add_combobox', 'add_entry',
           'add_imagemenu', 'add_label', 'add_menu', 'add_scale',
           'add_spinbox', 'add_tooltip',
           'ncvScatter',
           'ncvContour',
           'ncvMap',
           'ncvMain',
           'ncvue',
           ]
