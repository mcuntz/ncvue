#!/usr/bin/env python3
"""
Calling routine of ncvue.

The calling routine sets up the toplevel root window, opens the netcdf file
and gets an instance of the ncvMain class.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE),
Nancy, France.

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   ncvue

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Separate Tk() and Toplevel() widgets to communicate via Tk() between
     windows, Jan 2021, Matthias Cuntz
   * Set titlebar and taskbar icon only if "standalone" not in ipython or
     jupyter, May 2021, Matthias Cuntz
   * Different themes for different OS, May 2021, Matthias Cuntz
   * Font size 13 on Windows for plots, Jun 2021, Matthias Cuntz
   * Allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * Allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * Move themes/ and images/ directories from src/ncvue/ to src/ directory,
     Jan 2024, Matthias Cuntz
   * Move themes/ and images/ back to src/ncvue/, Feb 2024, Matthias Cuntz
   * Change formatting of file string for multiple files,
     Jul 2024, Matthias Cuntz
   * Use CustomTkinter if installed, Nov 2024, Matthias Cuntz
   * Use own ncvue-blue theme for customtkinter, Dec 2024, Matthias Cuntz
   * Include xarray to read input files, Feb 2025, Matthias Cuntz
   * Use ncvScreen for window sizes, Nov 2025, Matthias Cuntz
   * Use set_window_geometry from dfvScreen, Nov 2025, Matthias Cuntz

"""
import os
import platform
import sys
import tkinter as tk
import tkinter.ttk as ttk
try:
    import customtkinter
    from customtkinter import CTk as Tk
    from customtkinter import CTkToplevel as Toplevel
    ihavectk = True
except ModuleNotFoundError:
    from tkinter import Tk
    from tkinter import Toplevel
    ihavectk = False
try:
    import xarray as xr
    ihavex = True
except ModuleNotFoundError:
    ihavex = False
from matplotlib import pyplot as plt
import netCDF4 as nc
import numpy as np
from .ncvmethods import analyse_netcdf
from .ncvscreen import ncvScreen
from .ncvmain import ncvMain


__all__ = ['ncvue']


def ncvue(ncfile=[], miss=np.nan, usex=False):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    ncfile : list of str, optional
        Name of netcdf file (default: []).
    miss : float, optional
        Add value to list of missing values: _FillValue, missing_value,
        and the standard netCDF missing value for current datatype from
        netcdf4.default_fillvals (default: np.nan).
    usex : bool, optional
        If True, use xarray to read input files.
        Multiple input files will be read using xarray.open_mfdataset.

    """
    # print(mpl.get_backend())
    ios = platform.system()  # Windows, Darwin, Linux
    if ios == 'Windows':
        # make Windows aware of high resolution displays
        # https://stackoverflow.com/questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    # Pyinstaller sets _MEIPASS if macOS app
    bundle_dir = getattr(sys, '_MEIPASS',
                         os.path.abspath(os.path.dirname(__file__)))

    top = Tk()
    sc = ncvScreen(top)
    top.withdraw()
    # top.option_add("*Font", "Helvetica 10")

    # Check light/dark mode
    # https://stackoverflow.com/questions/65294987/detect-os-dark-mode-in-python

    # style = ttk.Style()
    # print(style.theme_names(), style.theme_use())
    if ios == 'Darwin':
        theme = 'aqua'
        style = ttk.Style()
        try:
            style.theme_use(theme)
        except:
            pass
        # top.tk.call('source', bundle_dir + '/themes/azure-2.0/azure.tcl')
        # theme = 'light'  # light, dark
        # top.tk.call("set_theme", theme)
    elif ios == 'Windows':
        top.option_add("*Font", "Helvetica 10")
        plt.rc('font', size=13)
        # standard Windows themes
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista',
        #  'xpnative')
        # theme = 'vista'
        # style = ttk.Style()
        # style.theme_use(theme)

        # style packages
        # Download from https://sourceforge.net/projects/tcl-awthemes/
        # top.tk.call('lappend', 'auto_path',
        #             bundle_dir + '/themes/awthemes-10.3.2')
        # theme = 'awdark'  # 'awlight', 'awdark'
        # top.tk.call('package', 'require', theme)
        # style = ttk.Style()
        # style.theme_use(theme)

        # single file styles
        # 'azure' and 'azure-dark' v1.x, 'Breeze'
        # top.tk.call('source', bundle_dir + '/themes/breeze/breeze.tcl')
        # theme = 'Breeze'
        # top.tk.call('source', bundle_dir + '/themes/azure-1.3/azure.tcl')
        # theme = 'azure'
        # top.tk.call('source', bundle_dir +
        #             '/themes/azure-1.3/azure-dark.tcl')
        # theme = 'azure-dark'
        # style = ttk.Style()
        # style.theme_use(theme)

        # 'azure' v2.x, 'sun-valley', 'forest' of rdbende
        top.tk.call('source', bundle_dir + '/themes/azure-2.0/azure.tcl')
        # top.tk.call('source', bundle_dir +
        #             '/themes/sun-valley-1.0/sun-valley.tcl')
        theme = 'light'  # light, dark
        top.tk.call("set_theme", theme)
    elif ios == 'Linux':
        # standard Linux schemes
        # theme = 'clam'  # 'clam', 'alt', 'default', 'classic'
        # style = ttk.Style()
        # style.theme_use(theme)

        # 'azure' v2.x, 'sun-valley', 'forest' of rdbende
        top.tk.call('source', bundle_dir + '/themes/azure-2.0/azure.tcl')
        theme = 'light'  # light, dark
        top.tk.call("set_theme", theme)

    if ihavectk:
        # customtkinter.set_default_color_theme("blue")
        # customtkinter.set_default_color_theme("dark-blue")
        # customtkinter.set_default_color_theme("green")
        # customtkinter.set_default_color_theme(
        #     f'{bundle_dir}/themes/customtkinter/dark-blue.json')
        customtkinter.set_default_color_theme(
            f'{bundle_dir}/themes/customtkinter/ncvue-blue.json')

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

    root = Toplevel()
    root.name = 'ncvOne'
    if len(ncfile) == 1:
        root.title("ncvue " + ncfile[0])
    else:
        root.title("ncvue")
    sc.set_window_geometry(root, sc.standard_window_size())
    # To make sure that it appears before any other window
    # https://github.com/TomSchimansky/CustomTkinter/issues/1517
    root.update()

    # Connect netcdf file and extracted information to top
    top.os     = ios     # operating system
    top.theme  = theme   # current theme
    top.icon   = icon    # app icon
    if ihavex:
        top.usex = usex   # use xarray
    else:
        top.usex = False  # use xarray
    top.fi     = []      # file name or file handle
    top.groups = []      # filename with increasing index or group names
    top.miss   = miss    # extra missing value
    top.dunlim = []      # name of unlimited dimension
    top.time   = []      # datetime variable
    top.tname  = []      # datetime variable name
    top.tvar   = []      # datetime variable name in netcdf file
    top.dtime  = []      # decimal year
    top.latvar = []      # name of latitude variable
    top.lonvar = []      # name of longitude variable
    top.latdim = []      # name of latitude dimension
    top.londim = []      # name of longitude dimension
    top.maxdim = 1       # maximum number of dimensions of all variables
                         # > 0 so that dimension spinboxes present
    top.cols   = []      # variable list

    if len(ncfile) > 0:
        if top.usex:
            if len(ncfile) > 1:
                top.fi = xr.open_mfdataset(ncfile)
            else:
                top.fi = xr.open_dataset(ncfile[0])
        else:
            for ii, nn in enumerate(ncfile):
                top.fi.append(nc.Dataset(nn, 'r'))
                if len(ncfile) > 1:
                    nnc = np.ceil(np.log10(len(ncfile))).astype(int)
                    top.groups.append(f'file{ii:0{nnc}d}')
            # Check groups
            if len(ncfile) == 1:
                top.groups = list(top.fi[0].groups.keys())
            else:
                for ii, nn in enumerate(ncfile):
                    if len(list(top.fi[ii].groups.keys())) > 0:
                        print(f'Either multiple files or one file with'
                              f' groups allowed as input. Multiple files'
                              f' given but file {nn} has groups.')
                        for fi in top.fi:
                            fi.close()
                        top.quit()
                        top.destroy()
        # Analyse netcdf file
        analyse_netcdf(top)

    def on_closing():
        if top.usex:
            if top.fi:
                top.fi.close()
        else:
            if len(top.fi) > 0:
                for fi in top.fi:
                    fi.close()
        top.quit()
        top.destroy()

    root.top = top
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 1st plotting window
    main_frame = ncvMain(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    top.mainloop()
