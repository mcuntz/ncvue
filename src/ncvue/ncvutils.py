#!/usr/bin/env python
"""
Utility functions for ncvue.

The utility functions do not depend on the ncvue class.
Functions depending on the class are in ncvmethods.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   DIMMETHODS
   add_cyclic
   clone_ncvmain
   format_coord_contour
   format_coord_map
   format_coord_scatter
   get_slice
   list_intersection
   set_axis_label
   set_miss
   spinbox_values
   vardim2var
   zip_dim_name_length

History
    * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
    * General get_slice function from individual methods for x, y, y2, z,
      Dec 2020, Matthias Cuntz
    * Added arithmetics to apply on axis/dimensions such as mean, std, etc.,
      Dec 2020, Matthias Cuntz
    * Added clone_ncvmain, removing its own module, Dec 2020, Matthias Cuntz
    * added SEPCHAR and DIMMETHODS, Jan 2021, Matthias Cuntz
    * pass only ncvMain widget to clone_ncvmain, Jan 2021, Matthias Cuntz
    * pass only root widget to clone_ncvmain, Jan 2021, Matthias Cuntz
    * set correct missing value for date variable in numpy's datetime64[ms]
      format May 2021, Matthias Cuntz
    * added format_coord functions for scatter, contour, and map,
      May 2021, Matthias Cuntz
    * replaced add_cyclic_point with add_cyclic as submitted to cartopy,
      Jun 2021, Matthias Cuntz
    * removed SEPCHAR, Jun 2021, Matthias Cuntz

"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
import numpy as np
import matplotlib.dates as mpld
import cartopy.crs as ccrs


__all__ = ['DIMMETHODS',
           'add_cyclic', 'clone_ncvmain',
           'format_coord_contour', 'format_coord_map', 'format_coord_scatter',
           'get_slice',
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


def _add_cyclic_data(data, axis=-1):
    """
    Add a cyclic point to a data array.

    Parameters
    ----------
    data : ndarray
        An n-dimensional array of data to add a cyclic point to.
    axis: int, optional
        Specifies the axis of the data array to add the cyclic point to.
        Defaults to the right-most axis.

    Returns
    -------
    The data array with a cyclic point added.

    """
    slicer = [slice(None)] * data.ndim
    try:
        slicer[axis] = slice(0, 1)
    except IndexError:
        estr = 'The specified axis does not correspond to an array dimension.'
        raise ValueError(estr)
    npc = np.ma if np.ma.is_masked(data) else np
    return npc.concatenate((data, data[tuple(slicer)]), axis=axis)


def _add_cyclic_lon(lon, axis=-1, cyclic=360):
    """
    Add a cyclic point to a longitude array.

    Parameters
    ----------
    lon: ndarray, optional
        An array which specifies the coordinate values for
        the dimension the cyclic point is to be added to.
    axis: int, optional
        Specifies the axis of the longitude array to add the cyclic point to.
        Defaults to the right-most axis.
    cyclic: float, optional
        Width of periodic domain (default: 360)

    Returns
    -------
    The coordinate `lon` with a cyclic point added.

    """
    npc = np.ma if np.ma.is_masked(lon) else np
    # get cyclic longitudes
    # clon is the code from basemap (addcyclic)
    # https://github.com/matplotlib/basemap/blob/master/lib/mpl_toolkits/basemap/__init__.py
    clon = (np.take(lon, [0], axis=axis) +
            cyclic * np.sign(np.diff(np.take(lon, [0, -1], axis=axis),
                                     axis=axis)))
    # basemap ensures that the values do not exceed cyclic
    # (next code line). We do not do this to deal with rotated grids that
    # might have values not exactly 0.
    #     clon = npc.where(clon <= cyclic, clon, np.mod(clon, cyclic))
    return npc.concatenate((lon, clon), axis=axis)


def _has_cyclic(lon, axis=-1, cyclic=360, prec=1e-4):
    """
    Check if longitudes already have a cyclic point.

    Checks all differences between the first and last
    longitudes along `axis` to be less than `prec`.

    Parameters
    ----------
    lon: ndarray, optional
        An array with the coordinate values to be checked for cyclic points.
    axis: int, optional
        Specifies the axis of the `lon` array to be checked.
        Defaults to the right-most axis.
    cyclic: float, optional
        Width of periodic domain (default: 360).
    prec: float, optional
        Maximal difference between first and last longitude to detect
        cyclic point (default: 1e-4).

    Returns
    -------
    True if a cyclic point was detected along the given axis,
    False otherwise.

    """
    npc = np.ma if np.ma.is_masked(lon) else np
    # transform to 0-cyclic, assuming e.g. -180 to 180 if any < 0
    lon1 = np.mod(npc.where(lon < 0, lon + cyclic, lon), cyclic)
    dd = np.diff(np.take(lon1, [0, -1], axis=axis), axis=axis)
    if npc.all(np.abs(dd) < prec):
        return True
    else:
        return False


def add_cyclic(data, coord=None, rowcoord=None, axis=-1,
               cyclic=360, prec=1e-4):
    """
    Add a cyclic point to an array and optionally corresponding
    column (`coord` ~ longitudes) and row coordinates
    (`rowcoord` ~ latitudes).

    The call is `add_cyclic(data[, coord[, rowcoord]])`.

    Checks all differences between the first and last
    coordinates along `axis` to be less than `prec`.

    Parameters
    ----------
    data : ndarray
        An n-dimensional array of data to add a cyclic point to.
    coord: ndarray, optional
        An n-dimensional array which specifies the coordinate values
        for the dimension the cyclic point is to be added to, i.e. normally the
        longitudes. Defaults to None.

        If `coord` is given than add_cyclic checks if a cyclic point is
        already present by checking all differences between the first and last
        coordinates to be less than `prec`.
        No point is added if a cyclic point was detected.

        `coord.shape[-1]` must be `data.shape[axis]` if coord is 1- or
        2-dimensional,
        `coord.shape[axis]` must be `data.shape[axis]` otherwise.
    rowcoord: ndarray, optional
        An n-dimensional array with the variable of the row
        coordinate, i.e. normally the latitudes.
        The cyclic point simply copies the last column. Defaults to None.

        `rowcoord.shape[-1]` must be `data.shape[axis]` if rowcoord is 1- or
        2-dimensional,
        `rowcoord.shape[axis]` must be `data.shape[axis]` otherwise.
    axis: int, optional
        Specifies the axis of the data array to add the cyclic point to,
        i.e. normally the longitudes. Defaults to the right-most axis.
    cyclic: int or float, optional
        Width of periodic domain (default: 360).
    prec: float, optional
        Maximal difference between first and last coordinate to detect
        cyclic point (default: 1e-4).

    Returns
    -------
    cyclic_data
        The data array with a cyclic point added.
    cyclic_coord
        The coordinate with a cyclic point, only returned if the `coord`
        keyword was supplied.
    cyclic_rowcoord
        The row coordinate with the last column duplicated, only returned
        if `coord` was 2- or n-dimensional and the `rowcoord` keyword was
        supplied.

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
    >>> cyclic_data = add_cyclic(data)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]

    Adding a cyclic point to a data array and an associated coordinate.
    >>> lons = np.arange(0, 360, 60)
    >>> cyclic_data, cyclic_lons = add_cyclic(data, coord=lons)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]
    >>> print(cyclic_lons)
    [   0.   60.  120.  180.  240.  300.  360.]

    Adding a cyclic point to a data array and an associated 2-dimensional
    coordinate.
    >>> lons = np.arange(0, 360, 60)
    >>> lats = np.arange(-90, 90, 180/5)
    >>> lon2d, lat2d = np.meshgrid(lons, lats)
    >>> cyclic_data, cyclic_lon2d = add_cyclic(data, coord=lon2d)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]
    >>> print(cyclic_lon2d)
    [[   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]]

    Adding a cyclic point to a data array and an associated 2-dimensional
    coordinate and a second raw variable.
    >>> lons = np.arange(0, 360, 60)
    >>> lats = np.arange(-90, 90, 180/5)
    >>> lon2d, lat2d = np.meshgrid(lons, lats)
    >>> cyclic_data, cyclic_lon2d, cyclic_lat2d = add_cyclic(
    ...     data, coord=lon2d, rowcoord=lat2d)
    >>> print(cyclic_data)  # doctest: +NORMALIZE_WHITESPACE
    [[ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]
     [ 0. 1. 2. 3. 4. 5. 0.]]
    >>> print(cyclic_lon2d)
    [[   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]
     [   0.   60.  120.  180.  240.  300.  360.]]
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
    >>> cyclic_data, cyclic_lon2d, cyclic_lat2d = add_cyclic(
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
    if coord is None:
        return _add_cyclic_data(data, axis=axis)
    else:
        if (coord.ndim > 2):
            caxis = axis
        else:
            caxis = -1
        if coord.shape[caxis] != data.shape[axis]:
            estr = 'coord.shape[{}] does not match'.format(caxis)
            estr += ' the size of the corresponding dimension of'
            estr += ' the data array: coord.shape[{}] ='.format(caxis)
            estr += ' {}, data.shape[{}] = {}.'.format(
                coord.shape[caxis], axis, data.shape[axis])
            raise ValueError(estr)
        if _has_cyclic(coord, axis=caxis, cyclic=cyclic, prec=prec):
            if rowcoord is None:
                return data, coord
            else:
                return data, coord, rowcoord
        else:
            odata = _add_cyclic_data(data, axis=axis)
            ocoord = _add_cyclic_lon(coord, axis=caxis, cyclic=cyclic)
            if rowcoord is None:
                return odata, ocoord
            else:
                if (rowcoord.ndim > 2):
                    raxis = axis
                else:
                    raxis = -1
                if rowcoord.shape[raxis] != data.shape[axis]:
                    estr = 'rowcoord.shape[{}] does not match'.format(raxis)
                    estr += ' the size of the corresponding dimension of'
                    estr += ' the data array: rowcoord.shape[{}] ='.format(
                        raxis)
                    estr += ' {}, data.shape[{}] = {}.'.format(
                        rowcoord.shape[raxis], axis, data.shape[axis])
                    raise ValueError(estr)
                orowcoord = _add_cyclic_data(rowcoord, axis=raxis)
                return odata, ocoord, orowcoord


def clone_ncvmain(widget):
    """
    Duplicate the main ncvue window.

    Parameters
    ----------
    widget : ncvue.ncvMain
        widget of ncvMain class.

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


def format_coord_contour(x, y, ax, xx, yy, zz):
    """
    Formatter function for contour plot including value of nearest array cell.

    Parameters
    ----------
    x, y : float
        Data coordinates of `ax`.
    ax: matplotlib.axes._subplots.AxesSubplot
        Matplotlib axes object for left-hand and right-hand y-axis, resp.
    xx, yy, zz: ndarray
        Numpy arrays with x-values, y-values, and z-values

    Returns
    -------
    String with coordinateds.

    Examples
    --------
    >>> ax = plt.subplot(111)
    >>> ax.pcolormesh(xx, yy, zz)
    >>> ax.format_coord = lambda x, y: format_coord_contour(
    ...     x, y, ax, xx, yy, zz)

    """
    # find closest grid cell
    # https://stackoverflow.com/questions/42577204/show-z-value-at-mouse-pointer-position-in-status-line-with-matplotlibs-pcolorme
    if xx.ndim > 1:
        xarr = xx[0, :]
    else:
        xarr = xx
    if xx.dtype == np.dtype('<M8[ms]'):
        xarr = mpld.date2num(xarr)
    if yy.ndim > 1:
        yarr = yy[:, 0]
    else:
        yarr = yy
    if yy.dtype == np.dtype('<M8[ms]'):
        yarr = mpld.date2num(yarr)
    if ((x > xarr.min()) & (x <= xarr.max()) &
        (y > yarr.min()) & (y <= yarr.max())):
        col = np.searchsorted(xarr, x) - 1
        row = np.searchsorted(yarr, y) - 1
        xout = xarr[col]
        yout = yarr[row]
        zout = zz[row, col]
    else:
        xout = x
        yout = y
        if zz.dtype == np.dtype('<M8[ms]'):
            zout = np.datetime64('NaT')
        else:
            zout = np.nan

    # Special treatment for datetime
    # https://stackoverflow.com/questions/49267011/matplotlib-datetime-from-event-coordinates
    if xx.dtype == np.dtype('<M8[ms]'):
        xstr = mpld.num2date(xout).strftime('%Y-%m-%d %H:%M:%S')
    else:
        xstr  = '{:.4g}'.format(xout)
    if yy.dtype == np.dtype('<M8[ms]'):
        ystr = mpld.num2date(yout).strftime('%Y-%m-%d %H:%M:%S')
    else:
        ystr  = '{:.4g}'.format(yout)
    if zz.dtype == np.dtype('<M8[ms]'):
        zstr = mpld.num2date(zout).strftime('%Y-%m-%d %H:%M:%S')
    else:
        zstr = '{:.4g}'.format(zout)
    out = 'x=' + xstr + ', y=' + ystr + ', z=' + zstr
    return out


def format_coord_map(x, y, ax, xx, yy, zz):
    """
    Formatter function for map including value of nearest array cell.

    Parameters
    ----------
    x, y : float
        Data coordinates of `ax`.
    ax: matplotlib.axes._subplots.AxesSubplot
        Matplotlib axes object for left-hand and right-hand y-axis, resp.
    xx, yy, zz: ndarray
        Numpy arrays with x-values, y-values, and z-values

    Returns
    -------
    String with coordinateds.

    Examples
    --------
    >>> ax = plt.subplot(111)
    >>> ax.pcolormesh(xx, yy, zz)
    >>> ax.format_coord = lambda x, y: format_coord_contour(
    ...     x, y, ax, xx, yy, zz)

    """
    # find closest grid cell
    xpp, ypp = ccrs.PlateCarree(central_longitude=0).transform_point(
        x, y, ax.projection)
    x360 = (xpp + 360.) % 360.
    y360 = ypp
    xx360 = (xx + 360.) % 360.
    yy360 = yy
    idx = np.abs((xx360 - x360)**2 + (yy360 - y360)**2).argmin()
    xout = xx.flat[idx]
    yout = yy.flat[idx]
    zout = zz.flat[idx]

    # from cartopy
    lon, lat = ccrs.Geodetic().transform_point(x, y, ax.projection)

    # xstr  = '{:.4g}'.format(xout)
    # ystr  = '{:.4g}'.format(yout)
    xstr  = '{:.4g}'.format(xout)
    ystr  = '{:.4g}'.format(yout)
    zstr  = '{:.4g}'.format(zout)
    ns = 'N' if lat >= 0. else 'S'
    ew = 'E' if lon >= 0. else 'W'
    latstr = u'{:.4f} \u00b0{:s}'.format(abs(lat), ns)
    lonstr = u'{:.4f} \u00b0{:s}'.format(abs(lon), ew)
    out  = u'x=' + xstr + ', y=' + ystr + ' (' + lonstr + ', ' + latstr + ')'
    out += ' z=' + zstr
    return out


def format_coord_scatter(x, y, ax, ax2, xdtype, ydtype, y2dtype):
    """
    Formatter function for scatter plot with left and right axis
    having the same x-axis.

    Parameters
    ----------
    x, y : float
        Data coordinates of `ax2`.
    ax, ax2: matplotlib.axes._subplots.AxesSubplot
        Matplotlib axes object for left-hand and right-hand y-axis, resp.
    xdtype, ydtype, y2dtype: numpy.dtype
        Numpy dtype of data of x-values (xdtype), left-hand side y-values
        (ydtype), and right-hand side y-values (y2dtype)

    Returns
    -------
    String with left-hand side and right hand-side coordinates.

    Examples
    --------
    >>> ax = plt.subplot(111)
    >>> ax2 = ax.twinx()
    >>> ax.plot(xx, yy)
    >>> ax2.plot(xx, yy2)
    >>> ax2.format_coord = lambda x, y: format_coord_scatter(
    ...     x, y, ax, ax2, xx.dtype, yy.dtype, yy2.dtype)

    """
    # convert to display coords
    # https://stackoverflow.com/questions/21583965/matplotlib-cursor-value-with-two-axes
    display_coord = ax2.transData.transform((x, y))
    # convert back to data coords with respect to ax
    inv      = ax.transData.inverted()
    ax_coord = inv.transform(display_coord)

    # Special treatment for datetime
    # https://stackoverflow.com/questions/49267011/matplotlib-datetime-from-event-coordinates
    if xdtype == np.dtype('<M8[ms]'):
        xstr = mpld.num2date(x).strftime('%Y-%m-%d %H:%M:%S')
    else:
        xstr  = '{:.3g}'.format(x)
    if ydtype == np.dtype('<M8[ms]'):
        ystr = mpld.num2date(ax_coord[1]).strftime('%Y-%m-%d %H:%M:%S')
    else:
        ystr  = '{:.3g}'.format(ax_coord[1])
    if y2dtype == np.dtype('<M8[ms]'):
        y2str = mpld.num2date(y).strftime('%Y-%m-%d %H:%M:%S')
    else:
        y2str = '{:.3g}'.format(y)
    out  = 'Left: (' + xstr + ', ' + ystr + ')'
    out += ' Right: (' + xstr + ', ' + y2str + ')'
    return out


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
    Set `x` to NaN or NaT for all values in miss.

    Parameters
    ----------
    miss : iterable
        values which shall be set to np.nan or np.datetime64('NaT') in `x`
    x : ndarray
        numpy array

    Returns
    -------
    ndarray
        `x` with all values set np.nan or np.datetime64('NaT')
        that are equal to any value in miss.

    Examples
    --------
    >>> x = fi.variables['time']
    >>> miss = get_miss(self, x)
    >>> x = set_miss(miss, x)

    """
    if x.dtype == np.dtype('<M8[ms]'):
        default = np.datetime64('NaT')
    else:
        default = np.nan
    for mm in miss:
        x = np.where(x == mm, default, x)
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
    return vardim[0:vardim.rfind('(')].rstrip()


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
