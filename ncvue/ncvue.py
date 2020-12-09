#!/usr/bin/env python
"""
Calling routine ncvue.

Written  Matthias Cuntz, Nov-Dec 2020
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
