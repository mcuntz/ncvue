#!/usr/bin/env python
"""
Contour panel of ncvue.

The panel allows plotting contour or mesh plots of 2D-variables.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* Open new netcdf file, communicate via top widget, Jan 2021, Matthias Cuntz

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvContour
"""
from __future__ import absolute_import, division, print_function
import sys
import tkinter as tk
try:
    import tkinter.ttk as ttk
except Exception:
    print('Using the themed widget set introduced in Tk 8.5.')
    sys.exit()
from tkinter import filedialog
import os
import numpy as np
import netCDF4 as nc
from .ncvutils   import clone_ncvmain, set_axis_label, vardim2var
from .ncvmethods import analyse_netcdf, get_slice_miss
from .ncvmethods import set_dim_x, set_dim_y, set_dim_z
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_spinbox, add_tooltip
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
plt.style.use('seaborn-darkgrid')


__all__ = ['ncvContour']


class ncvContour(ttk.Frame):
    """
    Panel for contour plots.

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

        super().__init__(master, **kwargs)

        self.name   = 'Contour'
        self.master = master
        self.top    = master.top
        # copy for ease of use
        self.fi     = self.top.fi
        self.miss   = self.top.miss
        self.dunlim = self.top.dunlim
        self.time   = self.top.time
        self.tname  = self.top.tname
        self.tvar   = self.top.tvar
        self.dtime  = self.top.dtime
        self.latvar = self.top.latvar
        self.lonvar = self.top.lonvar
        self.latdim = self.top.latdim
        self.londim = self.top.londim
        self.maxdim = self.top.maxdim
        self.cols   = self.top.cols

        # new window
        self.rowwin = ttk.Frame(self)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        self.newfile = ttk.Button(self.rowwin, text="Open File",
                                  command=self.newnetcdf)
        self.newfile.pack(side=tk.LEFT)
        self.newfiletip = add_tooltip(self.newfile, 'Open a new netcdf file')
        self.newwin = ttk.Button(
            self.rowwin, text="New Window",
            command=partial(clone_ncvmain, self.master))
        self.newwin.pack(side=tk.RIGHT)
        self.newwintip = add_tooltip(
            self.newwin, 'Open secondary ncvue window')

        # plotting canvas
        self.figure = Figure(facecolor="white", figsize=(1, 1))
        self.axes   = self.figure.add_subplot(111)
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
        # self.imaps  = [ tk.PhotoImage(file=os.path.dirname(__file__) +
        #                               '/images/' + i + '.png')
        #                 for i in self.cmaps ]
        bundle_dir = getattr(sys, '_MEIPASS',
                             os.path.abspath(os.path.dirname(__file__)))
        self.imaps  = [ tk.PhotoImage(file=bundle_dir +
                                      '/images/' + i + '.png')
                        for i in self.cmaps ]

        # 1. row
        # z-axis selection
        self.rowzz = ttk.Frame(self)
        self.rowzz.pack(side=tk.TOP, fill=tk.X)
        self.blockz = ttk.Frame(self.rowzz)
        self.blockz.pack(side=tk.LEFT)
        self.rowz = ttk.Frame(self.blockz)
        self.rowz.pack(side=tk.TOP, fill=tk.X)
        self.zlbl = tk.StringVar()
        self.zlbl.set("z")
        zlab = ttk.Label(self.rowz, textvariable=self.zlbl)
        zlab.pack(side=tk.LEFT)
        self.bprev_z = ttk.Button(self.rowz, text="<", width=1,
                                  command=self.prev_z)
        self.bprev_z.pack(side=tk.LEFT)
        self.bprev_ztip = add_tooltip(self.bprev_z, 'Previous variable')
        self.bnext_z = ttk.Button(self.rowz, text=">", width=1,
                                  command=self.next_z)
        self.bnext_z.pack(side=tk.LEFT)
        self.bnext_ztip = add_tooltip(self.bnext_z, 'Next variable')
        self.z = ttk.Combobox(self.rowz, values=columns, width=25)
        self.z.bind("<<ComboboxSelected>>", self.selected_z)
        self.z.pack(side=tk.LEFT)
        self.ztip = add_tooltip(self.z, 'Choose variable')
        self.trans_zlbl, self.trans_z, self.trans_ztip = add_checkbutton(
            self.rowz, label="transpose z", value=False, command=self.checked,
            tooltip="Transpose matrix")
        spacez = ttk.Label(self.rowz, text=" "*1)
        spacez.pack(side=tk.LEFT)
        self.zminlbl, self.zmin, self.zmintip = add_entry(
            self.rowz, label="zmin", text='None', width=7,
            command=self.entered_z,
            tooltip="Minimal display value. Free scaling if 'None'.")
        self.zmaxlbl, self.zmax, self.zmaxtip = add_entry(
            self.rowz, label="zmax", text='None', width=7,
            command=self.entered_z,
            tooltip="Maximal display value. Free scaling if 'None'.")
        # levels z
        self.rowzd = ttk.Frame(self.blockz)
        self.rowzd.pack(side=tk.TOP, fill=tk.X)
        self.zdlblval = []
        self.zdlbl    = []
        self.zdval    = []
        self.zd       = []
        self.zdtip    = []
        for i in range(self.maxdim):
            zdlblval, zdlbl, zdval, zd, zdtip = add_spinbox(
                self.rowzd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_z, state=tk.DISABLED, tooltip="None")
            self.zdlblval.append(zdlblval)
            self.zdlbl.append(zdlbl)
            self.zdval.append(zdval)
            self.zd.append(zd)
            self.zdtip.append(zdtip)

        # 2. row
        # x-axis selection
        self.rowxy = ttk.Frame(self)
        self.rowxy.pack(side=tk.TOP, fill=tk.X)
        self.blockx = ttk.Frame(self.rowxy)
        self.blockx.pack(side=tk.LEFT)
        self.rowx = ttk.Frame(self.blockx)
        self.rowx.pack(side=tk.TOP, fill=tk.X)
        self.xlbl, self.x, self.xtip = add_combobox(
            self.rowx, label="x", values=columns, command=self.selected_x,
            tooltip="Choose variable of x-axis.\nTake index if 'None' (fast).")
        self.inv_xlbl, self.inv_x, self.inv_xtip = add_checkbutton(
            self.rowx, label="invert x", value=False, command=self.checked,
            tooltip="Invert x-axis")
        self.rowxd = ttk.Frame(self.blockx)
        self.rowxd.pack(side=tk.TOP, fill=tk.X)
        self.xdlblval = []
        self.xdlbl    = []
        self.xdval    = []
        self.xd       = []
        self.xdtip    = []
        for i in range(self.maxdim):
            xdlblval, xdlbl, xdval, xd, xdtip = add_spinbox(
                self.rowxd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_x, state=tk.DISABLED, tooltip="None")
            self.xdlblval.append(xdlblval)
            self.xdlbl.append(xdlbl)
            self.xdval.append(xdval)
            self.xd.append(xd)
            self.xdtip.append(xdtip)
        # y-axis selection
        spacex = ttk.Label(self.rowxy, text=" "*3)
        spacex.pack(side=tk.LEFT)
        self.blocky = ttk.Frame(self.rowxy)
        self.blocky.pack(side=tk.LEFT)
        self.rowy = ttk.Frame(self.blocky)
        self.rowy.pack(side=tk.TOP, fill=tk.X)
        self.ylbl, self.y, self.ytip = add_combobox(
            self.rowy, label="y", values=columns, command=self.selected_y,
            tooltip="Choose variable of y-axis.\nTake index if 'None'.")
        self.inv_ylbl, self.inv_y, self.inv_ytip = add_checkbutton(
            self.rowy, label="invert y", value=False, command=self.checked,
            tooltip="Invert y-axis")
        self.rowyd = ttk.Frame(self.blocky)
        self.rowyd.pack(side=tk.TOP, fill=tk.X)
        self.ydlblval = []
        self.ydlbl    = []
        self.ydval    = []
        self.yd       = []
        self.ydtip    = []
        for i in range(self.maxdim):
            ydlblval, ydlbl, ydval, yd, ydtip = add_spinbox(
                self.rowyd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y, state=tk.DISABLED, tooltip="None")
            self.ydlblval.append(ydlblval)
            self.ydlbl.append(ydlbl)
            self.ydval.append(ydval)
            self.yd.append(yd)
            self.ydtip.append(ydtip)

        # 3. row
        # options
        self.rowcmap = ttk.Frame(self)
        self.rowcmap.pack(side=tk.TOP, fill=tk.X)
        self.cmaplbl, self.cmap, self.cmaptip = add_imagemenu(
            self.rowcmap, label="cmap", values=self.cmaps,
            images=self.imaps, command=self.selected_cmap,
            tooltip="Choose colormap")
        self.cmap['text']  = 'RdYlBu'
        self.cmap['image'] = self.imaps[self.cmaps.index('RdYlBu')]
        self.rev_cmaplbl, self.rev_cmap, self.rev_cmaptip = add_checkbutton(
            self.rowcmap, label="reverse cmap", value=False,
            command=self.checked,
            tooltip="Reverse colormap")
        self.meshlbl, self.mesh, self.meshtip = add_checkbutton(
            self.rowcmap, label="mesh", value=True,
            command=self.checked,
            tooltip="Pseudocolor plot if checked, plot contours if unchecked")
        self.gridlbl, self.grid, self.gridtip = add_checkbutton(
            self.rowcmap, label="grid", value=False,
            command=self.checked,
            tooltip="Draw major grid lines")

    #
    # Bindings
    #

    def checked(self):
        """
        Command called if any checkbutton was checked or unchecked.

        Redraws plot.
        """
        self.redraw()

    def entered_z(self, event):
        """
        Command called if values for `zmin`/`zmax` were entered.

        Triggering `event` was bound to entry.

        Redraws plot.
        """
        self.redraw()

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
            self.zmin.set('None')
            self.zmax.set('None')
            set_dim_z(self)
            self.x.set('')
            self.y.set('')
            self.inv_x.set(0)
            self.inv_y.set(0)
            set_dim_x(self)
            set_dim_y(self)
            self.redraw()

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
            self.zmin.set('None')
            self.zmax.set('None')
            set_dim_z(self)
            self.x.set('')
            self.y.set('')
            self.inv_x.set(0)
            self.inv_y.set(0)
            set_dim_x(self)
            set_dim_y(self)
            self.redraw()

    def newnetcdf(self):
        """
        Open a new netcdf file and connect it to top.
        """
        # get new netcdf file name
        ncfile = filedialog.askopenfilename(
            parent=self, title='Choose netcdf file', multiple=False)
        if ncfile:
            # close old netcdf file
            if self.top.fi:
                self.top.fi.close()
            # reset empty defaults of top
            self.top.dunlim = ''      # name of unlimited dimension
            self.top.time   = None    # datetime variable
            self.top.tname  = ''      # datetime variable name
            self.top.tvar   = ''      # datetime variable name in netcdf
            self.top.dtime  = None    # decimal year
            self.top.latvar = ''      # name of latitude variable
            self.top.lonvar = ''      # name of longitude variable
            self.top.latdim = ''      # name of latitude dimension
            self.top.londim = ''      # name of longitude dimension
            self.top.maxdim = 0       # maximum num of dims of all variables
            self.top.cols   = []      # variable list
            # open new netcdf file
            self.top.fi = nc.Dataset(ncfile, 'r')
            analyse_netcdf(self.top)
            # reset panel
            self.reinit()
            self.redraw()

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
        self.x.set('')
        self.y.set('')
        self.inv_x.set(0)
        self.inv_y.set(0)
        self.zmin.set('None')
        self.zmax.set('None')
        set_dim_x(self)
        set_dim_y(self)
        set_dim_z(self)
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

    #
    # Methods
    #

    def reinit(self):
        """
        Reinitialise the panel from top.
        """
        # reinit from top
        self.fi     = self.top.fi
        self.miss   = self.top.miss
        self.dunlim = self.top.dunlim
        self.time   = self.top.time
        self.tname  = self.top.tname
        self.tvar   = self.top.tvar
        self.dtime  = self.top.dtime
        self.latvar = self.top.latvar
        self.lonvar = self.top.lonvar
        self.latdim = self.top.latdim
        self.londim = self.top.londim
        self.maxdim = self.top.maxdim
        self.cols   = self.top.cols
        # reset dimensions
        for ll in self.zdlbl:
            ll.destroy()
        for ll in self.zd:
            ll.destroy()
        self.zdlblval = []
        self.zdlbl    = []
        self.zdval    = []
        self.zd       = []
        self.zdtip    = []
        for i in range(self.maxdim):
            zdlblval, zdlbl, zdval, zd, zdtip = add_spinbox(
                self.rowzd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_z, state=tk.DISABLED, tooltip="None")
            self.zdlblval.append(zdlblval)
            self.zdlbl.append(zdlbl)
            self.zdval.append(zdval)
            self.zd.append(zd)
            self.zdtip.append(zdtip)
        for ll in self.xdlbl:
            ll.destroy()
        for ll in self.xd:
            ll.destroy()
        self.xdlblval = []
        self.xdlbl    = []
        self.xdval    = []
        self.xd       = []
        self.xdtip    = []
        for i in range(self.maxdim):
            xdlblval, xdlbl, xdval, xd, xdtip = add_spinbox(
                self.rowxd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_x, state=tk.DISABLED, tooltip="None")
            self.xdlblval.append(xdlblval)
            self.xdlbl.append(xdlbl)
            self.xdval.append(xdval)
            self.xd.append(xd)
            self.xdtip.append(xdtip)
        for ll in self.ydlbl:
            ll.destroy()
        for ll in self.yd:
            ll.destroy()
        self.ydlblval = []
        self.ydlbl    = []
        self.ydval    = []
        self.yd       = []
        self.ydtip    = []
        for i in range(self.maxdim):
            ydlblval, ydlbl, ydval, yd, ydtip = add_spinbox(
                self.rowyd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y, state=tk.DISABLED, tooltip="None")
            self.ydlblval.append(ydlblval)
            self.ydlbl.append(ydlbl)
            self.ydval.append(ydval)
            self.yd.append(yd)
            self.ydtip.append(ydtip)
        # set variables
        columns = [''] + self.cols
        self.z['values'] = columns
        self.z.set(columns[0])
        self.zmin.set('None')
        self.zmax.set('None')
        self.x['values'] = columns
        self.x.set(columns[0])
        self.y['values'] = columns
        self.y.set(columns[0])

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
        self.axes = self.figure.add_subplot(111)
        xlim  = [None, None]
        ylim  = [None, None]
        # set x, y, axes labels
        vx = 'None'
        vy = 'None'
        vz = 'None'
        if (z != ''):
            # z axis
            vz = vardim2var(z)
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
            # both contourf and pcolormesh assume (row,col),
            # so transpose by default
            if not trans_z:
                zz = zz.T
        if (y != ''):
            # y axis
            vy = vardim2var(y)
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
            vx = vardim2var(x)
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
                nx = 1
            if (y != ''):
                ny = yy.shape[0]
            else:
                ny = 1
            zz = np.ones((ny, nx)) * np.nan
            zlab = ''
        if zz.ndim < 2:
            estr  = 'Contour: z (' + vz + ') is not 2-dimensional:'
            print(estr, zz.shape)
            return
        # set x and y to index if not selected
        if (x == ''):
            nx = zz.shape[1]
            xx = np.arange(nx)
            xlab = ''
        if (y == ''):
            ny = zz.shape[0]
            yy = np.arange(ny)
            ylab = ''
        # plot options
        if rev_cmap:
            cmap = cmap + '_r'
        # plot
        # cc = self.axes.imshow(zz[:, ::-1], aspect='auto', cmap=cmap,
        #                       interpolation='none')
        # cc = self.axes.matshow(zz[:, ::-1], aspect='auto', cmap=cmap,
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
        if mesh:
            try:
                # zz is matrix notation: (row, col)
                cc = self.axes.pcolormesh(xx, yy, zz, vmin=zmin, vmax=zmax,
                                          cmap=cmap, shading='nearest')
                cb = self.figure.colorbar(cc, fraction=0.05, shrink=0.75,
                                          extend=extend)
            except Exception:
                estr  = 'Contour: x (' + vx + '), y (' + vy + '),'
                estr += ' z (' + vz + ') shapes do not match for'
                estr += ' pcolormesh:'
                print(estr, xx.shape, yy.shape, zz.shape)
                return
        else:
            try:
                # if 1-D then len(x)==m (columns) and len(y)==n (rows): z(n,m)
                cc = self.axes.contourf(xx, yy, zz, vmin=zmin, vmax=zmax,
                                        cmap=cmap, extend=extend)
                cb = self.figure.colorbar(cc, fraction=0.05, shrink=0.75)
            except Exception:
                estr  = 'Contour: x (' + vx + '), y (' + vy + '),'
                estr += ' z (' + vz + ') shapes do not match for'
                estr += ' contourf:'
                print(estr, xx.shape, yy.shape, zz.shape)
                return
        # help(self.figure)
        cb.set_label(zlab)
        self.axes.xaxis.set_label_text(xlab)
        self.axes.yaxis.set_label_text(ylab)
        # # Does not work
        # # might do it by hand, i.e. get ticks and use axhline and axvline
        # self.axes.grid(True, lw=5, color='k', zorder=100)
        # self.axes.set_zorder(100)
        # self.axes.xaxis.grid(True, zorder=999)
        # self.axes.yaxis.grid(True, zorder=999)
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        # invert axes
        if inv_x:
            if (xlim[0] is not None):
                xlim = xlim[::-1]
                self.axes.set_xlim(xlim)
        if inv_y:
            if (ylim[0] is not None):
                ylim = ylim[::-1]
                self.axes.set_ylim(ylim)
        # draw grid lines
        xticks = np.array(self.axes.get_xticks())
        yticks = np.array(self.axes.get_yticks())
        if grid:
            ii = np.where((xticks > min(xlim)) & (xticks < max(xlim)))[0]
            if ii.size > 0:
                ggx = self.axes.vlines(xticks[ii], ylim[0], ylim[1],
                                       colors='w', linestyles='solid',
                                       linewidth=0.5)
            ii = np.where((yticks > min(ylim)) & (yticks < max(ylim)))[0]
            if ii.size > 0:
                ggy = self.axes.hlines(yticks[ii], xlim[0], xlim[1],
                                       colors='w', linestyles='solid',
                                       linewidth=0.5)
        # redraw
        self.canvas.draw()
        self.toolbar.update()
