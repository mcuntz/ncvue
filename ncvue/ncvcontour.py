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
import numpy as np
from .ncvutils   import get_miss, set_miss, spinbox_values
from .ncvwidgets import add_checkbutton, add_combobox
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
    from matplotlib import pyplot as plt

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

        acmaps = plt.colormaps()
        cmaps  = [ i for i in acmaps if not i.endswith('_r') ]

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

        # 2. row
        # levels z
        self.rowzlev = ttk.Frame(self)
        self.rowzlev.pack(side=tk.TOP, fill=tk.X)
        if self.maxdim > 0:
            self.zd0lbl, self.zd0val, self.zd0 = add_spinbox(
                self.rowzlev, label="0", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 1:
            self.zd1lbl, self.zd1val, self.zd1 = add_spinbox(
                self.rowzlev, label="1", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 2:
            self.zd2lbl, self.zd2val, self.zd2 = add_spinbox(
                self.rowzlev, label="2", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 3:
            self.zd3lbl, self.zd3val, self.zd3 = add_spinbox(
                self.rowzlev, label="3", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 4:
            self.zd4lbl, self.zd4val, self.zd4 = add_spinbox(
                self.rowzlev, label="4", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 5:
            self.zd5lbl, self.zd5val, self.zd5 = add_spinbox(
                self.rowzlev, label="5", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 6:
            self.zd6lbl, self.zd6val, self.zd6 = add_spinbox(
                self.rowzlev, label="6", values=(0,), wrap=True,
                command=self.spinned_z)
        if self.maxdim > 7:
            self.zd7lbl, self.zd7val, self.zd7 = add_spinbox(
                self.rowzlev, label="7", values=(0,), wrap=True,
                command=self.spinned_z)

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

        # 5. row
        # options
        self.rowcmap = ttk.Frame(self)
        self.rowcmap.pack(side=tk.TOP, fill=tk.X)
        self.cmaplbl, self.cmap = add_combobox(
            self.rowcmap, label="cmap", values=cmaps,
            command=self.selected, width=10)
        self.cmap.set('RdYlBu')
        self.rev_cmaplbl, self.rev_cmap = add_checkbutton(
            self.rowcmap, label="inverse cmap", value=False,
            command=self.checked)
        self.meshlbl, self.mesh = add_checkbutton(
            self.rowcmap, label="mesh", value=False,
            command=self.checked)

    #
    # Bindings
    #

    def checked(self):
        self.redraw()

    def next_z(self):
        z = self.z.get()
        cols = self.z["values"]
        idx  = cols.index(z)
        idx += 1
        if idx < len(cols):
            self.z.set(cols[idx])
            self.set_dim_z()
            self.x.set('')
            self.y.set('')
            self.set_dim_x()
            self.set_dim_y()
            self.redraw()

    def prev_z(self):
        z = self.z.get()
        cols = self.z["values"]
        idx  = cols.index(z)
        idx -= 1
        if idx > 0:
            self.z.set(cols[idx])
            self.set_dim_z()
            self.x.set('')
            self.y.set('')
            self.set_dim_x()
            self.set_dim_y()
            self.redraw()

    def selected(self, event=None):
        self.redraw()

    def selected_x(self, event=None):
        self.set_dim_x()
        self.redraw()

    def selected_y(self, event=None):
        self.set_dim_y()
        self.redraw()

    def selected_z(self, event=None):
        self.x.set('')
        self.y.set('')
        self.set_dim_x()
        self.set_dim_y()
        self.set_dim_z()
        self.redraw()

    def spinned_x(self, event=None):
        self.redraw()

    def spinned_y(self, event=None):
        self.redraw()

    def spinned_z(self, event=None):
        self.redraw()

    #
    # Set dimensions
    #

    def set_dim_x(self):
        """
        Set dimensions to the dimensions of the x-variable
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
        Set dimensions to the dimensions of the y-variable
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

    def set_dim_z(self):
        """
        Set dimensions to the dimensions of the z-variable
        """
        # reset dimensions
        if self.maxdim > 0:
            self.zd0.config(values=(0,), width=1)
            self.zd0lbl.set('0')
        if self.maxdim > 1:
            self.zd1.config(values=(0,), width=1)
            self.zd1lbl.set('1')
        if self.maxdim > 2:
            self.zd2.config(values=(0,), width=1)
            self.zd2lbl.set('2')
        if self.maxdim > 3:
            self.zd3.config(values=(0,), width=1)
            self.zd3lbl.set('3')
        if self.maxdim > 4:
            self.zd4.config(values=(0,), width=1)
            self.zd4lbl.set('4')
        if self.maxdim > 5:
            self.zd5.config(values=(0,), width=1)
            self.zd5lbl.set('5')
        if self.maxdim > 6:
            self.zd6.config(values=(0,), width=1)
            self.zd6lbl.set('6')
        if self.maxdim > 7:
            self.zd7.config(values=(0,), width=1)
            self.zd7lbl.set('7')
        z = self.z.get()
        if z != '':
            # set real dimensions
            vz = z.split()[0]
            if vz == self.tname:
                vz = self.tvar
            zz = self.fi.variables[vz]
            nall = 0
            if zz.ndim > 0:
                self.zd0.config(values=spinbox_values(zz.shape[0]), width=4)
                if (nall < 2) and (zz.shape[0] > 1):
                    nall += 1
                    self.zd0val.set('all')
                else:
                    self.zd0val.set(0)
                self.zd0lbl.set(zz.dimensions[0])
            if zz.ndim > 1:
                self.zd1.config(values=spinbox_values(zz.shape[1]), width=4)
                if (nall < 2) and (zz.shape[1] > 1):
                    nall += 1
                    self.zd1val.set('all')
                else:
                    self.zd1val.set(0)
                self.zd1lbl.set(zz.dimensions[1])
            if zz.ndim > 2:
                self.zd2.config(values=spinbox_values(zz.shape[2]), width=4)
                if (nall < 2) and (zz.shape[2] > 1):
                    nall += 1
                    self.zd2val.set('all')
                else:
                    self.zd2val.set(0)
                self.zd2lbl.set(zz.dimensions[2])
            if zz.ndim > 3:
                self.zd3.config(values=spinbox_values(zz.shape[3]), width=4)
                if (nall < 2) and (zz.shape[3] > 1):
                    nall += 1
                    self.zd3val.set('all')
                else:
                    self.zd3val.set(0)
                self.zd3lbl.set(zz.dimensions[3])
            if zz.ndim > 4:
                self.zd4.config(values=spinbox_values(zz.shape[4]), width=4)
                if (nall < 2) and (zz.shape[4] > 1):
                    nall += 1
                    self.zd4val.set('all')
                else:
                    self.zd4val.set(0)
                self.zd4lbl.set(zz.dimensions[4])
            if zz.ndim > 5:
                self.zd5.config(values=spinbox_values(zz.shape[5]), width=4)
                if (nall < 2) and (zz.shape[5] > 1):
                    nall += 1
                    self.zd5val.set('all')
                else:
                    self.zd5val.set(0)
                self.zd5lbl.set(zz.dimensions[5])
            if zz.ndim > 6:
                self.zd6.config(values=spinbox_values(zz.shape[6]), width=4)
                if (nall < 2) and (zz.shape[6] > 1):
                    nall += 1
                    self.zd6val.set('all')
                else:
                    self.zd6val.set(0)
                self.zd6lbl.set(zz.dimensions[6])
            if zz.ndim > 7:
                self.zd7.config(values=spinbox_values(zz.shape[7]), width=4)
                if (nall < 2) and (zz.shape[7] > 1):
                    nall += 1
                    self.zd7val.set('all')
                else:
                    self.zd7val.set(0)
                self.zd7lbl.set(zz.dimensions[7])

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

    def get_slice_z(self, z):
        """
        Get the slice from rhs y-variable selected in the level row
        """
        if z.ndim > 0:
            dim = self.zd0.get()
            if dim == 'all':
                s = range(0, z.shape[0])
            else:
                s = (int(dim),)
            zout = np.take(z, s, axis=0)
        else:
            zout = z
        if z.ndim > 1:
            dim = self.zd1.get()
            if dim == 'all':
                s = range(0, z.shape[1])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=1)
        if z.ndim > 2:
            dim = self.zd2.get()
            if dim == 'all':
                s = range(0, z.shape[2])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=2)
        if z.ndim > 3:
            dim = self.zd3.get()
            if dim == 'all':
                s = range(0, z.shape[3])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=3)
        if z.ndim > 4:
            dim = self.zd4.get()
            if dim == 'all':
                s = range(0, z.shape[4])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=4)
        if z.ndim > 5:
            dim = self.zd5.get()
            if dim == 'all':
                s = range(0, z.shape[5])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=5)
        if z.ndim > 6:
            dim = self.zd6.get()
            if dim == 'all':
                s = range(0, z.shape[6])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=6)
        if z.ndim > 7:
            dim = self.zd7.get()
            if dim == 'all':
                s = range(0, z.shape[7])
            else:
                s = (int(dim),)
            zout = np.take(zout, s, axis=7)

        return zout

    #
    # Plotting
    #

    def redraw(self, event=None):
        # get all states
        # rowz
        z = self.z.get()
        trans_z = self.trans_z.get()
        # rowxy
        x = self.x.get()
        y = self.y.get()
        inv_x = self.inv_x.get()
        inv_y = self.inv_y.get()
        # rowcmap
        cmap = self.cmap.get()
        rev_cmap = self.rev_cmap.get()
        mesh = self.mesh.get()

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
                else:
                    zz = self.time
                zlab = 'Date'
            else:
                zz = self.fi.variables[vz]
                zlab = zz.name
                try:
                    zlab += ' (' + zz.units + ')'
                except AttributeError:
                    pass
                miss = get_miss(self, zz)
                zz = self.get_slice_z(zz).squeeze()
                zz = set_miss(zz, miss)
                if trans_z:
                    zz = zz.T
        if (y != ''):
            # y axis
            vy = y.split()[0]
            if vy == self.tname:
                if mesh:
                    yy = self.dtime
                else:
                    yy = self.time
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
        if (x != ''):
            # x axis
            vx = x.split()[0]
            if vx == self.tname:
                if mesh:
                    xx = self.dtime
                else:
                    xx = self.time
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
        if mesh:
            try:
                cc = self.axes.pcolormesh(xx, yy, zz.T, cmap=cmap,
                                          shading='nearest')
            except Exception:
                estr  = 'Contour: x (' + vx + '), y (' + vy + '),'
                estr += ' z (' + vz + ') shapes do not match for'
                estr += ' pcolormesh:'
                print(estr, xx.shape, yy.shape, zz.shape)
                return
        else:
            try:
                cc = self.axes.contourf(xx, yy, zz.T, cmap=cmap)
            except Exception:
                estr  = 'Contour: x (' + vx + '), y (' + vy + '),'
                estr += ' z (' + vz + ') shapes do not match for'
                estr += ' contourf:'
                print(estr, xx.shape, yy.shape, zz.shape)
                return
        # help(self.figure)
        cb = self.figure.colorbar(cc, fraction=0.05, shrink=0.75)
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
        self.canvas.draw()
        self.toolbar.update()
