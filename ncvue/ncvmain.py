#!/usr/bin/env python
"""
Main ncvue window.

This sets up the main notebook window with the plotting panels and
analyses the netcdf file, e.g. determining the unlimited dimensions,
calculating dates, etc.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvMain
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
try:
    import tkinter.ttk as ttk
except Exception:
    import sys
    print('Using the themed widget set introduced in Tk 8.5.')
    print('Try to use mcview.py, which uses wxpython instead.')
    sys.exit()
import numpy as np
from .ncvutils   import vardim2var
from .ncvmethods import analyse_netcdf
from .ncvscatter import ncvScatter
from .ncvcontour import ncvContour
from .ncvmap     import ncvMap

__all__ = ['ncvMain']


# --------------------------------------------------------------------
# Window with plot panels
#

class ncvMain(ttk.Frame):
    """
    Main ncvue notebook window with the plotting panels.

    Sets up the notebook layout with the panels and analyses the netcdf file,
    e.g. determining the unlimited dimensions, calculating dates, etc. in
    __init__.

    Contains the method to analyse the netcdf file.
    """

    #
    # Window setup
    #

    def __init__(self, fi, master=None, miss=np.nan, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=1)

        self.name   = 'ncvMain'
        self.fi     = fi      # netcdf file
        self.master = master  # master window = root
        self.root   = master  # root window
        self.miss   = master.miss
        self.dunlim = ''      # name of unlimited dimension
        self.time   = None    # datetime variable
        self.tname  = ''      # datetime variable name
        self.tvar   = ''      # datetime variable name in netcdf file
        self.dtime  = None    # decimal year
        self.latvar = ''      # name of latitude variable
        self.lonvar = ''      # name of longitude variable
        self.latdim = ''      # name of latitude dimension
        self.londim = ''      # name of longitude dimension
        self.maxdim = 0       # maximum number of dimensions of all variables
        self.cols   = []      # variable list

        # Analyse netcdf file
        analyse_netcdf(self)

        # Notebook for tabs for future plot types
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tab_scatter = ncvScatter(self)
        self.tab_contour = ncvContour(self)
        self.tab_map     = ncvMap(self)

        mapfirst = False
        if self.latvar:
            vl = vardim2var(self.latvar)
            if np.prod(self.fi.variables[vl].shape) > 1:
                mapfirst = True
        if self.lonvar:
            vl = vardim2var(self.lonvar)
            if np.prod(self.fi.variables[vl].shape) > 1:
                mapfirst = True

        if mapfirst:
            self.tabs.add(self.tab_map, text=self.tab_map.name)
        self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
        self.tabs.add(self.tab_contour, text=self.tab_contour.name)
        if not mapfirst:
            self.tabs.add(self.tab_map, text=self.tab_map.name)
