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
from .ncvmethods import set_dim_x, set_dim_y, set_dim_zmap
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_scale, add_spinbox
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
        self.axes   = self.figure.add_subplot(111, projection=ccrs.PlateCarree(central_longitude=180.))
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
            self.rowt, label="delay (ms)", ini=200, from_=0, to=1000,
            length=100, orient=tk.HORIZONTAL, command=self.delay_t)

        # 2. row
        # z-axis selection
        self.rowz = ttk.Frame(self)
        self.rowz.pack(side=tk.TOP, fill=tk.X)
        # self.zlbl, self.z = add_combobox(self.rowz, label="z",
        #                                  values=columns,
        #                                  command=self.selected_z)
        self.zlbl = tk.StringVar()
        self.zlbl.set("var")
        zlab = ttk.Label(self.rowz, textvariable=self.zlbl)
        zlab.pack(side=tk.LEFT)
        # previous z
        self.bprev_z = ttk.Button(self.rowz, text="<", width=1,
                                  command=self.prev_z)
        self.bprev_z.pack(side=tk.LEFT)
        # next z
        self.bnext_z = ttk.Button(self.rowz, text=">", width=1,
                                  command=self.next_z)
        self.bnext_z.pack(side=tk.LEFT)
        self.z = ttk.Combobox(self.rowz, values=columns, width=25)
        self.z.bind("<<ComboboxSelected>>", self.selected_z)
        self.z.pack(side=tk.LEFT)
        self.trans_zlbl, self.trans_z = add_checkbutton(
            self.rowz, label="transpose", value=False, command=self.checked)
        spacez = ttk.Label(self.rowz, text=" "*1)
        spacez.pack(side=tk.LEFT)
        self.zminlbl, self.zmin = add_entry(self.rowz, label="vmin",
                                            text=0, width=7,
                                            command=self.entered_z)
        self.zmaxlbl, self.zmax = add_entry(self.rowz, label="vmax",
                                            text=1, width=7,
                                            command=self.entered_z)
        self.valllbl, self.vall = add_checkbutton(
            self.rowz, label="all", value=False, command=self.checked_all)

        # 3. row
        # levels z
        self.rowzlev = ttk.Frame(self)
        self.rowzlev.pack(side=tk.TOP, fill=tk.X)
        self.zdlbl = []
        self.zdval = []
        self.zd    = []
        for i in range(self.maxdim):
            zdlbl, zdval, zd = add_spinbox(
                self.rowzlev, label=str(i), values=(0,), wrap=True,
                command=self.spinned_z, state=tk.DISABLED)
            self.zdlbl.append(zdlbl)
            self.zdval.append(zdval)
            self.zd.append(zd)

        # 4. row
        # x- and y-axis selection
        self.rowxy = ttk.Frame(self)
        self.rowxy.pack(side=tk.TOP, fill=tk.X)
        self.xlbl, self.x = add_combobox(self.rowxy, label="x",
                                         values=columns,
                                         command=self.selected_x)
        self.inv_xlbl, self.inv_x = add_checkbutton(
            self.rowxy, label="invert x", value=False, command=self.checked)
        spacex = ttk.Label(self.rowxy, text=" "*3)
        spacex.pack(side=tk.LEFT)
        self.ylbl, self.y = add_combobox(self.rowxy, label="y",
                                         values=columns,
                                         command=self.selected_y)
        self.inv_ylbl, self.inv_y = add_checkbutton(
            self.rowxy, label="invert y", value=False, command=self.checked)

        # 5. row
        # levels x and y
        self.rowxylev = ttk.Frame(self)
        self.rowxylev.pack(side=tk.TOP, fill=tk.X)
        self.xdlbl = []
        self.xdval = []
        self.xd    = []
        for i in range(self.maxdim):
            xdlbl, xdval, xd = add_spinbox(
                self.rowxylev, label=str(i), values=(0,), wrap=True,
                command=self.spinned_x, state=tk.DISABLED)
            self.xdlbl.append(xdlbl)
            self.xdval.append(xdval)
            self.xd.append(xd)
        spacexy = ttk.Label(self.rowxylev, text=" "*10)
        spacexy.pack(side=tk.LEFT)
        self.ydlbl = []
        self.ydval = []
        self.yd    = []
        for i in range(self.maxdim):
            ydlbl, ydval, yd = add_spinbox(
                self.rowxylev, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y, state=tk.DISABLED)
            self.ydlbl.append(ydlbl)
            self.ydval.append(ydval)
            self.yd.append(yd)

        # 6. row
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
        self.gridlbl, self.grid = add_checkbutton(
            self.rowcmap, label="grid", value=False,
            command=self.checked)

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
        zmin, zmax = self.get_zminmax()
        self.zmin.set(zmin)
        self.zmax.set(zmax)
        self.redraw()

    def delay_t(self, delay):
        """
        Command called if delay scale was changed.

        `delay` is the chosen value on the scale slider.
        """
        self.anim.event_source.interval = int(float(delay)) + 1  # avoid 0

    def entered_z(self, event):
        """
        Command called if values for `zmin`/`zmax` were entered.

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
        it = int(self.zdval[self.iunlim].get())
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

    def next_z(self):
        """
        Command called if next button for the plotting variable was pressed.

        Resets `zmin`/`zmax` and z-dimensions, resets `x` and `y` variables
        as well as their options and dimensions. Redraws plot.
        """
        z = self.z.get()
        cols = self.z["values"]
        idx  = cols.index(z)
        idx += 1
        if idx < len(cols):
            self.z.set(cols[idx])
            self.set_unlim(cols[idx])
            self.tstep['to'] = self.nunlim - 1
            zmin, zmax = self.get_zminmax()
            self.zmin.set(zmin)
            self.zmax.set(zmax)
            set_dim_zmap(self)
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
        it = int(self.zdval[self.iunlim].get())
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

    def prev_z(self):
        """
        Command called if previous button for the plotting variable was
        pressed.

        Resets `zmin`/`zmax` and z-dimensions, resets `x` and `y` variables
        as well as their options and dimensions. Redraws plot.
        """
        z = self.z.get()
        cols = self.z["values"]
        idx  = cols.index(z)
        idx -= 1
        if idx > 0:
            self.z.set(cols[idx])
            self.set_unlim(cols[idx])
            self.tstep['to'] = self.nunlim - 1
            zmin, zmax = self.get_zminmax()
            self.zmin.set(zmin)
            self.zmax.set(zmax)
            set_dim_zmap(self)
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

    def selected_x(self, event):
        """
        Command called if x-variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `x` options and dimensions. Redraws plot.
        """
        self.inv_x.set(0)
        set_dim_x(self)
        self.redraw()

    def selected_y(self, event):
        """
        Command called if y-variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `y` options and dimensions. Redraws plot.
        """
        self.inv_y.set(0)
        set_dim_y(self)
        self.redraw()

    def selected_z(self, event):
        """
        Command called if plotting variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `zmin`/`zmax` and z-dimensions, resets `x` and `y` variables
        as well as their options and dimensions. Redraws plot.
        """
        z = self.z.get()
        self.set_unlim(z)
        self.tstep['to'] = self.nunlim - 1
        zmin, zmax = self.get_zminmax()
        self.zmin.set(zmin)
        self.zmax.set(zmax)
        set_dim_zmap(self)
        self.redraw()

    def spinned_x(self, event=None):
        """
        Command called if spinbox of x-dimensions was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.
        """
        self.redraw()

    def spinned_y(self, event=None):
        """
        Command called if spinbox of y-dimensions was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.
        """
        self.redraw()

    def spinned_z(self, event=None):
        """
        Command called if spinbox of z-dimensions was changed.

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

    def get_zminmax(self):
        from numpy.random import default_rng
        z = self.z.get()
        if (z != ''):
            vz = z.split()[0]
            zz = self.fi.variables[vz]
            miss = get_miss(self, zz)
            all  = self.vall.get()
            if all or (np.sum(zz.shape[:-2]) < 100):
                zz   = set_miss(miss, zz)
                zmin = np.nanmin(zz)
                zmax = np.nanmax(zz)
            else:
                rng = default_rng()
                zmin = np.inf
                zmax = -np.inf
                for nn in range(100):
                    ss = []
                    for i in range(zz.ndim):
                        if i < zz.ndim-2:
                            idim = rng.integers(0, zz.shape[i])
                            s = slice(idim, idim+1)
                        else:
                            s = slice(0, zz.shape[i])
                        ss.append(s)
                    izz   = zz[tuple(ss)]
                    izz   = set_miss(miss, izz)
                    izmin = np.nanmin(izz)
                    izmax = np.nanmax(izz)
                    zmin  = min(zmin, izmin)
                    zmax  = max(zmax, izmax)
            return (zmin, zmax)
        else:
            return (0, 1)

    def set_tstep(self, it):
        """
        Make all steps when changing time step.

        `it` (int) is the time step.

        Sets the time dimension spinbox, sets the time step scale,
        write the time on top.
        """
        self.zdval[self.iunlim].set(it)
        self.tstepval.set(it)
        try:
            self.timelbl.set(np.around(self.time[it], 4))
        except TypeError:
            self.timelbl.set(self.time[it])

    def set_unlim(self, z):
        """
        Set index and length of unlimited dimension of variable `z`.

        `z` (str) is the variable name as in the selection comboboxes, i.e.
        `var = self.fi.variables[z.split()[0]]`.

        Sets `self.nunlim` to the length of the unlimited dimension and
        `self.iunlim` to the index in variable.dimensions if
        `self.dunlim ~= ''` and `self.dunlim` in var.dimensions.

        Takes `self.iunlim=0` and `self.nunlim=variable.shape[0]` if
        self.dunlim == ''` or `self.dunlim` not in var.dimensions.
        """
        vz = z.split()[0]
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

        Reads `x`, `y`, `z` variable names, the current settings of
        their dimension spinboxes, as well as all other plotting options.
        Then redraws the plot.
        """
        # get all states
        # rowz
        z = self.z.get()
        trans_z = self.trans_z.get()
        zmin = self.zmin.get()
        if zmin == 'None':
            zmin = None
        else:
            zmin = float(zmin)
        zmax = self.zmax.get()
        if zmax == 'None':
            zmax = None
        else:
            zmax = float(zmax)
        # rowxy
        x = self.x.get()
        y = self.y.get()
        inv_x = self.inv_x.get()
        inv_y = self.inv_y.get()
        # rowcmap
        cmap = self.cmap['text']
        rev_cmap = self.rev_cmap.get()
        mesh = self.mesh.get()
        grid = self.grid.get()
        # Clear figure instead of axes because colorbar is on figure
        # Have to add axes again.
        self.figure.clear()
        # self.axes = self.figure.add_subplot(111)
        self.axes = self.figure.add_subplot(111, projection=ccrs.PlateCarree(central_longitude=180.))
        xlim  = [None, None]
        ylim  = [None, None]
        # set x, y, axes labels
        vx = 'None'
        vy = 'None'
        vz = 'None'
        if (z != ''):
            # z axis
            vz = z.split()[0]
            if vz == self.tname:
                # should throw an error later
                if mesh:
                    zz = self.dtime
                    zlab = 'Year'
                else:
                    zz = self.time
                    zlab = 'Date'
            else:
                zz = self.fi.variables[vz]
                zlab = set_axis_label(zz)
            zz = get_slice_miss(self, self.zd, zz)
            if trans_z:
                zz = zz.T
            if inv_x:
                zz = np.fliplr(zz)
            if inv_y:
                zz = np.flipud(zz)
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
            yy = get_slice_miss(self, self.yd, yy)
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
            xx = get_slice_miss(self, self.xd, xx)
        # set z to nan if not selected
        if (z == ''):
            if (x != ''):
                nx = xx.shape[0]
            else:
                nx = 360
            if (y != ''):
                ny = yy.shape[0]
            else:
                ny = 180
            zz = np.ones((ny, nx)) * np.nan
            zlab = ''
        if zz.ndim < 2:
            estr  = 'Contour: z (' + vz + ') is not 2-dimensional:'
            print(estr, zz.shape)
            return
        # set x and y to index if not selected
        if (x == ''):
            nx = zz.shape[1]
            xx = np.arange(nx) * 360./float(nx)
            xx += 0.5 * (xx[1] - xx[0])
            xlab = ''
        if (y == ''):
            ny = zz.shape[0]
            yy = np.arange(ny) * 180./float(ny) - 90.
            yy += 0.5 * (yy[1] - yy[0])
            ylab = ''
        # plot options
        if rev_cmap:
            cmap = cmap + '_r'
        # plot
        # cc = self.axes.imshow(zz[:, ::-1].T, aspect='auto', cmap=cmap,
        #                       interpolation='none')
        # cc = self.axes.matshow(zz[:, ::-1].T, aspect='auto', cmap=cmap,
        #                        interpolation='none')
        extend = 'neither'
        if zmin is not None:
            zz = np.maximum(zz, zmin)
            if zmax is None:
                extend = 'min'
            else:
                extend = 'both'
        if zmax is not None:
            zz = np.minimum(zz, zmax)
            if zmin is None:
                extend = 'max'
            else:
                extend = 'both'
        self.ixxmean = xx.mean()
        self.ixx, self.iyy = np.meshgrid(xx, yy)
        # cartopy.contourf needs cyclic longitude for wrap around
        self.ixxc = np.append(self.ixx, self.ixx[:, -1:] + self.ixx[:, -1:] -
                              self.ixx[:, -2:-1], axis=1)
        self.iyyc = np.append(self.iyy, self.iyy[:, -1:], axis=1)
        self.izz     = zz
        self.idata_transform = ccrs.PlateCarree()
        self.izmin   = zmin
        self.izmax   = zmax
        self.icmap   = cmap
        self.iextend = extend
        # self.img_extent = (xx.min(), xx.max(), yy.min(), yy.max())
        if mesh:
            try:
                # zz is matrix notation: (row, col)
                # self.cc = self.axes.pcolormesh(
                #     xx, yy, zz, vmin=zmin, vmax=zmax, cmap=cmap,
                #     shading='nearest')
                self.cc = self.axes.pcolormesh(
                    self.ixx, self.iyy, self.izz,
                    vmin=self.izmin, vmax=self.izmax,
                    cmap=self.icmap, shading='nearest',
                    transform=self.idata_transform)
                # self.cc = self.axes.imshow(
                #     zz, vmin=zmin, vmax=zmax, cmap=cmap,
                #     origin='upper', extent=self.img_extent,
                #     transform=self.idata_transform)
                self.cb = self.figure.colorbar(self.cc, fraction=0.05,
                                               shrink=0.75,
                                               extend=self.iextend)
            except Exception:
                estr  = 'Contour: x (' + vx + '), y (' + vy + '),'
                estr += ' z (' + vz + ') shapes do not match for'
                estr += ' pcolormesh:'
                print(estr, self.ixx.shape, self.iyy.shape, self.izz.shape)
                return
        else:
            try:
                # if 1-D then len(x)==m (columns) and len(y)==n (rows): z(n,m)
                # self.cc = self.axes.contourf(xx, yy, zz, vmin=zmin,
                #                              vmax=zmax, cmap=cmap,
                #                              extend=extend)
                self.izzc = add_cyclic_point(self.izz)
                self.cc = self.axes.contourf(
                    self.ixxc, self.iyyc, self.izzc,
                    vmin=self.izmin, vmax=self.izmax,
                    cmap=self.icmap, extend=self.iextend,
                    transform=self.idata_transform)
                self.cb = self.figure.colorbar(self.cc, fraction=0.05,
                                               shrink=0.75)
                # self.cc, = self.axes.plot(yy, zz[0,:])
            except Exception:
                estr  = 'Contour: x (' + vx + '), y (' + vy + '),'
                estr += ' z (' + vz + ') shapes do not match for'
                estr += ' contourf:'
                print(estr, self.ixxc.shape, self.iyyc.shape, self.izzc.shape)
                return
        # help(self.figure)
        self.axes.coastlines()
        self.axes.gridlines(draw_labels=True, linewidth=0)
        self.cb.set_label(zlab)
        self.axes.xaxis.set_label_text(xlab)
        self.axes.yaxis.set_label_text(ylab)
        if grid:
            self.axes.gridlines(draw_labels=False)
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
        z = self.z.get()
        if (z != ''):
            trans_z = self.trans_z.get()
            mesh    = self.mesh.get()
            rep     = self.repeat.get()
            inv_x   = self.inv_x.get()
            inv_y   = self.inv_y.get()
            vz = z.split()[0]
            zz = self.fi.variables[vz]
            # slice
            try:
                it = int(self.zdval[self.iunlim].get())
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
            zz = get_slice_miss(self, self.zd, zz)
            if trans_z:
                zz = zz.T
            if inv_x:
                zz = np.fliplr(zz)
            if inv_y:
                zz = np.flipud(zz)
            self.izz = zz
            # set data
            if mesh:
                # update works well on "normal" pcolormesh but not on Cartopy's
                # self.cc.set_array(zz)
                # Both, imshow and pcolormesh need to remove the old
                # image.AxesImage or collections.QuadMesh first and then redraw
                # because the set_data (imshow) and set_array (pcolormesh) do
                # not respect transformations.
                self.cc.remove()
                self.cc = self.axes.pcolormesh(
                    self.ixx, self.iyy, self.izz,
                    vmin=self.izmin, vmax=self.izmax,
                    cmap=self.icmap, shading='nearest',
                    transform=self.idata_transform)
                # self.cc.remove()
                # self.cc = self.axes.imshow(
                #     zz, vmin=self.izmin, vmax=self.izmax, cmap=self.icmap,
                #     origin='upper', extent=self.img_extent,
                #     transform=self.idata_transform)
            else:
                # http://matplotlib.1069221.n5.nabble.com/update-an-existing-contour-plot-with-new-data-td23889.html
                for coll in self.cc.collections:
                    self.axes.collections.remove(coll)
                self.izzc = add_cyclic_point(self.izz)
                self.cc = self.axes.contourf(
                    self.ixxc, self.iyyc, self.izzc,
                    vmin=self.izmin, vmax=self.izmax,
                    cmap=self.icmap, extend=self.iextend,
                    transform=self.idata_transform)
            self.canvas.draw()
            return self.cc,
