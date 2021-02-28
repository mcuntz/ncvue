#!/usr/bin/env python
"""
Utility functions for ncvue.

The utility functions do not depend on the ncvue class.
Functions depending on the class are in ncvmethods.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* General get_slice function from individual methods for x, y, y2, z,
  Dec 2020, Matthias Cuntz
* Added arithmetics to apply on axis/dimensions such as mean, std, etc.,
  Dec 2020, Matthias Cuntz
* Added clone_ncvmain, removing its own module, Dec 2020, Matthias Cuntz
* added SEPCHAR and DIMMETHODS, Jan 2021, Matthias Cuntz
* pass only ncvMain widget to clone_ncvmain, Jan 2021, Matthias Cuntz
* pass only root widget to clone_ncvmain, Jan 2021, Matthias Cuntz

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   DIMMETHODS
   SEPCHAR
   add_cyclic_point
   clone_ncvmain
   get_slice
   list_intersection
   set_axis_label
   set_miss
   spinbox_values
   vardim2var
   zip_dim_name_length
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
import numpy as np


__all__ = ['DIMMETHODS', 'SEPCHAR',
           'add_cyclic_point', 'clone_ncvmain', 'get_slice',
           'list_intersection', 'set_axis_label', 'set_miss',
           'spinbox_values', 'vardim2var', 'zip_dim_name_length']


DIMMETHODS = ('mean', 'std', 'min', 'max', 'ptp', 'sum', 'median', 'var')
"""
Arithmetic methods implemented on dimensions.

mean - average
std - standard deviation
min - minimum
max - maximum
ptp - point-to-point amplitude = max - min
sum - sum
median - 50-percentile
var - variance
"""


SEPCHAR = chr(6)
"""
Invisible character to split strings.

ASCII character 6 = ACKNOWLEDGE (ACK)
"""


def add_cyclic_point(data, coord=None, rowcoord=None, axis=-1):
    """
    Add a cyclic point to an array and optionally a corresponding
    coordinate.

    Parameters
    ----------
    data : ndarray
        An n-dimensional array of data to add a cyclic point to.
    coord: ndarray, optional
        A 1- or 2-dimensional array which specifies the coordinate values for
        the dimension the cyclic point is to be added to. Defaults to None.

        If `coord` is given than add_cyclic_point checks if cyclic point is
        already present by checking `sin(coord[0]) == sin(coord[-1])`.
        No point is added if cyclic point was detected.

        Length of `coord` must be `data.shape[axis]` if 1-dimensional.

        `coord.shape[-1]` must be `data.shape[axis]` if 2-dimensional.
    rowcoord: ndarray, optional
        A 2-dimensional array with the variable of the row coordinate.
        The cyclic point simply copies the last column. Only considered if
        `coord` is 2-dimensional. Defaults to None.

        `rowcoord.shape[-1]` must be `data.shape[axis]`.
    axis: optional
        Specifies the axis of the data array to add the cyclic point to.
        Defaults to the right-most axis.

    Returns
    -------
    cyclic_data
        The data array with a cyclic point added.
    cyclic_coord
        The coordinate with a cyclic point, only returned if the `coord`
        keyword was supplied.
    cyclic_rowcoord
        The row coordinate with the last column duplicated, only returned
        if `coord` was 2-dimensional and the `lat` keyword was supplied.

    Examples
    --------
    Adding a cyclic point to a data array, where the cyclic dimension is
    the right-most dimension.
    .. testsetup::
        >>> from distutils.version import LooseVersion
        >>> import numpy as np
        >>> if LooseVersion(np.__version__) >= '1.14.0':
        ...     # To provide consistent doctests.
        ...     np.set_printoptions(legacy='1.13')
    >>> import numpy as np
    >>> data = np.ones([5, 6]) * np.arange(6)
    >>> cyclic_data = add_cyclic_point(data)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]

    Adding a cyclic point to a data array and an associated coordinate.
    >>> lons = np.arange(0, 360, 60)
    >>> cyclic_data, cyclic_lons = add_cyclic_point(data, coord=lons)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]
    >>> print(cyclic_lons)
    [  0  60 120 180 240 300 360]

    Adding a cyclic point to a data array and an associated 2-dimensional
    coordinate.
    >>> lons = np.arange(0, 360, 60)
    >>> lats = np.arange(-90, 90, 180/5)
    >>> lon2d, lat2d = np.meshgrid(lons, lats)
    >>> cyclic_data, cyclic_lon2d = add_cyclic_point(data, coord=lon2d)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]
    >>> print(cyclic_lon2d)
    [[  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]]

    Adding a cyclic point to a data array and an associated 2-dimensional
    coordinate and a second raw variable.
    >>> lons = np.arange(0, 360, 60)
    >>> lats = np.arange(-90, 90, 180/5)
    >>> lon2d, lat2d = np.meshgrid(lons, lats)
    >>> cyclic_data, cyclic_lon2d, cyclic_lat2d = add_cyclic_point(
    ...     data, coord=lon2d, rowcoord=lat2d)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]
    >>> print(cyclic_lon2d)
    [[  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]
     [  0  60 120 180 240 300 360]]
    >>> print(cyclic_lat2d)
    [[-90. -90. -90. -90. -90. -90. -90.]
     [-54. -54. -54. -54. -54. -54. -54.]
     [-18. -18. -18. -18. -18. -18. -18.]
     [ 18.  18.  18.  18.  18.  18.  18.]
     [ 54.  54.  54.  54.  54.  54.  54.]]

    Not adding a cyclic point if cyclic point detected in coord.
    >>> lons = np.arange(0, 361, 72)
    >>> lats = np.arange(-90, 90, 180/5)
    >>> lon2d, lat2d = np.meshgrid(lons, lats)
    >>> cyclic_data, cyclic_lon2d, cyclic_lat2d = add_cyclic_point(
    ...     data, coord=lon2d, rowcoord=lat2d)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5.]
     [ 0. 1. 2. 3. 4. 5.]
     [ 0. 1. 2. 3. 4. 5.]
     [ 0. 1. 2. 3. 4. 5.]
     [ 0. 1. 2. 3. 4. 5.]]
    >>> print(cyclic_lon2d)
    [[  0  72 144 216 288 360]
     [  0  72 144 216 288 360]
     [  0  72 144 216 288 360]
     [  0  72 144 216 288 360]
     [  0  72 144 216 288 360]]
    >>> print(cyclic_lat2d)
    [[-90. -90. -90. -90. -90. -90.]
     [-54. -54. -54. -54. -54. -54.]
     [-18. -18. -18. -18. -18. -18.]
     [ 18.  18.  18.  18.  18.  18.]
     [ 54.  54.  54.  54.  54.  54.]]
    """
    if coord is not None:
        if (coord.ndim < 1) or (coord.ndim > 2):
            estr = 'The coordinate must be 1- or 2-dimensional.'
            raise ValueError(estr)
        if (coord.ndim == 1):
            if len(coord) != data.shape[axis]:
                estr  = 'The length of the coordinate does not match'
                estr += ' the size of the corresponding dimension of'
                estr += ' the data array: len(coord) ='
                estr += ' {}, data.shape[{}] = {}.'.format(
                    len(coord), axis, data.shape[axis])
                raise ValueError(estr)
            # check if cyclic point already present
            # atol=1e-5 because coordinates often float32
            # and np.sin(np.deg2rad(np.float32(360.))) == 1.7484555e-07
            # add a bit of tolerance, e.g. cyclic points from rotated grid
            # I have seen differences of > 1e-5 in this case. Test is on
            # sine so that atol=1e-5 seems sufficient because 180/pi ~ 57.
            if np.ma.allclose(np.ma.sin(np.deg2rad(coord[0])),
                              np.ma.sin(np.deg2rad(coord[-1])),
                              atol=1.0e-5):
                if rowcoord is None:
                    return data, coord
                else:
                    return data, coord, rowcoord
            # # old code: must be equally spaced, adding diff
            # # delta_coord = np.diff(coord)
            # # if not np.allclose(delta_coord, delta_coord[0]):
            # #     raise ValueError('The coordinate must be equally spaced.')
            # # new_coord = ma.concatenate((coord,
            # #                             coord[-1:] + delta_coord[0]))
            # new code: just add 360 degree to first lon
            new_coord = np.ma.concatenate((coord, coord[0:1] + 360.))
        if (coord.ndim == 2):
            if coord.shape[-1] != data.shape[axis]:
                estr  = 'coord.shape[-1] does not match'
                estr += ' the size of the corresponding dimension of'
                estr += ' the data array: coord.shape[-1] ='
                estr += ' {}, data.shape[{}] = {}.'.format(
                    coord.shape[-1], axis, data.shape[axis])
                raise ValueError(estr)
            if rowcoord is not None:
                if not np.all(coord.shape == rowcoord.shape):
                    estr  = 'rowcoord.shape does not match'
                    estr += ' coord.shape: coord.shape[] =,'
                    estr += ' {}, rowcoord.shape = {}.'.format(
                        coord.shape, rowcoord.shape)
                    raise ValueError(estr)
            # check if cyclic point already present
            # atol=1e-5 see comment above
            if np.ma.allclose(np.ma.sin(np.deg2rad(coord[:, 0])),
                              np.ma.sin(np.deg2rad(coord[:, -1])),
                              atol=1.0e-5):
                if rowcoord is None:
                    return data, coord
                else:
                    return data, coord, rowcoord
            new_coord = np.ma.append(coord, coord[:, 0:1] + 360., axis=1)
            if rowcoord is not None:
                new_rowcoord = np.ma.append(rowcoord, rowcoord[:, -1:], axis=1)
    slicer = [slice(None)] * data.ndim
    try:
        slicer[axis] = slice(0, 1)
    except IndexError:
        estr = 'The specified axis does not correspond to an array dimension.'
        raise ValueError(estr)
    new_data = np.ma.concatenate((data, data[tuple(slicer)]), axis=axis)
    if coord is None:
        return new_data
    else:
        if (coord.ndim == 2) and (rowcoord is not None):
            return new_data, new_coord, new_rowcoord
        else:
            return new_data, new_coord


def clone_ncvmain(widget):
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
    ...     command=partial(clone_ncvmain, self.master))
    """
    # parent = widget.nametowidget(widget.winfo_parent())
    if widget.name != 'ncvMain':
        print('clone_ncvmain failed. Widget should be ncvMain.')
        print('widget.name is: ', widget.name)
        import sys
        sys.exit()

    root = tk.Toplevel()
    root.name = 'ncvClone'
    root.title("Secondary ncvue window")
    root.geometry('1000x800+150+100')

    root.top = widget.top

    # https://stackoverflow.com/questions/46505982/is-there-a-way-to-clone-a-tkinter-widget
    cls = widget.__class__
    clone = cls(root)
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
    y : ndarray or netCDF4._netCDF4.Variable
        Input array or netcdf variable

    Returns
    -------
    ndarray
        Slice of `y` chosen by with spinboxes.

    Examples
    --------
    >>> vy = vardim2var(y)
    >>> yy = self.fi.variables[vy]
    >>> miss = get_miss(self, yy)
    >>> yy = get_slice_y(self.yd, yy).squeeze()
    >>> yy = set_miss(miss, yy)
    """
    methods = ['all']
    methods.extend(DIMMETHODS)
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
        imeth = list_intersection(dd, DIMMETHODS)
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
        return (('all',) + tuple(range(ndim)) + DIMMETHODS)
    else:
        return (0,)


def vardim2var(vardim):
    """
    Extract variable name from 'variable (dim1=ndim1,)' string.

    Parameters
    ----------
    vardim : string
        Variable name with dimensions, such as 'latitude (lat=32,lon=64)'.

    Returns
    -------
    string
        Variable name.

    Examples
    --------
    >>> vardim2var('latitude (lat=32,lon=64)')
    latitude
    """
    return vardim.split(SEPCHAR)[0].rstrip()


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
