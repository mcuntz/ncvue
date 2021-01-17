#!/usr/bin/env python
"""
Main ncvue window.

This sets up the main notebook window with the plotting panels and
analyses the netcdf file, e.g. determining the unlimited dimensions,
calculating dates, etc.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvMain
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk
try:
    import tkinter.ttk as ttk
except Exception:
    import sys
    print('Using the themed widget set introduced in Tk 8.5.')
    print('Try to use mcview.py, which uses wxpython instead.')
    sys.exit()
import numpy as np
import curses.ascii as ca
from .ncvutils   import SEPCHAR, vardim2var, zip_dim_name_length
from .ncvscatter import ncvScatter
from .ncvcontour import ncvContour
from .ncvmap     import ncvMap

__all__ = ['ncvMain']


# --------------------------------------------------------------------
# Window with plot panels
#

class ncvMain(ttk.Frame):
    """
    Main ncvue notebook window with the plotting panels.

    Sets up the notebook layout with the panels and analyses the netcdf file,
    e.g. determining the unlimited dimensions, calculating dates, etc. in
    __init__.

    Contains the method to analyse the netcdf file.
    """

    #
    # Window setup
    #

    def __init__(self, fi, master=None, miss=np.nan, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=1)

        self.name   = 'ncvMain'
        self.fi     = fi      # netcdf file
        self.master = master  # master window = root
        self.root   = master  # root window
        self.miss   = master.miss
        self.dunlim = ''      # name of unlimited dimension
        self.time   = None    # datetime variable
        self.tname  = ''      # datetime variable name
        self.tvar   = ''      # datetime variable name in netcdf file
        self.dtime  = None    # decimal year
        self.latvar = ''      # name of latitude variable
        self.lonvar = ''      # name of longitude variable
        self.latdim = ''      # name of latitude dimension
        self.londim = ''      # name of longitude dimension
        self.maxdim = 0       # maximum number of dimensions of all variables
        self.cols   = []      # variable list

        # Analyse netcdf file
        self.analyse_netcdf()

        # Notebook for tabs for future plot types
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tab_scatter = ncvScatter(self)
        self.tab_contour = ncvContour(self)
        self.tab_map     = ncvMap(self)

        mapfirst = False
        if self.latvar:
            vl = vardim2var(self.latvar)
            if np.prod(self.fi.variables[vl].shape) > 1:
                mapfirst = True
        if self.lonvar:
            vl = vardim2var(self.lonvar)
            if np.prod(self.fi.variables[vl].shape) > 1:
                mapfirst = True

        if mapfirst:
            self.tabs.add(self.tab_map, text=self.tab_map.name)
        self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
        self.tabs.add(self.tab_contour, text=self.tab_contour.name)
        if not mapfirst:
            self.tabs.add(self.tab_map, text=self.tab_map.name)

    #
    # Methods
    #

    # analyse netcdf file
    def analyse_netcdf(self):
        """
        Analyse the netcdf file.

        Determining the unlimited dimensions, calculate dates, make list of
        variables.
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
