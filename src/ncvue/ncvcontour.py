#!/usr/bin/env python
"""
Contour panel of ncvue.

The panel allows plotting contour or mesh plots of 2D-variables.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvContour

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Open new netcdf file, communicate via top widget,
     Jan 2021, Matthias Cuntz
   * Write coordinates and value on bottom of plotting canvas,
     May 2021, Matthias Cuntz
   * Address fi.variables[name] directly by fi[name], Jan 2024, Matthias Cuntz
   * Allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * Allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * Move images/ directory from src/ncvue/ to src/ directory,
     Jan 2024, Matthias Cuntz
   * Move themes/ and images/ back to src/ncvue/, Feb 2024, Matthias Cuntz
   * Add Quit button, Nov 2024, Matthias Cuntz
   * Use CustomTkinter if installed, Nov 2024, Matthias Cuntz
   * Use add_button, add_label widgets, Feb 2025, Matthias Cuntz
   * Use add_combobox instead of Combobox directly, Feb 2025, Matthias Cuntz
   * Include xarray to read input files, Feb 2025, Matthias Cuntz
   * Draw canvas as last element so that UI controls are displayed
     as long as possible, Dec 2025, Matthias Cuntz

"""
import os
import sys
import tkinter as tk
try:
    from customtkinter import CTkFrame as Frame
    ihavectk = True
except ModuleNotFoundError:
    from tkinter.ttk import Frame
    ihavectk = False
import netCDF4 as nc
import numpy as np
try:
    import xarray as xr
    ihavex = True
except ModuleNotFoundError:
    ihavex = False
from .ncvutils import clone_ncvmain, format_coord_contour, selvar
from .ncvutils import set_axis_label, vardim2var
from .ncvmethods import analyse_netcdf, get_slice_miss
from .ncvmethods import set_dim_x, set_dim_y, set_dim_z
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_spinbox, add_label, add_button
# import matplotlib
# matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
try:
    # plt.style.use('seaborn-v0_8-darkgrid')
    plt.style.use('seaborn-v0_8-dark')
except OSError:
    # plt.style.use('seaborn-darkgrid')
    plt.style.use('seaborn-dark')
# plt.style.use('fast')


__all__ = ['ncvContour']


class ncvContour(Frame):
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
        self.usex   = self.top.usex
        self.fi     = self.top.fi
        self.groups = self.top.groups
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

        # selections and options
        columns = [''] + self.cols

        allcmaps = plt.colormaps()
        self.cmaps = [ i for i in allcmaps if not i.endswith('_r') ]
        self.cmaps.sort()
        bundle_dir = getattr(sys, '_MEIPASS',
                             os.path.abspath(os.path.dirname(__file__)))
        self.imaps = [ tk.PhotoImage(file=f'{bundle_dir}/images/{i}.png')
                       for i in self.cmaps ]
        if ihavectk:
            # width of combo boxes in px
            combowidth = 288
            # widths of entry widgets in px
            ewsmall = 20
            ewmed = 45
            ewbig = 70
            ewvbig = 117
            # pad between label and entry
            padx = 5
            # width of animation and variables buttons
            bwidth = 35
            # width of projections menu
            mwidth = 70
        else:
            # width of combo boxes in characters
            combowidth = 33
            # widths of entry widgets in characters
            ewsmall = 3
            ewmed = 4
            ewbig = 7
            ewvbig = 11
            # pad between label and entry (not used)
            padx = 5
            # width of animation and variables buttons
            bwidth = 1
            # width of projections menu
            mwidth = 13

        # new window
        self.rowwin = Frame(self)
        self.newfile, self.newfiletip = add_button(
            self.rowwin, text='Open File', command=self.newnetcdf,
            tooltip='Open a new netcdf file')
        if ihavex:
            self.newxarray, self.newxarraytip = add_button(
                self.rowwin, text='Open xarray', command=self.newxarray,
                tooltip='Open new netcdf file(s) with xarray')
        self.newwin, self.newwintip = add_button(
            self.rowwin, text='New Window', nopack=True,
            command=partial(clone_ncvmain, self.master),
            tooltip='Open secondary ncvue window')
        self.newwin.pack(side=tk.RIGHT)

        # plotting canvas
        self.rowcanvas = Frame(self)
        self.figure = Figure(facecolor='white', figsize=(1, 1))
        self.axes   = self.figure.add_subplot(111)
        self.axes2  = self.axes.twinx()
        self.axes2.yaxis.set_label_position('right')
        self.axes2.yaxis.tick_right()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.rowcanvas)
        self.canvas.draw()
        self.tkcanvas = self.canvas.get_tk_widget()
        self.tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # matplotlib toolbar
        # toolbar uses pack internally -> put into frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.rowcanvas,
                                            pack_toolbar=True)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 1. row
        # z-axis selection
        self.rowzz = Frame(self)
        self.blockz = Frame(self.rowzz)
        self.blockz.pack(side=tk.LEFT)
        self.rowz = Frame(self.blockz)
        self.rowz.pack(side=tk.TOP, fill=tk.X)
        lkwargs = {}
        if ihavectk:
            lkwargs.update({'padx': padx})
        zlab = add_label(self.rowz, text='z', **lkwargs)
        spacep = add_label(self.rowz, text=' ' * 1)
        self.bprev_z, self.bprev_ztip = add_button(
            self.rowz, text='<', command=self.prev_z, width=bwidth,
            tooltip='Previous variable')
        self.bnext_z, self.bnext_ztip = add_button(
            self.rowz, text='>', command=self.next_z, width=bwidth,
            tooltip='Next variable')
        self.zframe, self.zlbl, self.z, self.ztip = add_combobox(
            self.rowz, label='', values=columns,
            command=self.selected_z, width=combowidth, padx=0,
            tooltip='Choose variable')
        self.zframe.pack(side=tk.LEFT)
        self.trans_zframe, self.trans_zlbl, self.trans_z, self.trans_ztip = (
            add_checkbutton(self.rowz, label='transpose z', value=False,
                            command=self.checked,
                            tooltip='Transpose matrix'))
        self.trans_zframe.pack(side=tk.LEFT)
        spacez = add_label(self.rowz, text=' ')
        self.zminframe, self.zminlbl, self.zmin, self.zmintip = add_entry(
            self.rowz, label='zmin', text='None', width=ewvbig, padx=padx,
            command=self.entered_z,
            tooltip='Minimal display value. Free scaling if "None".')
        self.zminframe.pack(side=tk.LEFT)
        self.zmaxframe, self.zmaxlbl, self.zmax, self.zmaxtip = add_entry(
            self.rowz, label='zmax', text='None', width=ewvbig, padx=padx,
            command=self.entered_z,
            tooltip='Maximal display value. Free scaling if "None".')
        self.zmaxframe.pack(side=tk.LEFT)
        # levels z
        self.rowzd = Frame(self.blockz)
        self.rowzd.pack(side=tk.TOP, fill=tk.X)
        self.zdframe = []
        self.zdlblval = []
        self.zdlbl    = []
        self.zdval    = []
        self.zd       = []
        self.zdtip    = []
        for i in range(self.maxdim):
            zdframe, zdlblval, zdlbl, zdval, zd, zdtip = add_spinbox(
                self.rowzd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_z, state=tk.DISABLED, tooltip='None')
            self.zdframe.append(zdframe)
            self.zdlblval.append(zdlblval)
            self.zdlbl.append(zdlbl)
            self.zdval.append(zdval)
            self.zd.append(zd)
            self.zdtip.append(zdtip)
            zdframe.pack(side=tk.LEFT)

        # 2. row
        # x-axis selection
        self.rowxy = Frame(self)
        self.blockx = Frame(self.rowxy)
        self.blockx.pack(side=tk.LEFT)
        self.rowx = Frame(self.blockx)
        self.rowx.pack(side=tk.TOP, fill=tk.X)
        self.xframe, self.xlbl, self.x, self.xtip = add_combobox(
            self.rowx, label='x', values=columns, command=self.selected_x,
            width=combowidth, padx=padx,
            tooltip=('Choose variable of x-axis.\nTakes index if "None",'
                     ' which is much faster.'))
        self.xframe.pack(side=tk.LEFT)
        self.inv_xframe, self.inv_xlbl, self.inv_x, self.inv_xtip = (
            add_checkbutton(self.rowx, label='invert x', value=False,
                            command=self.checked,
                            tooltip='Invert x-axis'))
        self.inv_xframe.pack(side=tk.LEFT)
        self.rowxd = Frame(self.blockx)
        self.rowxd.pack(side=tk.TOP, fill=tk.X)
        self.xdframe = []
        self.xdlblval = []
        self.xdlbl    = []
        self.xdval    = []
        self.xd       = []
        self.xdtip    = []
        for i in range(self.maxdim):
            xdframe, xdlblval, xdlbl, xdval, xd, xdtip = add_spinbox(
                self.rowxd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_x, state=tk.DISABLED, tooltip='None')
            self.xdframe.append(xdframe)
            self.xdlblval.append(xdlblval)
            self.xdlbl.append(xdlbl)
            self.xdval.append(xdval)
            self.xd.append(xd)
            self.xdtip.append(xdtip)
            xdframe.pack(side=tk.LEFT)
        # y-axis selection
        spacex = add_label(self.rowxy, text='   ')
        self.blocky = Frame(self.rowxy)
        self.blocky.pack(side=tk.LEFT)
        self.rowy = Frame(self.blocky)
        self.rowy.pack(side=tk.TOP, fill=tk.X)
        self.yframe, self.ylbl, self.y, self.ytip = add_combobox(
            self.rowy, label='y', values=columns, command=self.selected_y,
            width=combowidth, padx=padx,
            tooltip='Choose variable of y-axis.\nTakes index if "None".')
        self.yframe.pack(side=tk.LEFT)
        self.inv_yframe, self.inv_ylbl, self.inv_y, self.inv_ytip = (
            add_checkbutton(self.rowy, label='invert y', value=False,
                            command=self.checked,
                            tooltip='Invert y-axis'))
        self.inv_yframe.pack(side=tk.LEFT)
        self.rowyd = Frame(self.blocky)
        self.rowyd.pack(side=tk.TOP, fill=tk.X)
        self.ydframe  = []
        self.ydlblval = []
        self.ydlbl    = []
        self.ydval    = []
        self.yd       = []
        self.ydtip    = []
        for i in range(self.maxdim):
            ydframe, ydlblval, ydlbl, ydval, yd, ydtip = add_spinbox(
                self.rowyd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y, state=tk.DISABLED, tooltip='None')
            self.ydframe.append(ydframe)
            self.ydlblval.append(ydlblval)
            self.ydlbl.append(ydlbl)
            self.ydval.append(ydval)
            self.yd.append(yd)
            self.ydtip.append(ydtip)
            ydframe.pack(side=tk.LEFT)

        # 3. row
        # options
        self.rowcmap = Frame(self)
        self.cmapframe, self.cmaplbl, self.cmap, self.cmaptip = add_imagemenu(
            self.rowcmap, label='cmap', values=self.cmaps,
            images=self.imaps, command=self.selected_cmap,
            tooltip='Choose colormap')
        self.cmapframe.pack(side=tk.LEFT)
        self.cmap['text']  = 'RdYlBu'
        self.cmap['image'] = self.imaps[self.cmaps.index('RdYlBu')]
        self.rev_cmapframe, self.rev_cmaplbl, self.rev_cmap, self.rev_cmaptip = (
            add_checkbutton(self.rowcmap, label='reverse cmap', value=False,
                            command=self.checked,
                            tooltip='Reverse colormap'))
        self.rev_cmapframe.pack(side=tk.LEFT)
        self.meshframe, self.meshlbl, self.mesh, self.meshtip = (
            add_checkbutton(self.rowcmap, label='mesh', value=True,
                            command=self.checked,
                            tooltip=('Pseudocolor plot if checked,'
                                     ' contours if unchecked')))
        self.meshframe.pack(side=tk.LEFT)
        self.gridframe, self.gridlbl, self.grid, self.gridtip = (
            add_checkbutton(self.rowcmap, label='grid', value=False,
                            command=self.checked,
                            tooltip='Draw major grid lines'))
        self.gridframe.pack(side=tk.LEFT)
        # Quit button
        self.bquit, self.bquittip = add_button(
            self.rowcmap, text='Quit', command=self.master.top.destroy,
            nopack=True, tooltip='Quit ncvue')
        self.bquit.pack(side=tk.RIGHT)

        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        self.rowcmap.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowxy.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowzz.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        self.rowcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

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
        if ihavectk:
            cols = self.z.cget('values')
        else:
            cols = self.z['values']
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
        if ihavectk:
            cols = self.z.cget('values')
        else:
            cols = self.z['values']
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
        ncfile = tk.filedialog.askopenfilename(
            parent=self, title='Choose netcdf file(s)', multiple=True)
        if len(ncfile) > 0:
            # close old netcdf file
            if self.usex:
                if self.top.fi:
                    self.top.fi.close()
            else:
                if len(self.top.fi) > 0:
                    for fi in self.top.fi:
                        fi.close()
            # reset empty defaults of top
            self.top.usex   = False  # open file with netCDF4 or xarray
            self.top.fi     = []  # file name or file handle
            self.top.groups = []  # filename with incr. index or group names
            self.top.dunlim = []  # name of unlimited dimension
            self.top.time   = []  # datetime variable
            self.top.tname  = []  # datetime variable name
            self.top.tvar   = []  # datetime variable name in netcdf
            self.top.dtime  = []  # decimal year
            self.top.latvar = []  # name of latitude variable
            self.top.lonvar = []  # name of longitude variable
            self.top.latdim = []  # name of latitude dimension
            self.top.londim = []  # name of longitude dimension
            self.top.maxdim = 0   # maximum num of dims of all variables
            self.top.cols   = []  # variable list
            # open new netcdf file
            ianalyse = True
            for ii, nn in enumerate(ncfile):
                self.top.fi.append(nc.Dataset(nn, 'r'))
                if len(ncfile) > 1:
                    nnc = np.ceil(np.log10(len(ncfile))).astype(int)
                    self.top.groups.append(f'file{ii:0{nnc}d}')
            # Check groups
            if len(ncfile) == 1:
                self.top.groups = list(self.top.fi[0].groups.keys())
            else:
                for ii, nn in enumerate(ncfile):
                    if len(list(self.top.fi[ii].groups.keys())) > 0:
                        print(f'Either multiple files or one file with'
                              f' groups allowed as input. Multiple files'
                              f' given but file {nn} has groups.')
                        for fi in self.top.fi:
                            fi.close()
                        ianalyse = False
            if ianalyse:
                analyse_netcdf(self.top)
            # reset panel
            self.reinit()
            self.redraw()

    def newxarray(self):
        """
        Open a new netcdf file and connect it to top.

        """
        # get new netcdf file name
        ncfile = tk.filedialog.askopenfilename(
            parent=self, title='Choose netcdf file(s)', multiple=True)
        if len(ncfile) > 0:
            # close old netcdf file
            if self.usex:
                if self.top.fi:
                    self.top.fi.close()
            else:
                if len(self.top.fi) > 0:
                    for fi in self.top.fi:
                        fi.close()
            # reset empty defaults of top
            self.top.usex   = True  # open file with netCDF4 or xarray
            self.top.fi     = []  # file name or file handle
            self.top.groups = []  # filename with incr. index or group names
            self.top.dunlim = []  # name of unlimited dimension
            self.top.time   = []  # datetime variable
            self.top.tname  = []  # datetime variable name
            self.top.tvar   = []  # datetime variable name in netcdf
            self.top.dtime  = []  # decimal year
            self.top.latvar = []  # name of latitude variable
            self.top.lonvar = []  # name of longitude variable
            self.top.latdim = []  # name of latitude dimension
            self.top.londim = []  # name of longitude dimension
            self.top.maxdim = 0   # maximum num of dims of all variables
            self.top.cols   = []  # variable list
            # open new netcdf file
            if len(ncfile) > 1:
                self.top.fi = xr.open_mfdataset(ncfile)
            else:
                self.top.fi = xr.open_dataset(ncfile[0])
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
        self.usex   = self.top.usex
        self.fi     = self.top.fi
        self.groups = self.top.groups
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
        for ll in self.zdframe:
            ll.destroy()
        self.zdframe  = []
        self.zdlblval = []
        self.zdlbl    = []
        self.zdval    = []
        self.zd       = []
        self.zdtip    = []
        for i in range(self.maxdim):
            zdframe, zdlblval, zdlbl, zdval, zd, zdtip = add_spinbox(
                self.rowzd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_z, state=tk.DISABLED, tooltip='None')
            self.zdframe.append(zdframe)
            self.zdlblval.append(zdlblval)
            self.zdlbl.append(zdlbl)
            self.zdval.append(zdval)
            self.zd.append(zd)
            self.zdtip.append(zdtip)
            zdframe.pack(side=tk.LEFT)
        for ll in self.xdlbl:
            ll.destroy()
        for ll in self.xd:
            ll.destroy()
        for ll in self.xdframe:
            ll.destroy()
        self.xdframe  = []
        self.xdlblval = []
        self.xdlbl    = []
        self.xdval    = []
        self.xd       = []
        self.xdtip    = []
        for i in range(self.maxdim):
            xdframe, xdlblval, xdlbl, xdval, xd, xdtip = add_spinbox(
                self.rowxd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_x, state=tk.DISABLED, tooltip='None')
            self.xdframe.append(xdframe)
            self.xdlblval.append(xdlblval)
            self.xdlbl.append(xdlbl)
            self.xdval.append(xdval)
            self.xd.append(xd)
            self.xdtip.append(xdtip)
            xdframe.pack(side=tk.LEFT)
        for ll in self.ydlbl:
            ll.destroy()
        for ll in self.yd:
            ll.destroy()
        for ll in self.ydframe:
            ll.destroy()
        self.ydframe  = []
        self.ydlblval = []
        self.ydlbl    = []
        self.ydval    = []
        self.yd       = []
        self.ydtip    = []
        for i in range(self.maxdim):
            ydframe, ydlblval, ydlbl, ydval, yd, ydtip = add_spinbox(
                self.rowyd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y, state=tk.DISABLED, tooltip='None')
            self.ydframe.append(ydframe)
            self.ydlblval.append(ydlblval)
            self.ydlbl.append(ydlbl)
            self.ydval.append(ydval)
            self.yd.append(yd)
            self.ydtip.append(ydtip)
            ydframe.pack(side=tk.LEFT)
        # set variables
        columns = [''] + self.cols
        if ihavectk:
            self.z.configure(values=columns)
        else:
            self.z['values'] = columns
        self.z.set(columns[0])
        self.zmin.set('None')
        self.zmax.set('None')
        if ihavectk:
            self.x.configure(values=columns)
        else:
            self.x['values'] = columns
        self.x.set(columns[0])
        if ihavectk:
            self.y.configure(values=columns)
        else:
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
            gz, vz = vardim2var(z, self.groups)
            if self.usex:
                tnamez = self.tname
                dtimez = self.dtime
                timez = self.time
            else:
                tnamez = self.tname[gz]
                dtimez = self.dtime[gz]
                timez = self.time[gz]
            if vz == tnamez:
                # should throw an error later
                if mesh:
                    zz = dtimez
                    zlab = 'Year'
                else:
                    zz = timez
                    zlab = 'Date'
            else:
                zz = selvar(self, vz)
                zlab = set_axis_label(zz)
            zz = get_slice_miss(self, self.zd, zz)
            # both contourf and pcolormesh assume (row,col),
            # so transpose by default
            if not trans_z:
                zz = zz.T
        if (y != ''):
            # y axis
            gy, vy = vardim2var(y, self.groups)
            if self.usex:
                tnamey = self.tname
                dtimey = self.dtime
                timey = self.time
            else:
                tnamey = self.tname[gy]
                dtimey = self.dtime[gy]
                timey = self.time[gy]
            if vy == tnamey:
                if mesh:
                    yy = dtimey
                    ylab = 'Year'
                else:
                    yy = timey
                    ylab = 'Date'
            else:
                yy = selvar(self, vy)
                ylab = set_axis_label(yy)
            yy = get_slice_miss(self, self.yd, yy)
        if (x != ''):
            # x axis
            gx, vx = vardim2var(x, self.groups)
            if self.usex:
                tnamex = self.tname
                dtimex = self.dtime
                timex = self.time
            else:
                tnamex = self.tname[gx]
                dtimex = self.dtime[gx]
                timex = self.time[gx]
            if vx == tnamex:
                if mesh:
                    xx = dtimex
                    xlab = 'Year'
                else:
                    xx = timex
                    xlab = 'Date'
            else:
                xx = selvar(self, vx)
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
            print('Contour: z ({vz}) is not 2-dimensional:', zz.shape)
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
                print(f'Contour: x ({vx}), y ({vy}), z ({vz}) shapes do not'
                      f' match for pcolormesh:', xx.shape, yy.shape, zz.shape)
                return
        else:
            try:
                # if 1-D then len(x)==m (columns) and len(y)==n (rows): z(n,m)
                cc = self.axes.contourf(xx, yy, zz, vmin=zmin, vmax=zmax,
                                        cmap=cmap, extend=extend)
                cb = self.figure.colorbar(cc, fraction=0.05, shrink=0.75)
            except Exception:
                print(f'Contour: x ({vx}), y ({vy}), z ({vz}) shapes do not'
                      f' match for contourf:', xx.shape, yy.shape, zz.shape)
                return
        # help(self.figure)
        cb.set_label(zlab)
        self.axes.xaxis.set_label_text(xlab)
        self.axes.yaxis.set_label_text(ylab)
        self.axes.format_coord = lambda x, y: format_coord_contour(
            x, y, self.axes, xx, yy, zz)
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
        self.axes.grid(False)
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
