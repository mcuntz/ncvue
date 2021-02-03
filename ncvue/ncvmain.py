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
* Added check_new_netcdf method that re-initialises all panels if netcdf file
  changed, Jan 2021, Matthias Cuntz

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
    sys.exit()
import numpy as np
from .ncvutils   import vardim2var
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

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=1)

        self.name   = 'ncvMain'
        self.master = master      # master window, i.e. root
        self.top    = master.top  # top window

        # Notebook for tabs for future plot types
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tab_scatter = ncvScatter(self)
        self.tab_contour = ncvContour(self)
        self.tab_map     = ncvMap(self)

        mapfirst = False
        if self.top.latvar:
            vl = vardim2var(self.top.latvar)
            if np.prod(self.top.fi.variables[vl].shape) > 1:
                mapfirst = True
        if self.top.lonvar:
            vl = vardim2var(self.top.lonvar)
            if np.prod(self.top.fi.variables[vl].shape) > 1:
                mapfirst = True

        if mapfirst:
            self.tabs.add(self.tab_map, text=self.tab_map.name)
        self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
        self.tabs.add(self.tab_contour, text=self.tab_contour.name)
        if not mapfirst:
            self.tabs.add(self.tab_map, text=self.tab_map.name)

        self.tabs.bind("<<NotebookTabChanged>>", self.check_new_netcdf)
        self.tabs.bind("<Enter>", self.check_new_netcdf)

    #
    # Methods
    #

    def check_new_netcdf(self, event):
        """
        Command called if notebook panel changed or mouse pointer enters a
        window. It checks if netcdf file was changed in any panel of any window
        and re-initialises all plot panels (of the current window).
        """
        if self.tab_scatter.top.fi != self.tab_scatter.fi:
            self.tab_scatter.reinit()
            self.tab_scatter.redraw()
        if self.tab_contour.top.fi != self.tab_contour.fi:
            self.tab_contour.reinit()
            self.tab_contour.redraw()
        if self.tab_map.top.fi != self.tab_map.fi:
            self.tab_map.reinit()
            self.tab_map.redraw()
