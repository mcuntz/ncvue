#!/usr/bin/env python
"""
Contour panel of ncvue

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
import os
import numpy as np
from .ncvutils   import set_axis_label, set_miss
from .ncvmethods import get_miss
from .ncvmethods import get_slice_x, get_slice_y, get_slice_z
from .ncvmethods import set_dim_x, set_dim_y, set_dim_z
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_spinbox
from .ncvclone   import clone_ncvmain
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
plt.style.use('seaborn-darkgrid')


__all__ = ['ncvContour']


class ncvContour(ttk.Frame):
    """
    Panel for contour plots.
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

        # new window
        self.rowwin = ttk.Frame(self)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        self.newwin = ttk.Button(
            self.rowwin, text="New Window",
            command=partial(clone_ncvmain, self.master, self.fi, self.miss))
        self.newwin.pack(side=tk.RIGHT)

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
        self.imaps  = [ tk.PhotoImage(file=os.path.dirname(__file__) +
                                      '/images/' + i + '.png')
                        for i in self.cmaps ]

        # 1. row
        # z-axis selection
        self.rowz = ttk.Frame(self)
        self.rowz.pack(side=tk.TOP, fill=tk.X)
        # self.zlbl, self.z = add_combobox(self.rowz, label="z",
        #                                  values=columns,
        #                                  command=self.selected_z)
        self.zlbl = tk.StringVar()
        self.zlbl.set("z")
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
            self.rowz, label="transpose z", value=False, command=self.checked)
        spacez = ttk.Label(self.rowz, text=" "*1)
        spacez.pack(side=tk.LEFT)
        self.zminlbl, self.zmin = add_entry(self.rowz, label="zmin",
                                            text='None', width=7,
                                            command=self.entered_z)
        self.zmaxlbl, self.zmax = add_entry(self.rowz, label="zmax",
                                            text='None', width=7,
                                            command=self.entered_z)

        # 2. row
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

        # 3. row
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

        # 4. row
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

        # 5. row
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

    #
    # Bindings
    #

    def checked(self):
        """
        Method called if any checkbutton was checked or unchecked.

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
                miss = get_miss(self, zz)
                zz = get_slice_z(self, zz).squeeze()
                zz = set_miss(zz, miss)
                if trans_z:
                    zz = zz.T
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
            miss = get_miss(self, yy)
            yy = get_slice_y(self, yy).squeeze()
            yy = set_miss(yy, miss)
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
            miss = get_miss(self, xx)
            xx = get_slice_x(self, xx).squeeze()
            xx = set_miss(xx, miss)
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
            zz = np.ones((nx, ny)) * np.nan
            zlab = ''
        if zz.ndim < 2:
            estr  = 'Contour: z (' + vz + ') is not 2-dimensional:'
            print(estr, zz.shape)
            return
        # set x and y to index if not selected
        if (x == ''):
            nx = zz.shape[0]
            xx = np.arange(nx)
            xlab = ''
        if (y == ''):
            ny = zz.shape[1]
            yy = np.arange(ny)
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
        if mesh:
            try:
                cc = self.axes.pcolormesh(xx, yy, zz.T, vmin=zmin, vmax=zmax,
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
                cc = self.axes.contourf(xx, yy, zz.T, vmin=zmin, vmax=zmax,
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
