#!/usr/bin/env python
"""
Utility functions for ncvue.

The utility functions do not depend on the ncvue class.
Functions depending on the class are in ncvmethods.

Written  Matthias Cuntz, Nov-Dec 2020
"""
from __future__ import absolute_import, division, print_function
import numpy as np


__all__ = ['list_intersection', 'set_axis_label', 'set_miss',
           'spinbox_values', 'zip_dim_name_length']


def list_intersection(lst1, lst2):
    """
    Intersection of two lists.

    From: https://www.geeksforgeeks.org/python-intersection-two-lists/
    Method using set() with builtin intersection (their method 3).

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
    return list(set(lst1).intersection(lst2))


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


def set_miss(x, miss):
    """
    Set `x` to NaN for all values in miss.

    Parameters
    ----------
    x : ndarray
        numpy array
    miss : iterable
        values which shall be set to np.nan in `x`

    Returns
    -------
    ndarray
        `x` with all values set np.nan that are equal to any value in miss.

    Examples
    --------
    >>> x = fi.variables['time']
    >>> miss = get_miss(self, x)
    >>> x = set_miss(x, miss)
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
        return (('all',) + tuple(range(ndim)) + ('mean', 'std'))
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
