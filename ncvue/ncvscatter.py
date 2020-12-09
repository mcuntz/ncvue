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
from .ncvutils   import get_miss, set_miss, spinbox_values
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
        from matplotlib import pyplot as plt

        super().__init__(master, **kwargs)

        self.name   = 'Scatter'
        self.master = master
        self.root   = master.root
        self.fi     = master.fi
        self.miss   = master.miss
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
        if self.maxdim > 0:
            self.xd0lbl, self.xd0val, self.xd0 = add_spinbox(
                self.rowxylev, label="0", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 1:
            self.xd1lbl, self.xd1val, self.xd1 = add_spinbox(
                self.rowxylev, label="1", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 2:
            self.xd2lbl, self.xd2val, self.xd2 = add_spinbox(
                self.rowxylev, label="2", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 3:
            self.xd3lbl, self.xd3val, self.xd3 = add_spinbox(
                self.rowxylev, label="3", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 4:
            self.xd4lbl, self.xd4val, self.xd4 = add_spinbox(
                self.rowxylev, label="4", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 5:
            self.xd5lbl, self.xd5val, self.xd5 = add_spinbox(
                self.rowxylev, label="5", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 6:
            self.xd6lbl, self.xd6val, self.xd6 = add_spinbox(
                self.rowxylev, label="6", values=(0,), wrap=True,
                command=self.spinned_x)
        if self.maxdim > 7:
            self.xd7lbl, self.xd7val, self.xd7 = add_spinbox(
                self.rowxylev, label="7", values=(0,), wrap=True,
                command=self.spinned_x)
        spacexy = ttk.Label(self.rowxylev, text=" "*10)
        spacexy.pack(side=tk.LEFT)
        if self.maxdim > 0:
            self.yd0lbl, self.yd0val, self.yd0 = add_spinbox(
                self.rowxylev, label="0", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 1:
            self.yd1lbl, self.yd1val, self.yd1 = add_spinbox(
                self.rowxylev, label="1", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 2:
            self.yd2lbl, self.yd2val, self.yd2 = add_spinbox(
                self.rowxylev, label="2", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 3:
            self.yd3lbl, self.yd3val, self.yd3 = add_spinbox(
                self.rowxylev, label="3", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 4:
            self.yd4lbl, self.yd4val, self.yd4 = add_spinbox(
                self.rowxylev, label="4", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 5:
            self.yd5lbl, self.yd5val, self.yd5 = add_spinbox(
                self.rowxylev, label="5", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 6:
            self.yd6lbl, self.yd6val, self.yd6 = add_spinbox(
                self.rowxylev, label="6", values=(0,), wrap=True,
                command=self.spinned_y)
        if self.maxdim > 7:
            self.yd7lbl, self.yd7val, self.yd7 = add_spinbox(
                self.rowxylev, label="7", values=(0,), wrap=True,
                command=self.spinned_y)

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
        self.same_ylbl, self.same_y = add_checkbutton(
            self.rowy2, label="same y-axes", value=False,
            command=self.checked_yy2)

        # 5. row
        # levels y2
        self.rowxy2lev = ttk.Frame(self)
        self.rowxy2lev.pack(side=tk.TOP, fill=tk.X)
        if self.maxdim > 0:
            self.y2d0lbl, self.y2d0val, self.y2d0 = add_spinbox(
                self.rowxy2lev, label="0", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 1:
            self.y2d1lbl, self.y2d1val, self.y2d1 = add_spinbox(
                self.rowxy2lev, label="1", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 2:
            self.y2d2lbl, self.y2d2val, self.y2d2 = add_spinbox(
                self.rowxy2lev, label="2", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 3:
            self.y2d3lbl, self.y2d3val, self.y2d3 = add_spinbox(
                self.rowxy2lev, label="3", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 4:
            self.y2d4lbl, self.y2d4val, self.y2d4 = add_spinbox(
                self.rowxy2lev, label="4", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 5:
            self.y2d5lbl, self.y2d5val, self.y2d5 = add_spinbox(
                self.rowxy2lev, label="5", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 6:
            self.y2d6lbl, self.y2d6val, self.y2d6 = add_spinbox(
                self.rowxy2lev, label="6", values=(0,), wrap=True,
                command=self.spinned_y2)
        if self.maxdim > 7:
            self.y2d7lbl, self.y2d7val, self.y2d7 = add_spinbox(
                self.rowxy2lev, label="7", values=(0,), wrap=True,
                command=self.spinned_y2)

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
            self.set_dim_y()
            self.redraw()

    def prev_y(self):
        y = self.y.get()
        cols = self.y["values"]
        idx  = cols.index(y)
        idx -= 1
        if idx > 0:
            self.y.set(cols[idx])
            self.set_dim_y()
            self.redraw()

    def selected_x(self, event):
        self.set_dim_x()
        self.redraw()

    def selected_y(self, event):
        self.set_dim_y()
        self.redraw()

    def selected_y2(self, event):
        self.set_dim_y2()
        self.redraw()

    def spinned_x(self, event=None):
        self.redraw()

    def spinned_y(self, event=None):
        self.redraw()

    def spinned_y2(self, event=None):
        self.redraw()

    #
    # Set dimensions
    #

    def set_dim_x(self):
        """
        Set dimensions to the dimensions of the variable of the x-axis
        """
        # reset dimensions
        if self.maxdim > 0:
            self.xd0.config(values=(0,), width=1)
            self.xd0lbl.set('0')
        if self.maxdim > 1:
            self.xd1.config(values=(0,), width=1)
            self.xd1lbl.set('1')
        if self.maxdim > 2:
            self.xd2.config(values=(0,), width=1)
            self.xd2lbl.set('2')
        if self.maxdim > 3:
            self.xd3.config(values=(0,), width=1)
            self.xd3lbl.set('3')
        if self.maxdim > 4:
            self.xd4.config(values=(0,), width=1)
            self.xd4lbl.set('4')
        if self.maxdim > 5:
            self.xd5.config(values=(0,), width=1)
            self.xd5lbl.set('5')
        if self.maxdim > 6:
            self.xd6.config(values=(0,), width=1)
            self.xd6lbl.set('6')
        if self.maxdim > 7:
            self.xd7.config(values=(0,), width=1)
            self.xd7lbl.set('7')
        x = self.x.get()
        if x != '':
            # set real dimensions
            vx = x.split()[0]
            if vx == self.tname:
                vx = self.tvar
            xx = self.fi.variables[vx]
            nall = 0
            if xx.ndim > 0:
                self.xd0.config(values=spinbox_values(xx.shape[0]), width=4)
                if (nall == 0) and (xx.shape[0] > 1):
                    nall += 1
                    self.xd0val.set('all')
                else:
                    self.xd0val.set(0)
                self.xd0lbl.set(xx.dimensions[0])
            if xx.ndim > 1:
                self.xd1.config(values=spinbox_values(xx.shape[1]), width=4)
                if (nall == 0) and (xx.shape[1] > 1):
                    nall += 1
                    self.xd1val.set('all')
                else:
                    self.xd1val.set(0)
                self.xd1lbl.set(xx.dimensions[1])
            if xx.ndim > 2:
                self.xd2.config(values=spinbox_values(xx.shape[2]), width=4)
                if (nall == 0) and (xx.shape[2] > 1):
                    nall += 1
                    self.xd2val.set('all')
                else:
                    self.xd2val.set(0)
                self.xd2lbl.set(xx.dimensions[2])
            if xx.ndim > 3:
                self.xd3.config(values=spinbox_values(xx.shape[3]), width=4)
                if (nall == 0) and (xx.shape[3] > 1):
                    nall += 1
                    self.xd3val.set('all')
                else:
                    self.xd3val.set(0)
                self.xd3lbl.set(xx.dimensions[3])
            if xx.ndim > 4:
                self.xd4.config(values=spinbox_values(xx.shape[4]), width=4)
                if (nall == 0) and (xx.shape[4] > 1):
                    nall += 1
                    self.xd4val.set('all')
                else:
                    self.xd4val.set(0)
                self.xd4lbl.set(xx.dimensions[4])
            if xx.ndim > 5:
                self.xd5.config(values=spinbox_values(xx.shape[5]), width=4)
                if (nall == 0) and (xx.shape[5] > 1):
                    nall += 1
                    self.xd5val.set('all')
                else:
                    self.xd5val.set(0)
                self.xd5lbl.set(xx.dimensions[5])
            if xx.ndim > 6:
                self.xd6.config(values=spinbox_values(xx.shape[6]), width=4)
                if (nall == 0) and (xx.shape[6] > 1):
                    nall += 1
                    self.xd6val.set('all')
                else:
                    self.xd6val.set(0)
                self.xd6lbl.set(xx.dimensions[6])
            if xx.ndim > 7:
                self.xd7.config(values=spinbox_values(xx.shape[7]), width=4)
                if (nall == 0) and (xx.shape[7] > 1):
                    nall += 1
                    self.xd7val.set('all')
                else:
                    self.xd7val.set(0)
                self.xd7lbl.set(xx.dimensions[7])

    def set_dim_y(self):
        """
        Set dimensions to the dimensions of the variable of the lhs y-axis
        """
        # reset dimensions
        if self.maxdim > 0:
            self.yd0.config(values=(0,), width=1)
            self.yd0lbl.set('0')
        if self.maxdim > 1:
            self.yd1.config(values=(0,), width=1)
            self.yd1lbl.set('1')
        if self.maxdim > 2:
            self.yd2.config(values=(0,), width=1)
            self.yd2lbl.set('2')
        if self.maxdim > 3:
            self.yd3.config(values=(0,), width=1)
            self.yd3lbl.set('3')
        if self.maxdim > 4:
            self.yd4.config(values=(0,), width=1)
            self.yd4lbl.set('4')
        if self.maxdim > 5:
            self.yd5.config(values=(0,), width=1)
            self.yd5lbl.set('5')
        if self.maxdim > 6:
            self.yd6.config(values=(0,), width=1)
            self.yd6lbl.set('6')
        if self.maxdim > 7:
            self.yd7.config(values=(0,), width=1)
            self.yd7lbl.set('7')
        y = self.y.get()
        if y != '':
            # set real dimensions
            vy = y.split()[0]
            if vy == self.tname:
                vy = self.tvar
            yy = self.fi.variables[vy]
            nall = 0
            if yy.ndim > 0:
                self.yd0.config(values=spinbox_values(yy.shape[0]), width=4)
                if (nall == 0) and (yy.shape[0] > 1):
                    nall += 1
                    self.yd0val.set('all')
                else:
                    self.yd0val.set(0)
                self.yd0lbl.set(yy.dimensions[0])
            if yy.ndim > 1:
                self.yd1.config(values=spinbox_values(yy.shape[1]), width=4)
                if (nall == 0) and (yy.shape[1] > 1):
                    nall += 1
                    self.yd1val.set('all')
                else:
                    self.yd1val.set(0)
                self.yd1lbl.set(yy.dimensions[1])
            if yy.ndim > 2:
                self.yd2.config(values=spinbox_values(yy.shape[2]), width=4)
                if (nall == 0) and (yy.shape[2] > 1):
                    nall += 1
                    self.yd2val.set('all')
                else:
                    self.yd2val.set(0)
                self.yd2lbl.set(yy.dimensions[2])
            if yy.ndim > 3:
                self.yd3.config(values=spinbox_values(yy.shape[3]), width=4)
                if (nall == 0) and (yy.shape[3] > 1):
                    nall += 1
                    self.yd3val.set('all')
                else:
                    self.yd3val.set(0)
                self.yd3lbl.set(yy.dimensions[3])
            if yy.ndim > 4:
                self.yd4.config(values=spinbox_values(yy.shape[4]), width=4)
                if (nall == 0) and (yy.shape[4] > 1):
                    nall += 1
                    self.yd4val.set('all')
                else:
                    self.yd4val.set(0)
                self.yd4lbl.set(yy.dimensions[4])
            if yy.ndim > 5:
                self.yd5.config(values=spinbox_values(yy.shape[5]), width=4)
                if (nall == 0) and (yy.shape[5] > 1):
                    nall += 1
                    self.yd5val.set('all')
                else:
                    self.yd5val.set(0)
                self.yd5lbl.set(yy.dimensions[5])
            if yy.ndim > 6:
                self.yd6.config(values=spinbox_values(yy.shape[6]), width=4)
                if (nall == 0) and (yy.shape[6] > 1):
                    nall += 1
                    self.yd6val.set('all')
                else:
                    self.yd6val.set(0)
                self.yd6lbl.set(yy.dimensions[6])
            if yy.ndim > 7:
                self.yd7.config(values=spinbox_values(yy.shape[7]), width=4)
                if (nall == 0) and (yy.shape[7] > 1):
                    nall += 1
                    self.yd7val.set('all')
                else:
                    self.yd7val.set(0)
                self.yd7lbl.set(yy.dimensions[7])

    def set_dim_y2(self):
        """
        Set dimensions to the dimensions of the variable of the rhs y-axis
        """
        # reset dimensions
        if self.maxdim > 0:
            self.y2d0.config(values=(0,), width=1)
            self.y2d0lbl.set('0')
        if self.maxdim > 1:
            self.y2d1.config(values=(0,), width=1)
            self.y2d1lbl.set('1')
        if self.maxdim > 2:
            self.y2d2.config(values=(0,), width=1)
            self.y2d2lbl.set('2')
        if self.maxdim > 3:
            self.y2d3.config(values=(0,), width=1)
            self.y2d3lbl.set('3')
        if self.maxdim > 4:
            self.y2d4.config(values=(0,), width=1)
            self.y2d4lbl.set('4')
        if self.maxdim > 5:
            self.y2d5.config(values=(0,), width=1)
            self.y2d5lbl.set('5')
        if self.maxdim > 6:
            self.y2d6.config(values=(0,), width=1)
            self.y2d6lbl.set('6')
        if self.maxdim > 7:
            self.y2d7.config(values=(0,), width=1)
            self.y2d7lbl.set('7')
        y2 = self.y2.get()
        if y2 != '':
            # set real dimensions
            vy2 = y2.split()[0]
            if vy2 == self.tname:
                vy2 = self.tvar
            yy2 = self.fi.variables[vy2]
            nall = 0
            if yy2.ndim > 0:
                self.y2d0.config(values=spinbox_values(yy2.shape[0]), width=4)
                if (nall == 0) and (yy2.shape[0] > 1):
                    nall += 1
                    self.y2d0val.set('all')
                else:
                    self.y2d0val.set(0)
                self.y2d0lbl.set(yy2.dimensions[0])
            if yy2.ndim > 1:
                self.y2d1.config(values=spinbox_values(yy2.shape[1]), width=4)
                if (nall == 0) and (yy2.shape[1] > 1):
                    nall += 1
                    self.y2d1val.set('all')
                else:
                    self.y2d1val.set(0)
                self.y2d1lbl.set(yy2.dimensions[1])
            if yy2.ndim > 2:
                self.y2d2.config(values=spinbox_values(yy2.shape[2]), width=4)
                if (nall == 0) and (yy2.shape[2] > 1):
                    nall += 1
                    self.y2d2val.set('all')
                else:
                    self.y2d2val.set(0)
                self.y2d2lbl.set(yy2.dimensions[2])
            if yy2.ndim > 3:
                self.y2d3.config(values=spinbox_values(yy2.shape[3]), width=4)
                if (nall == 0) and (yy2.shape[3] > 1):
                    nall += 1
                    self.y2d3val.set('all')
                else:
                    self.y2d3val.set(0)
                self.y2d3lbl.set(yy2.dimensions[3])
            if yy2.ndim > 4:
                self.y2d4.config(values=spinbox_values(yy2.shape[4]), width=4)
                if (nall == 0) and (yy2.shape[4] > 1):
                    nall += 1
                    self.y2d4val.set('all')
                else:
                    self.y2d4val.set(0)
                self.y2d4lbl.set(yy2.dimensions[4])
            if yy2.ndim > 5:
                self.y2d5.config(values=spinbox_values(yy2.shape[5]), width=4)
                if (nall == 0) and (yy2.shape[5] > 1):
                    nall += 1
                    self.y2d5val.set('all')
                else:
                    self.y2d5val.set(0)
                self.y2d5lbl.set(yy2.dimensions[5])
            if yy2.ndim > 6:
                self.y2d6.config(values=spinbox_values(yy2.shape[6]), width=4)
                if (nall == 0) and (yy2.shape[6] > 1):
                    nall += 1
                    self.y2d6val.set('all')
                else:
                    self.y2d6val.set(0)
                self.y2d6lbl.set(yy2.dimensions[6])
            if yy2.ndim > 7:
                self.y2d7.config(values=spinbox_values(yy2.shape[7]), width=4)
                if (nall == 0) and (yy2.shape[7] > 1):
                    nall += 1
                    self.y2d7val.set('all')
                else:
                    self.y2d7val.set(0)
                self.y2d7lbl.set(yy2.dimensions[7])

    #
    # Get variable slices
    #

    def get_slice_x(self, x):
        """
        Get the slice from x-variable selected in the level row
        """
        if x.ndim > 0:
            dim = self.xd0.get()
            if dim == 'all':
                s = range(0, x.shape[0])
            else:
                s = (int(dim),)
            xout = np.take(x, s, axis=0)
        else:
            xout = x
        if x.ndim > 1:
            dim = self.xd1.get()
            if dim == 'all':
                s = range(0, x.shape[1])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=1)
        if x.ndim > 2:
            dim = self.xd2.get()
            if dim == 'all':
                s = range(0, x.shape[2])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=2)
        if x.ndim > 3:
            dim = self.xd3.get()
            if dim == 'all':
                s = range(0, x.shape[3])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=3)
        if x.ndim > 4:
            dim = self.xd4.get()
            if dim == 'all':
                s = range(0, x.shape[4])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=4)
        if x.ndim > 5:
            dim = self.xd5.get()
            if dim == 'all':
                s = range(0, x.shape[5])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=5)
        if x.ndim > 6:
            dim = self.xd6.get()
            if dim == 'all':
                s = range(0, x.shape[6])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=6)
        if x.ndim > 7:
            dim = self.xd7.get()
            if dim == 'all':
                s = range(0, x.shape[7])
            else:
                s = (int(dim),)
            xout = np.take(xout, s, axis=7)

        return xout

    def get_slice_y(self, y):
        """
        Get the slice from lhs y-variable selected in the level row
        """
        if y.ndim > 0:
            dim = self.yd0.get()
            if dim == 'all':
                s = range(0, y.shape[0])
            else:
                s = (int(dim),)
            yout = np.take(y, s, axis=0)
        else:
            yout = y
        if y.ndim > 1:
            dim = self.yd1.get()
            if dim == 'all':
                s = range(0, y.shape[1])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=1)
        if y.ndim > 2:
            dim = self.yd2.get()
            if dim == 'all':
                s = range(0, y.shape[2])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=2)
        if y.ndim > 3:
            dim = self.yd3.get()
            if dim == 'all':
                s = range(0, y.shape[3])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=3)
        if y.ndim > 4:
            dim = self.yd4.get()
            if dim == 'all':
                s = range(0, y.shape[4])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=4)
        if y.ndim > 5:
            dim = self.yd5.get()
            if dim == 'all':
                s = range(0, y.shape[5])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=5)
        if y.ndim > 6:
            dim = self.yd6.get()
            if dim == 'all':
                s = range(0, y.shape[6])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=6)
        if y.ndim > 7:
            dim = self.yd7.get()
            if dim == 'all':
                s = range(0, y.shape[7])
            else:
                s = (int(dim),)
            yout = np.take(yout, s, axis=7)

        return yout

    def get_slice_y2(self, y2):
        """
        Get the slice from rhs y-variable selected in the level row
        """
        if y2.ndim > 0:
            dim = self.y2d0.get()
            if dim == 'all':
                s = range(0, y2.shape[0])
            else:
                s = (int(dim),)
            y2out = np.take(y2, s, axis=0)
        else:
            y2out = y2
        if y2.ndim > 1:
            dim = self.y2d1.get()
            if dim == 'all':
                s = range(0, y2.shape[1])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=1)
        if y2.ndim > 2:
            dim = self.y2d2.get()
            if dim == 'all':
                s = range(0, y2.shape[2])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=2)
        if y2.ndim > 3:
            dim = self.y2d3.get()
            if dim == 'all':
                s = range(0, y2.shape[3])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=3)
        if y2.ndim > 4:
            dim = self.y2d4.get()
            if dim == 'all':
                s = range(0, y2.shape[4])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=4)
        if y2.ndim > 5:
            dim = self.y2d5.get()
            if dim == 'all':
                s = range(0, y2.shape[5])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=5)
        if y2.ndim > 6:
            dim = self.y2d6.get()
            if dim == 'all':
                s = range(0, y2.shape[6])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=6)
        if y2.ndim > 7:
            dim = self.y2d7.get()
            if dim == 'all':
                s = range(0, y2.shape[7])
            else:
                s = (int(dim),)
            y2out = np.take(y2out, s, axis=7)

        return y2out

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
                ylab  = self.fi.variables[vy].name
                try:
                    ylab += ' (' + self.fi.variables[vy].units + ')'
                except AttributeError:
                    pass
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
                ylab  = self.fi.variables[vy].name
                try:
                    ylab += ' (' + self.fi.variables[vy].units + ')'
                except AttributeError:
                    pass
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
                    ylab = yy.name
                    try:
                        ylab += ' (' + yy.units + ')'
                    except AttributeError:
                        pass
                miss = get_miss(self, yy)
                yy = self.get_slice_y(yy).squeeze()
                yy = set_miss(yy, miss)
            # y2 axis
            if y2 != '':
                vy2 = y2.split()[0]
                if vy2 == self.tname:
                    yy2   = self.time
                    ylab2 = 'Date'
                else:
                    yy2   = self.fi.variables[vy2]
                    ylab2 = yy2.name
                    try:
                        ylab2 += ' (' + yy2.units + ')'
                    except AttributeError:
                        pass
                miss = get_miss(self, yy2)
                yy2 = self.get_slice_y2(yy2).squeeze()
                yy2 = set_miss(yy2, miss)
            if (x != ''):
                # x axis
                vx = x.split()[0]
                if vx == self.tname:
                    xx   = self.time
                    xlab = 'Date'
                else:
                    xx   = self.fi.variables[vx]
                    xlab = xx.name
                    try:
                        xlab += ' (' + xx.units + ')'
                    except AttributeError:
                        pass
                miss = get_miss(self, xx)
                xx = self.get_slice_x(xx).squeeze()
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

            self.x0  = x
            self.y0  = y
            self.y20 = y2
            self.canvas.draw()
            self.toolbar.update()
