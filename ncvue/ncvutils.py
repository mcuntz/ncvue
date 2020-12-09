#!/usr/bin/env python
"""
Utility functions for ncvue

Written  Matthias Cuntz, Nov-Dec 2020
"""
from __future__ import absolute_import, division, print_function
import numpy as np
import netCDF4 as nc
# nc.default_fillvals but with keys as variables['var'].dtype
nctypes = [ np.dtype(i) for i in nc.default_fillvals ]
ncfill  = dict(zip(nctypes, list(nc.default_fillvals.values())))
ncfill.update({np.dtype('O'): np.nan})


__all__ = ['get_miss', 'set_miss', 'spinbox_values',
           'zip_dim_name_length']


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
    Tuple for Spinbox values with 'all' before range(ndim) if ndim>1,
    otherwise single entry (0,)

    Parameters
    ----------
    ndim : int
        Size of dimension.

    Returns
    -------
    tuple
        (('all',) + tuple(range(ndim))) if ndim > 1
        (0,) else

    Examples
    --------
    >>> self.xd0.config(values=spinbox_values(xx.shape[0]))
    """
    if ndim > 1:
        return (('all',) + tuple(range(ndim)))
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
