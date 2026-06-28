#!/usr/bin/env python
"""
Map panel of ncvue.

The panel allows plotting contour or mesh maps of georeferenced data.
Maps can be animated along the time axis.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvMap

History
   * Written Dec 2020-Jan 2021 by Matthias Cuntz (mc (at) macu (dot) de)
   * Open new netcdf file, communicate via top widget,
     Jan 2021, Matthias Cuntz
   * Write coordinates and value on bottom of plotting canvas,
     May 2021, Matthias Cuntz
   * Larger pad for colorbar, Jun 2021, Matthias Cuntz
   * Work with files without an unlimited (time) dimension (set_tstep),
     Oct 2021, Matthias Cuntz
   * Address fi.variables[name] directly by fi[name], Jan 2024, Matthias Cuntz
   * Allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * Allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * Move images/ directory from src/ncvue/ to src/ directory,
     Jan 2024, Matthias Cuntz
   * Added borders, rivers, and lakes checkbuttons, Feb 2024, Matthias Cuntz
   * Move themes/ and images/ back to src/ncvue/, Feb 2024, Matthias Cuntz
   * Use matplotlib.colormaps[name] instead of
     matplotlib.colormaps.get_cmap(name), Jul 2024, Matthias Cuntz
   * Use draw_idle instead of draw in update method for faster animation,
     Jul 2024, Matthias Cuntz
   * Add Quit button, Nov 2024, Matthias Cuntz
   * Use CustomTkinter if installed, Nov 2024, Matthias Cuntz
   * Use add_button, add_label widgets, Feb 2025, Matthias Cuntz
   * Use add_combobox instead of Combobox directly, Feb 2025, Matthias Cuntz
   * Remove delay, Feb 2025, Matthias Cuntz
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
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import netCDF4 as nc
import numpy as np
try:
    import xarray as xr
    ihavex = True
except ModuleNotFoundError:
    ihavex = False
from .ncvutils import add_cyclic, clone_ncvmain, format_coord_map, selvar
from .ncvutils import set_axis_label, set_miss, vardim2var
from .ncvmethods import analyse_netcdf, get_slice_miss, get_miss
from .ncvmethods import set_dim_lon, set_dim_lat, set_dim_var
from .ncvwidgets import add_button, add_checkbutton, add_combobox, add_entry
from .ncvwidgets import add_imagemenu, add_label, add_menu, add_scale
from .ncvwidgets import add_spinbox
import matplotlib as mpl
from matplotlib import pyplot as plt
try:
    # plt.style.use('seaborn-v0_8-darkgrid')
    plt.style.use('seaborn-v0_8-dark')
except OSError:
    # plt.style.use('seaborn-darkgrid')
    plt.style.use('seaborn-dark')
# plt.style.use('fast')


__all__ = ['ncvMap']


class ncvMap(Frame):
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
        from matplotlib import animation
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

        super().__init__(master, **kwargs)

        self.name   = 'Map'
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

        # unlimited dimension control
        self.iunlim = -1  # index of dunlim in dimensions of current var
        self.nunlim = 0   # length of dunlim of current plot variable

        # selections and options
        columns = [''] + self.cols

        allcmaps = plt.colormaps()
        self.cmaps  = [ i for i in allcmaps if not i.endswith('_r') ]
        self.cmaps.sort()
        bundle_dir = getattr(sys, '_MEIPASS',
                             os.path.abspath(os.path.dirname(__file__)))
        self.imaps  = [ tk.PhotoImage(file=f'{bundle_dir}/images/{i}.png')
                        for i in self.cmaps ]

        # only projections with keyword: central_longitude
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
        if ihavectk:
            # width of combo boxes in px
            combowidth = 297
            smallcombowidth = 81
            # widths of entry widgets in px
            ewsmall = 18
            ewmed = 45
            ewbig = 72
            ewvbig = 117
            # pad between label and entry
            padx = 5
            # width of animation and variables buttons
            bwidth = 35
            # width of projections menu
            mwidth = 70
        else:
            # width of combo boxes in characters
            combowidth = 32
            smallcombowidth = 8
            # widths of entry widgets in characters
            ewsmall = 3
            ewmed = 5
            ewbig = 7
            ewvbig = 11
            # pad between label and entry (not used)
            padx = 5
            # width of animation and variables buttons
            bwidth = 2
            # width of projections menu
            mwidth = 13

        # open file and new window buttons
        self.rowwin = Frame(self)
        self.newfile, self.newfiletip = add_button(
            self.rowwin, text='Open File', command=self.newnetcdf,
            tooltip='Open new netcdf file(s)')
        if ihavex:
            self.newxarray, self.newxarraytip = add_button(
                self.rowwin, text='Open xarray', command=self.newxarray,
                tooltip='Open new netcdf file(s) with xarray')
        spacew = add_label(self.rowwin, text='   ')
        time_label1 = add_label(self.rowwin, text='Time: ')
        self.timelbl, time_label2 = add_label(self.rowwin, '')
        self.newwin, self.newwintip = add_button(
            self.rowwin, text='New Window', nopack=True,
            command=partial(clone_ncvmain, self.master),
            tooltip='Open secondary ncvue window')
        self.newwin.pack(side=tk.RIGHT)

        # plotting canvas
        self.rowcanvas = Frame(self)
        self.figure = Figure(facecolor='white', figsize=(1, 1))
        self.axes = self.figure.add_subplot(
            111, projection=ccrs.PlateCarree())
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.rowcanvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.rowcanvas)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 1. row
        # controls
        self.rowt = Frame(self)
        ntime = 1
        self.tstepframe, self.tsteplbl, self.tstepval, self.tstep, self.tsteptip = (
            add_scale(self.rowt, label='step', ini=0, from_=0, to=ntime,
                      length=100, orient=tk.HORIZONTAL, command=self.tstep_t,
                      tooltip='Slide to go to time step'))
        self.tstepframe.pack(side=tk.LEFT)
        spacet = add_label(self.rowt, text=' ' * 1)

        # first t, previous t, etc.
        self.first_time, self.first_timetip = add_button(
            self.rowt, text='|<<', command=self.first_t, width=bwidth,
            tooltip='First time step')
        self.prev_time, self.prev_timetip = add_button(
            self.rowt, text='|<', command=self.prev_t, width=bwidth,
            tooltip='Previous time step')
        self.prun_timelbl, self.prun_time, self.prun_timetip = add_button(
            self.rowt, '<', command=self.prun_t, width=bwidth,
            tooltip='Run backwards')
        self.nrun_timelbl, self.nrun_time, self.nrun_timetip = add_button(
            self.rowt, '>', command=self.nrun_t, width=bwidth,
            tooltip='Run forwards')
        self.next_time, self.next_timetip = add_button(
            self.rowt, text='>|', command=self.next_t, width=bwidth,
            tooltip='Next time step')
        self.last_time, self.last_timetip = add_button(
            self.rowt, text='>>|', command=self.last_t, width=bwidth,
            tooltip='Last time step')
        # repeat
        spacer = add_label(self.rowt, text=' ' * 1)
        reps = ['once', 'repeat', 'reflect']
        tstr = ('Run time steps once, repeat from start when at end,'
                ' or continue running backwards when at end')
        self.repeatframe, self.repeatlbl, self.repeat, self.repeattip = (
            add_combobox(self.rowt, label='repeat', values=reps,
                         width=smallcombowidth, padx=padx,
                         command=self.repeat_t, tooltip=tstr))
        self.repeat.set('repeat')
        self.repeatframe.pack(side=tk.LEFT)

        # 2. row
        # variable-axis selection
        self.rowvv = Frame(self)

        self.blockv = Frame(self.rowvv)
        self.blockv.pack(side=tk.LEFT)

        self.rowv = Frame(self.blockv)
        self.rowv.pack(side=tk.TOP, fill=tk.X)
        lkwargs = {}
        if ihavectk:
            lkwargs.update({'padx': padx})
        vlab = add_label(self.rowv, text='var', **lkwargs)
        spacep = add_label(self.rowv, text=' ' * 1)
        self.bprev_v, self.bprev_vtip = add_button(
            self.rowv, text='<', command=self.prev_v, width=bwidth,
            tooltip='Previous variable')
        self.bnext_v, self.bnext_vtip = add_button(
            self.rowv, text='>', command=self.next_v, width=bwidth,
            tooltip='Next variable')
        self.vframe, self.vlbl, self.v, self.vtip = add_combobox(
            self.rowv, label='', values=columns,
            command=self.selected_v, width=combowidth, padx=0,
            tooltip='Choose variable')
        self.vframe.pack(side=tk.LEFT)
        self.trans_vframe, self.trans_vlbl, self.trans_v, self.trans_vtip = (
            add_checkbutton(
                self.rowv, label='transpose var', value=False,
                command=self.checked,
                tooltip='Transpose array, i.e. exchanging lat and lon'))
        self.trans_vframe.pack(side=tk.LEFT)
        spacev = add_label(self.rowv, text=' ' * 1)
        self.vminframe, self.vminlbl, self.vmin, self.vmintip = add_entry(
            self.rowv, label='vmin', text=0, width=ewvbig,
            command=self.entered_v,
            tooltip='Minimal display value', padx=padx)
        self.vminframe.pack(side=tk.LEFT)
        self.vmaxframe, self.vmaxlbl, self.vmax, self.vmaxtip = add_entry(
            self.rowv, label='vmax', text=1, width=ewvbig,
            command=self.entered_v,
            tooltip='Maximal display value', padx=padx)
        self.vmaxframe.pack(side=tk.LEFT)
        tstr  = ('If checked, determine vmin/vmax from all fields,\n'
                 'otherwise from 50 random fields')
        self.vallframe, self.valllbl, self.vall, self.valltip = (
            add_checkbutton(self.rowv, label='all', value=False,
                            command=self.checked_all, tooltip=tstr))
        self.vallframe.pack(side=tk.LEFT)

        # levels var
        self.rowvd = Frame(self.blockv)
        self.rowvd.pack(side=tk.TOP, fill=tk.X)
        self.vdframe  = []
        self.vdlblval = []
        self.vdlbl    = []
        self.vdval    = []
        self.vd       = []
        self.vdtip    = []
        for i in range(self.maxdim):
            vdframe, vdlblval, vdlbl, vdval, vd, vdtip = add_spinbox(
                self.rowvd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_v, state=tk.DISABLED, tooltip='None')
            self.vdframe.append(vdframe)
            self.vdlblval.append(vdlblval)
            self.vdlbl.append(vdlbl)
            self.vdval.append(vdval)
            self.vd.append(vd)
            self.vdtip.append(vdtip)
            vdframe.pack(side=tk.LEFT)

        # 3. row
        # lon-axis selection
        self.rowll = Frame(self)

        self.blocklon = Frame(self.rowll)
        self.blocklon.pack(side=tk.LEFT)

        self.rowlon = Frame(self.blocklon)
        self.rowlon.pack(side=tk.TOP, fill=tk.X)
        self.lonframe, self.lonlbl, self.lon, self.lontip = add_combobox(
            self.rowlon, label='lon', values=columns, padx=padx,
            command=self.selected_lon, width=combowidth,
            tooltip='Longitude variable.\nSet "empty" for matrix plot.')
        self.lonframe.pack(side=tk.LEFT)
        self.inv_lonframe, self.inv_lonlbl, self.inv_lon, self.inv_lontip = (
            add_checkbutton(self.rowlon, label='invert lon', value=False,
                            command=self.checked,
                            tooltip='Invert longitudes'))
        self.inv_lonframe.pack(side=tk.LEFT)
        self.shift_lonframe, self.shift_lonlbl, self.shift_lon, self.shift_lontip = (
            add_checkbutton(self.rowlon, label='shift lon/2', value=False,
                            command=self.checked,
                            tooltip='Roll longitudes by half its size'))
        self.shift_lonframe.pack(side=tk.LEFT)

        self.rowlond = Frame(self.blocklon)
        self.rowlond.pack(side=tk.TOP, fill=tk.X)
        self.londframe  = []
        self.londlblval = []
        self.londlbl    = []
        self.londval    = []
        self.lond       = []
        self.londtip    = []
        for i in range(self.maxdim):
            londframe, londlblval, londlbl, londval, lond, londtip = (
                add_spinbox(self.rowlond, label=str(i), values=(0,), wrap=True,
                            command=self.spinned_lon, state=tk.DISABLED,
                            tooltip='None'))
            self.londframe.append(londframe)
            self.londlblval.append(londlblval)
            self.londlbl.append(londlbl)
            self.londval.append(londval)
            self.lond.append(lond)
            self.londtip.append(londtip)
            londframe.pack(side=tk.LEFT)

        # lat-axis selection
        spacex = add_label(self.rowll, text=' ' * 3)

        self.blocklat = Frame(self.rowll)
        self.blocklat.pack(side=tk.LEFT)

        self.rowlat = Frame(self.blocklat)
        self.rowlat.pack(side=tk.TOP, fill=tk.X)
        self.latframe, self.latlbl, self.lat, self.lattip = add_combobox(
            self.rowlat, label='lat', values=columns, padx=padx,
            command=self.selected_lat, width=combowidth,
            tooltip='Longitude variable.\nSet "empty" for matrix plot.')
        self.latframe.pack(side=tk.LEFT)
        self.inv_latframe, self.inv_latlbl, self.inv_lat, self.inv_lattip = (
            add_checkbutton(self.rowlat, label='invert lat', value=False,
                            command=self.checked,
                            tooltip='Invert longitudes'))
        self.inv_latframe.pack(side=tk.LEFT)

        self.rowlatd = Frame(self.blocklat)
        self.rowlatd.pack(side=tk.TOP, fill=tk.X)
        self.latdframe  = []
        self.latdlblval = []
        self.latdlbl    = []
        self.latdval    = []
        self.latd       = []
        self.latdtip    = []
        for i in range(self.maxdim):
            latdframe, latdlblval, latdlbl, latdval, latd, latdtip = (
                add_spinbox(self.rowlatd, label=str(i), values=(0,), wrap=True,
                            command=self.spinned_lat, state=tk.DISABLED,
                            tooltip='None'))
            self.latdframe.append(latdframe)
            self.latdlblval.append(latdlblval)
            self.latdlbl.append(latdlbl)
            self.latdval.append(latdval)
            self.latd.append(latd)
            self.latdtip.append(latdtip)
            latdframe.pack(side=tk.LEFT)

        # 4. row
        # options
        self.rowcmap = Frame(self)
        self.cmapframe, self.cmaplbl, self.cmap, self.cmaptip = add_imagemenu(
            self.rowcmap, label='cmap', values=self.cmaps,
            images=self.imaps, command=self.selected_cmap,
            tooltip='Choose colormap')
        self.cmap['text']  = 'RdYlBu'
        self.cmap['image'] = self.imaps[self.cmaps.index('RdYlBu')]
        self.cmapframe.pack(side=tk.LEFT)
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
        self.iglobalframe, self.igloballbl, self.iglobal, self.iglobaltip = (
            add_checkbutton(self.rowcmap, label='global', value=False,
                            command=self.checked,
                            tooltip='Assume global extent'))
        self.iglobalframe.pack(side=tk.LEFT)
        self.coastframe, self.coastlbl, self.coast, self.coasttip = (
            add_checkbutton(self.rowcmap, label='coast', value=True,
                            command=self.checked,
                            tooltip='Draw continental coast lines'))
        self.coastframe.pack(side=tk.LEFT)
        self.bordersframe, self.borderslbl, self.borders, self.borderstip = (
            add_checkbutton(self.rowcmap, label='borders', value=False,
                            command=self.checked,
                            tooltip='Draw country borders'))
        self.bordersframe.pack(side=tk.LEFT)
        self.riversframe, self.riverslbl, self.rivers, self.riverstip = (
            add_checkbutton(self.rowcmap, label='rivers', value=False,
                            command=self.checked,
                            tooltip='Draw rivers'))
        self.riversframe.pack(side=tk.LEFT)
        self.lakesframe, self.lakeslbl, self.lakes, self.lakestip = (
            add_checkbutton(self.rowcmap, label='lakes', value=False,
                            command=self.checked,
                            tooltip='Draw major lakes'))
        self.lakesframe.pack(side=tk.LEFT)
        self.gridframe, self.gridlbl, self.grid, self.gridtip = (
            add_checkbutton(self.rowcmap, label='grid', value=False,
                            command=self.checked,
                            tooltip='Draw major grid lines'))
        self.gridframe.pack(side=tk.LEFT)

        # 7. row
        # projections
        self.rowproj = Frame(self)
        self.projframe, self.projlbl, self.proj, self.projtip = add_menu(
            self.rowproj, label='projection', values=self.projs,
            command=self.selected_proj, width=mwidth,
            tooltip='Choose projection')
        if ihavectk:
            self.proj.set('PlateCarree')
        else:
            self.proj['text'] = 'PlateCarree'
        self.projframe.pack(side=tk.LEFT)
        tstr = ('Central longitude of projection.\n'
                'Determined from longitude variable if None.')
        self.clonframe, self.clonlbl, self.clon, self.clontip = add_entry(
            self.rowproj, label='central lon', text='None', width=ewmed,
            command=self.entered_clon, tooltip=tstr, padx=padx)
        self.clonframe.pack(side=tk.LEFT)
        # Quit button
        self.bquit, self.bquittip = add_button(
            self.rowproj, text='Quit', command=self.master.top.destroy,
            nopack=True, tooltip='Quit ncvue')
        self.bquit.pack(side=tk.RIGHT)

        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        self.rowproj.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowcmap.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowll.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowvv.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowt.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        self.rowcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # set lat/lon
        if self.usex:
            if self.lonvar:
                self.lon.set(self.lonvar)
                self.inv_lon.set(0)
                self.shift_lon.set(0)
                set_dim_lon(self)
            if self.latvar:
                self.lat.set(self.latvar)
                self.inv_lat.set(0)
                set_dim_lat(self)
        else:
            if any(self.lonvar):
                idx = [ i for i, l in enumerate(self.lonvar) if l ]
                self.lon.set(self.lonvar[idx[0]])
                self.inv_lon.set(0)
                self.shift_lon.set(0)
                set_dim_lon(self)
            if any(self.latvar):
                idx = [ i for i, l in enumerate(self.latvar) if l ]
                self.lat.set(self.latvar[idx[0]])
                self.inv_lat.set(0)
                set_dim_lat(self)

        # set global
        x = self.lon.get()
        if (x != ''):
            gx, vx = vardim2var(x, self.groups)
            xx = selvar(self, vx)
            xx = get_slice_miss(self, self.lond, xx)
            if np.any(np.isfinite(xx)):
                xx = (xx + 360.) % 360.
            if (xx.max() - xx.min()) > 150.:
                self.iglobal.set(1)
            else:
                self.iglobal.set(0)

        # animation
        rep = self.repeat.get()
        if rep == 'repeat':
            irepeat = True
        else:
            irepeat = False
        self.anim_first   = True   # True: stops in self.update at first call
        self.anim_running = True   # True/False: animation running or not
        self.anim_inc     = 1      # 1/-1: forward or backward run
        maxtime = 1
        if self.usex:
            if self.tvar:
                zz = selvar(self, self.tvar)
                maxtime = max(zz.size, maxtime)
        else:
            for vz in self.tvar:
                if vz:
                    zz = selvar(self, vz)
                    maxtime = max(zz.size, maxtime)
        self.anim = animation.FuncAnimation(
            self.figure, self.update, init_func=self.redraw,
            interval=1, repeat=irepeat, save_count=maxtime)

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

    def nrun_t(self):
        """
        Command called if forward run button was pressed.

        """
        srun = self.nrun_timelbl.get()
        if srun == '>':
            if not self.anim_running:
                self.anim_inc = 1
                self.anim.event_source.start()
                self.anim_running = True
                self.nrun_timelbl.set('||')
        elif srun == '||':
            if self.anim_running:
                self.anim.event_source.stop()
                self.anim_running = False
                self.nrun_timelbl.set('>')

    def next_t(self):
        """
        Command called if next frame button was pressed.

        """
        try:
            it = int(self.vdval[self.iunlim].get())
        except ValueError:
            it = -1
        if (it < self.nunlim - 1) and (it >= 0):
            it += 1
            self.set_tstep(it)
            self.update(it, isframe=True)
        elif it == self.nunlim - 1:
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
        if ihavectk:
            cols = self.v.cget('values')
        else:
            cols = self.v['values']
        idx  = cols.index(v)
        idx += 1
        if idx < len(cols):
            self.v.set(cols[idx])
            self.set_unlim(cols[idx])
            if ihavectk:
                self.tstep.configure(to=self.nunlim - 1)
                from_ = self.tstep.cget('from_')
                to = self.tstep.cget('to')
                self.tstep.configure(number_of_steps=to - from_ + 1)
            else:
                self.tstep['to'] = self.nunlim - 1
            self.set_tstep(0)
            vmin, vmax = self.get_vminmax()
            self.vmin.set(vmin)
            self.vmax.set(vmax)
            set_dim_var(self)
            self.redraw()

    def prev_t(self):
        """
        Command called if previous frame button was pressed.

        """
        try:
            it = int(self.vdval[self.iunlim].get())
        except ValueError:
            it = -1
        if it > 0:
            it -= 1
            self.set_tstep(it)
            self.update(it, isframe=True)
        elif it == 0:
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
        if ihavectk:
            cols = self.v.cget('values')
        else:
            cols = self.v['values']
        idx  = cols.index(v)
        idx -= 1
        if idx > 0:
            self.v.set(cols[idx])
            self.set_unlim(cols[idx])
            if ihavectk:
                self.tstep.configure(to=self.nunlim - 1)
                from_ = self.tstep.cget('from_')
                to = self.tstep.cget('to')
                self.tstep.configure(number_of_steps=to - from_ + 1)
            else:
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
        srun = self.prun_timelbl.get()
        if srun == '<':
            if not self.anim_running:
                self.anim_inc = -1
                self.anim.event_source.start()
                self.anim_running = True
                self.prun_timelbl.set('||')
        elif srun == '||':
            if self.anim_running:
                self.anim.event_source.stop()
                self.anim_running = False
                self.prun_timelbl.set('<')

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
        if ihavectk:
            self.proj.set(value)
        else:
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
        if ihavectk:
            self.tstep.configure(to=self.nunlim - 1)
            from_ = self.tstep.cget('from_')
            to = self.tstep.cget('to')
            self.tstep.configure(number_of_steps=to - from_ + 1)
        else:
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
        try:
            it = int(self.vdval[self.iunlim].get())
            self.set_tstep(it)
        except ValueError:  # mean, std, etc.
            pass
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
            gz, vz = vardim2var(v, self.groups)
            if self.usex:
                tname = self.tname
            else:
                tname = self.tname[gz]
            if vz == tname:
                return (0, 1)
            vv = selvar(self, vz)
            imiss = get_miss(self, vv)
            iall  = self.vall.get()
            if iall or (np.sum(vv.shape[:-2]) < 50):
                vv   = set_miss(imiss, vv)
                vmin = np.nanmin(vv)
                vmax = np.nanmax(vv)
            else:
                rng = default_rng()
                vmin = np.inf
                vmax = -np.inf
                for nn in range(50):
                    ss = []
                    for i in range(vv.ndim):
                        if i < vv.ndim - 2:
                            idim = rng.integers(0, vv.shape[i])
                            s = slice(idim, idim + 1)
                        else:
                            s = slice(0, vv.shape[i])
                        ss.append(s)
                    ivv   = vv[tuple(ss)]
                    ivv   = set_miss(imiss, ivv)
                    ivmin = np.nanmin(ivv)
                    ivmax = np.nanmax(ivv)
                    vmin  = min(vmin, ivmin)
                    vmax  = max(vmax, ivmax)
            return (vmin, vmax)
        else:
            return (0, 1)

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
        self.iunlim = -1
        self.nunlim = 0
        # reset dimensions
        for ll in self.vdlbl:
            ll.destroy()
        for ll in self.vd:
            ll.destroy()
        for ll in self.vdframe:
            ll.destroy()
        self.vdframe  = []
        self.vdlblval = []
        self.vdlbl    = []
        self.vdval    = []
        self.vd       = []
        self.vdtip    = []
        for i in range(self.maxdim):
            vdframe, vdlblval, vdlbl, vdval, vd, vdtip = add_spinbox(
                self.rowvd, label=str(i), values=(0,), wrap=True,
                command=self.spinned_v, state=tk.DISABLED, tooltip='None')
            self.vdframe.append(vdframe)
            self.vdlblval.append(vdlblval)
            self.vdlbl.append(vdlbl)
            self.vdval.append(vdval)
            self.vd.append(vd)
            self.vdtip.append(vdtip)
            vdframe.pack(side=tk.LEFT)
        for ll in self.latdlbl:
            ll.destroy()
        for ll in self.latd:
            ll.destroy()
        for ll in self.latdframe:
            ll.destroy()
        self.latdframe  = []
        self.latdlblval = []
        self.latdlbl    = []
        self.latdval    = []
        self.latd       = []
        self.latdtip    = []
        for i in range(self.maxdim):
            latdframe, latdlblval, latdlbl, latdval, latd, latdtip = (
                add_spinbox(self.rowlatd, label=str(i), values=(0,), wrap=True,
                            command=self.spinned_lat, state=tk.DISABLED,
                            tooltip='None'))
            self.latdframe.append(latdframe)
            self.latdlblval.append(latdlblval)
            self.latdlbl.append(latdlbl)
            self.latdval.append(latdval)
            self.latd.append(latd)
            self.latdtip.append(latdtip)
            latdframe.pack(side=tk.LEFT)
        for ll in self.londlbl:
            ll.destroy()
        for ll in self.lond:
            ll.destroy()
        for ll in self.londframe:
            ll.destroy()
        self.londframe  = []
        self.londlblval = []
        self.londlbl    = []
        self.londval    = []
        self.lond       = []
        self.londtip    = []
        for i in range(self.maxdim):
            londframe, londlblval, londlbl, londval, lond, londtip = (
                add_spinbox(self.rowlond, label=str(i), values=(0,), wrap=True,
                            command=self.spinned_lon, state=tk.DISABLED,
                            tooltip='None'))
            self.londframe.append(londframe)
            self.londlblval.append(londlblval)
            self.londlbl.append(londlbl)
            self.londval.append(londval)
            self.lond.append(lond)
            self.londtip.append(londtip)
            londframe.pack(side=tk.LEFT)
        # set time step
        if ihavectk:
            self.tstep.configure(to=1)
            from_ = self.tstep.cget('from_')
            to = self.tstep.cget('to')
            self.tstep.configure(number_of_steps=to - from_ + 1)
        else:
            self.tstep['to'] = 1
        self.tstepval.set(0)
        self.repeat.set('repeat')
        # set variables
        columns = [''] + self.cols
        if ihavectk:
            self.v.configure(values=columns)
        else:
            self.v['values'] = columns
        self.v.set(columns[0])
        self.vmin.set('None')
        self.vmax.set('None')
        # set lat/lon
        if ihavectk:
            self.lon.configure(values=columns)
        else:
            self.lon['values'] = columns
        self.lon.set(columns[0])
        if ihavectk:
            self.lat.configure(values=columns)
        else:
            self.lat['values'] = columns
        self.lat.set(columns[0])
        if self.usex:
            if self.latvar:
                self.lat.set(self.latvar)
                self.inv_lat.set(0)
                set_dim_lat(self)
            if self.lonvar:
                self.lon.set(self.lonvar)
                self.inv_lon.set(0)
                self.shift_lon.set(0)
                set_dim_lon(self)
        else:
            if any(self.latvar):
                idx = [ i for i, l in enumerate(self.latvar) if l ]
                self.lat.set(self.latvar[idx[0]])
                self.inv_lat.set(0)
                set_dim_lat(self)
            if any(self.lonvar):
                idx = [ i for i, l in enumerate(self.lonvar) if l ]
                self.lon.set(self.lonvar[idx[0]])
                self.inv_lon.set(0)
                self.shift_lon.set(0)
                set_dim_lon(self)
        x = self.lon.get()
        if (x != ''):
            gx, vx = vardim2var(x, self.groups)
            xx = selvar(self, vx)
            xx = get_slice_miss(self, self.lond, xx)
            xx = xx + 360.
            if (xx.max() - xx.min()) > 150.:
                self.iglobal.set(1)
            else:
                self.iglobal.set(0)

    def set_tstep(self, it):
        """
        Make all steps when changing time step.

        `it` (int) is the time step.

        Sets the time dimension spinbox, sets the time step scale,
        write the time on top.

        """
        v = self.v.get()
        gz, vz = vardim2var(v, self.groups)
        if self.usex:
            dunlim = self.dunlim
            time = self.time
        else:
            dunlim = self.dunlim[gz]
            time = self.time[gz]
        try:
            zz = selvar(self, vz)
            if self.usex:
                dims = zz.dims
            else:
                dims = zz.dimensions
            has_unlim = dunlim in dims
        except IndexError:
            has_unlim = False  # datetime
        if dunlim and has_unlim:
            self.vdval[self.iunlim].set(it)
            self.tstepval.set(it)
            if self.usex:
                self.timelbl.set(str(time.values[it]))
            else:
                try:
                    self.timelbl.set(np.around(time[it], 4))
                except TypeError:
                    self.timelbl.set(time[it])

    def set_unlim(self, v):
        """
        Set index and length of unlimited dimension of variable `v`.

        `v` (str) is the variable name as in the selection comboboxes, i.e.
        `gvar, var = vardim2var(self.fi[v)]`.

        Sets `self.nunlim` to the length of the unlimited dimension and
        `self.iunlim` to the index in variable.dimensions if
        `self.dunlim ~= ''` and `self.dunlim` in var.dimensions.

        Takes `self.iunlim=0` and `self.nunlim=variable.shape[0]` if
        self.dunlim == ''` or `self.dunlim` not in var.dimensions.

        """
        gz, vz = vardim2var(v, self.groups)
        if self.usex:
            tname = self.tname
            time = self.time
            dunlim = self.dunlim
        else:
            tname = self.tname[gz]
            time = self.time[gz]
            dunlim = self.dunlim[gz]
        if vz == tname:
            self.iunlim = 0
            self.nunlim = time.size
        else:
            zz = selvar(self, vz)
            if self.usex:
                dims = zz.dims
            else:
                dims = zz.dimensions
            if dunlim:
                if dunlim in dims:
                    self.iunlim = dims.index(dunlim)
                else:
                    self.iunlim = 0
            else:
                self.iunlim = 0
            if zz.ndim > 0:
                self.nunlim = zz.shape[self.iunlim]
            else:
                self.nunlim = 0

    #
    # Plotting
    #

    # def redraw(self):
    #     pass

    def redraw(self):
        """
        Redraws the plot.

        Reads `lon`, `lat`, `variable` names, the current settings of
        their dimension spinboxes, as well as all other plotting options.
        Then redraws the plot.

        """
        # stop animation
        self.anim.event_source.stop()
        self.anim_running = False
        # get all states
        # rowv
        v = self.v.get()
        trans_v = self.trans_v.get()
        vmin = self.vmin.get()
        if vmin == 'None':
            vmin = None
        else:
            try:
                vmin = float(vmin)
            except ValueError:
                vmin = None
        vmax = self.vmax.get()
        if vmax == 'None':
            vmax = None
        else:
            try:
                vmax = float(vmax)
            except ValueError:
                vmax = None
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
        self.iiglobal = self.iglobal.get()
        coast    = self.coast.get()
        borders  = self.borders.get()
        rivers   = self.rivers.get()
        lakes    = self.lakes.get()
        grid     = self.grid.get()
        if ihavectk:
            proj = self.proj.get()
        else:
            proj = self.proj['text']
        self.iproj = self.iprojs[self.projs.index(proj)]
        clon     = self.clon.get()
        # set x, y, axes labels
        vx = 'None'
        vy = 'None'
        vz = 'None'
        if (v != ''):
            # variable
            gz, vz = vardim2var(v, self.groups)
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
                    vv = dtimez
                    vlab = 'Year'
                else:
                    vv = timez
                    vlab = 'Date'
            else:
                vv = selvar(self, vz)
                vlab = set_axis_label(vv)
            vv = get_slice_miss(self, self.vd, vv)
            if trans_v:
                vv = vv.T
            if shift_lon:
                vv = np.roll(vv, vv.shape[1] // 2, axis=1)
        else:
            vlab = ''
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
            yy = get_slice_miss(self, self.latd, yy)
        else:
            ylab = ''
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
            xx = get_slice_miss(self, self.lond, xx)
            # set central longitude of projection
            # make in 0-360, otherwise always 0 if -180 to 180
            if np.any(np.isfinite(xx)):
                xx360 = (xx + 360.) % 360.
            else:
                xx360 = xx
            if xx.size > 1:
                if xx.ndim > 1:
                    x0 = xx[:, 0].mean()
                    if self.iiglobal:
                        # -2 instead of -1 to avoid possible cyclic longitude
                        x1 = xx[:, -2].mean()
                    else:
                        x1 = xx[:, -1].mean()
                else:
                    x0 = xx[0]
                    if self.iiglobal:
                        x1 = xx[-2]
                    else:
                        x1 = xx[-1]
                self.ixxmean = 0.5 * (x1 + x0)
                if self.iiglobal:
                    # round it to next 180 degrees to get 0 or 180
                    self.ixxmean = np.around(self.ixxmean / 180., 0) * 180.
            else:
                self.ixxmean = xx360[0]
            # seems to work better if central lon in projection
            # is set from -180 to 180 even if lon is given in 0-360
            if self.ixxmean > 180.:
                self.ixxmean -= 360.
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
                print(f'Map: var ({vz}) is not 2-dimensional:', vv.shape)
                return
            # set x and y to index if not selected
            if (x == ''):
                nx = vv.shape[1]
                xx = -180. + np.arange(nx) / float(nx) * 360.
                xx += 0.5 * (xx[1] - xx[0])
                xlab = ''
            if (y == ''):
                ny = vv.shape[0]
                yy = -90. + np.arange(ny) / float(ny) * 180.
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
                print(f'Map: lon ({vx}), lat ({vy}) dimensions not 1D or 2D:',
                      xx.shape, yy.shape)
                return
            if inv_lon:
                self.ixx = np.fliplr(self.ixx)
            if inv_lat:
                self.iyy = np.flipud(self.iyy)
            self.ivv = vv
            if self.iiglobal:
                # cartopy.contourf needs cyclic longitude for wrap around
                self.ivvc, self.ixxc, self.iyyc = add_cyclic(
                    self.ivv, x=self.ixx, y=self.iyy)
                # # special treatment if fringe points < 1e-4 apart
                # # This works but it did still not display correctly the
                # # test file of GDPS from cuizinart
                # # -> do not do it for the moment
                # if np.ma.allclose(np.ma.sin(np.deg2rad(self.ixxc[:, 0])),
                #                   np.ma.sin(np.deg2rad(self.ixxc[:, -1])),
                #                   atol=1.0e-5):
                #     if np.ma.allclose(self.ixxc[:, 0], self.ixxc[:, -1],
                #                       atol=1.0e-4):
                #         self.ixxc = self.ixxc.astype(float)
                #         self.ixxc[:, -1] = self.ixxc[:, 0] + 360.
            else:
                self.ivvc = self.ivv
                self.ixxc = self.ixx
                self.iyyc = self.iyy
            self.itrans  = ccrs.PlateCarree()
            self.ivmin   = vmin
            self.ivmax   = vmax
            self.icmap   = cmap
            self.ncmap   = mpl.colormaps[self.icmap].N
            self.ncmap   = self.ncmap if self.ncmap < 256 else 15
            self.iextend = extend
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
                        transform=self.itrans)
                    # self.cc = self.axes.imshow(
                    #     vv, vmin=vmin, vmax=vmax, cmap=cmap,
                    #     origin='upper', extent=self.img_extent,
                    #     transform=self.itrans)
                    self.cb = self.figure.colorbar(self.cc, fraction=0.05,
                                                   shrink=0.75, pad=0.07,
                                                   extend=self.iextend)
                except Exception:
                    print(f'Map pcolormesh: lon ({vx}), lat ({vy}),'
                          f' var ({vz}) shapes do not match:',
                          self.ixx.shape, self.iyy.shape, self.ivv.shape)
                    return
            else:
                try:
                    # if 1-D then len(x)==m (columns) and
                    #     len(y)==n (rows): v(n,m)
                    self.cc = self.axes.contourf(
                        self.ixxc, self.iyyc, self.ivvc, self.ncmap,
                        vmin=self.ivmin, vmax=self.ivmax,
                        cmap=self.icmap, extend=self.iextend,
                        transform=self.itrans)
                    self.cb = self.figure.colorbar(self.cc, fraction=0.05,
                                                   shrink=0.75, pad=0.07)
                    # self.cc, = self.axes.plot(yy, vv[0,:])
                except Exception:
                    print('Map contourf: lon ({vx}), lat ({vy}),'
                          f' var ({vz}) shapes do not match for:',
                          self.ixxc.shape, self.iyyc.shape, self.ivvc.shape)
                    return
            self.cb.set_label(vlab)
            self.axes.format_coord = lambda x, y: format_coord_map(
                x, y, self.axes, self.ixx, self.iyy, self.ivv)
        # help(self.figure)
        if self.iiglobal:
            self.axes.set_global()
        if coast:
            # self.axes.coastlines()
            self.axes.add_feature(cfeature.COASTLINE)
            self.axes.gridlines(draw_labels=True, linewidth=0,
                                x_inline=False, y_inline=False)
        if borders:
            self.axes.add_feature(cfeature.BORDERS, edgecolor='grey')
        if rivers:
            self.axes.add_feature(cfeature.RIVERS)
        if lakes:
            self.axes.add_feature(cfeature.LAKES, alpha=0.5)
        self.axes.xaxis.set_label_text(xlab)
        self.axes.yaxis.set_label_text(ylab)
        if grid:
            self.axes.gridlines(draw_labels=False,
                                x_inline=False, y_inline=False)
        # redraw
        self.canvas.draw()
        self.toolbar.update()

    # def update(self, frame, isframe=False):
    #     pass

    def update(self, frame, isframe=False):
        """
        Updates data of the current plot.

        """
        if self.anim_first:
            self.anim.event_source.stop()
            self.anim_running = False
            self.anim_first   = False
            return
        # variable
        v = self.v.get()
        if (v != ''):
            trans_v = self.trans_v.get()
            mesh = self.mesh.get()
            rep = self.repeat.get()
            # inv_lon = self.inv_lon.get()
            # inv_lat = self.inv_lat.get()
            shift_lon = self.shift_lon.get()
            gz, vz = vardim2var(v, self.groups)
            if self.usex:
                if vz == self.tname:
                    vz = self.tvar
            else:
                if vz == self.tname[gz]:
                    vz = self.tvar[gz]
            vv = selvar(self, vz)
            # slice
            try:
                it = int(self.vdval[self.iunlim].get())
                if not isframe:
                    if (self.anim_inc == 1) and (it == self.nunlim - 1):
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
            if vv.ndim < 2:
                self.anim.event_source.stop()
                self.anim_running = False
                return
            if trans_v:
                vv = vv.T
            if shift_lon:
                vv = np.roll(vv, vv.shape[1] // 2, axis=1)
            self.ivv = vv
            # set data
            if mesh:
                # update works well on 'normal' pcolormesh but not on Cartopy's
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
                    transform=self.itrans)
                # self.cc.remove()
                # self.cc = self.axes.imshow(
                #     vv, vmin=self.ivmin, vmax=self.ivmax, cmap=self.icmap,
                #     origin='upper', extent=self.img_extent,
                #     transform=self.itrans)
            else:
                # # https://discourse.matplotlib.org/t/update-an-existing-contour-plot-with-new-data/13935
                # for coll in self.cc.collections:
                #     self.axes.collections.remove(coll)
                self.cc.remove()
                if self.iiglobal:
                    # self.ivvc = add_cyclic(self.ivv)
                    self.ivvc, self.ixxc = add_cyclic(
                        self.ivv, x=self.ixx)
                else:
                    self.ivvc = self.ivv
                self.cc = self.axes.contourf(
                    self.ixxc, self.iyyc, self.ivvc, self.ncmap,
                    vmin=self.ivmin, vmax=self.ivmax,
                    cmap=self.icmap, extend=self.iextend,
                    transform=self.itrans)
            self.canvas.draw_idle()
            return self.cc,
