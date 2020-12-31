#!/usr/bin/env python
"""
Common methods for panels of ncvue.

Methods normally belong to a class and be called like self.method(args).
We have several panels in ncvue that would have the same methods such as
getting slices from arrays. These are hence gathered here, all start with
the first argument self, which is the class instance, and are called like
method(self, args).

The methods could also be put onto a common class (based on ttk.Frame) on
which ncvContour, etc. would then be based.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* Slice arrays with slice function rather than numpy.take,
  Dec 2020, Matthias Cuntz
* Moved individual get_slice_? methods for x, y, y2, z as general get_slice
  function to ncvutils, Dec 2020, Matthias Cuntz
* Added convenience method get_slice_miss, Dec 2020, Matthias Cuntz

.. moduleauthor:: Matthias Cuntz

The following methods are provided:

.. autosummary::
   get_miss
   get_slice_miss
   set_dim_x
   set_dim_y
   set_dim_y2
   set_dim_z
   set_dim_zmap
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
import numpy as np
from .ncvutils import get_slice, set_miss, spinbox_values
import netCDF4 as nc
# nc.default_fillvals but with keys as variables['var'].dtype
nctypes = [ np.dtype(i) for i in nc.default_fillvals ]
ncfill  = dict(zip(nctypes, list(nc.default_fillvals.values())))
ncfill.update({np.dtype('O'): np.nan})


__all__ = ['get_miss', 'get_slice_miss',
           'set_dim_x', 'set_dim_y', 'set_dim_y2',
           'set_dim_z', 'set_dim_zmap']


#
# Get list of missing values
#

def get_miss(self, x):
    """
    Get list of missing values, i.e. self.miss, x._FillValue,
    x.missing_value, and from netcdf4.default_fillvals.

    Parameters
    ----------
    self : class
        ncvue class
    x : netCDF4._netCDF4.Variable
        netcdf variable

    Returns
    -------
    list
        List with missing values self.miss, x._FillValue,
        x.missing_value if present,  and from netcdf4.default_fillvals

    Examples
    --------
    >>> x = fi.variables['time']
    >>> miss = get_miss(self, x)
    """
    out = [ncfill[x.dtype]]
    try:
        out += [self.miss]
    except AttributeError:
        pass
    try:
        out += [x._FillValue]
    except AttributeError:
        pass
    try:
        out += [x.missing_value]
    except AttributeError:
        pass
    return out


#
# Get slice and set missing value
#

def get_slice_miss(self, dimspins, x):
    """
    Convenience method to get list of missing values (get_miss),
    choose slice of array (get_slice), and set missing values to
    NaN in slice (set_miss).

    Parameters
    ----------
    self : class
        ncvue class
    dimspins : list
        List of tk.Spinbox widgets of dimensions
    x : netCDF4._netCDF4.Variable
        netcdf variable

    Returns
    -------
    ndarray
        Extracted array slice with missing values set to np.NaN

    Examples
    --------
    >>> x = fi.variables['time']
    >>> xx = get_slice_miss(self, x)
    """
    miss = get_miss(self, x)
    xx   = get_slice(dimspins, x).squeeze()
    xx   = set_miss(miss, xx)
    return xx


#
# Set dimensions
#

def set_dim_x(self):
    """
    Set spinboxes of x-dimensions.

    Set labels and value lists, including 'all' to select all entries,
    as well as 'mean', 'std', etc. for common operations on the axis.

    Select 'all' for the unlimited dimension if it exists, otherwise
    for the first dimension, and select 0 for all other dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of x-dimensions set.

    Examples
    --------
    >>> set_dim_x(self)
    """
    # reset dimensions
    for i in range(self.maxdim):
        self.xd[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.xdlbl[i].set(str(i))
    x = self.x.get()
    if x != '':
        # set real dimensions
        vx = x.split()[0]
        if vx == self.tname:
            vx = self.tvar
        xx = self.fi.variables[vx]
        nall = 0
        if self.dunlim in xx.dimensions:
            i = xx.dimensions.index(self.dunlim)
            ww = max(5, int(np.ceil(np.log10(xx.shape[i]))))  # 5~median
            self.xd[i].config(values=spinbox_values(xx.shape[i]), width=ww,
                              state=tk.NORMAL)
            nall += 1
            self.xdval[i].set('all')
            self.xdlbl[i].set(xx.dimensions[i])
        for i in range(xx.ndim):
            if xx.dimensions[i] != self.dunlim:
                ww = max(5, int(np.ceil(np.log10(xx.shape[i]))))
                self.xd[i].config(values=spinbox_values(xx.shape[i]), width=ww,
                                  state=tk.NORMAL)
                if (nall == 0) and (xx.shape[i] > 1):
                    nall += 1
                    self.xdval[i].set('all')
                else:
                    self.xdval[i].set(0)
                self.xdlbl[i].set(xx.dimensions[i])


def set_dim_y(self):
    """
    Set spinboxes of y-dimensions of the left-hand-side (lhs).

    Set labels and value lists, including 'all' to select all entries,
    as well as 'mean', 'std', etc. for common operations on the axis.

    Select 'all' for the unlimited dimension if it exists, otherwise
    for the first dimension, and select 0 for all other dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of lhs y-dimensions set.

    Examples
    --------
    >>> set_dim_y(self)
    """
    # reset dimensions
    for i in range(self.maxdim):
        self.yd[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.ydlbl[i].set(str(i))
    y = self.y.get()
    if y != '':
        # set real dimensions
        vy = y.split()[0]
        if vy == self.tname:
            vy = self.tvar
        yy = self.fi.variables[vy]
        nall = 0
        if self.dunlim in yy.dimensions:
            i = yy.dimensions.index(self.dunlim)
            ww = max(5, int(np.ceil(np.log10(yy.shape[i]))))  # 5~median
            self.yd[i].config(values=spinbox_values(yy.shape[i]), width=ww,
                              state=tk.NORMAL)
            nall += 1
            self.ydval[i].set('all')
            self.ydlbl[i].set(yy.dimensions[i])
        for i in range(yy.ndim):
            if yy.dimensions[i] != self.dunlim:
                ww = max(5, int(np.ceil(np.log10(yy.shape[i]))))
                self.yd[i].config(values=spinbox_values(yy.shape[i]), width=ww,
                                  state=tk.NORMAL)
                if (nall == 0) and (yy.shape[i] > 1):
                    nall += 1
                    self.ydval[i].set('all')
                else:
                    self.ydval[i].set(0)
                self.ydlbl[i].set(yy.dimensions[i])


def set_dim_y2(self):
    """
    Set spinboxes of y2-dimensions of the right-hand-side (rhs).

    Set labels and value lists, including 'all' to select all entries,
    as well as 'mean', 'std', etc. for common operations on the axis.

    Select 'all' for the unlimited dimension if it exists, otherwise
    for the first dimension, and select 0 for all other dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of rhs y-dimensions set.

    Examples
    --------
    >>> set_dim_y2(self)
    """
    # reset dimensions
    for i in range(self.maxdim):
        self.y2d[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.y2dlbl[i].set(str(i))
    y2 = self.y2.get()
    if y2 != '':
        # set real dimensions
        vy2 = y2.split()[0]
        if vy2 == self.tname:
            vy2 = self.tvar
        yy2 = self.fi.variables[vy2]
        nall = 0
        if self.dunlim in yy2.dimensions:
            i = yy2.dimensions.index(self.dunlim)
            ww = max(5, int(np.ceil(np.log10(yy2.shape[i]))))  # 5~median
            self.y2d[i].config(values=spinbox_values(yy2.shape[i]), width=ww,
                               state=tk.NORMAL)
            nall += 1
            self.y2dval[i].set('all')
            self.y2dlbl[i].set(yy2.dimensions[i])
        for i in range(yy2.ndim):
            if yy2.dimensions[i] != self.dunlim:
                ww = max(5, int(np.ceil(np.log10(yy2.shape[i]))))
                self.y2d[i].config(values=spinbox_values(yy2.shape[i]),
                                   width=ww, state=tk.NORMAL)
                if (nall == 0) and (yy2.shape[i] > 1):
                    nall += 1
                    self.y2dval[i].set('all')
                else:
                    self.y2dval[i].set(0)
                self.y2dlbl[i].set(yy2.dimensions[i])


def set_dim_z(self):
    """
    Set spinboxes of z-dimensions.

    Set labels and value lists, including 'all' to select all entries,
    as well as 'mean', 'std', etc. for common operations on the axis.

    Select 'all' for the unlimited dimension if it exists, otherwise
    for the first dimension, as well as for a second dimension and select
    0 for all other dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of z-dimensions set.

    Examples
    --------
    >>> set_dim_z(self)
    """
    # reset dimensions
    for i in range(self.maxdim):
        self.zd[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.zdlbl[i].set(str(i))
    z = self.z.get()
    if z != '':
        # set real dimensions
        vz = z.split()[0]
        if vz == self.tname:
            vz = self.tvar
        zz = self.fi.variables[vz]
        nall = 0
        if self.dunlim in zz.dimensions:
            i = zz.dimensions.index(self.dunlim)
            ww = max(5, int(np.ceil(np.log10(zz.shape[i]))))  # 5~median
            self.zd[i].config(values=spinbox_values(zz.shape[i]), width=ww,
                              state=tk.NORMAL)
            nall += 1
            self.zdval[i].set('all')
            self.zdlbl[i].set(zz.dimensions[i])
        for i in range(zz.ndim):
            if zz.dimensions[i] != self.dunlim:
                ww = max(5, int(np.ceil(np.log10(zz.shape[i]))))
                self.zd[i].config(values=spinbox_values(zz.shape[i]), width=ww,
                                  state=tk.NORMAL)
                if (nall <= 1) and (zz.shape[i] > 1):
                    nall += 1
                    self.zdval[i].set('all')
                else:
                    self.zdval[i].set(0)
                self.zdlbl[i].set(zz.dimensions[i])


def set_dim_zmap(self):
    """
    Set spinboxes of z-dimensions in Map panel.

    Set labels and value lists, including 'all' to select all entries,
    as well as 'mean', 'std', etc. for common operations on the axis.

    Select 'all' for the first two limited dimensions and select
    0 for all other dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of z-dimensions set.

    Examples
    --------
    >>> set_dim_zmap(self)
    """
    # reset dimensions
    for i in range(self.maxdim):
        self.zd[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.zdlbl[i].set(str(i))
    z = self.z.get()
    if z != '':
        # set real dimensions
        vz = z.split()[0]
        if vz == self.tname:
            vz = self.tvar
        zz = self.fi.variables[vz]
        nall = 0
        for i in range(zz.ndim):
            ww = max(5, int(np.ceil(np.log10(zz.shape[i]))))  # 5~median
            self.zd[i].config(values=spinbox_values(zz.shape[i]), width=ww,
                              state=tk.NORMAL)
            if ((zz.dimensions[i] != self.dunlim) and (nall <= 1) and
                (zz.shape[i] > 1)):
                nall += 1
                self.zdval[i].set('all')
            else:
                self.zdval[i].set(0)
            self.zdlbl[i].set(zz.dimensions[i])
