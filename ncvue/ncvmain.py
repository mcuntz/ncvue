#!/usr/bin/env python
"""
Main window of ncvue.

Written  Matthias Cuntz, Nov-Dec 2020
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
from .ncvutils   import zip_dim_name_length
from .ncvscatter import ncvScatter
from .ncvcontour import ncvContour
from .ncvmap     import ncvMap


__all__ = ['ncvMain']


# --------------------------------------------------------------------
# Window with plot panels
#

class ncvMain(ttk.Frame):
    """
    New plotting window with different plotting panels.
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
        self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
        self.tabs.add(self.tab_contour, text=self.tab_contour.name)
        self.tabs.add(self.tab_map, text=self.tab_map.name)

    #
    # Methods
    #

    # analyse netcdf file
    def analyse_netcdf(self):
        import datetime as dt
        try:
            import cftime as cf
        except ModuleNotFoundError:
            import netCDF4 as cf
        # search unlimited dimension
        self.dunlimited = ''
        for dd in self.fi.dimensions:
            if self.fi.dimensions[dd].isunlimited():
                self.dunlimited = dd
                break
        # search for time variable
        self.time  = None
        self.tname = ''
        self.tvar  = ''
        self.dtime = None
        for vv in self.fi.variables:
            if ((vv.lower() == 'time') or (vv.lower() == 'datetime') or
                (vv.lower() == 'date')):
                self.tvar = vv
                if vv.lower() == 'datetime':
                    self.tname = 'date'
                else:
                    self.tname = 'datetime'
                try:
                    tunit = self.fi.variables[self.tvar].units
                except AttributeError:
                    tunit = ''
                try:
                    tcal = self.fi.variables[self.tvar].calendar
                except AttributeError:
                    tcal = 'standard'
                self.time = self.fi.variables[self.tvar][:]
                # time dimension "day as %Y%m%d.%f" from cdo.
                if ' as ' in tunit:
                    itunit = tunit.split()[2]
                    dtime = []
                    for tt in self.time:
                        stt = str(tt).split('.')
                        sstt = ('00'+stt[0])[-8:] + '.' + stt[1]
                        dtime.append(dt.datetime.strptime(sstt, itunit))
                    ntime = cf.date2num(dtime,
                                        'days since 0001-01-01 00:00:00')
                    self.dtime = cf.num2date(ntime,
                                             'days since 0001-01-01 00:00:00')
                else:
                    try:
                        self.dtime = cf.num2date(self.time, tunit,
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
                try:
                    self.time = cf.num2date(
                        self.time, tunit, calendar=tcal,
                        only_use_cftime_datetimes=False,
                        only_use_python_datetimes=True)
                except TypeError:
                    self.time = cf.num2date(self.time, tunit,
                                            calendar=tcal)
                except ValueError:
                    # if not possible use decimal year
                    self.time = self.dtime
                break
        # construct different lists depending on number of dimensions
        if self.time is not None:
            addt = [
                self.tname + ' ' +
                str(tuple(zip_dim_name_length(self.fi.variables[self.tvar]))) ]
            self.cols += addt
        ivars = []
        for vv in self.fi.variables:
            # ss = self.fi.variables[vv].shape
            ss = tuple(zip_dim_name_length(self.fi.variables[vv]))
            self.maxdim = max(self.maxdim, len(ss))
            ivars.append((vv, ss, len(ss)))
        self.cols += sorted([ vv[0] + ' ' + str(vv[1]) for vv in ivars ])
