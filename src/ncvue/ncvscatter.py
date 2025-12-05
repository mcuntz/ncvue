#!/usr/bin/env python
"""
Scatter/Line panel of ncvue.

The panel allows plotting variables against time or two variables against
each other. A second variable can be plotted in the same graph using the
right-hand-side y-axis.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020-2021 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvScatter

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Open new netcdf file, communicate via top widget,
     Jan 2021, Matthias Cuntz
   * Write left-hand side and right-hand side values on bottom of plotting
     canvas, May 2021, Matthias Cuntz
   * Address fi.variables[name] directly by fi[name], Jan 2024, Matthias Cuntz
   * Allow groups in netcdf files, Jan 2024, Matthias Cuntz
   * Allow multiple netcdf files, Jan 2024, Matthias Cuntz
   * Move themes/ and images/ back to src/ncvue/, Feb 2024, Matthias Cuntz
   * Add Quit button, Nov 2024, Matthias Cuntz
   * Use CustomTkinter if installed, Nov 2024, Matthias Cuntz
   * Use add_button, add_label widgets, Feb 2025, Matthias Cuntz
   * Use add_combobox instead of Combobox directly, Feb 2025, Matthias Cuntz
   * Add previous and next for right-hand-side axis, Feb 2025, Matthias Cuntz
   * Include xarray to read input files, Feb 2025, Matthias Cuntz
   * Add xlim, ylim, and y2lim options, Jun 2025, Matthias Cuntz
   * Bugfix for setting axes limits, Jun 2025, Matthias Cuntz
   * Tooltip for xlim and ylim includes datetime, Nov 2025, Matthias Cuntz
   * Draw canvas as last element so that UI controls are displayed
     as long as possible, Dec 2025, Matthias Cuntz

"""
import tkinter as tk
try:
    from customtkinter import CTkFrame as Frame
    ihavectk = True
except ModuleNotFoundError:
    from tkinter.ttk import Frame
    ihavectk = False
import numpy as np
import netCDF4 as nc
try:
    import xarray as xr
    ihavex = True
except ModuleNotFoundError:
    ihavex = False
from .ncvutils import clone_ncvmain, format_coord_scatter, selvar
from .ncvutils import set_axis_label, vardim2var, parse_entry
from .ncvmethods import analyse_netcdf, get_slice_miss
from .ncvmethods import set_dim_x, set_dim_y, set_dim_y2
from .ncvwidgets import add_checkbutton, add_combobox, add_entry
from .ncvwidgets import add_spinbox, add_label, add_button
from .ncvscreen import ncvScreen
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


__all__ = ['ncvScatter']


def _minmax_ylim(self, ylim, ylim2):
    """
    Get minimum of first elements of lists `ylim` and `ylim2` and
    maximum of second element of the two lists.

    Returns minimum, maximum.

    """
    if (ylim[0] is not None) and (ylim2[0] is not None):
        ymin = min(ylim[0], ylim2[0])
    else:
        if (ylim[0] is not None):
            ymin = ylim[0]
        else:
            ymin = ylim2[0]
    if (ylim[1] is not None) and (ylim2[1] is not None):
        ymax = max(ylim[1], ylim2[1])
    else:
        if (ylim[1] is not None):
            ymax = ylim[1]
        else:
            ymax = ylim2[1]
    return ymin, ymax


class ncvScatter(Frame):
    """
    Panel for scatter and line plots.

    Sets up the layout with the figure canvas, variable selectors, dimension
    spinboxes, and options in __init__.

    Contains various commands that manage what will be drawn or redrawn if
    something is selected, changed, checked, etc.

    Contains three drawing routines. `redraw_y` and `redraw_y2` redraw the
    y-axes without changing zoom level, etc. `redraw` is called if a new
    x-variable was selected or the `Redraw`-button was pressed. It resets
    all axes, resetting zoom, etc.

    """

    #
    # Setup panel
    #

    def __init__(self, master, **kwargs):
        from functools import partial
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        from matplotlib.figure import Figure

        super().__init__(master, **kwargs)

        self.name   = 'Scatter/Line'
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
        # colors
        c = list(plt.rcParams['axes.prop_cycle'])
        col1 = c[0]['color']  # blue
        col2 = c[3]['color']  # red
        # color tooltip
        ctstr = ('- color names: red, green, blue, yellow, ...\n'
                 '- single characters: b (blue), g (green), r (red), c (cyan),'
                 ' m (magenta), y (yellow), k (black), w (white)\n'
                 '- hex RGB: #rrggbb such such as #ff9300 (orange)\n'
                 '- gray level: float between 0 and 1\n'
                 '- RGA (red, green, blue) or RGBA (red, green, blue, alpha)'
                 ' tuples between 0 and 1, e.g. (1, 0.57, 0) for orange\n'
                 '- name from xkcd color survey, e.g. xkcd:sky blue')
        # marker tooltip
        mtstr = ('. (point), "," (pixel), o (circle),\n'
                 'v (triangle_down), ^ (triangle_up),\n'
                 '< (triangle_left), > (triangle_right),\n'
                 '1 (tri_down), 2 (tri_up), 3 (tri_left), 4 (tri_right),'
                 ' 8 (octagon),\n'
                 's (square), p (pentagon), P (plus (filled)),\n'
                 '* (star), h (hexagon1), H (hexagon2),\n'
                 '+ (plus), x (x), X (x (filled)),\n'
                 'D (diamond), d (thin_diamond),\n'
                 '| (vline), _ (hline), or None')
        # xlim, ylim tooltip
        ltstr = ("min, max\n"
                 "Set to None for free scaling.\n"
                 "Datetime must be in iso8601 format, e.g. 2025-11-23")
        # high-resolution screens
        sc = ncvScreen(self.top)
        if ihavectk:
            # width of combo boxes in px
            combowidth = 288
            # widths of entry widgets in px
            ewsmall = 20
            ewmed = 45
            ewbig = 70
            ew2big = 100
            # pad between label and entry
            padx = 3
            # width of animation and variables buttons
            bwidth = 35
            # width of projections menu
            mwidth = 70
        else:
            # width of combo boxes in characters
            combowidth = 28
            # widths of entry widgets in characters
            ewsmall = 3
            ewmed = 5
            ewbig = 7
            ew2big = 10
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
        self.figure = Figure(facecolor='white', figsize=(1, 1))  # , dpi=sc.dpi_default)
        self.axes   = self.figure.add_subplot(111)
        self.axes2  = self.axes.twinx()
        self.axes2.yaxis.set_label_position('right')
        self.axes2.yaxis.tick_right()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.rowcanvas)
        self.canvas.draw()
        self.tkcanvas = self.canvas.get_tk_widget()
        self.tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # matplotlib toolbar
        # toolbar uses pack internally -> put into frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.rowcanvas,
                                            pack_toolbar=True)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 1. row: x- and lhs y-axis selection
        self.rowxy = Frame(self)
        # block with x and its dimensions
        self.blockx = Frame(self.rowxy)
        self.blockx.pack(side=tk.LEFT)
        # x
        self.rowx = Frame(self.blockx)
        self.rowx.pack(side=tk.TOP, fill=tk.X)
        self.xframe, self.xlbl, self.x, self.xtip = add_combobox(
            self.rowx, label='x', values=columns, command=self.selected_x,
            width=combowidth, padx=padx,
            tooltip=('Choose variable of x-axis.\nTakes index if "None",'
                     ' which is much faster.'))
        self.xframe.pack(side=tk.LEFT)
        # invert x
        self.inv_xframe, self.inv_xlbl, self.inv_x, self.inv_xtip = (
            add_checkbutton(self.rowx, label='invert x', value=False,
                            command=self.checked_x, tooltip='Invert x-axis'))
        self.inv_xframe.pack(side=tk.LEFT)
        # x dimensions
        self.rowxd = Frame(self.blockx)
        self.rowxd.pack(side=tk.TOP, fill=tk.X)
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

        # space between x and y blocks
        spacex = add_label(self.rowxy, text=' ' * 2)

        # block with y and its dimensions
        self.blocky = Frame(self.rowxy)
        self.blocky.pack(side=tk.LEFT)
        # y
        self.rowy = Frame(self.blocky)
        self.rowy.pack(side=tk.TOP, fill=tk.X)
        lkwargs = {}
        if ihavectk:
            lkwargs.update({'padx': padx})
        ylab = add_label(self.rowy, text='y', **lkwargs)
        spacep = add_label(self.rowy, text=' ' * 1)
        self.bprev_y, self.bprev_ytip = add_button(
            self.rowy, text='<', command=self.prev_y, width=bwidth,
            tooltip='Previous variable')
        self.bnext_y, self.bnext_ytip = add_button(
            self.rowy, text='>', command=self.next_y, width=bwidth,
            tooltip='Next variable')
        self.yframe, self.ylbl, self.y, self.ytip = add_combobox(
            self.rowy, label='', values=columns, command=self.selected_y,
            width=combowidth, padx=0,
            tooltip='Choose variable of y-axis')
        self.yframe.pack(side=tk.LEFT)
        self.line_y = []
        self.inv_yframe, self.inv_ylbl, self.inv_y, self.inv_ytip = (
            add_checkbutton(self.rowy, label='invert y', value=False,
                            command=self.checked_y, tooltip='Inert y-axis'))
        self.inv_yframe.pack(side=tk.LEFT)
        # y dimensions
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

        # redraw button
        self.bredraw, self.bredrawtip = add_button(
            self.rowxy, text='Redraw', command=self.redraw, nopack=True,
            tooltip='Redraw, resetting zoom')
        self.bredraw.pack(side=tk.RIGHT)

        # 2. row
        # options for lhs y-axis
        self.rowxyopt = Frame(self)
        self.lsframe, self.lslbl, self.ls, self.lstip = add_entry(
            self.rowxyopt, label='ls', text='-', width=ewmed,
            command=self.entered_y, padx=padx,
            tooltip='Line style: -, --, -., :, or None')
        self.lsframe.pack(side=tk.LEFT)
        self.lwframe, self.lwlbl, self.lw, self.lwtip = add_entry(
            self.rowxyopt, label='lw', text='1', width=ewsmall,
            command=self.entered_y, tooltip='Line width', padx=padx)
        self.lwframe.pack(side=tk.LEFT)
        self.lcframe, self.lclbl, self.lc, self.lctip = add_entry(
            self.rowxyopt, label='c', text=col1, width=ewbig,
            command=self.entered_y, padx=padx,
            tooltip='Line color:\n' + ctstr)
        self.lcframe.pack(side=tk.LEFT)
        self.markerframe, self.markerlbl, self.marker, self.markertip = (
            add_entry(self.rowxyopt, label='marker', text='None', width=ewmed,
                      command=self.entered_y, padx=padx,
                      tooltip='Marker symbol:\n' + mtstr))
        self.markerframe.pack(side=tk.LEFT)
        self.msframe, self.mslbl, self.ms, self.mstip = add_entry(
            self.rowxyopt, label='ms', text='1', width=ewsmall,
            command=self.entered_y, tooltip='Marker size', padx=padx)
        self.msframe.pack(side=tk.LEFT)
        self.mfcframe, self.mfclbl, self.mfc, self.mfctip = add_entry(
            self.rowxyopt, label='mfc', text=col1, width=ewbig,
            command=self.entered_y, padx=padx,
            tooltip='Marker fill color:\n' + ctstr)
        self.mfcframe.pack(side=tk.LEFT)
        self.mecframe, self.meclbl, self.mec, self.mectip = add_entry(
            self.rowxyopt, label='mec', text=col1, width=ewbig,
            command=self.entered_y, padx=padx,
            tooltip='Marker edge color:\n' + ctstr)
        self.mecframe.pack(side=tk.LEFT)
        self.mewframe, self.mewlbl, self.mew, self.mewtip = add_entry(
            self.rowxyopt, label='mew', text='1', width=ewsmall, padx=padx,
            command=self.entered_y, tooltip='Marker edge width')
        self.mewframe.pack(side=tk.LEFT)

        # x- and y-limit
        self.rowxlim = Frame(self)
        self.xlimframe, self.xlimlbl, self.xlim, self.xlimtip = add_entry(
            self.rowxlim, label="xlim", text='None', width=ew2big,
            command=self.entered_y, padx=padx, tooltip=ltstr)
        self.xlimframe.pack(side=tk.LEFT)
        space3 = add_label(self.rowxlim, text=' ' * 3)
        self.ylimframe, self.ylimlbl, self.ylim, self.ylimtip = add_entry(
            self.rowxlim, label="ylim", text='None', width=ew2big,
            command=self.entered_y, padx=padx, tooltip=ltstr)
        self.ylimframe.pack(side=tk.LEFT)

        # empty row
        self.rowspace = Frame(self)
        rowspace = add_label(self.rowspace, text=' ')

        # 3. row
        # rhs y-axis 2 selection
        self.rowyy2 = Frame(self)
        self.blocky2 = Frame(self.rowyy2)
        self.blocky2.pack(side=tk.LEFT)
        self.rowy2 = Frame(self.blocky2)
        self.rowy2.pack(side=tk.TOP, fill=tk.X)
        lkwargs = {}
        if ihavectk:
            lkwargs.update({'padx': padx})
        ylab2 = add_label(self.rowy2, text='y2', **lkwargs)
        spacep2 = add_label(self.rowy2, text=' ' * 1)
        self.bprev_y2, self.bprev_y2tip = add_button(
            self.rowy2, text='<', command=self.prev_y2, width=bwidth,
            tooltip='Previous variable')
        self.bnext_y2, self.bnext_y2tip = add_button(
            self.rowy2, text='>', command=self.next_y2, width=bwidth,
            tooltip='Next variable')
        self.y2frame, self.y2lbl, self.y2, self.y2tip = add_combobox(
            self.rowy2, label='', values=columns,
            command=self.selected_y2, width=combowidth, padx=0,
            tooltip='Choose variable for right-hand-side y-axis')
        self.y2frame.pack(side=tk.LEFT)
        self.line_y2 = []
        self.inv_y2frame, self.inv_y2lbl, self.inv_y2, self.inv_y2tip = (
            add_checkbutton(self.rowy2, label='invert y2', value=False,
                            command=self.checked_y2,
                            tooltip='Invert right-hand-side y-axis'))
        self.inv_y2frame.pack(side=tk.LEFT)
        spacey2 = add_label(self.rowy2, text=' ')
        tstr = 'Same limits for left-hand-side and right-hand-side y-axes'
        self.same_yframe, self.same_ylbl, self.same_y, self.same_ytip = (
            add_checkbutton(self.rowy2, label='same y-axes', value=False,
                            command=self.checked_yy2, tooltip=tstr))
        self.same_yframe.pack(side=tk.LEFT)
        self.rowy2d = Frame(self.blocky2)
        self.rowy2d.pack(side=tk.TOP, fill=tk.X)
        self.y2dframe  = []
        self.y2dlblval = []
        self.y2dlbl    = []
        self.y2dval    = []
        self.y2d       = []
        self.y2dtip    = []
        for i in range(self.maxdim):
            y2dframe, y2dlblval, y2dlbl, y2dval, y2d, y2dtip = add_spinbox(
                self.rowy2d, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y2, state=tk.DISABLED, tooltip='None')
            self.y2dframe.append(y2dframe)
            self.y2dlblval.append(y2dlblval)
            self.y2dlbl.append(y2dlbl)
            self.y2dval.append(y2dval)
            self.y2d.append(y2d)
            self.y2dtip.append(y2dtip)
            y2dframe.pack(side=tk.LEFT)

        # 4. row
        # options for rhs y-axis 2
        self.rowy2opt = Frame(self)
        self.ls2frame, self.ls2lbl, self.ls2, self.ls2tip = add_entry(
            self.rowy2opt, label='ls', text='-', width=ewmed,
            command=self.entered_y2, padx=padx,
            tooltip='Line style: -, --, -., :, or None')
        self.ls2frame.pack(side=tk.LEFT)
        self.lw2frame, self.lw2lbl, self.lw2, self.lw2tip = add_entry(
            self.rowy2opt, label='lw', text='1', width=ewsmall, padx=padx,
            command=self.entered_y2, tooltip='Line width')
        self.lw2frame.pack(side=tk.LEFT)
        self.lc2frame, self.lc2lbl, self.lc2, self.lc2tip = add_entry(
            self.rowy2opt, label='c', text=col2, width=ewbig,
            command=self.entered_y2, padx=padx,
            tooltip='Line color:\n' + ctstr)
        self.lc2frame.pack(side=tk.LEFT)
        self.marker2frame, self.marker2lbl, self.marker2, self.marker2tip = (
            add_entry(self.rowy2opt, label='marker', text='None', width=ewmed,
                      command=self.entered_y2, padx=padx,
                      tooltip='Marker symbol:\n' + mtstr))
        self.marker2frame.pack(side=tk.LEFT)
        self.ms2frame, self.ms2lbl, self.ms2, self.ms2tip = add_entry(
            self.rowy2opt, label='ms', text='1', width=ewsmall, padx=padx,
            command=self.entered_y2, tooltip='Marker size')
        self.ms2frame.pack(side=tk.LEFT)
        self.mfc2frame, self.mfc2lbl, self.mfc2, self.mfc2tip = add_entry(
            self.rowy2opt, label='mfc', text=col2, width=ewbig, padx=padx,
            command=self.entered_y2, tooltip='Marker fill color:\n' + ctstr)
        self.mfc2frame.pack(side=tk.LEFT)
        self.mec2frame, self.mec2lbl, self.mec2, self.mec2tip = add_entry(
            self.rowy2opt, label='mec', text=col2, width=ewbig, padx=padx,
            command=self.entered_y2, tooltip='Marker edge color:\n' + ctstr)
        self.mec2frame.pack(side=tk.LEFT)
        self.mew2frame, self.mew2lbl, self.mew2, self.mew2tip = add_entry(
            self.rowy2opt, label='mew', text='1', width=ewsmall, padx=padx,
            command=self.entered_y2, tooltip='Marker edge width')
        self.mew2frame.pack(side=tk.LEFT)
        
        # Quit button
        self.rowquit = Frame(self)

        # block with y2lim
        self.blocky2lim = Frame(self.rowquit)
        self.blocky2lim.pack(side=tk.LEFT)
        self.y2limframe, self.y2limlbl, self.y2lim, self.y2limtip = add_entry(
            self.blocky2lim, label="y2lim", text='None', width=ew2big,
            command=self.entered_y2, padx=padx, tooltip=ltstr)
        self.y2limframe.pack(side=tk.LEFT)

        self.bquit, self.bquittip = add_button(
            self.rowquit, text='Quit', command=self.master.top.destroy,
            nopack=True, tooltip='Quit ncvue')
        self.bquit.pack(side=tk.RIGHT)

        # From matplotlib example 'embedding_in_tk_sgskip.py'
        # Packing order is important. Widgets are processed sequentially and if there
        # is no space left, because the window is too small, they are not displayed.
        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        self.rowquit.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowy2opt.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowyy2.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowspace.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowxlim.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowxyopt.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowxy.pack(side=tk.BOTTOM, fill=tk.X)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        self.rowcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    #
    # Event bindings
    #

    def checked_x(self):
        """
        Command called if any checkbutton for x-axis was checked or unchecked.

        Redraws left-hand-side and right-hand-side y-axes.

        """
        self.redraw_y()
        self.redraw_y2()

    def checked_y(self):
        """
        Command called if any checkbutton for left-hand-side y-axis was checked
        or unchecked.

        Redraws left-hand-side y-axis.

        """
        self.redraw_y()

    def checked_y2(self):
        """
        Command called if any checkbutton for right-hand-side y-axis was
        checked or unchecked.

        Redraws right-hand-side y-axis.

        """
        self.redraw_y2()

    def checked_yy2(self):
        """
        Command called if any checkbutton was checked or unchecked
        that concerns both, the left-hand-side and right-hand-side
        y-axes.

        Redraws left-hand-side and right-hand-side y-axes.

        """
        self.ylim.set('None')
        self.y2lim.set('None')
        self.redraw_y()
        self.redraw_y2()

    def entered_y(self, event):
        """
        Command called if option was entered for left-hand-side y-axis.

        Redraws left-hand-side y-axis.

        """
        self.redraw_y()

    def entered_y2(self, event):
        """
        Command called if option was entered for right-hand-side y-axis.

        Redraws right-hand-side y-axis.

        """
        self.redraw_y2()

    def next_y(self):
        """
        Command called if next button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        y = self.y.get()
        if ihavectk:
            cols = self.y.cget('values')
        else:
            cols = self.y['values']
        idx  = cols.index(y)
        idx += 1
        if idx < len(cols):
            self.y.set(cols[idx])
            set_dim_y(self)
            self.ylim.set('None')
            self.redraw()

    def next_y2(self):
        """
        Command called if next button for the right-hand-side y-variable was
        pressed.

        Resets dimensions of right-hand-side y-variable.
        Redraws plot.

        """
        y2 = self.y2.get()
        if ihavectk:
            cols = self.y2.cget('values')
        else:
            cols = self.y2['values']
        idx  = cols.index(y2)
        idx += 1
        if idx < len(cols):
            self.y2.set(cols[idx])
            set_dim_y2(self)
            self.y2lim.set('None')
            self.redraw()

    # def onpick(self, event):
    #     print('in pick')
    #     print('you pressed', event.button, event.xdata, event.ydata)
    #     thisline = event.artist
    #     xdata = thisline.get_xdata()
    #     ydata = thisline.get_ydata()
    #     ind = event.ind
    #     points = tuple(zip(xdata[ind], ydata[ind]))
    #     print('onpick points:', points)

    def prev_y(self):
        """
        Command called if previous button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        y = self.y.get()
        if ihavectk:
            cols = self.y.cget('values')
        else:
            cols = self.y['values']
        idx  = cols.index(y)
        idx -= 1
        if idx > 0:
            self.y.set(cols[idx])
            set_dim_y(self)
            self.ylim.set('None')
            self.redraw()

    def prev_y2(self):
        """
        Command called if previous button for the right-hand-side y-variable
        was pressed.

        Resets dimensions of right-hand-side y-variable.
        Redraws plot.

        """
        y2 = self.y2.get()
        if ihavectk:
            cols = self.y2.cget('values')
        else:
            cols = self.y2['values']
        idx  = cols.index(y2)
        idx -= 1
        if idx > 0:
            self.y2.set(cols[idx])
            set_dim_y2(self)
            self.y2lim.set('None')
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
            if self.top.usex:
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

    def selected_x(self, event):
        """
        Command called if x-variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Resets `x` dimensions. Redraws plot.

        """
        set_dim_x(self)
        self.xlim.set('None')
        self.redraw()

    def selected_y(self, event):
        """
        Command called if left-hand-side y-variable was selected with
        combobox.

        Triggering `event` was bound to the combobox.

        Resets left-hand-side `y` dimensions. Redraws plot.

        """
        set_dim_y(self)
        self.ylim.set('None')
        self.redraw()

    def selected_y2(self, event):
        """
        Command called if right-hand-side y-variable was selected with
        combobox.

        Triggering `event` was bound to the combobox.

        Resets right-hand-side `y` dimensions. Redraws plot.

        """
        set_dim_y2(self)
        self.y2lim.set('None')
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
        Command called if spinbox of any dimension of left-hand-side
        y-variable was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.

        """
        self.redraw()

    def spinned_y2(self, event=None):
        """
        Command called if spinbox of any dimension of right-hand-side
        y-variable was changed.

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
        for ll in self.y2dlbl:
            ll.destroy()
        for ll in self.y2d:
            ll.destroy()
        for ll in self.y2dframe:
            ll.destroy()
        self.y2dframe  = []
        self.y2dlblval = []
        self.y2dlbl    = []
        self.y2dval    = []
        self.y2d       = []
        self.y2dtip    = []
        for i in range(self.maxdim):
            y2dframe, y2dlblval, y2dlbl, y2dval, y2d, y2dtip = add_spinbox(
                self.rowy2d, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y2, state=tk.DISABLED, tooltip='None')
            self.y2dframe.append(y2dframe)
            self.y2dlblval.append(y2dlblval)
            self.y2dlbl.append(y2dlbl)
            self.y2dval.append(y2dval)
            self.y2d.append(y2d)
            self.y2dtip.append(y2dtip)
            y2dframe.pack(side=tk.LEFT)
        # set variables
        columns = [''] + self.cols
        if ihavectk:
            self.x.configure(values=columns)
        else:
            self.x['values'] = columns
        self.x.set(columns[0])
        self.xlim.set('None')
        if ihavectk:
            self.y.configure(values=columns)
        else:
            self.y['values'] = columns
        self.y.set(columns[0])
        self.ylim.set('None')
        if ihavectk:
            self.y2.configure(values=columns)
        else:
            self.y2['values'] = columns
        self.y2.set(columns[0])
        self.y2lim.set('None')

    #
    # Plot
    #

    def redraw_y(self):
        """
        Redraw the left-hand-side y-axis.

        Reads left-hand-side `y` variable name, the current settings of
        its dimension spinboxes, as well as all other plotting options.
        Then redraws the left-hand-side y-axis.

        """
        # get all states
        # rowxy
        y = self.y.get()
        if y != '':
            inv_y = self.inv_y.get()
            ylim = parse_entry(self.ylim.get())
            ylim2 = parse_entry(self.y2lim.get())
            # rowxyopt
            ls  = self.ls.get()
            lw  = float(self.lw.get())
            c   = str(self.lc.get())
            try:
                if isinstance(eval(c), tuple):
                    c = eval(c)
            except:  # several different exceptions possible
                pass
            m   = self.marker.get()
            ms  = float(self.ms.get())
            mfc = self.mfc.get()
            try:
                if isinstance(eval(mfc), tuple):
                    mfc = eval(mfc)
            except:
                pass
            mec = self.mec.get()
            try:
                if isinstance(eval(mec), tuple):
                    mec = eval(mec)
            except:
                pass
            mew = float(self.mew.get())
            # rowy2
            y2  = self.y2.get()
            same_y = self.same_y.get()
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mfc,
                     'markeredgecolor': mec,
                     'markeredgewidth': mew}
            gy, vy = vardim2var(y, self.groups)
            if self.usex:
                tnamey = self.tname
            else:
                tnamey = self.tname[gy]
            if vy == tnamey:
                ylab = 'Date'
                pargs['color'] = c
            else:
                vvy = selvar(self, vy)
                ylab = set_axis_label(vvy)
                # ToDo with dimensions
                if len(self.line_y) == 1:
                    # set color only if single line,
                    # None and 'None' do not work for multiple lines
                    pargs['color'] = c
            # set style
            for ll in self.line_y:
                plt.setp(ll, **pargs)
            if 'color' in pargs:
                ic = pargs['color']
                if (ic != 'None'):
                    self.axes.spines['left'].set_color(ic)
                    self.axes.tick_params(axis='y', colors=ic)
                    self.axes.yaxis.label.set_color(ic)
            self.axes.yaxis.set_label_text(ylab)
            # same y-axes
            if not isinstance(ylim, list):
                ylim = self.axes.get_ylim()
            if not isinstance(ylim2, list):
                ylim2 = self.axes2.get_ylim()
            if same_y and (y2 != ''):
                ymin, ymax = _minmax_ylim(ylim, ylim2)
                if (ymin is not None) and (ymax is not None):
                    ylim  = [ymin, ymax]
                    ylim2 = [ymin, ymax]
                self.axes.set_ylim(ylim)
                self.axes2.set_ylim(ylim2)
            # invert y-axis
            if inv_y and (ylim[0] is not None):
                if ylim[0] < ylim[1]:
                    ylim = ylim[::-1]
                self.axes.set_ylim(ylim)
            else:
                if ylim[1] < ylim[0]:
                    ylim = ylim[::-1]
                self.axes.set_ylim(ylim)
            # invert x-axis
            inv_x = self.inv_x.get()
            xlim = parse_entry(self.xlim.get())
            if not isinstance(xlim, list):
                xlim = self.axes.get_xlim()
            if inv_x and (xlim[0] is not None):
                if xlim[0] < xlim[1]:
                    xlim = xlim[::-1]
                self.axes.set_xlim(xlim)
            else:
                if xlim[1] < xlim[0]:
                    xlim = xlim[::-1]
                self.axes.set_xlim(xlim)
            # redraw
            self.canvas.draw()
            self.toolbar.update()

    def redraw_y2(self):
        """
        Redraw the right-hand-side y-axis.

        Reads right-hand-side `y` variable name, the current settings of
        its dimension spinboxes, as well as all other plotting options.
        Then redraws the right-hand-side y-axis.

        """
        # get all states
        # rowy2
        y2 = self.y2.get()
        if y2 != '':
            # rowxy
            y = self.y.get()
            # rowy2
            inv_y2 = self.inv_y2.get()
            same_y = self.same_y.get()
            ylim = parse_entry(self.ylim.get())
            ylim2 = parse_entry(self.y2lim.get())
            # rowy2opt
            ls  = self.ls2.get()
            lw  = float(self.lw2.get())
            c   = self.lc2.get()
            try:
                if isinstance(eval(c), tuple):
                    c = eval(c)
            except:
                pass
            m   = self.marker2.get()
            ms  = float(self.ms2.get())
            mfc = self.mfc2.get()
            try:
                if isinstance(eval(mfc), tuple):
                    mfc = eval(mfc)
            except:
                pass
            mec = self.mec2.get()
            try:
                if isinstance(eval(mec), tuple):
                    mec = eval(mec)
            except:
                pass
            mew = float(self.mew2.get())
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mfc,
                     'markeredgecolor': mec,
                     'markeredgewidth': mew}
            gy, vy = vardim2var(y2, self.groups)
            if self.usex:
                tnamey = self.tname
            else:
                tnamey = self.tname[gy]
            if vy == tnamey:
                ylab = 'Date'
                pargs['color'] = c
            else:
                vvy = selvar(self, vy)
                ylab = set_axis_label(vvy)
                if len(self.line_y2) == 1:
                    # set color only if single line,
                    # None and 'None' do not work for multiple lines
                    pargs['color'] = c
            # set style
            for ll in self.line_y2:
                plt.setp(ll, **pargs)
            if 'color' in pargs:
                ic = pargs['color']
                if (ic != 'None'):
                    self.axes2.spines['left'].set_color(ic)
                    self.axes2.tick_params(axis='y', colors=ic)
                    self.axes2.yaxis.label.set_color(ic)
            self.axes2.yaxis.set_label_text(ylab)
            # same y-axes
            if not isinstance(ylim, list):
                ylim = self.axes.get_ylim()
            if not isinstance(ylim2, list):
                ylim2 = self.axes2.get_ylim()
            if same_y and (y2 != ''):
                ymin, ymax = _minmax_ylim(ylim, ylim2)
                if (ymin is not None) and (ymax is not None):
                    ylim  = [ymin, ymax]
                    ylim2 = [ymin, ymax]
                self.axes.set_ylim(ylim)
                self.axes2.set_ylim(ylim2)
            # invert y-axis
            ylim = ylim2
            if inv_y2 and (ylim[0] is not None):
                if ylim[0] < ylim[1]:
                    ylim = ylim[::-1]
                self.axes2.set_ylim(ylim)
            else:
                if ylim[1] < ylim[0]:
                    ylim = ylim[::-1]
                self.axes2.set_ylim(ylim)
            # invert x-axis
            inv_x = self.inv_x.get()
            xlim = parse_entry(self.xlim.get())
            if not isinstance(xlim, list):
                xlim = self.axes.get_xlim()
            if inv_x and (xlim[0] is not None):
                if xlim[0] < xlim[1]:
                    xlim = xlim[::-1]
                self.axes.set_xlim(xlim)
            else:
                if xlim[1] < xlim[0]:
                    xlim = xlim[::-1]
                self.axes.set_xlim(xlim)
            # redraw
            self.canvas.draw()
            self.toolbar.update()

    def redraw(self, event=None):
        """
        Redraw the left-hand-side and right-hand-side y-axis.

        Reads the two `y` variable names, the current settings of
        their dimension spinboxes, as well as all other plotting options.
        Then redraws the both y-axes.

        """
        # get all states
        # rowxy
        x = self.x.get()
        y = self.y.get()
        # rowy2
        y2 = self.y2.get()

        # Clear both axes first, otherwise x-axis only shows
        # if line2 is chosen.
        self.axes.clear()
        self.axes2.clear()
        self.axes2.yaxis.set_label_position('right')
        self.axes2.yaxis.tick_right()
        # ylim = [None, None]
        # ylim2 = [None, None]
        # set x, y, axes labels
        vx  = 'None'
        vy  = 'None'
        vy2 = 'None'
        if (y != '') or (y2 != ''):
            # y axis
            if y != '':
                gy, vy = vardim2var(y, self.groups)
                if self.usex:
                    tnamey = self.tname
                    timey = self.time
                else:
                    tnamey = self.tname[gy]
                    timey = self.time[gy]
                if vy == tnamey:
                    yy   = timey
                    ylab = 'Date'
                else:
                    yy = selvar(self, vy)
                    ylab = set_axis_label(yy)
                yy = get_slice_miss(self, self.yd, yy)
            # y2 axis
            if y2 != '':
                gy2, vy2 = vardim2var(y2, self.groups)
                if self.usex:
                    tnamey2 = self.tname
                    timey2 = self.time
                else:
                    tnamey2 = self.tname[gy2]
                    timey2 = self.time[gy2]
                if vy2 == tnamey2:
                    yy2   = timey2
                    ylab2 = 'Date'
                else:
                    yy2 = selvar(self, vy2)
                    ylab2 = set_axis_label(yy2)
                yy2 = get_slice_miss(self, self.y2d, yy2)
            if (x != ''):
                # x axis
                gx, vx = vardim2var(x, self.groups)
                if self.usex:
                    tnamex = self.tname
                    timex = self.time
                else:
                    tnamex = self.tname[gx]
                    timex = self.time[gx]
                if vx == tnamex:
                    xx   = timex
                    xlab = 'Date'
                else:
                    xx = selvar(self, vx)
                    xlab = set_axis_label(xx)
                xx = get_slice_miss(self, self.xd, xx)
            else:
                # set x to index if not selected
                if (y != ''):
                    nx = yy.shape[0]
                elif (y2 != ''):
                    nx = yy2.shape[0]
                else:
                    nx = 0
                xx   = np.arange(nx)
                xlab = ''
            # set y-axes to nan if not selected
            if (y == ''):
                yy   = np.ones_like(xx, dtype='float') * np.nan
                ylab = ''
            if (y2 == ''):
                yy2   = np.ones_like(xx, dtype='float') * np.nan
                ylab2 = ''
            # plot
            # y-axis
            try:
                # , picker=True, pickradius=5)
                self.line_y = self.axes.plot(xx, yy)
            except Exception:
                print(f'Scatter: x ({vx}) and y ({vy})'
                      f' shapes do not match for plot:',
                      xx.shape, yy.shape)
                return
            self.axes.xaxis.set_label_text(xlab)
            self.axes.yaxis.set_label_text(ylab)
            # y2-axis
            try:
                # , picker=True, pickradius=5)
                self.line_y2 = self.axes2.plot(xx, yy2)
            except Exception:
                print(f'Scatter: x ({vx}) and y2 ({vy2})'
                      f' shapes do not match for plot:',
                      xx.shape, yy2.shape)
                return
            self.axes2.format_coord = lambda x, y: format_coord_scatter(
                x, y, self.axes, self.axes2, xx.dtype, yy.dtype, yy2.dtype)
            self.axes2.xaxis.set_label_text(xlab)
            self.axes2.yaxis.set_label_text(ylab2)
            # styles, invert, same axes, etc.
            self.redraw_y()
            self.redraw_y2()
            # redraw
            self.canvas.draw()
            self.toolbar.update()
