#!/usr/bin/env python
"""
Main ncvue window.

This sets up the main notebook window with the plotting panels and
analyses the netcdf file, e.g. determining the unlimited dimensions,
calculating dates, etc.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvMain

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Added check_new_netcdf method that re-initialises all panels if netcdf
     file changed, Jan 2021, Matthias Cuntz
   * Address fi.variables[name] directly by fi[name], Jan 2024, Matthias Cuntz
   * Allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * Allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * Use CustomTkinter if installed, Nov 2024, Matthias Cuntz
   * Have same tab order and only select Map if detected,
     Dec 2024, Matthias Cuntz

"""
import tkinter as tk
import tkinter.ttk as ttk
try:
    from customtkinter import CTkTabview as Frame
    ihavectk = True
except ModuleNotFoundError:
    from tkinter.ttk import Frame
    ihavectk = False
import numpy as np
from .ncvutils import vardim2var, selvar
from .ncvscatter import ncvScatter
from .ncvcontour import ncvContour
from .ncvmap import ncvMap

__all__ = ['ncvMain']


# --------------------------------------------------------------------
# Window with plot panels
#

class ncvMain(Frame):
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

        mapfirst = False
        if any(self.top.latvar):
            idx = [ i for i, l in enumerate(self.top.latvar) if l ]
            gl, vl = vardim2var(self.top.latvar[idx[0]],
                                self.top.groups)
            vv = selvar(self.top, vl)
            if np.prod(vv.shape) > 1:
                mapfirst = True
        if any(self.top.lonvar):
            idx = [ i for i, l in enumerate(self.top.lonvar) if l ]
            gl, vl = vardim2var(self.top.lonvar[idx[0]],
                                self.top.groups)
            vv = selvar(self.top, vl)
            if np.prod(vv.shape) > 1:
                mapfirst = True

        if ihavectk:  # self is CTkTabview
            stab = 'Scatter/Line'
            self.add(stab)
            istab = self.tab(stab)
            istab.name   = self.name
            istab.master = self.master
            istab.top    = self.top
            self.tab_scatter = ncvScatter(istab)
            self.tab_scatter.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            ctab = 'Contour'
            self.add(ctab)
            ictab = self.tab(ctab)
            ictab.name   = self.name
            ictab.master = self.master
            ictab.top    = self.top
            self.tab_contour = ncvContour(ictab)
            self.tab_contour.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            mtab = 'Map'
            self.add(mtab)
            imtab = self.tab(mtab)
            imtab.name   = self.name
            imtab.master = self.master
            imtab.top    = self.top
            self.tab_map = ncvMap(imtab)
            self.tab_map.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            if mapfirst:
                self.set("Map")

            # self.bind("<<NotebookTabChanged>>", self.check_new_netcdf)
            # self.bind("<Enter>", self.check_new_netcdf)
        else:
            # Notebook for tabs for future plot types
            self.tabs = ttk.Notebook(self)
            self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            self.tab_scatter = ncvScatter(self)
            self.tab_contour = ncvContour(self)
            self.tab_map     = ncvMap(self)

            self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
            self.tabs.add(self.tab_contour, text=self.tab_contour.name)
            self.tabs.add(self.tab_map, text=self.tab_map.name)

            if mapfirst:
                self.tabs.select(self.tab_map)

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
