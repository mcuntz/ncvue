#!/usr/bin/env python
"""
Utility functions for ncvue.

The utility functions do not depend on the ncvue class.
Functions depending on the class are in ncvmethods.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* General get_slice function from individual methods for x, y, y2, z,
  Dec 2020, Matthias Cuntz
* Added arithmetics to apply on axis/dimensions such as mean, std, etc.,
  Dec 2020, Matthias Cuntz
* Added clone_ncvmain, removing its own module, Dec 2020, Matthias Cuntz

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   clone_ncvmain
   get_slice
   list_intersection
   set_axis_label
   set_miss
   spinbox_values
   zip_dim_name_length
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
import numpy as np


__all__ = ['clone_ncvmain', 'get_slice', 'list_intersection',
           'set_axis_label', 'set_miss', 'spinbox_values',
           'zip_dim_name_length']


def clone_ncvmain(widget, fi, miss):
    """
    Duplicate the main ncvue window.

    Parameters
    ----------
    widget : ncvue.ncvMain
        widget of ncvMain class.
    fi : netCDF4._netCDF4.Dataset
        netcdf dataset
    miss : float
        Additional value that will be set to np.nan in netcdf variables.

    Returns
    -------
    Another ncvue window will be created.

    Examples
    --------
    >>> self.newwin = ttk.Button(
    ...     self.rowwin, text="New Window",
    ...     command=partial(clone_ncvmain, self.master, self.fi, self.miss))
    """
    # parent = widget.nametowidget(widget.winfo_parent())
    if widget.name != 'ncvMain':
        print('clone_ncvmain failed. Widget should be ncvMain.')
        print('widget.name is: ', widget.name)
        import sys
        sys.exit()

    self = tk.Toplevel()
    self.name = 'ncvClone'
    self.title("Secondary ncvue window")
    self.geometry('1000x800')
    self.miss = miss

    # https://stackoverflow.com/questions/46505982/is-there-a-way-to-clone-a-tkinter-widget
    cls = widget.__class__
    clone = cls(fi, master=self, miss=miss)
    for key in widget.configure():
        if key != 'class':
            clone.configure({key: widget.cget(key)})

    return clone


def get_slice(dimspins, y):
    """
    Get slice of variable `y` inquiring the spinboxes `dimspins`.

    Parameters
    ----------
    dimspins : list
        List of tk.Spinbox widgets of dimensions
    y : ndarray
        numpy array

    Returns
    -------
    ndarray
        Slice of `y` chosen by with spinboxes.

    Examples
    --------
    >>> vy = y.split()[0]
    >>> yy = self.fi.variables[vy]
    >>> miss = get_miss(self, yy)
    >>> yy = get_slice_y(self.yd, yy).squeeze()
    >>> yy = set_miss(miss, yy)
    """
    methods = ['all',
               'mean', 'std',
               'min', 'max', 'ptp',
               'sum', 'median', 'var']
    dd = []
    ss = []
    for i in range(y.ndim):
        dim = dimspins[i].get()
        if dim in methods:
            s = slice(0, y.shape[i])
        else:
            idim = int(dim)
            s = slice(idim, idim+1)
        dd.append(dim)
        ss.append(s)
    if len(ss) > 0:
        methods = methods[1:]  # w/o 'all'
        imeth = list_intersection(dd, methods)
        if len(imeth) > 0:
            yout = y[tuple(ss)]
            ii = [ i for i, d in enumerate(dd) if d in imeth ]
            ii.reverse()  # last axis first
            for i in ii:
                if dd[i] == 'mean':
                    yout = np.ma.mean(yout, axis=i)
                elif dd[i] == 'std':
                    yout = np.ma.std(yout, axis=i)
                elif dd[i] == 'min':
                    yout = np.ma.min(yout, axis=i)
                elif dd[i] == 'max':
                    yout = np.ma.max(yout, axis=i)
                elif dd[i] == 'ptp':
                    yout = np.ma.ptp(yout, axis=i)
                elif dd[i] == 'sum':
                    yout = np.ma.sum(yout, axis=i)
                elif dd[i] == 'median':
                    yout = np.ma.median(yout, axis=i)
                elif dd[i] == 'var':
                    yout = np.ma.var(yout, axis=i)
            return yout
        else:
            return y[tuple(ss)]
    else:
        return np.array([], dtype=y.dtype)


def list_intersection(lst1, lst2):
    """
    Intersection of two lists.

    From:
    https://stackoverflow.com/questions/3697432/how-to-find-list-intersection
    Using list comprehension for small lists and set() method with builtin
    intersection for longer lists.

    Parameters
    ----------
    lst1, lst2 : list
        Python lists

    Returns
    -------
    list
        List with common elements in both input lists.

    Examples
    --------
    >>> lst1 = [ 4, 9, 1, 17, 11, 26, 28, 28, 26, 66, 91]
    >>> lst2 = [9, 9, 74, 21, 45, 11, 63]
    >>> print(Intersection(lst1, lst2))
    [9, 11]
    """
    if (len(lst1) > 10) or (len(lst2) > 10):
        return list(set(lst1).intersection(lst2))
    else:
        return [ ll for ll in lst1 if ll in lst2 ]


def set_axis_label(ncvar):
    """
    Set label plotting axis from name and unit of given variable
    `ncvar`.

    Parameters
    ----------
    ncvar : netCDF4._netCDF4.Variable
        netcdf variables class

    Returns
    -------
    str
        Label string: name (unit)

    Examples
    --------
    >>> ylab = set_axis_label(fi.variables['w_soil'])
    """
    try:
        lab = ncvar.long_name
    except AttributeError:
        try:
            lab = ncvar.standard_name
        except AttributeError:
            lab = ncvar.name
    try:
        lab += ' (' + ncvar.units + ')'
    except AttributeError:
        pass
    return lab


def set_miss(miss, x):
    """
    Set `x` to NaN for all values in miss.

    Parameters
    ----------
    miss : iterable
        values which shall be set to np.nan in `x`
    x : ndarray
        numpy array

    Returns
    -------
    ndarray
        `x` with all values set np.nan that are equal to any value in miss.

    Examples
    --------
    >>> x = fi.variables['time']
    >>> miss = get_miss(self, x)
    >>> x = set_miss(miss, x)
    """
    for mm in miss:
        x = np.where(x == mm, np.nan, x)
    return x


def spinbox_values(ndim):
    """
    Tuple for Spinbox values with 'all' before range(`ndim`) and
    'mean', 'std', etc. after range(`ndim`) if `ndim`>1,
    otherwise single entry (0,).

    Parameters
    ----------
    ndim : int
        Size of dimension.

    Returns
    -------
    tuple
        (('all',) + tuple(range(ndim)) + ('mean','std',...)) if ndim > 1
        (0,) else

    Examples
    --------
    >>> self.xd0.config(values=spinbox_values(xx.shape[0]))
    """
    if ndim > 1:
        methods = ('mean', 'std', 'min', 'max', 'ptp', 'sum', 'median', 'var')
        return (('all',) + tuple(range(ndim)) + methods)
    else:
        return (0,)


def zip_dim_name_length(ncvar):
    """
    Combines dimension names and length of netcdf variable in list of strings.

    Parameters
    ----------
    ncvar : netCDF4._netCDF4.Variable
        netcdf variables class

    Returns
    -------
    list
        List of dimension name and length in the form 'dim=len'.

    Examples
    --------
    >>> import netCDF4 as nc
    >>> ifile = 'test.nc'
    >>> fi = nc.Dataset(ifile, 'r')
    >>> w_soil = fi.variables['w_soil']
    >>> print(zip_dim_name_length(w_soil))
    ('ntime=17520', 'nsoil=30')
    """
    out = []
    for i in range(ncvar.ndim):
        out.append(ncvar.dimensions[i]+'='+str(ncvar.shape[i]))
    return out
