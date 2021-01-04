#!/usr/bin/env python
"""
Map panel of ncvue.

The panel allows plotting contour or mesh maps of georeferenced data.
Maps can be animated along the time axis.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Dec 2020-Jan 2021 by Matthias Cuntz (mc (at) macu (dot) de)

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvMap
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
import os
import numpy as np
from .ncvutils   import clone_ncvmain, set_axis_label, set_miss
from .ncvmethods import get_slice_miss, get_miss
from .ncvmethods import set_dim_lon, set_dim_lat, set_dim_var
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_menu, add_scale, add_spinbox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
plt.style.use('seaborn-darkgrid')
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point


__all__ = ['ncvMap']


class ncvMap(ttk.Frame):
    """
    Panel for maps.

    Sets up the layout with the figure canvas, variable selectors, dimension
    spinboxes, and options in __init__.

    Contains various commands that manage what will be drawn or redrawn if
    something is selected, changed, checked, etc.
    """

    #
    # Panel setup
    #

    def __init__(self, master, **kwargs):
        from functools import partial
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        from matplotlib.figure import Figure
        from matplotlib import animation

        super().__init__(master, **kwargs)

        self.name   = 'Map'
        self.master = master
        self.root   = master.root
        self.fi     = master.fi
        self.miss   = master.miss
        self.dunlim = master.dunlim
        self.time   = master.time
        self.tname  = master.tname
        self.tvar   = master.tvar
        self.dtime  = master.dtime
        self.latvar = master.latvar
        self.lonvar = master.lonvar
        self.latdim = master.latdim
        self.londim = master.londim
        self.maxdim = master.maxdim
        self.cols   = master.cols

        # unlimited dimension control
        self.iunlim = -1  # index of dunlim in dimensions of current var
        self.nunlim = 0   # length of dunlim of current plot variable

        # new window
        self.rowwin = ttk.Frame(self)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        time_label1 = ttk.Label(self.rowwin, text='Time: ')
        time_label1.pack(side=tk.LEFT)
        self.timelbl = tk.StringVar()
        self.timelbl.set('')
        time_label2 = ttk.Label(self.rowwin, textvariable=self.timelbl)
        time_label2.pack(side=tk.LEFT)
        self.newwin = ttk.Button(
            self.rowwin, text="New Window",
            command=partial(clone_ncvmain, self.master, self.fi, self.miss))
        self.newwin.pack(side=tk.RIGHT)

        # plotting canvas
        self.figure = Figure(facecolor="white", figsize=(1, 1))
        # self.axes   = self.figure.add_subplot(111)
        self.axes   = self.figure.add_subplot(111,
                                              projection=ccrs.PlateCarree())
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        # pack
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # grid instead of pack - does not work
        # self.canvas.get_tk_widget().grid(column=0, row=0,
        #     sticky=(tk.N, tk.S, tk.E, tk.W))
        # self.canvas.get_tk_widget().columnconfigure(0, weight=1)
        # self.canvas.get_tk_widget().rowconfigure(0, weight=1)

        # matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # selections and options
        columns = [''] + self.cols

        allcmaps = plt.colormaps()
        self.cmaps  = [ i for i in allcmaps if not i.endswith('_r') ]
        self.cmaps.sort()
        self.imaps  = [ tk.PhotoImage(file=os.path.dirname(__file__) +
                                      '/images/' + i + '.png')
                        for i in self.cmaps ]

        self.projs = ['AlbersEqualArea', 'AzimuthalEquidistant', 'EckertI',
                      'EckertII', 'EckertIII', 'EckertIV', 'EckertV',
                      'EckertVI', 'EqualEarth', 'EquidistantConic',
                      'InterruptedGoodeHomolosine',
                      'LambertAzimuthalEqualArea', 'LambertConformal',
                      'LambertCylindrical', 'Mercator', 'Miller', 'Mollweide',
                      'NorthPolarStereo', 'PlateCarree', 'Robinson',
                      'Sinusoidal', 'SouthPolarStereo', 'Stereographic']
        self.iprojs = [ccrs.AlbersEqualArea, ccrs.AzimuthalEquidistant,
                       ccrs.EckertI, ccrs.EckertII, ccrs.EckertIII,
                       ccrs.EckertIV, ccrs.EckertV, ccrs.EckertVI,
                       ccrs.EqualEarth, ccrs.EquidistantConic,
                       ccrs.InterruptedGoodeHomolosine,
                       ccrs.LambertAzimuthalEqualArea, ccrs.LambertConformal,
                       ccrs.LambertCylindrical, ccrs.Mercator, ccrs.Miller,
                       ccrs.Mollweide, ccrs.NorthPolarStereo, ccrs.PlateCarree,
                       ccrs.Robinson, ccrs.Sinusoidal, ccrs.SouthPolarStereo,
                       ccrs.Stereographic]

        # 1. row
        # controls
        self.rowt = ttk.Frame(self)
        self.rowt.pack(side=tk.TOP, fill=tk.X)
        ntime = 1
        self.tsteplbl, self.tstepval, self.tstep = add_scale(
            self.rowt, label="step", ini=0, from_=0, to=ntime,
            length=100, orient=tk.HORIZONTAL, command=self.tstep_t)
        spacet = ttk.Label(self.rowt, text=" "*1)
        spacet.pack(side=tk.LEFT)
        # first t
        self.first_t = ttk.Button(self.rowt, text="|<<", width=3,
                                  command=self.first_t)
        self.first_t.pack(side=tk.LEFT)
        # previous t
        self.prev_t = ttk.Button(self.rowt, text="|<", width=2,
                                 command=self.prev_t)
        self.prev_t.pack(side=tk.LEFT)
        # run t backwards
        self.prun_t = ttk.Button(self.rowt, text="<", width=1,
                                 command=self.prun_t)
        self.prun_t.pack(side=tk.LEFT)
        # pause t
        self.pause_t = ttk.Button(self.rowt, text="||", width=1,
                                  command=self.pause_t)
        self.pause_t.pack(side=tk.LEFT)
        # run t forward
        self.nrun_t = ttk.Button(self.rowt, text=">", width=1,
                                 command=self.nrun_t)
        self.nrun_t.pack(side=tk.LEFT)
        # next t
        self.next_t = ttk.Button(self.rowt, text=">|", width=2,
                                 command=self.next_t)
        self.next_t.pack(side=tk.LEFT)
        # last t
        self.last_t = ttk.Button(self.rowt, text=">>|", width=3,
                                 command=self.last_t)
        self.last_t.pack(side=tk.LEFT)
        # repeat
        spacer = ttk.Label(self.rowt, text=" "*1)
        spacer.pack(side=tk.LEFT)
        reps = ['once', 'repeat', 'reflect']
        self.repeatlbl, self.repeat = add_combobox(
            self.rowt, label="repeat", values=reps, width=5,
            command=self.repeat_t)
        self.repeat.set('repeat')
        self.last_t.pack(side=tk.LEFT)
        # delay
        spaced = ttk.Label(self.rowt, text=" "*1)
        spaced.pack(side=tk.LEFT)
        self.delaylbl, self.delayval, self.delay = add_scale(
            self.rowt, label="delay (ms)", ini=1, from_=1, to=1000,
            length=100, orient=tk.HORIZONTAL, command=self.delay_t)

        # 2. row
        # variable-axis selection
        self.rowvv = ttk.Frame(self)
        self.rowvv.pack(side=tk.TOP, fill=tk.X)
        self.blockv = ttk.Frame(self.rowvv)
        self.blockv.pack(side=tk.LEFT)
        self.rowv = ttk.Frame(self.blockv)
        self.rowv.pack(side=tk.TOP, fill=tk.X)
        self.vlbl = tk.StringVar()
        self.vlbl.set("var")
        vlab = ttk.Label(self.rowv, textvariable=self.vlbl)
        vlab.pack(side=tk.LEFT)
        self.bprev_v = ttk.Button(self.rowv, text="<", width=1,
                                  command=self.prev_v)
        self.bprev_v.pack(side=tk.LEFT)
        self.bnext_v = ttk.Button(self.rowv, text=">", width=1,
                                  command=self.next_v)
        self.bnext_v.pack(side=tk.LEFT)
        self.v = ttk.Combobox(self.rowv, values=columns, width=25)
        self.v.bind("<<ComboboxSelected>>", self.selected_v)
        self.v.pack(side=tk.LEFT)
        self.trans_vlbl, self.trans_v = add_checkbutton(
            self.rowv, label="transpose var", value=False, command=self.checked)
        spacev = ttk.Label(self.rowv, text=" "*1)
        spacev.pack(side=tk.LEFT)
        self.vminlbl, self.vmin = add_entry(self.rowv, label="vmin",
                                            text=0, width=11,
                                            command=self.entered_v)
        self.vmaxlbl, self.vmax = add_entry(self.rowv, label="vmax",
                                            text=1, width=11,
                                            command=self.entered_v)
        self.valllbl, self.vall = add_checkbutton(
            self.rowv, label="all", value=False, command=self.checked_all)
        # levels var
        self.rowvd = ttk.Frame(self.blockv)
        self.rowvd.pack(side=tk.TOP, fill=tk.X)
        self.vdlbl = []
        self.vdval = []
        self.vd    = []
        for i in range(self.maxdim):
            vdlbl, vdval, vd = add_spinbox(
                self.rowvd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_v, state=tk.DISABLED)
            self.vdlbl.append(vdlbl)
            self.vdval.append(vdval)
            self.vd.append(vd)

        # 3. row
        # lon-axis selection
        self.rowll = ttk.Frame(self)
        self.rowll.pack(side=tk.TOP, fill=tk.X)
        self.blocklon = ttk.Frame(self.rowll)
        self.blocklon.pack(side=tk.LEFT)
        self.rowlon = ttk.Frame(self.blocklon)
        self.rowlon.pack(side=tk.TOP, fill=tk.X)
        self.lonlbl, self.lon = add_combobox(self.rowlon, label="lon",
                                             values=columns,
                                             command=self.selected_lon)
        self.inv_lonlbl, self.inv_lon = add_checkbutton(
            self.rowlon, label="invert lon", value=False, command=self.checked)
        self.shift_lonlbl, self.shift_lon = add_checkbutton(
            self.rowlon, label="shift lon/2", value=False, command=self.checked)
        self.rowlond = ttk.Frame(self.blocklon)
        self.rowlond.pack(side=tk.TOP, fill=tk.X)
        self.londlbl = []
        self.londval = []
        self.lond    = []
        for i in range(self.maxdim):
            londlbl, londval, lond = add_spinbox(
                self.rowlond, label=str(i), values=(0,), wrap=True,
                command=self.spinned_lon, state=tk.DISABLED)
            self.londlbl.append(londlbl)
            self.londval.append(londval)
            self.lond.append(lond)
        # lat-axis selection
        spacex = ttk.Label(self.rowll, text=" "*3)
        spacex.pack(side=tk.LEFT)
        self.blocklat = ttk.Frame(self.rowll)
        self.blocklat.pack(side=tk.LEFT)
        self.rowlat = ttk.Frame(self.blocklat)
        self.rowlat.pack(side=tk.TOP, fill=tk.X)
        self.latlbl, self.lat = add_combobox(self.rowlat, label="lat",
                                             values=columns,
                                             command=self.selected_lat)
        self.inv_latlbl, self.inv_lat = add_checkbutton(
            self.rowlat, label="invert lat", value=False, command=self.checked)
        self.rowlatd = ttk.Frame(self.blocklat)
        self.rowlatd.pack(side=tk.TOP, fill=tk.X)
        self.latdlbl = []
        self.latdval = []
        self.latd    = []
        for i in range(self.maxdim):
            latdlbl, latdval, latd = add_spinbox(
                self.rowlatd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_lat, state=tk.DISABLED)
            self.latdlbl.append(latdlbl)
            self.latdval.append(latdval)
            self.latd.append(latd)

        # 4. row
        # options
        self.rowcmap = ttk.Frame(self)
        self.rowcmap.pack(side=tk.TOP, fill=tk.X)
        self.cmaplbl, self.cmap = add_imagemenu(
            self.rowcmap, label="cmap", values=self.cmaps,
            images=self.imaps, command=self.selected_cmap)
        self.cmap['text']  = 'RdYlBu'
        self.cmap['image'] = self.imaps[self.cmaps.index('RdYlBu')]
        self.rev_cmaplbl, self.rev_cmap = add_checkbutton(
            self.rowcmap, label="inverse cmap", value=False,
            command=self.checked)
        self.meshlbl, self.mesh = add_checkbutton(
            self.rowcmap, label="mesh", value=False,
            command=self.checked)
        self.coastlbl, self.coast = add_checkbutton(
            self.rowcmap, label="coast", value=True,
            command=self.checked)
        self.gridlbl, self.grid = add_checkbutton(
            self.rowcmap, label="grid", value=False,
            command=self.checked)

        # 7. row
        # projections
        self.rowproj = ttk.Frame(self)
        self.rowproj.pack(side=tk.TOP, fill=tk.X)
        self.projlbl, self.proj = add_menu(
            self.rowproj, label="projection", values=self.projs,
            command=self.selected_proj, width=26)
        self.proj['text'] = 'PlateCarree'
        self.clonlbl, self.clon = add_entry(self.rowproj, label="central lon",
                                            text='None', width=4,
                                            command=self.entered_clon)

        # set lat/lon
        if self.latvar:
            self.lat.set(self.latvar)
            self.inv_lat.set(0)
            set_dim_lat(self)
        if self.lonvar:
            self.lon.set(self.lonvar)
            self.inv_lon.set(0)
            self.shift_lon.set(0)
            set_dim_lon(self)

        # animation
        rep = self.repeat.get()
        if rep == 'repeat':
            irepeat = True
        else:
            irepeat = False
        self.anim_running = True
        self.anim_inc     = 1      # 1/-1: forward or backward run
        self.anim = animation.FuncAnimation(self.figure, self.update,
                                            init_func=self.redraw,
                                            interval=self.delayval.get(),
                                            repeat=irepeat)
        # self.anim.event_source.stop()
        # self.anim_running = False  # True/False: running or paused animation

    #
    # Bindings
    #

    def checked(self):
        """
        Command called if any checkbutton was checked or unchecked.

        Redraws plot.
        """
        self.redraw()

    def checked_all(self):
        """
        Command called if any checkbutton 'all' for vmin/vmax was checked or
        unchecked.

        Resets vmin/vmax, redraws plot.
        """
        vmin, vmax = self.get_vminmax()
        self.vmin.set(vmin)
        self.vmax.set(vmax)
        self.redraw()

    def delay_t(self, delay):
        """
        Command called if delay scale was changed.

        `delay` is the chosen value on the scale slider.
        """
        self.anim.event_source.interval = int(float(delay))

    def entered_clon(self, event):
        """
        Command called if values central longitude was entered.

        Triggering `event` was bound to entry.

        Redraws plot.
        """
        self.redraw()

    def entered_v(self, event):
        """
        Command called if values for `vmin`/`vmax` were entered.

        Triggering `event` was bound to entry.

        Redraws plot.
        """
        self.redraw()

    def first_t(self):
        """
        Command called if first frame button was pressed.
        """
        it = 0
        self.set_tstep(it)
        self.update(it, isframe=True)

    def last_t(self):
        """
        Command called if last frame button was pressed.
        """
        it = self.nunlim - 1
        self.set_tstep(it)
        self.update(it, isframe=True)

    def nrun_t(self):
        """
        Command called if forward run button was pressed.
        """
        if not self.anim_running:
            self.anim_inc = 1
            self.anim.event_source.start()
            self.anim_running = True

    def next_t(self):
        """
        Command called if next frame button was pressed.
        """
        it = int(self.vdval[self.iunlim].get())
        if it < self.nunlim-1:
            it += 1
            self.set_tstep(it)
            self.update(it, isframe=True)
        else:
            rep = self.repeat.get()
            if rep != 'once':
                if rep == 'repeat':
                    it = 0
                else:  # reflect
                    it -= 1
                self.set_tstep(it)
                self.update(it, isframe=True)

    def next_v(self):
        """
        Command called if next button for the plotting variable was pressed.

        Resets `vmin`/`vmax` and variable-dimensions. Redraws plot.
        """
        v = self.v.get()
        cols = self.v["values"]
        idx  = cols.index(v)
        idx += 1
        if idx < len(cols):
            self.v.set(cols[idx])
            self.set_unlim(cols[idx])
            self.tstep['to'] = self.nunlim - 1
            self.set_tstep(0)
            vmin, vmax = self.get_vminmax()
            self.vmin.set(vmin)
            self.vmax.set(vmax)
            set_dim_var(self)
            self.redraw()

    def pause_t(self):
        """
        Command called if pause button was pressed.
        """
        if self.anim_running:
            self.anim.event_source.stop()
            self.anim_running = False

    def prev_t(self):
        """
        Command called if previous frame button was pressed.
        """
        it = int(self.vdval[self.iunlim].get())
        if it > 0:
            it -= 1
            self.set_tstep(it)
            self.update(it, isframe=True)
        else:
            rep = self.repeat.get()
            if rep != 'once':
                if rep == 'repeat':
                    it = self.nunlim - 1
                else:  # reflect
                    it += 1
                self.set_tstep(it)
                self.update(it, isframe=True)

    def prev_v(self):
        """
        Command called if previous button for the plotting variable was
        pressed.

        Resets `vmin`/`vmax` and v-dimensions. Redraws plot.
        """
        v = self.v.get()
        cols = self.v["values"]
        idx  = cols.index(v)
        idx -= 1
        if idx > 0:
            self.v.set(cols[idx])
            self.set_unlim(cols[idx])
            self.tstep['to'] = self.nunlim - 1
            self.set_tstep(0)
            vmin, vmax = self.get_vminmax()
            self.vmin.set(vmin)
            self.vmax.set(vmax)
            set_dim_var(self)
            self.redraw()

    def prun_t(self):
        """
        Command called if run backwards button was pressed.
        """
        if not self.anim_running:
            self.anim_inc = -1
            self.anim.event_source.start()
            self.anim_running = True

    def repeat_t(self, event):
        """
        Command called if repeat option was chosen with combobox.

        Triggering `event` was bound to the combobox.
        """
        rep = self.repeat.get()
        if rep == 'once':
            irepeat = False
        else:
            # need not to stop also for reflect
            irepeat = True
        self.anim.repeat = irepeat

    def selected_cmap(self, value):
        """
        Command called if cmap was chosen from menu.

        `value` is the chosen colormap.

        Sets text and image on the menubutton.
        """
        self.cmap['text']  = value
        self.cmap['image'] = self.imaps[self.cmaps.index(value)]
        self.redraw()

    def selected_lat(self, event):
        """
        Command called if latitude-variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `lat` options and dimensions. Redraws plot.
        """
        self.inv_lat.set(0)
        set_dim_lat(self)
        self.redraw()

    def selected_lon(self, event):
        """
        Command called if x-variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `x` options and dimensions. Redraws plot.
        """
        self.inv_lon.set(0)
        self.shift_lon.set(0)
        set_dim_lon(self)
        self.redraw()

    def selected_proj(self, value):
        """
        Command called if projection was chosen from menu.

        `value` is the chosen projection.

        Sets text on the menubutton.
        """
        self.proj['text'] = value
        self.redraw()

    def selected_v(self, event):
        """
        Command called if plotting variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `vmin`/`vmax` and variable-dimensions. Redraws plot.
        """
        v = self.v.get()
        self.set_unlim(v)
        self.tstep['to'] = self.nunlim - 1
        self.set_tstep(0)
        vmin, vmax = self.get_vminmax()
        self.vmin.set(vmin)
        self.vmax.set(vmax)
        set_dim_var(self)
        self.redraw()

    def spinned_lon(self, event=None):
        """
        Command called if spinbox of x-dimensions was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.
        """
        self.redraw()

    def spinned_lat(self, event=None):
        """
        Command called if spinbox of latitude-dimensions was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.
        """
        self.redraw()

    def spinned_v(self, event=None):
        """
        Command called if spinbox of variable-dimensions was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.
        """
        self.redraw()

    def tstep_t(self, step):
        """
        Command called if tstep was changed.

        `step` is the chosen value on the scale slider.
        """
        it = int(float(step))
        self.set_tstep(it)
        self.update(it, isframe=True)

    #
    # Methods
    #

    def get_vminmax(self):
        from numpy.random import default_rng
        v = self.v.get()
        if (v != ''):
            vz = v.split()[0]
            vv = self.fi.variables[vz]
            miss = get_miss(self, vv)
            all  = self.vall.get()
            if all or (np.sum(vv.shape[:-2]) < 100):
                vv   = set_miss(miss, vv)
                vmin = np.nanmin(vv)
                vmax = np.nanmax(vv)
            else:
                rng = default_rng()
                vmin = np.inf
                vmax = -np.inf
                for nn in range(100):
                    ss = []
                    for i in range(vv.ndim):
                        if i < vv.ndim-2:
                            idim = rng.integers(0, vv.shape[i])
                            s = slice(idim, idim+1)
                        else:
                            s = slice(0, vv.shape[i])
                        ss.append(s)
                    ivv   = vv[tuple(ss)]
                    ivv   = set_miss(miss, ivv)
                    ivmin = np.nanmin(ivv)
                    ivmax = np.nanmax(ivv)
                    vmin  = min(vmin, ivmin)
                    vmax  = max(vmax, ivmax)
            return (vmin, vmax)
        else:
            return (0, 1)

    def set_tstep(self, it):
        """
        Make all steps when changing time step.

        `it` (int) is the time step.

        Sets the time dimension spinbox, sets the time step scale,
        write the time on top.
        """
        self.vdval[self.iunlim].set(it)
        self.tstepval.set(it)
        try:
            self.timelbl.set(np.around(self.time[it], 4))
        except TypeError:
            self.timelbl.set(self.time[it])

    def set_unlim(self, v):
        """
        Set index and length of unlimited dimension of variable `v`.

        `v` (str) is the variable name as in the selection comboboxes, i.e.
        `var = self.fi.variables[v.split()[0]]`.

        Sets `self.nunlim` to the length of the unlimited dimension and
        `self.iunlim` to the index in variable.dimensions if
        `self.dunlim ~= ''` and `self.dunlim` in var.dimensions.

        Takes `self.iunlim=0` and `self.nunlim=variable.shape[0]` if
        self.dunlim == ''` or `self.dunlim` not in var.dimensions.
        """
        vz = v.split()[0]
        if vz == self.tname:
            self.iunlim = 0
            self.nunlim = self.time.size
        else:
            if self.dunlim:
                if self.dunlim in self.fi.variables[vz].dimensions:
                    self.iunlim = (
                        self.fi.variables[vz].dimensions.index(self.dunlim))
                else:
                    self.iunlim = 0
            else:
                self.iunlim = 0
            self.nunlim = self.fi.variables[vz].shape[self.iunlim]

    #
    # Plotting
    #

    def redraw(self):
        """
        Redraws the plot.

        Reads `lon`, `lat`, `variable` names, the current settings of
        their dimension spinboxes, as well as all other plotting options.
        Then redraws the plot.
        """
        # get all states
        # rowv
        v = self.v.get()
        trans_v = self.trans_v.get()
        vmin = self.vmin.get()
        if vmin == 'None':
            vmin = None
        else:
            vmin = float(vmin)
        vmax = self.vmax.get()
        if vmax == 'None':
            vmax = None
        else:
            vmax = float(vmax)
        # rowll
        x = self.lon.get()
        y = self.lat.get()
        inv_lon   = self.inv_lon.get()
        inv_lat   = self.inv_lat.get()
        shift_lon = self.shift_lon.get()
        # rowcmap
        cmap     = self.cmap['text']
        rev_cmap = self.rev_cmap.get()
        mesh     = self.mesh.get()
        grid     = self.grid.get()
        coast    = self.coast.get()
        proj     = self.proj['text']
        self.iproj = self.iprojs[self.projs.index(proj)]
        clon     = self.clon.get()
        # set x, y, axes labels
        vx = 'None'
        vy = 'None'
        vz = 'None'
        if (v != ''):
            # variable
            vz = v.split()[0]
            if vz == self.tname:
                # should throw an error later
                if mesh:
                    vv = self.dtime
                    vlab = 'Year'
                else:
                    vv = self.time
                    vlab = 'Date'
            else:
                vv = self.fi.variables[vz]
                vlab = set_axis_label(vv)
            vv = get_slice_miss(self, self.vd, vv)
            if trans_v:
                vv = vv.T
            if shift_lon:
                vv = np.roll(vv, vv.shape[1]//2, axis=1)
        else:
            vlab = ''
        if (y != ''):
            # y axis
            vy = y.split()[0]
            if vy == self.tname:
                if mesh:
                    yy = self.dtime
                    ylab = 'Year'
                else:
                    yy = self.time
                    ylab = 'Date'
            else:
                yy   = self.fi.variables[vy]
                ylab = set_axis_label(yy)
            yy = get_slice_miss(self, self.latd, yy)
        else:
            ylab = ''
        if (x != ''):
            # x axis
            vx = x.split()[0]
            if vx == self.tname:
                if mesh:
                    xx = self.dtime
                    xlab = 'Year'
                else:
                    xx = self.time
                    xlab = 'Date'
            else:
                xx   = self.fi.variables[vx]
                xlab = set_axis_label(xx)
            xx = get_slice_miss(self, self.lond, xx)
            # set central longitude of projection
            # round it to get 0 or 180 even if mid points are is on 0,
            # for example
            dxx = np.diff(xx).mean()
            self.ixxmean = np.around(xx.mean()/dxx, 0) * dxx
        else:
            xlab = ''
            self.ixxmean = 0.
        if clon != 'None':
            self.iclon = float(clon)
        else:
            self.iclon = self.ixxmean
        # plot options
        if rev_cmap:
            cmap = cmap + '_r'
        # Clear figure instead of axes because colorbar is on figure
        self.figure.clear()
        # Have to add axes again.
        self.axes = self.figure.add_subplot(
            111, projection=self.iproj(central_longitude=self.iclon))
        # plot only if variable given
        if (v != ''):
            if vv.ndim < 2:
                estr  = 'Map: var (' + vz + ') is not 2-dimensional:'
                print(estr, vv.shape)
                return
            # set x and y to index if not selected
            if (x == ''):
                nx = vv.shape[1]
                xx = -180. + np.arange(nx) * 360./float(nx)
                xx += 0.5 * (xx[1] - xx[0])
                xlab = ''
            if (y == ''):
                ny = vv.shape[0]
                yy = np.arange(ny) * 180./float(ny) - 90.
                yy += 0.5 * (yy[1] - yy[0])
                ylab = ''
            # plot
            # cc = self.axes.imshow(vv[:, ::-1].T, aspect='auto', cmap=cmap,
            #                       interpolation='none')
            # cc = self.axes.matshow(vv[:, ::-1].T, aspect='auto', cmap=cmap,
            #                        interpolation='none')
            extend = 'neither'
            if vmin is not None:
                vv = np.maximum(vv, vmin)
                if vmax is None:
                    extend = 'min'
                else:
                    extend = 'both'
            if vmax is not None:
                vv = np.minimum(vv, vmax)
                if vmin is None:
                    extend = 'max'
                else:
                    extend = 'both'
            if (xx.ndim == 1) and (yy.ndim == 1):
                self.ixx, self.iyy = np.meshgrid(xx, yy)
            elif (xx.ndim == 1) and (yy.ndim == 2):
                self.ixx, tmp = np.meshgrid(xx, yy[:, 0])
                self.iyy = yy
            elif (xx.ndim == 2) and (yy.ndim == 1):
                self.ixx, self.iyy = np.meshgrid(xx, yy)
                tmp, self.iyy = np.meshgrid(xx[0, :], yy)
                self.ixx = xx
            elif (xx.ndim == 2) and (yy.ndim == 2):
                self.ixx = xx
                self.iyy = yy
            else:
                estr  = 'Map: lon (' + vx + '), lat (' + vy + ')'
                estr += ' dimensions not 1D or 2D:'
                print(estr, xx.shape, yy.shape)
                return
            if inv_lon:
                self.ixx = np.fliplr(self.ixx)
            if inv_lat:
                self.iyy = np.flipud(self.iyy)
            # cartopy.contourf needs cyclic longitude for wrap around
            self.ixxc = np.append(self.ixx, self.ixx[:, -1:] +
                                  self.ixx[:, -1:] - self.ixx[:, -2:-1],
                                  axis=1)
            self.iyyc = np.append(self.iyy, self.iyy[:, -1:], axis=1)
            self.ivv     = vv
            self.itransform = ccrs.PlateCarree()
            self.ivmin   = vmin
            self.ivmax   = vmax
            self.icmap   = cmap
            self.iextend = extend
            # self.img_extent = (xx.min(), xx.max(), yy.min(), yy.max())
            if mesh:
                try:
                    # vv is matrix notation: (row, col)
                    # self.cc = self.axes.pcolormesh(
                    #     xx, yy, vv, vmin=vmin, vmax=vmax, cmap=cmap,
                    #     shading='nearest')
                    self.cc = self.axes.pcolormesh(
                        self.ixx, self.iyy, self.ivv,
                        vmin=self.ivmin, vmax=self.ivmax,
                        cmap=self.icmap, shading='nearest',
                        transform=self.itransform)
                    # self.cc = self.axes.imshow(
                    #     vv, vmin=vmin, vmax=vmax, cmap=cmap,
                    #     origin='upper', extent=self.img_extent,
                    #     transform=self.itransform)
                    self.cb = self.figure.colorbar(self.cc, fraction=0.05,
                                                   shrink=0.75,
                                                   extend=self.iextend)
                except Exception:
                    estr  = 'Map pcolormesh: lon (' + vx + '), '
                    estr += ' lat (' + vy + '), var (' + vz + ') shapes do not'
                    estr += ' match:'
                    print(estr, self.ixx.shape, self.iyy.shape, self.ivv.shape)
                    return
            else:
                try:
                    # if 1-D then len(x)==m (columns) and
                    #     len(y)==n (rows): v(n,m)
                    self.ivvc = add_cyclic_point(self.ivv)
                    self.cc = self.axes.contourf(
                        self.ixxc, self.iyyc, self.ivvc,
                        vmin=self.ivmin, vmax=self.ivmax,
                        cmap=self.icmap, extend=self.iextend,
                        transform=self.itransform)
                    self.cb = self.figure.colorbar(self.cc, fraction=0.05,
                                                   shrink=0.75)
                    # self.cc, = self.axes.plot(yy, vv[0,:])
                except Exception:
                    estr  = 'Map contourf: lon (' + vx + '), lat (' + vy + '),'
                    estr += ' var (' + vz + ') shapes do not match for:'
                    print(estr, self.ixxc.shape, self.iyyc.shape,
                          self.ivvc.shape)
                    return
            self.cb.set_label(vlab)
        # help(self.figure)
        if coast:
            self.axes.coastlines()
            self.axes.gridlines(draw_labels=True, linewidth=0,
                                x_inline=False, y_inline=False)
        self.axes.xaxis.set_label_text(xlab)
        self.axes.yaxis.set_label_text(ylab)
        if grid:
            self.axes.gridlines(draw_labels=False,
                                x_inline=False, y_inline=False)
        # redraw
        self.canvas.draw()
        self.toolbar.update()
        self.anim.event_source.stop()
        self.anim_running = False

    def update(self, frame, isframe=False):
        """
        Updates data of the current the plot.
        """
        # variable
        v = self.v.get()
        if (v != ''):
            trans_v   = self.trans_v.get()
            mesh      = self.mesh.get()
            rep       = self.repeat.get()
            inv_lon   = self.inv_lon.get()
            inv_lat   = self.inv_lat.get()
            shift_lon = self.shift_lon.get()
            vz = v.split()[0]
            vv = self.fi.variables[vz]
            # slice
            try:
                it = int(self.vdval[self.iunlim].get())
                if not isframe:
                    if (self.anim_inc == 1) and (it == self.nunlim-1):
                        if rep == 'repeat':
                            it = 0
                        elif rep == 'reflect':
                            self.anim_inc = -1
                            it += self.anim_inc
                        else:  # once
                            self.anim.event_source.stop()
                            self.anim_running = False
                    elif (self.anim_inc == -1) and (it == 0):
                        if rep == 'repeat':
                            it = self.nunlim - 1
                        elif rep == 'reflect':
                            self.anim_inc = 1
                            it += self.anim_inc
                        else:  # once
                            self.anim.event_source.stop()
                            self.anim_running = False
                    else:
                        it += self.anim_inc
            except ValueError:
                it = 0
            self.set_tstep(it)
            vv = get_slice_miss(self, self.vd, vv)
            if trans_v:
                vv = vv.T
            if shift_lon:
                vv = np.roll(vv, vv.shape[1]//2, axis=1)
            self.ivv = vv
            # set data
            if mesh:
                # update works well on "normal" pcolormesh but not on Cartopy's
                # self.cc.set_array(vv)
                # Both, imshow and pcolormesh need to remove the old
                # image.AxesImage or collections.QuadMesh first and then redraw
                # because the set_data (imshow) and set_array (pcolormesh) do
                # not respect transformations.
                self.cc.remove()
                self.cc = self.axes.pcolormesh(
                    self.ixx, self.iyy, self.ivv,
                    vmin=self.ivmin, vmax=self.ivmax,
                    cmap=self.icmap, shading='nearest',
                    transform=self.itransform)
                # self.cc.remove()
                # self.cc = self.axes.imshow(
                #     vv, vmin=self.ivmin, vmax=self.ivmax, cmap=self.icmap,
                #     origin='upper', extent=self.img_extent,
                #     transform=self.itransform)
            else:
                # http://matplotlib.1069221.n5.nabble.com/update-an-existing-contour-plot-with-new-data-td23889.html
                for coll in self.cc.collections:
                    self.axes.collections.remove(coll)
                self.ivvc = add_cyclic_point(self.ivv)
                self.cc = self.axes.contourf(
                    self.ixxc, self.iyyc, self.ivvc,
                    vmin=self.ivmin, vmax=self.ivmax,
                    cmap=self.icmap, extend=self.iextend,
                    transform=self.itransform)
            self.canvas.draw()
            return self.cc,
