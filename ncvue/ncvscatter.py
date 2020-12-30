#!/usr/bin/env python
"""
Scatter/Line panel of ncvue

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
from .ncvutils   import set_axis_label, set_miss
from .ncvmethods import get_miss
from .ncvmethods import get_slice_x, get_slice_y, get_slice_y2
from .ncvmethods import set_dim_x, set_dim_y, set_dim_y2
from .ncvwidgets import add_checkbutton, add_combobox, add_entry
from .ncvwidgets import add_spinbox
from .ncvclone   import clone_ncvmain
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
plt.style.use('seaborn-darkgrid')


__all__ = ['ncvScatter']


class ncvScatter(ttk.Frame):
    """
    Panel for scatter plots.
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
        self.axes2  = self.axes.twinx()
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
        c = list(plt.rcParams['axes.prop_cycle'])
        col1 = c[0]['color']  # blue
        col2 = c[3]['color']  # red

        # 1. row
        # x- and lhs y-axis selection
        self.rowxy = ttk.Frame(self)
        self.rowxy.pack(side=tk.TOP, fill=tk.X)
        self.xlbl, self.x = add_combobox(self.rowxy, label="x",
                                         values=columns,
                                         command=self.selected_x)
        self.x0 = ''
        self.line_x = []
        self.inv_xlbl, self.inv_x = add_checkbutton(
            self.rowxy, label="invert x", value=False,
            command=self.checked_x)
        spacex = ttk.Label(self.rowxy, text=" "*3)
        spacex.pack(side=tk.LEFT)
        # self.ylbl, self.y = add_combobox(self.rowxy, label="y",
        #                                   values=columns,
        #                                   command=self.selected_y)
        self.ylbl = tk.StringVar()
        self.ylbl.set("y")
        ylab = ttk.Label(self.rowxy, textvariable=self.ylbl)
        ylab.pack(side=tk.LEFT)
        # previous y
        self.bprev_y = ttk.Button(self.rowxy, text="<", width=1,
                                  command=self.prev_y)
        self.bprev_y.pack(side=tk.LEFT)
        # next y
        self.bnext_y = ttk.Button(self.rowxy, text=">", width=1,
                                  command=self.next_y)
        self.bnext_y.pack(side=tk.LEFT)
        self.y = ttk.Combobox(self.rowxy, values=columns, width=25)
        # long = len(max(columns, key=len))
        # self.y.configure(width=(max(20, long//2)))
        self.y.bind("<<ComboboxSelected>>", self.selected_y)
        self.y.pack(side=tk.LEFT)
        self.y0 = ''
        self.line_y = []
        self.inv_ylbl, self.inv_y = add_checkbutton(
            self.rowxy, label="invert y", value=False,
            command=self.checked_y)
        # redraw button
        self.bredraw = ttk.Button(self.rowxy, text="Redraw",
                                  command=self.redraw)
        self.bredraw.pack(side=tk.RIGHT)

        # 2. row
        # levels x and y
        self.rowxylev = ttk.Frame(self)
        self.rowxylev.pack(side=tk.TOP, fill=tk.X)
        self.xdlbl = []
        self.xdval = []
        self.xd    = []
        for i in range(self.maxdim):
            xdlbl, xdval, xd = add_spinbox(
                self.rowxylev, label=str(i), values=(0,), wrap=True,
                command=self.spinned_x)
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
                command=self.spinned_y)
            self.ydlbl.append(ydlbl)
            self.ydval.append(ydval)
            self.yd.append(yd)

        # 3. row
        # options for lhs y-axis
        self.rowxyopt = ttk.Frame(self)
        self.rowxyopt.pack(side=tk.TOP, fill=tk.X)
        self.lslbl, self.ls = add_entry(self.rowxyopt, label="ls", text='-',
                                        width=4, command=self.entered_y)
        self.lwlbl, self.lw = add_entry(self.rowxyopt, label="lw", text='1',
                                        width=2, command=self.entered_y)
        self.lclbl, self.lc = add_entry(self.rowxyopt, label="c", text=col1,
                                        width=7, command=self.entered_y)
        self.markerlbl, self.marker = add_entry(self.rowxyopt, label="marker",
                                                text='None', width=4,
                                                command=self.entered_y)
        self.mslbl, self.ms = add_entry(self.rowxyopt, label="ms", text='1',
                                        width=2, command=self.entered_y)
        self.mfclbl, self.mfc = add_entry(self.rowxyopt, label="mfc",
                                          text=col1, width=7,
                                          command=self.entered_y)
        self.mfclbl, self.mec = add_entry(self.rowxyopt, label="mec",
                                          text=col1, width=7,
                                          command=self.entered_y)
        self.mewlbl, self.mew = add_entry(self.rowxyopt, label="mew",
                                          text='1', width=2,
                                          command=self.entered_y)

        # space
        self.rowspace = ttk.Frame(self)
        self.rowspace.pack(side=tk.TOP, fill=tk.X)
        rowspace = ttk.Label(self.rowspace, text=" ")
        rowspace.pack(side=tk.LEFT)

        # 4. row
        # rhs y-axis 2 selection
        self.rowy2 = ttk.Frame(self)
        self.rowy2.pack(side=tk.TOP, fill=tk.X)
        self.y2lbl, self.y2 = add_combobox(self.rowy2, label="y2",
                                           values=columns,
                                           command=self.selected_y2)
        self.y20 = ''
        self.line_y2 = []
        self.inv_y2lbl, self.inv_y2 = add_checkbutton(
            self.rowy2, label="invert y2", value=False,
            command=self.checked_y2)
        spacey2 = ttk.Label(self.rowy2, text=" "*1)
        spacey2.pack(side=tk.LEFT)
        self.same_ylbl, self.same_y = add_checkbutton(
            self.rowy2, label="same y-axes", value=False,
            command=self.checked_yy2)

        # 5. row
        # levels y2
        self.rowxy2lev = ttk.Frame(self)
        self.rowxy2lev.pack(side=tk.TOP, fill=tk.X)
        self.y2dlbl = []
        self.y2dval = []
        self.y2d    = []
        for i in range(self.maxdim):
            y2dlbl, y2dval, y2d = add_spinbox(
                self.rowxy2lev, label=str(i), values=(0,), wrap=True,
                command=self.spinned_y2)
            self.y2dlbl.append(y2dlbl)
            self.y2dval.append(y2dval)
            self.y2d.append(y2d)

        # 6. row
        # options for rhs y-axis 2
        self.rowy2opt = ttk.Frame(self)
        self.rowy2opt.pack(side=tk.TOP, fill=tk.X)
        self.ls2lbl, self.ls2 = add_entry(self.rowy2opt, label="ls",
                                          text='-', width=4,
                                          command=self.entered_y2)
        self.lw2lbl, self.lw2 = add_entry(self.rowy2opt, label="lw",
                                          text='1', width=2,
                                          command=self.entered_y2)
        self.lc2lbl, self.lc2 = add_entry(self.rowy2opt, label="c",
                                          text=col2, width=7,
                                          command=self.entered_y2)
        self.marker2lbl, self.marker2 = add_entry(self.rowy2opt,
                                                  label="marker",
                                                  text='None', width=4,
                                                  command=self.entered_y2)
        self.ms2lbl, self.ms2 = add_entry(self.rowy2opt, label="ms",
                                          text='1', width=2,
                                          command=self.entered_y2)
        self.mfc2lbl, self.mfc2 = add_entry(self.rowy2opt, label="mfc",
                                            text=col2, width=7,
                                            command=self.entered_y2)
        self.mfc2lbl, self.mec2 = add_entry(self.rowy2opt, label="mec",
                                            text=col2, width=7,
                                            command=self.entered_y2)
        self.mew2lbl, self.mew2 = add_entry(self.rowy2opt, label="mew",
                                            text='1', width=2,
                                            command=self.entered_y2)

    #
    # Event bindings
    #

    def checked_x(self):
        self.redraw_y()
        self.redraw_y2()

    def checked_y(self):
        self.redraw_y()

    def checked_y2(self):
        self.redraw_y2()

    def checked_yy2(self):
        self.redraw_y()
        self.redraw_y2()

    def entered_y(self, event):
        self.redraw_y()

    def entered_y2(self, event):
        self.redraw_y2()

    def next_y(self):
        y = self.y.get()
        cols = self.y["values"]
        idx  = cols.index(y)
        idx += 1
        if idx < len(cols):
            self.y.set(cols[idx])
            set_dim_y(self)
            self.redraw()

    def prev_y(self):
        y = self.y.get()
        cols = self.y["values"]
        idx  = cols.index(y)
        idx -= 1
        if idx > 0:
            self.y.set(cols[idx])
            set_dim_y(self)
            self.redraw()

    def selected_x(self, event):
        set_dim_x(self)
        self.redraw()

    def selected_y(self, event):
        set_dim_y(self)
        self.redraw()

    def selected_y2(self, event):
        set_dim_y2(self)
        self.redraw()

    def spinned_x(self, event=None):
        self.redraw()

    def spinned_y(self, event=None):
        self.redraw()

    def spinned_y2(self, event=None):
        self.redraw()

    #
    # Plot
    #

    def redraw_y(self, event=None):
        """
        Redraw the lhs y-axis
        """
        # get all states
        # rowxy
        y = self.y.get()
        if y != '':
            inv_y = self.inv_y.get()
            # rowxyopt
            ls  = self.ls.get()
            lw  = float(self.lw.get())
            c   = self.lc.get()
            m   = self.marker.get()
            ms  = float(self.ms.get())
            mfc = self.mfc.get()
            mec = self.mec.get()
            mew = float(self.mew.get())
            # rowy2
            y2  = self.y2.get()
            same_y = self.same_y.get()
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mec,
                     'markeredgecolor': mfc,
                     'markeredgewidth': mew}
            vy = y.split()[0]
            if vy == self.tname:
                ylab = 'Date'
                pargs['color'] = c
            else:
                ylab = set_axis_label(self.fi.variables[vy])
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
            ylim  = self.axes.get_ylim()
            ylim2 = self.axes2.get_ylim()
            if same_y and (y2 != ''):
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
            xlim  = self.axes.get_xlim()
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

    def redraw_y2(self, event=None):
        """
        Redraw the rhs y-axis
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
            # rowy2opt
            ls  = self.ls2.get()
            lw  = float(self.lw2.get())
            c   = self.lc2.get()
            m   = self.marker2.get()
            ms  = float(self.ms2.get())
            mfc = self.mfc2.get()
            mec = self.mec2.get()
            mew = float(self.mew2.get())
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mec,
                     'markeredgecolor': mfc,
                     'markeredgewidth': mew}
            vy = y2.split()[0]
            if vy == self.tname:
                ylab = 'Date'
                pargs['color'] = c
            else:
                ylab = set_axis_label(self.fi.variables[vy])
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
            ylim  = self.axes.get_ylim()
            ylim2 = self.axes2.get_ylim()
            if same_y and (y2 != ''):
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
            xlim  = self.axes.get_xlim()
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
        Redraw the lhs and rhs y-axes
        """
        # get all states
        # rowxy
        x = self.x.get()
        y = self.y.get()
        # rowy2
        y2 = self.y2.get()

        # Clear both axes first, otherwise x-axis only shows
        # if line2 is chosen.
        # if (x != self.x0) or (y != self.y0):
        self.axes.clear()
        # if (x != self.x0) or (y2 != self.y20):
        self.axes2.clear()
        ylim  = [None, None]
        ylim2 = [None, None]
        # set x, y, axes labels
        vx  = 'None'
        vy  = 'None'
        vy2 = 'None'
        if (y != '') or (y2 != ''):
            # y axis
            if y != '':
                vy = y.split()[0]
                if vy == self.tname:
                    yy   = self.time
                    ylab = 'Date'
                else:
                    yy   = self.fi.variables[vy]
                    ylab = set_axis_label(yy)
                miss = get_miss(self, yy)
                yy = get_slice_y(self, yy).squeeze()
                yy = set_miss(yy, miss)
            # y2 axis
            if y2 != '':
                vy2 = y2.split()[0]
                if vy2 == self.tname:
                    yy2   = self.time
                    ylab2 = 'Date'
                else:
                    yy2   = self.fi.variables[vy2]
                    ylab2 = set_axis_label(yy2)
                miss = get_miss(self, yy2)
                yy2 = get_slice_y2(self, yy2).squeeze()
                yy2 = set_miss(yy2, miss)
            if (x != ''):
                # x axis
                vx = x.split()[0]
                if vx == self.tname:
                    xx   = self.time
                    xlab = 'Date'
                else:
                    xx   = self.fi.variables[vx]
                    xlab = set_axis_label(xx)
                miss = get_miss(self, xx)
                xx = get_slice_x(self, xx).squeeze()
                xx = set_miss(xx, miss)
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
                yy   = np.ones_like(xx)*np.nan
                ylab = ''
            if (y2 == ''):
                yy2   = np.ones_like(xx)*np.nan
                ylab2 = ''
            # plot
            # y-axis
            try:
                self.line_y = self.axes.plot(xx, yy)
            except Exception:
                estr  = 'Scatter: x (' + vx + ') and y (' + vy + ')'
                estr += ' shapes do not match for plot:'
                print(estr, xx.shape, yy.shape)
                return
            self.axes.xaxis.set_label_text(xlab)
            self.axes.yaxis.set_label_text(ylab)
            # y2-axis
            try:
                self.line_y2 = self.axes2.plot(xx, yy2)
            except Exception:
                estr  = 'Scatter: x (' + vx + ') and y2 (' + vy2 + ')'
                estr += ' shapes do not match for plot:'
                print(estr, xx.shape, yy2.shape)
                return
            self.axes2.xaxis.set_label_text(xlab)
            self.axes2.yaxis.set_label_text(ylab2)
            # styles, invert, same axes, etc.
            self.redraw_y()
            self.redraw_y2()
            # redraw
            self.x0  = x
            self.y0  = y
            self.y20 = y2
            self.canvas.draw()
            self.toolbar.update()
