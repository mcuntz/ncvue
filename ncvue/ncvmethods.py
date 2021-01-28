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

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* Slice arrays with slice function rather than numpy.take,
  Dec 2020, Matthias Cuntz
* Moved individual get_slice_? methods for x, y, y2, z as general get_slice
  function to ncvutils, Dec 2020, Matthias Cuntz
* Added convenience method get_slice_miss, Dec 2020, Matthias Cuntz
* set_dim_lon, set_dim_lat, set_dim_var for Map panel,
  Jan 2021, Matthias Cuntz
* set latdim, londim to all on map var, determined in ncvMain,
  Jan 2021, Matthias Cuntz
* catch non numpy.dtype in set_miss, Jan 2021, Matthias Cuntz
* catch variables that have only one string or similar,
  Jan 2021, Matthias Cuntz
* added tooltip to dimensions, Jan 2021, Matthias Cuntz
* added analyse_netcdf from ncvmain, Jan 2021, Matthias Cuntz
* use dlblval instead of dlbl to set dimension labels, Jan 2021, Matthias Cuntz

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
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
import numpy as np
from .ncvutils import DIMMETHODS, get_slice, set_miss, spinbox_values
from .ncvutils import SEPCHAR, vardim2var, zip_dim_name_length
import netCDF4 as nc
# nc.default_fillvals but with keys as variables['var'].dtype
nctypes = [ np.dtype(i) for i in nc.default_fillvals ]
ncfill  = dict(zip(nctypes, list(nc.default_fillvals.values())))
ncfill.update({np.dtype('O'): np.nan})


__all__ = ['analyse_netcdf', 'get_miss', 'get_slice_miss',
           'set_dim_lat', 'set_dim_lon', 'set_dim_var',
           'set_dim_x', 'set_dim_y', 'set_dim_y2', 'set_dim_z']


#
# Analyse netcdf file
#

def analyse_netcdf(self):
    """
    Analyse a netcdf file for the unlimited dimension, calculating datetime,
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
    # search unlimited dimension
    self.dunlim = ''
    for dd in self.fi.dimensions:
        if self.fi.dimensions[dd].isunlimited():
            self.dunlim = dd
            break
    #
    # search for time variable and make datetime variable
    self.time  = None
    self.tname = ''
    self.tvar  = ''
    self.dtime = None
    for vv in self.fi.variables:
        isunlim = False
        if self.dunlim:
            if vv.lower() == self.fi.dimensions[self.dunlim].name.lower():
                isunlim = True
        if ( isunlim or vv.lower().startswith('time_') or
             (vv.lower() == 'time') or (vv.lower() == 'datetime') or
             (vv.lower() == 'date') ):
            self.tvar = vv
            if vv.lower() == 'datetime':
                self.tname = 'date'
            else:
                self.tname = 'datetime'
            try:
                tunit = self.fi.variables[self.tvar].units
            except AttributeError:
                tunit = ''
            # assure 01, etc. if values < 10
            if tunit.find('since') > 0:
                tt = tunit.split()
                dd = tt[2].split('-')
                dd[0] = ('000'+dd[0])[-4:]
                dd[1] = ('0'+dd[1])[-2:]
                dd[2] = ('0'+dd[1])[-2:]
                tt[2] = '-'.join(dd)
                tunit = ' '.join(tt)
            try:
                tcal = self.fi.variables[self.tvar].calendar
            except AttributeError:
                tcal = 'standard'
            time = self.fi.variables[self.tvar][:]
            # time dimension "day as %Y%m%d.%f" from cdo.
            if ' as ' in tunit:
                itunit = tunit.split()[2]
                dtime = []
                for tt in time:
                    stt = str(tt).split('.')
                    sstt = ('00'+stt[0])[-8:] + '.' + stt[1]
                    dtime.append(dt.datetime.strptime(sstt, itunit))
                ntime = cf.date2num(dtime,
                                    'days since 0001-01-01 00:00:00')
                self.dtime = cf.num2date(ntime,
                                         'days since 0001-01-01 00:00:00')
            else:
                try:
                    self.dtime = cf.num2date(time, tunit,
                                             calendar=tcal)
                except ValueError:
                    self.dtime = None
            if self.dtime is not None:
                ntime = len(self.dtime)
                if (tcal == '360_day'):
                    ndays = [360.]*ntime
                elif (tcal == '365_day'):
                    ndays = [365.]*ntime
                elif (tcal == 'noleap'):
                    ndays = [365.]*ntime
                elif (tcal == '366_day'):
                    ndays = [366.]*ntime
                elif (tcal == 'all_leap'):
                    ndays = [366.]*ntime
                else:
                    ndays = [ 365. +
                              float((((t.year%4) == 0) &
                                     ((t.year%100) != 0)) |
                                    ((t.year%400) == 0))
                              for t in self.dtime ]
                self.dtime = np.array([
                    t.year +
                    (t.dayofyr-1 + t.hour / 24. +
                     t.minute / 1440 + t.second / 86400.) / ndays[i]
                    for i, t in enumerate(self.dtime) ])
            # make datetime variable
            if self.time is None:
                try:
                    self.time = cf.num2date(
                        time, tunit, calendar=tcal,
                        only_use_cftime_datetimes=False,
                        only_use_python_datetimes=True)
                except:
                    self.time = None
            if self.time is None:
                try:
                    self.time = cf.num2date(time, tunit,
                                            calendar=tcal)
                except:
                    self.time = None
            if self.time is None:
                # if not possible use decimal year
                self.time = self.dtime
            if self.time is None:
                # could not interpret time at all,
                # e.g. if units = "months since ..."
                self.time  = time
                self.dtime = time
            break
    #
    # construct list of variable names with dimensions
    if self.time is not None:
        addt = [
            self.tname + ' ' + SEPCHAR +
            str(tuple(zip_dim_name_length(self.fi.variables[self.tvar])))]
        self.cols += addt
    ivars = []
    for vv in self.fi.variables:
        # ss = self.fi.variables[vv].shape
        ss = tuple(zip_dim_name_length(self.fi.variables[vv]))
        self.maxdim = max(self.maxdim, len(ss))
        ivars.append((vv, ss, len(ss)))
    self.cols += sorted([ vv[0] + ' ' + SEPCHAR + str(vv[1])
                          for vv in ivars ])
    #
    # search for lat/lon variables
    self.latvar = ''
    self.lonvar = ''
    # first sweep: *name must be "latitude" and
    #              units must be "degrees_north"
    if not self.latvar:
        for vv in self.fi.variables:
            try:
                sname = self.fi.variables[vv].standard_name
            except AttributeError:
                try:
                    sname = self.fi.variables[vv].long_name
                except AttributeError:
                    sname = self.fi.variables[vv].name
            if sname.lower() == 'latitude':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees_north':
                    self.latvar = vv
    if not self.lonvar:
        for vv in self.fi.variables:
            try:
                sname = self.fi.variables[vv].standard_name
            except AttributeError:
                try:
                    sname = self.fi.variables[vv].long_name
                except AttributeError:
                    sname = self.fi.variables[vv].name
            if sname.lower() == 'longitude':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees_east':
                    self.lonvar = vv
    # second sweep: name must start with lat and
    #               units must be "degrees_north"
    if not self.latvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            if sname[0:3].lower() == 'lat':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees_north':
                    self.latvar = vv
    if not self.lonvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            if sname[0:3].lower() == 'lon':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees_east':
                    self.lonvar = vv
    # third sweep: name must contain lat and
    #              units must be "degrees_north"
    if not self.latvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            sname = sname.lower()
            if sname.find('lat') >= 0:
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees_north':
                    self.latvar = vv
    if not self.lonvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            sname = sname.lower()
            if sname.find('lon') >= 0:
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees_east':
                    self.lonvar = vv
    # fourth sweep: same as first but units can be "degrees"
    if not self.latvar:
        for vv in self.fi.variables:
            try:
                sname = self.fi.variables[vv].standard_name
            except AttributeError:
                try:
                    sname = self.fi.variables[vv].long_name
                except AttributeError:
                    sname = self.fi.variables[vv].name
            if sname.lower() == 'latitude':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees':
                    self.latvar = vv
    if not self.lonvar:
        for vv in self.fi.variables:
            try:
                sname = self.fi.variables[vv].standard_name
            except AttributeError:
                try:
                    sname = self.fi.variables[vv].long_name
                except AttributeError:
                    sname = self.fi.variables[vv].name
            if sname.lower() == 'longitude':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees':
                    self.lonvar = vv
    # fifth sweep: same as second but units can be "degrees"
    if not self.latvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            if sname[0:3].lower() == 'lat':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees':
                    self.latvar = vv
    if not self.lonvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            if sname[0:3].lower() == 'lon':
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees':
                    self.lonvar = vv
    # sixth sweep: same as third but units can be "degrees"
    if not self.latvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            sname = sname.lower()
            if sname.find('lat') >= 0:
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees':
                    self.latvar = vv
    if not self.lonvar:
        for vv in self.fi.variables:
            sname = self.fi.variables[vv].name
            sname = sname.lower()
            if sname.find('lon') >= 0:
                try:
                    sunit = self.fi.variables[vv].units
                except AttributeError:
                    sunit = ''
                if sunit.lower() == 'degrees':
                    self.lonvar = vv
    #
    # determine lat/lon dimensions
    self.latdim = ''
    self.londim = ''
    if self.latvar:
        latshape = self.fi.variables[self.lonvar].shape
        if (len(latshape) < 1) or (len(latshape) > 2):
            estr  = 'Something went wrong determining lat/lon:'
            estr += ' latitude variable is not 1D or 2D.'
            print(estr)
            estr = 'latitude variable with dimensions:'
            ldim = self.fi.variables[self.latvar].dimensions
            print(estr, self.latvar, ldim)
            estr = 'longitude variable with dimensions:'
            ldim = self.fi.variables[self.lonvar].dimensions
            print(estr, self.lonvar, ldim)
            self.latvar = ''
            self.lonvar = ''
        else:
            self.latdim = self.fi.variables[self.latvar].dimensions[0]
    if self.lonvar:
        lonshape = self.fi.variables[self.lonvar].shape
        if len(lonshape) == 1:
            self.londim = self.fi.variables[self.lonvar].dimensions[0]
        elif len(lonshape) == 2:
            self.londim = self.fi.variables[self.lonvar].dimensions[1]
        else:
            estr  = 'Something went wrong determining lat/lon:'
            estr += ' longitude variable is not 1D or 2D.'
            print(estr)
            estr = 'latitude variable with dimensions:'
            ldim = self.fi.variables[self.latvar].dimensions
            print(estr, self.latvar, ldim)
            estr = 'longitude variable with dimensions:'
            ldim = self.fi.variables[self.lonvar].dimensions
            print(estr, self.lonvar, ldim)
            self.latvar = ''
            self.lonvar = ''
    #
    # add units to lat/lon name
    if self.latvar:
        idim = tuple(zip_dim_name_length(self.fi.variables[self.latvar]))
        self.latvar = self.latvar + ' ' + SEPCHAR + str(idim)
    if self.lonvar:
        idim = tuple(zip_dim_name_length(self.fi.variables[self.lonvar]))
        self.lonvar = self.lonvar + ' ' + SEPCHAR + str(idim)


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
    try:
        out = [ncfill[x.dtype]]
    except KeyError:
        out = []
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
    lat = self.lat.get()
    if lat != '':
        # set real dimensions
        vl = vardim2var(lat)
        if vl == self.tname:
            vl = self.tvar
        ll = self.fi.variables[vl]
        for i in range(ll.ndim):
            ww = max(4, int(np.ceil(np.log10(ll.shape[i]))))
            self.latd[i].config(values=spinbox_values(ll.shape[i]), width=ww,
                                state=tk.NORMAL)
            if (ll.shape[i] > 1):
                self.latdval[i].set('all')
            else:
                self.latdval[i].set(0)
            self.latdlblval[i].set(ll.dimensions[i])
            if ll.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    ll.shape[i]-1)
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
    lon = self.lon.get()
    if lon != '':
        # set real dimensions
        vl = vardim2var(lon)
        if vl == self.tname:
            vl = self.tvar
        ll = self.fi.variables[vl]
        for i in range(ll.ndim):
            ww = max(4, int(np.ceil(np.log10(ll.shape[i]))))
            self.lond[i].config(values=spinbox_values(ll.shape[i]), width=ww,
                                state=tk.NORMAL)
            if (ll.shape[i] > 1):
                self.londval[i].set('all')
            else:
                self.londval[i].set(0)
            self.londlblval[i].set(ll.dimensions[i])
            if ll.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    ll.shape[i]-1)
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
    v = self.v.get()
    if v != '':
        # set real dimensions
        vz = vardim2var(v)
        if vz == self.tname:
            vz = self.tvar
        vv = self.fi.variables[vz]
        nall = 0
        if self.latdim:
            if self.latdim in vv.dimensions:
                i = vv.dimensions.index(self.latdim)
                ww = max(5, int(np.ceil(np.log10(vv.shape[i]))))  # 5~median
                self.vd[i].config(values=spinbox_values(vv.shape[i]), width=ww,
                                  state=tk.NORMAL)
                nall += 1
                self.vdval[i].set('all')
                self.vdlblval[i].set(vv.dimensions[i])
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i]-1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)
        if self.londim:
            if self.londim in vv.dimensions:
                i = vv.dimensions.index(self.londim)
                ww = max(5, int(np.ceil(np.log10(vv.shape[i]))))  # 5~median
                self.vd[i].config(values=spinbox_values(vv.shape[i]), width=ww,
                                  state=tk.NORMAL)
                nall += 1
                self.vdval[i].set('all')
                self.vdlblval[i].set(vv.dimensions[i])
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i]-1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)
        for i in range(vv.ndim):
            ww = max(5, int(np.ceil(np.log10(vv.shape[i]))))  # 5~median
            self.vd[i].config(values=spinbox_values(vv.shape[i]), width=ww,
                              state=tk.NORMAL)
            if ((vv.dimensions[i] != self.latdim) and
                (vv.dimensions[i] != self.londim) and
                (nall <= 1) and (vv.shape[i] > 1)):
                nall += 1
                self.vdval[i].set('all')
                self.vdlblval[i].set(vv.dimensions[i])
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i]-1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.vdtip[i].set(tstr)
            elif ((vv.dimensions[i] != self.latdim) and
                  (vv.dimensions[i] != self.londim)):
                self.vdval[i].set(0)
                self.vdlblval[i].set(vv.dimensions[i])
                if vv.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        vv.shape[i]-1)
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
    x = self.x.get()
    if x != '':
        # set real dimensions
        vx = vardim2var(x)
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
            self.xdlblval[i].set(xx.dimensions[i])
            if xx.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    xx.shape[i]-1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.xdtip[i].set(tstr)
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
                self.xdlblval[i].set(xx.dimensions[i])
                if xx.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        xx.shape[i]-1)
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
    y = self.y.get()
    if y != '':
        # set real dimensions
        vy = vardim2var(y)
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
            self.ydlblval[i].set(yy.dimensions[i])
            if yy.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    yy.shape[i]-1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.ydtip[i].set(tstr)
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
                self.ydlblval[i].set(yy.dimensions[i])
                if yy.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        yy.shape[i]-1)
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
    y2 = self.y2.get()
    if y2 != '':
        # set real dimensions
        vy2 = vardim2var(y2)
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
            self.y2dlblval[i].set(yy2.dimensions[i])
            if yy2.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    yy2.shape[i]-1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.y2dtip[i].set(tstr)
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
                self.y2dlblval[i].set(yy2.dimensions[i])
                if yy2.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        yy2.shape[i]-1)
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
    z = self.z.get()
    if z != '':
        # set real dimensions
        vz = vardim2var(z)
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
            self.zdlblval[i].set(zz.dimensions[i])
            if zz.shape[i] > 1:
                tstr  = "Specific dimension value: 0-{:d}\n".format(
                    zz.shape[i]-1)
                tstr += "or arithmetic operation on axis:\n"
                tstr += "  " + ", ".join(DIMMETHODS)
            else:
                tstr = "Single dimension: 0"
            self.zdtip[i].set(tstr)
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
                self.zdlblval[i].set(zz.dimensions[i])
                if zz.shape[i] > 1:
                    tstr  = "Specific dimension value: 0-{:d}\n".format(
                        zz.shape[i]-1)
                    tstr += "or arithmetic operation on axis:\n"
                    tstr += "  " + ", ".join(DIMMETHODS)
                else:
                    tstr = "Single dimension: 0"
                self.zdtip[i].set(tstr)
