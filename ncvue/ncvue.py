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

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   ncvue
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
import numpy as np
import netCDF4 as nc
from .ncvmain import ncvMain


__all__ = ['ncvue']


def ncvue(ncfile, miss=np.nan):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    ncfile : str
        Name of netcdf file.
    miss : float, optional
        Add value to list of missing values: _FillValue, missing_value,
        and the standard netCDF missing value for current datatype from
        netcdf4.default_fillvals.
    """
    fi = nc.Dataset(ncfile, 'r')

    root = tk.Tk()
    root.name = 'root'
    root.title("ncvue "+ncfile)
    root.geometry('1000x800+100+100')
    root.miss = miss

    # 1st plotting window
    main_frame = ncvMain(fi, master=root)

    root.mainloop()

    fi.close()
