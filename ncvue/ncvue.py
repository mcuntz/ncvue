#!/usr/bin/env python
"""
Calling routine of ncvue.

The calling routine sets up the toplevel root window, opens the netcdf file
and gets an instance of the ncvMain class.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* Separate Tk() and Toplevel() widgets to communicate via Tk() between windows,
  Jan 2021, Matthias Cuntz
* Set titlebar and taskbar icon only if "standalone" not in ipython or jupyter,
  May 2021, Matthias Cuntz
* Different themes for different OS, May 2021, Matthias Cuntz

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   ncvue
"""
from __future__ import absolute_import, division, print_function
import sys
import tkinter as tk
try:
    import tkinter.ttk as ttk
except Exception:
    print('Using the themed widget set introduced in Tk 8.5.')
    sys.exit()
import os
import platform
import numpy as np
import netCDF4 as nc
from .ncvmethods import analyse_netcdf
from .ncvmain import ncvMain


__all__ = ['ncvue']


def ncvue(ncfile='', miss=np.nan):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    ncfile : str, optional
        Name of netcdf file (default: '').
    miss : float, optional
        Add value to list of missing values: _FillValue, missing_value,
        and the standard netCDF missing value for current datatype from
        netcdf4.default_fillvals (default: np.nan).
    """
    ios = platform.system()  # Windows, Darwin, Linux
    if ios == 'Windows':
        # make Windows aware of high resolution displays
        # https://stackoverflow.com/questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    # if macOS app then _MEIPASS is set
    bundle_dir = getattr(sys, '_MEIPASS',
                         os.path.abspath(os.path.dirname(__file__)))

    top = tk.Tk()
    top.withdraw()
    # top.option_add("*Font", "Helvetica 10")

    # Check light/dark mode
    # https://stackoverflow.com/questions/65294987/detect-os-dark-mode-in-python

    # style = ttk.Style()
    # print(style.theme_names(), style.theme_use())
    if ios == 'Darwin':
        theme = 'aqua'
    elif ios == 'Windows':
        # # style packages
        # # top.tk.call('lappend', 'auto_path',
        # #             bundle_dir + '/themes/awthemes-10.3.0')
        # # theme = 'awlight'  # 'awlight', 'awdark'
        # # top.tk.call('package', 'require', theme)

        # single file styles
        # top.tk.call('source', bundle_dir + '/themes/breeze/breeze.tcl')
        top.tk.call('source', bundle_dir + '/themes/azure/azure.tcl')
        # top.tk.call('source', bundle_dir + '/themes/azure/azure-dark.tcl')
        theme = 'azure'  # 'azure', 'azure-dark', 'Breeze'
    elif ios == 'Linux':
        theme = 'clam'  # 'clam', 'alt', 'default', 'classic'
    style = ttk.Style()
    style.theme_use(theme)

    # set titlebar and taskbar icon only if "standalone",
    # i.e. not ipython or jupyter
    try:
        whichpy = get_ipython().__class__.__name__
    except NameError:
        whichpy = ''
    if not whichpy:
        icon = tk.PhotoImage(file=bundle_dir + '/images/ncvue_icon.png')
        top.iconphoto(True, icon)  # True: apply to all future toplevels
    else:
        icon = None

    root = tk.Toplevel()
    root.name = 'ncvOne'
    root.title("ncvue " + ncfile)
    root.geometry('1000x800+100+100')

    # Connect netcdf file and extracted information to top
    top.os     = ios     # operating system
    top.theme  = theme   # current theme
    top.icon   = icon    # app icon
    top.fi     = ncfile  # file name or file handle
    top.miss   = miss    # extra missing value
    top.dunlim = ''      # name of unlimited dimension
    top.time   = None    # datetime variable
    top.tname  = ''      # datetime variable name
    top.tvar   = ''      # datetime variable name in netcdf file
    top.dtime  = None    # decimal year
    top.latvar = ''      # name of latitude variable
    top.lonvar = ''      # name of longitude variable
    top.latdim = ''      # name of latitude dimension
    top.londim = ''      # name of longitude dimension
    top.maxdim = 1       # maximum number of dimensions of all variables
                         # > 0 so that dimension spinboxes present
    top.cols   = []      # variable list
    if ncfile:
        top.fi = nc.Dataset(ncfile, 'r')
        # Analyse netcdf file
        analyse_netcdf(top)
    root.top = top

    def on_closing():
        if top.fi:
            top.fi.close()
        top.quit()
        top.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 1st plotting window
    main_frame = ncvMain(root)

    top.mainloop()
