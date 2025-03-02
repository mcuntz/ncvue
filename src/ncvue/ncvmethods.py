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

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following methods are provided:

.. autosummary::
   analyse_netcdf
   get_miss
   get_slice_miss
   set_dim_lat
   set_dim_lon
   set_dim_var
   set_dim_x
   set_dim_y
   set_dim_y2
   set_dim_z

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Slice arrays with slice function rather than numpy.take,
     Dec 2020, Matthias Cuntz
   * Moved individual get_slice? methods for x, y, y2, z as general get_slice
     function to ncvutils, Dec 2020, Matthias Cuntz
   * Added convenience method get_slice_miss, Dec 2020, Matthias Cuntz
   * set_dim_lon, set_dim_lat, set_dim_var for Map panel,
     Jan 2021, Matthias Cuntz
   * Set latdim, londim to all on map var, determined in ncvMain,
     Jan 2021, Matthias Cuntz
   * Catch non numpy.dtype in set_miss, Jan 2021, Matthias Cuntz
   * Catch variables that have only one string or similar,
     Jan 2021, Matthias Cuntz
   * Added tooltip to dimensions, Jan 2021, Matthias Cuntz
   * Added analyse_netcdf from ncvmain, Jan 2021, Matthias Cuntz
   * Use dlblval instead of dlbl to set dimension labels,
     Jan 2021, Matthias Cuntz
   * Make self.time numpy's datetime64[ms] format, May 2021, Matthias Cuntz
   * Add numpy's datetime64[ms] to missing values, May 2021, Matthias Cuntz
   * Removed bug in detection of lon/lat (analyse_netcdf),
     Oct 2021, Matthias Cuntz
   * Identify lon/lat also by axis attributes x/y or X/Y (analyse_netcdf),
     Oct 2021, Matthias Cuntz
   * Do not default the unlimited dimension to 'all' if no lon/lat were found,
     (get_dim_var) Oct 2021, Matthias Cuntz
   * Address fi.variables[name] directly by fi[name], Jan 2024, Matthias Cuntz
   * Allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * Squeeze output in get_slice_miss only if more than 1 dim,
     Jan 2024, Matthias Cuntz
   * Allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * Rename analyse_netcdf to analyse_netcdf_xarray_ncvue,
     add new analyse_netcdf, Feb 2025, Matthias Cuntz
   * Use new get_standard_name and get_units from ncvutils,
     Feb 2025, Matthias Cuntz
   * Add analyse_netcdf_xarray, Feb 2025, Matthias Cuntz

"""
import tkinter as tk
import numpy as np
from .ncvutils import DIMMETHODS, get_slice, set_miss, spinbox_values
from .ncvutils import vardim2var, selvar
from .ncvutils import xzip_dim_name_length, zip_dim_name_length
from .ncvutils import get_standard_name, get_units
import netCDF4 as nc
# nc.default_fillvals but with keys as variables['var'].dtype
nctypes = [ np.dtype(i) for i in nc.default_fillvals ]
ncfill  = dict(zip(nctypes, list(nc.default_fillvals.values())))
ncfill.update({np.dtype('O'): np.nan})
ncfill.update({np.dtype('<M8[ms]'): np.datetime64('NaT')})
ncfill.update({np.dtype('<M8[ns]'): np.datetime64('NaT')})


__all__ = ['analyse_netcdf',
           'get_miss', 'get_slice_miss',
           'set_dim_lat', 'set_dim_lon', 'set_dim_var',
           'set_dim_x', 'set_dim_y', 'set_dim_y2', 'set_dim_z']


#
# Analyse netcdf file
#

def analyse_netcdf(self):
    """
    Call analyse_netcdf_xarray or analyse_netcdf_ncvue depending on self.usex

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    Set variables:
        self.dunlim,
        self.time, self.tname, self.tvar, self.dtime,
        self.cols,
        self.latvar, self.lonvar, self.latdim, self.londim

    Examples
    --------
    >>> analyse_netcdf(self)

    """
    if self.usex:
        analyse_netcdf_xarray(self)
    else:
        analyse_netcdf_ncvue(self)


def analyse_netcdf_ncvue(self):
    """
    Analyse netcdf file(s) for the unlimited dimension, calculating datetime,
    variables, latitudes/longitudes variables and dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    Set variables:
        self.dunlim,
        self.time, self.tname, self.tvar, self.dtime,
        self.cols,
        self.latvar, self.lonvar, self.latdim, self.londim

    Examples
    --------
    >>> analyse_netcdf(self)

    """
    import datetime as dt
    try:
        import cftime as cf
    except ModuleNotFoundError:
        import netCDF4 as cf
    #
    ngroups = len(self.groups)
    for ig in range(max(ngroups, 1)):
        if len(self.fi) == 1:
            if ngroups > 0:
                ffi = self.fi[0]
                fi = ffi[self.groups[ig]]
                gname = self.groups[ig] + '/'
            else:
                fi = self.fi[ig]
                gname = ''
        else:
            fi = self.fi[ig]
            gname = self.groups[ig] + '/'
        #
        # search unlimited dimension
        self.dunlim.append('')
        for dd in fi.dimensions:
            if fi.dimensions[dd].isunlimited():
                self.dunlim[ig] = dd
                break
        #
        # search for time variable and make datetime variable
        self.time.append(None)
        self.tname.append('')
        self.tvar.append('')
        self.dtime.append(None)
        for vv in fi.variables:
            isunlim = False
            if self.dunlim[ig]:
                if vv.lower() == fi.dimensions[self.dunlim[ig]].name.lower():
                    isunlim = True
            if ( isunlim or vv.lower().startswith('time_') or
                 (vv.lower() == 'time') or (vv.lower() == 'datetime') or
                 (vv.lower() == 'date') ):
                self.tvar[ig] = gname + vv
                if vv.lower() == 'datetime':
                    self.tname[ig] = gname + 'date'
                else:
                    self.tname[ig] = gname + 'datetime'
                try:
                    ivar = selvar(self, self.tvar[ig])
                    tunit = ivar.units
                except AttributeError:
                    tunit = ''
                # assure 01, etc. if values < 1000, 10, 10 in year, month, day
                if tunit.find('since') > 0:
                    tt = tunit.split()
                    dd = tt[2].split('-')
                    tt[2] = (f'{int(dd[0]):04d}-{int(dd[1]):02d}-'
                             f'{int(dd[2]):02d}')
                    tunit = ' '.join(tt)
                try:
                    ivar = selvar(self, self.tvar[ig])
                    tcal = ivar.calendar
                except AttributeError:
                    tcal = 'standard'
                ivar = selvar(self, self.tvar[ig])
                time = ivar[:]
                # time dimension "day as %Y%m%d.%f" from cdo.
                if ' as ' in tunit:
                    itunit = tunit.split()[2]
                    dtime = []
                    for tt in time:
                        stt = str(tt).split('.')
                        sstt = ('00' + stt[0])[-8:] + '.' + stt[1]
                        dtime.append(dt.datetime.strptime(sstt, itunit))
                    ntime = cf.date2num(dtime,
                                        'days since 0001-01-01 00:00:00')
                    self.dtime[ig] = cf.num2date(
                        ntime,
                        'days since 0001-01-01 00:00:00')
                else:
                    try:
                        self.dtime[ig] = cf.num2date(time, tunit,
                                                     calendar=tcal)
                    except ValueError:
                        self.dtime[ig] = None
                if self.dtime[ig] is not None:
                    ntime = len(self.dtime[ig])
                    if (tcal == '360_day'):
                        ndays = [360.] * ntime
                    elif (tcal == '365_day'):
                        ndays = [365.] * ntime
                    elif (tcal == 'noleap'):
                        ndays = [365.] * ntime
                    elif (tcal == '366_day'):
                        ndays = [366.] * ntime
                    elif (tcal == 'all_leap'):
                        ndays = [366.] * ntime
                    else:
                        ndays = [ 365. +
                                  float((((t.year % 4) == 0) &
                                         ((t.year % 100) != 0)) |
                                        ((t.year % 400) == 0))
                                  for t in self.dtime[ig] ]
                    self.dtime[ig] = np.array([
                        t.year +
                        (t.dayofyr - 1 + t.hour / 24. +
                         t.minute / 1440 + t.second / 86400.) / ndays[i]
                        for i, t in enumerate(self.dtime[ig]) ])
                # make datetime variable
                if self.time[ig] is None:
                    try:
                        ttime = cf.num2date(
                            time, tunit, calendar=tcal,
                            only_use_cftime_datetimes=False,
                            only_use_python_datetimes=True)
                        self.time[ig] = np.array([ dd.isoformat()
                                                   for dd in ttime ],
                                                 dtype='datetime64[ms]')
                    except:
                        self.time[ig] = None
                if self.time[ig] is None:
                    try:
                        ttime = cf.num2date(time, tunit,
                                            calendar=tcal)
                        self.time[ig] = np.array([ dd.isoformat()
                                                   for dd in ttime ],
                                                 dtype='datetime64[ms]')
                    except:
                        self.time[ig] = None
                if self.time[ig] is None:
                    # if not possible use decimal year
                    self.time[ig] = self.dtime[ig]
                if self.time[ig] is None:
                    # could not interpret time at all,
                    # e.g. if units = "months since ..."
                    self.time[ig] = time
                    self.dtime[ig] = time
                break
        #
        # construct list of variable names with dimensions
        if self.time[ig] is not None:
            ivar = selvar(self, self.tvar[ig])
            addt = [self.tname[ig] + ' ' +
                    str(tuple(zip_dim_name_length(ivar)))]
            self.cols += addt
        ivars = []
        for vv in fi.variables:
            vname = gname + vv
            ss = tuple(zip_dim_name_length(fi[vv]))
            self.maxdim = max(self.maxdim, len(ss))
            ivars.append((vname, ss, len(ss)))
        self.cols += sorted([ vv[0] + ' ' + str(vv[1])
                              for vv in ivars ])
        #
        # search for lat/lon variables
        self.latvar.append('')
        self.lonvar.append('')
        # first sweep: *name must be "latitude" and
        #              units must be "degrees_north"
        if not self.latvar[ig]:
            for vv in fi.variables:
                sname = get_standard_name(fi[vv])
                if sname.lower() == 'latitude':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees_north':
                        self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                sname = get_standard_name(fi[vv])
                if sname.lower() == 'longitude':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees_east':
                        self.lonvar[ig] = gname + vv
        # second sweep: name must start with lat and
        #               units must be "degrees_north"
        if not self.latvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                if sname[0:3].lower() == 'lat':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees_north':
                        self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                if sname[0:3].lower() == 'lon':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees_east':
                        self.lonvar[ig] = gname + vv
        # third sweep: name must contain lat and
        #              units must be "degrees_north"
        if not self.latvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                sname = sname.lower()
                if sname.find('lat') >= 0:
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees_north':
                        self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                sname = sname.lower()
                if sname.find('lon') >= 0:
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees_east':
                        self.lonvar[ig] = gname + vv
        # fourth sweep: axis is 'Y' or 'y'
        if not self.latvar[ig]:
            for vv in fi.variables:
                try:
                    saxis = fi[vv].axis
                except AttributeError:
                    saxis = ''
                if saxis.lower() == 'y':
                    self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                try:
                    saxis = fi[vv].axis
                except AttributeError:
                    saxis = ''
                if saxis.lower() == 'x':
                    self.lonvar[ig] = gname + vv
        # fifth sweep: same as first but units can be simply "degrees"
        if not self.latvar[ig]:
            for vv in fi.variables:
                sname = get_standard_name(fi[vv])
                if sname.lower() == 'latitude':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees':
                        self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                sname = get_standard_name(fi[vv])
                if sname.lower() == 'longitude':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees':
                        self.lonvar[ig] = gname + vv
        # sixth sweep: same as second but units can be simply "degrees"
        if not self.latvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                if sname[0:3].lower() == 'lat':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees':
                        self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                if sname[0:3].lower() == 'lon':
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees':
                        self.lonvar[ig] = gname + vv
        # seventh sweep: same as third but units can be simply "degrees"
        if not self.latvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                sname = sname.lower()
                if sname.find('lat') >= 0:
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees':
                        self.latvar[ig] = gname + vv
        if not self.lonvar[ig]:
            for vv in fi.variables:
                sname = fi[vv].name
                sname = sname.lower()
                if sname.find('lon') >= 0:
                    sunit = get_units(fi[vv])
                    if sunit.lower() == 'degrees':
                        self.lonvar[ig] = gname + vv
        #
        # determine lat/lon dimensions
        self.latdim.append('')
        self.londim.append('')
        if self.latvar[ig]:
            ivar = selvar(self, self.latvar[ig])
            latshape = ivar.shape
            if (len(latshape) < 1) or (len(latshape) > 2):
                print('Something went wrong determining lat/lon:'
                      ' latitude variable is not 1D or 2D.\n'
                      'latitude variable with dimensions:',
                      self.latvar[ig], ivar.dimensions)
                self.latvar[ig] = ''
            else:
                self.latdim[ig] = ivar.dimensions[0]
        if self.lonvar[ig]:
            ivar = selvar(self, self.lonvar[ig])
            lonshape = ivar.shape
            if len(lonshape) == 1:
                self.londim[ig] = ivar.dimensions[0]
            elif len(lonshape) == 2:
                self.londim[ig] = ivar.dimensions[1]
            else:
                print('Something went wrong determining lat/lon:'
                      ' longitude variable is not 1D or 2D.\n'
                      'longitude variable with dimensions:',
                      self.lonvar[ig], ivar.dimensions)
                self.lonvar[ig] = ''
        #
        # add units to lat/lon name
        if self.latvar[ig]:
            ivar = selvar(self, self.latvar[ig])
            idim = tuple(zip_dim_name_length(ivar))
            self.latvar[ig] = self.latvar[ig] + ' ' + str(idim)
        if self.lonvar[ig]:
            ivar = selvar(self, self.lonvar[ig])
            idim = tuple(zip_dim_name_length(ivar))
            self.lonvar[ig] = self.lonvar[ig] + ' ' + str(idim)


def analyse_netcdf_xarray(self):
    """
    Analyse netcdf file(s) opened with xarray for time (= unlimited),
    variables, latitudes/longitudes variables and dimensions.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    Set variables:
        self.dunlim,
        self.time, self.tname, self.tvar, self.dtime,
        self.cols,
        self.latvar, self.lonvar, self.latdim, self.londim

    Examples
    --------
    >>> analyse_netcdf_xarray(self)

    """
    import xarray as xr

    #
    # search time
    self.dunlim = None
    self.time = None
    self.tname = ''
    self.tvar = None
    self.dtime = None
    for cc in self.fi.coords:
        if np.issubdtype(self.fi.coords[cc].dtype, np.datetime64):
            self.dunlim = cc
            break
    if self.dunlim is None:
        if 'time' in self.fi.coords:
            self.dunlim = 'time'
    if self.dunlim is not None:
        self.time = self.fi.coords[self.dunlim]
        self.tname = self.dunlim
        self.tvar = self.dunlim
        self.dtime = self.time

    #
    # construct list of variable names with dimensions
    if self.time is not None:
        addt = [self.tname + ' ' +
                str(tuple(xzip_dim_name_length(self.fi[self.tvar])))]
        self.cols += addt
    ivars = []
    for vv in self.fi.variables:
        if vv != self.tname:
            ss = tuple(xzip_dim_name_length(self.fi[vv]))
            ndim = self.fi[vv].ndim
            self.maxdim = max(self.maxdim, ndim)
            ivars.append((vv, ss, ndim))
    self.cols += sorted([ vv[0] + ' ' + str(vv[1])
                          for vv in ivars ])

    #
    # search for lat/lon variables
    # first sweep: units must be "degrees_north" and "degrees_east"
    self.latvar = ''
    self.lonvar = ''
    for cc in self.fi.coords:
        ccoord = self.fi.coords[cc]
        cunits = get_units(ccoord)
        if cunits == 'degrees_north':
            self.latvar = cc
        if cunits == 'degrees_east':
            self.lonvar = cc
    # second sweep: axis is 'x', 'y', or 'X', 'Y'
    if not self.latvar:
        for cc in self.fi.coords:
            if cc.lower() == 'y':
                self.latvar = cc
    if not self.lonvar:
        for cc in self.fi.coords:
            if cc.lower() == 'x':
                self.lonvar = cc

    #
    # determine lat/lon dimensions
    self.latdim = ''
    self.londim = ''

    #
    # add units to lat/lon name
    if self.latvar:
        idim = tuple(xzip_dim_name_length(self.fi[self.latvar]))
        self.latvar = self.latvar + ' ' + str(idim)
    if self.lonvar:
        idim = tuple(xzip_dim_name_length(self.fi[self.lonvar]))
        self.lonvar = self.lonvar + ' ' + str(idim)


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
    >>> x = fi['time']
    >>> miss = get_miss(self, x)

    """
    try:
        out = [ncfill[x.dtype]]
    except KeyError:
        out = []
    try:
        if x.dtype != np.dtype('<M8[ms]'):
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
    NaN or np.datetime64('NaT') in slice (set_miss).

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
        Extracted array slice with missing values set to
        np.NaN or np.datetime64('NaT')

    Examples
    --------
    >>> x = fi['time']
    >>> xx = get_slice_miss(self, x)

    """
    miss = get_miss(self, x)
    xx = get_slice(dimspins, x)
    if xx.ndim > 1:
        xx = xx.squeeze()
    xx = set_miss(miss, xx)
    # catch variables that have only one string or similar
    try:
        sx = xx.shape[0]
    except IndexError:
        xx = np.array([np.nan])
    return xx


#
# Set dimensions
#

# set_dim_lat/lon/var could also be methods of ncvMap.
# Leave them here for their concordance with set_dim_x/y/z

def set_dim_lat(self):
    """
    Set spinboxes of latitude-dimensions.

    Set labels and value lists. Select 'all' for all dimension.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of latitude-dimensions set.

    Examples
    --------
    >>> set_dim_lat(self)

    """
    # reset dimensions
    for i in range(self.maxdim):
        self.latd[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.latdlblval[i].set(str(i))
        self.latdtip[i].set("")
        self.latdframe[i].pack(side='left')
    lat = self.lat.get()
    if lat != '':
        # set real dimensions
        gl, vl = vardim2var(lat, self.groups)
        if self.usex:
            if vl == self.tname:
                vl = self.tvar
        else:
            if vl == self.tname[gl]:
                vl = self.tvar[gl]
        ll = selvar(self, vl)
        for i in range(ll.ndim):
            ww = max(4, int(np.ceil(np.log10(ll.shape[i]))))
            self.latd[i].config(values=spinbox_values(ll.shape[i]), width=ww,
                                state=tk.NORMAL)
            if (ll.shape[i] > 1):
                self.latdval[i].set('all')
            else:
                self.latdval[i].set('0')
            if self.usex:
                self.latdlblval[i].set(str(ll.dims[i]))
            else:
                self.latdlblval[i].set(str(ll.dimensions[i]))
            self.latdframe[i].pack(side='left')
            if ll.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    ll.shape[i] - 1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.latdtip[i].set(tstr)


def set_dim_lon(self):
    """
    Set spinboxes of longitude-dimensions.

    Set labels and value lists. Select 'all' for all dimension.

    Parameters
    ----------
    self : class
        ncvue class

    Returns
    -------
    None
        Labels and values of spinboxes of longitude-dimensions set.

    Examples
    --------
    >>> set_dim_lon(self)

    """
    # reset dimensions
    for i in range(self.maxdim):
        self.lond[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.londlblval[i].set(str(i))
        self.londtip[i].set("")
        self.londframe[i].pack(side='left')
    lon = self.lon.get()
    if lon != '':
        # set real dimensions
        gl, vl = vardim2var(lon, self.groups)
        if self.usex:
            if vl == self.tname:
                vl = self.tvar
        else:
            if vl == self.tname[gl]:
                vl = self.tvar[gl]
        ll = selvar(self, vl)
        for i in range(ll.ndim):
            ww = max(4, int(np.ceil(np.log10(ll.shape[i]))))
            self.lond[i].config(values=spinbox_values(ll.shape[i]), width=ww,
                                state=tk.NORMAL)
            if (ll.shape[i] > 1):
                self.londval[i].set('all')
            else:
                self.londval[i].set('0')
            if self.usex:
                self.londlblval[i].set(str(ll.dims[i]))
            else:
                self.londlblval[i].set(str(ll.dimensions[i]))
            self.londframe[i].pack(side='left')
            if ll.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    ll.shape[i] - 1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.londtip[i].set(tstr)


def set_dim_var(self):
    """
    Set spinboxes of varable-dimensions in Map panel.

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
        Labels and values of spinboxes of variable-dimensions set.

    Examples
    --------
    >>> set_dim_var(self)

    """
    # reset dimensions
    for i in range(self.maxdim):
        self.vd[i].config(values=(0,), width=1, state=tk.DISABLED)
        self.vdlblval[i].set(str(i))
        self.vdtip[i].set("")
        self.vdframe[i].pack(side='left')
    v = self.v.get()
    if v != '':
        # set real dimensions
        gz, vz = vardim2var(v, self.groups)
        if self.usex:
            if vz == self.tname:
                vz = self.tvar
        else:
            if vz == self.tname[gz]:
                vz = self.tvar[gz]
        vv = selvar(self, vz)
        if self.usex:
            latdim = self.latdim
            londim = self.londim
            dunlim = self.dunlim
            dims = vv.dims
        else:
            latdim = self.latdim[gz]
            londim = self.londim[gz]
            dunlim = self.dunlim[gz]
            dims = vv.dimensions
        nall = 0
        if latdim:
            if latdim in dims:
                i = dims.index(latdim)
                ww = max(5, int(np.ceil(np.log10(vv.shape[i]))))  # 5~median
                self.vd[i].config(values=spinbox_values(vv.shape[i]), width=ww,
                                  state=tk.NORMAL)
                nall += 1
                self.vdval[i].set('all')
                self.vdlblval[i].set(str(dims[i]))
                self.vdframe[i].pack(side='left')
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)
        if londim:
            if londim in dims:
                i = vv.dimensions.index(londim)
                ww = max(5, int(np.ceil(np.log10(vv.shape[i]))))  # 5~median
                self.vd[i].config(values=spinbox_values(vv.shape[i]), width=ww,
                                  state=tk.NORMAL)
                nall += 1
                self.vdval[i].set('all')
                self.vdlblval[i].set(str(dims[i]))
                self.vdframe[i].pack(side='left')
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)
        for i in range(vv.ndim):
            ww = max(5, int(np.ceil(np.log10(vv.shape[i]))))  # 5~median
            self.vd[i].config(values=spinbox_values(vv.shape[i]), width=ww,
                              state=tk.NORMAL)
            if ( (dims[i] != latdim) and
                 (dims[i] != londim) and
                 (dims[i] != dunlim) and
                 (nall <= 1) and (vv.shape[i] > 1) ):
                nall += 1
                self.vdval[i].set('all')
                self.vdlblval[i].set(str(dims[i]))
                self.vdframe[i].pack(side='left')
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)
            elif ((dims[i] != latdim) and
                  (dims[i] != londim)):
                self.vdval[i].set('0')
                self.vdlblval[i].set(str(dims[i]))
                self.vdframe[i].pack(side='left')
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)


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
        self.xdlblval[i].set(str(i))
        self.xdtip[i].set("")
        self.xdframe[i].pack(side='left')
    x = self.x.get()
    if x != '':
        # set real dimensions
        gx, vx = vardim2var(x, self.groups)
        if self.usex:
            if vx == self.tname:
                vx = self.tvar
        else:
            if vx == self.tname[gx]:
                vx = self.tvar[gx]
        xx = selvar(self, vx)
        if self.usex:
            dunlim = self.dunlim
            dims = xx.dims
        else:
            dunlim = self.dunlim[gx]
            dims = xx.dimensions
        nall = 0
        if dunlim in dims:
            i = dims.index(dunlim)
            ww = max(5, int(np.ceil(np.log10(xx.shape[i]))))  # 5~median
            self.xd[i].config(values=spinbox_values(xx.shape[i]), width=ww,
                              state=tk.NORMAL)
            nall += 1
            self.xdval[i].set('all')
            self.xdlblval[i].set(str(dims[i]))
            self.xdframe[i].pack(side='left')
            if xx.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    xx.shape[i] - 1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.xdtip[i].set(tstr)
        for i in range(xx.ndim):
            if dims[i] != dunlim:
                ww = max(5, int(np.ceil(np.log10(xx.shape[i]))))
                self.xd[i].config(values=spinbox_values(xx.shape[i]), width=ww,
                                  state=tk.NORMAL)
                if (nall == 0) and (xx.shape[i] > 1):
                    nall += 1
                    self.xdval[i].set('all')
                else:
                    self.xdval[i].set('0')
                self.xdlblval[i].set(str(dims[i]))
                self.xdframe[i].pack(side='left')
                if xx.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        xx.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.xdtip[i].set(tstr)


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
        self.ydlblval[i].set(str(i))
        self.ydtip[i].set("")
        self.ydframe[i].pack(side='left')
    y = self.y.get()
    if y != '':
        # set real dimensions
        gy, vy = vardim2var(y, self.groups)
        if self.usex:
            if vy == self.tname:
                vy = self.tvar
        else:
            if vy == self.tname[gy]:
                vy = self.tvar[gy]
        yy = selvar(self, vy)
        if self.usex:
            dunlim = self.dunlim
            dims = yy.dims
        else:
            dunlim = self.dunlim[gy]
            dims = yy.dimensions
        nall = 0
        if dunlim in dims:
            i = dims.index(dunlim)
            ww = max(5, int(np.ceil(np.log10(yy.shape[i]))))  # 5~median
            self.yd[i].config(values=spinbox_values(yy.shape[i]), width=ww,
                              state=tk.NORMAL)
            nall += 1
            self.ydval[i].set('all')
            self.ydlblval[i].set(str(dims[i]))
            self.ydframe[i].pack(side='left')
            if yy.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    yy.shape[i] - 1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.ydtip[i].set(tstr)
        for i in range(yy.ndim):
            if dims[i] != dunlim:
                ww = max(5, int(np.ceil(np.log10(yy.shape[i]))))
                self.yd[i].config(values=spinbox_values(yy.shape[i]), width=ww,
                                  state=tk.NORMAL)
                if (nall == 0) and (yy.shape[i] > 1):
                    nall += 1
                    self.ydval[i].set('all')
                else:
                    self.ydval[i].set('0')
                self.ydlblval[i].set(str(dims[i]))
                self.ydframe[i].pack(side='left')
                if yy.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        yy.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.ydtip[i].set(tstr)


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
        self.y2dlblval[i].set(str(i))
        self.y2dtip[i].set("")
        self.y2dframe[i].pack(side='left')
    y2 = self.y2.get()
    if y2 != '':
        # set real dimensions
        gy2, vy2 = vardim2var(y2, self.groups)
        if self.usex:
            if vy2 == self.tname:
                vy2 = self.tvar
        else:
            if vy2 == self.tname[gy2]:
                vy2 = self.tvar[gy2]
        yy2 = selvar(self, vy2)
        if self.usex:
            dunlim = self.dunlim
            dims = yy2.dims
        else:
            dunlim = self.dunlim[gy2]
            dims = yy2.dimensions
        nall = 0
        if dunlim in dims:
            i = dims.index(dunlim)
            ww = max(5, int(np.ceil(np.log10(yy2.shape[i]))))  # 5~median
            self.y2d[i].config(values=spinbox_values(yy2.shape[i]), width=ww,
                               state=tk.NORMAL)
            nall += 1
            self.y2dval[i].set('all')
            self.y2dlblval[i].set(str(dims[i]))
            self.y2dframe[i].pack(side='left')
            if yy2.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    yy2.shape[i] - 1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.y2dtip[i].set(tstr)
        for i in range(yy2.ndim):
            if dims[i] != dunlim:
                ww = max(5, int(np.ceil(np.log10(yy2.shape[i]))))
                self.y2d[i].config(values=spinbox_values(yy2.shape[i]),
                                   width=ww, state=tk.NORMAL)
                if (nall == 0) and (yy2.shape[i] > 1):
                    nall += 1
                    self.y2dval[i].set('all')
                else:
                    self.y2dval[i].set('0')
                self.y2dlblval[i].set(str(dims[i]))
                self.y2dframe[i].pack(side='left')
                if yy2.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        yy2.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.y2dtip[i].set(tstr)


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
        self.zdlblval[i].set(str(i))
        self.zdtip[i].set("")
        self.zdframe[i].pack(side='left')
    z = self.z.get()
    if z != '':
        # set real dimensions
        gz, vz = vardim2var(z, self.groups)
        if self.usex:
            if vz == self.tname:
                vz = self.tvar
        else:
            if vz == self.tname[gz]:
                vz = self.tvar[gz]
        zz = selvar(self, vz)
        if self.usex:
            dunlim = self.dunlim
            dims = zz.dims
        else:
            dunlim = self.dunlim[gz]
            dims = zz.dimensions
        nall = 0
        if dunlim in dims:
            i = dims.index(dunlim)
            ww = max(5, int(np.ceil(np.log10(zz.shape[i]))))  # 5~median
            self.zd[i].config(values=spinbox_values(zz.shape[i]), width=ww,
                              state=tk.NORMAL)
            nall += 1
            self.zdval[i].set('all')
            self.zdlblval[i].set(str(dims[i]))
            self.zdframe[i].pack(side='left')
            if zz.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    zz.shape[i] - 1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.zdtip[i].set(tstr)
        for i in range(zz.ndim):
            if dims[i] != dunlim:
                ww = max(5, int(np.ceil(np.log10(zz.shape[i]))))
                self.zd[i].config(values=spinbox_values(zz.shape[i]), width=ww,
                                  state=tk.NORMAL)
                if (nall <= 1) and (zz.shape[i] > 1):
                    nall += 1
                    self.zdval[i].set('all')
                else:
                    self.zdval[i].set('0')
                self.zdlblval[i].set(str(dims[i]))
                self.zdframe[i].pack(side='left')
                if zz.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        zz.shape[i] - 1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.zdtip[i].set(tstr)
