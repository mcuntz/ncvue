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

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   ncvue
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
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

    top = tk.Tk()
    top.withdraw()

    root = tk.Toplevel()
    root.name = 'ncvOne'
    root.title("ncvue "+ncfile)
    root.geometry('1000x800+100+100')

    # Connect netcdf file and extracted information to top
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
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 1st plotting window
    main_frame = ncvMain(root)

    top.mainloop()
