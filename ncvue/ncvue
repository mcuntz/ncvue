#!/usr/bin/env python
"""
usage: ncvue [-h] [netcdf_file]

A minimal GUI for a quick view of netcdf files.

positional arguments:
  netcdf_file      netcdf file

optional arguments:
  -h, --help       show this help message and exit


Example command line:
    ncvue MuSICA_out_2009.nc

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
import netCDF4 as nc
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
plt.style.use('seaborn-darkgrid')
# nc.default_fillvals but with keys as variables['var'].dtype
nctypes = [ np.dtype(i) for i in nc.default_fillvals ]
ncfill  = dict(zip(nctypes, list(nc.default_fillvals.values())))
ncfill.update({np.dtype('O'): np.nan})

# Possible improvements
# 1. Fix scale colour scale in Contour.
# 1. Add grid by hand in contour plot.
# 1. Smarter get_slice so that not whole variable is read all the time.
# 1. Document script
# 1. Map panel
# 1. Make own repository and pip package


# --------------------------------------------------------------------
# Helper functions
#

def get_miss(self, x):
    """
    Get list of missing values, i.e. self.miss, x._FillValue,
    x.missing_value, and from netcdf4.default_fillvals.

    Parameters
    ----------
    self : class
        ncvue class
    x : netCDF4._netCDF4.Variable
        netcdf variable

    Returns
    -------
    list
        List with missing values self.miss, x._FillValue,
        x.missing_value if present,  and from netcdf4.default_fillvals

    Examples
    --------
    >>> x = fi.variables['time']
    >>> miss = get_miss(self, x)
    """
    out = [ncfill[x.dtype]]
    try:
        out += [self.miss]
    except AttributeError:
        pass
    try:
        out += [x._FillValue]
    except AttributeError:
        pass
    try:
        out += [x.missing_value]
    except AttributeError:
        pass
    return out


def set_miss(x, miss):
    """
    Set `x` to NaN for all values in miss.

    Parameters
    ----------
    x : ndarray
        numpy array
    miss : iterable
        values which shall be set to np.nan in `x`

    Returns
    -------
    ndarray
        `x` with all values set np.nan that are equal to any value in miss.

    Examples
    --------
    >>> x = fi.variables['time']
    >>> miss = get_miss(self, x)
    >>> x = set_miss(x, miss)
    """
    for mm in miss:
        x = np.where(x == mm, np.nan, x)
    return x


def spinbox_values(ndim):
    """
    Tuple for Spinbox values with 'all' before range(ndim) if ndim>1,
    otherwise single entry (0,)

    Parameters
    ----------
    ndim : int
        Size of dimension.

    Returns
    -------
    tuple
        (('all',) + tuple(range(ndim))) if ndim > 1
        (0,) else

    Examples
    --------
    >>> self.xd0.config(values=spinbox_values(xx.shape[0]))
    """
    if ndim > 1:
        return (('all',) + tuple(range(ndim)))
    else:
        return (0,)


def zip_dim_name_length(ncvar):
    """
    Combines dimension names and length of netcdf variable in list of strings.

    Parameters
    ----------
    ncvar : netCDF4._netCDF4.Variable
        netcdf variables class

    Returns
    -------
    list
        List of dimension name and length in the form 'dim=len'.

    Examples
    --------
    >>> import netCDF4 as nc
    >>> ifile = 'test.nc'
    >>> fi = nc.Dataset(ifile, 'r')
    >>> w_soil = fi.variables['w_soil']
    >>> print(zip_dim_name_length(w_soil))
    ('ntime=17520', 'nsoil=30')
    """
    out = []
    for i in range(ncvar.ndim):
        out.append(ncvar.dimensions[i]+'='+str(ncvar.shape[i]))
    return out


#
# Widgets
#

def add_checkbutton(frame, label="", value=False, command=None, **kwargs):
    """
    Add a left-aligned ttk.Checkbutton.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears on the checkbutton (default: "")
    value : bool, optional
        Initial state of the checkbutton (default: False)
    command : function, optional
        Function to be called whenever the state of the
        checkbutton changes (default: None).
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Checkbutton

    Returns
    -------
    tk.StringVar, tk.BooleanVar
        variable for the text on the checkbutton,
        control variable tracking current state of checkbutton

    Examples
    --------
    >>> self.rowzxy = ttk.Frame(self)
    >>> self.rowzxy.pack(side=tk.TOP, fill=tk.X)
    >>> self.inv_xlbl, self.inv_x = add_checkbutton(
    ...     self.rowzxy, label="invert x", value=False, command=self.checked)
    """
    check_label = tk.StringVar()
    check_label.set(label)
    bvar = tk.BooleanVar(value=value)
    cb = ttk.Checkbutton(frame, variable=bvar, textvariable=check_label,
                         command=command, **kwargs)
    cb.pack(side=tk.LEFT, padx=3)
    return check_label, bvar


def add_combobox(frame, label="", values=[], command=None, **kwargs):
    """
    Add a left-aligned ttk.Combobox with a ttk.Label before.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears in front of the combobox (default: "")
    values : list of str, optional
        The choices that will appear in the drop-down menu (default: [])
    command : function, optional
        Handler function to be bound to the combobox for the event
        <<ComboboxSelected>> (default: None).
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Combobox

    Returns
    -------
    tk.StringVar, ttk.Combobox
        variable for the text before the combobox,
        combobox widget

    Examples
    --------
    >>> self.rowzxy = ttk.Frame(self)
    >>> self.rowzxy.pack(side=tk.TOP, fill=tk.X)
    >>> self.xlbl, self.x = add_combobox(
    ...     self.rowzxy, label="x", values=columns, command=self.selected)
    """
    width = kwargs.pop('width', 25)
    cb_label = tk.StringVar()
    cb_label.set(label)
    label = ttk.Label(frame, textvariable=cb_label)
    label.pack(side=tk.LEFT)
    cb = ttk.Combobox(frame, values=values, width=width, **kwargs)
    # long = len(max(values, key=len))
    # cb.configure(width=(max(20, long//2)))
    if command is not None:
        cb.bind("<<ComboboxSelected>>", command)
    cb.pack(side=tk.LEFT)
    return cb_label, cb


def add_entry(frame, label="", text="", command=None, **kwargs):
    """
    Add a left-aligned ttk.Entry with a ttk.Label before.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears in front of the entry (default: "")
    text : str, optional
        Initial text in the entry area (default: "")
    command : function, optional
        Handler function to be bound to the entry for the events
        <Return>, '<Key-Return>', and '<FocusOut>' (default: None).
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Entry

    Returns
    -------
    tk.StringVar, tk.StringVar
        variable for the text before the entry,
        variable for the text in the entry area

    Examples
    --------
    >>> self.rowxyopt = ttk.Frame(self)
    >>> self.rowxyopt.pack(side=tk.TOP, fill=tk.X)
    >>> self.lslbl, self.ls = add_entry(
    ...     self.rowxyopt, label="ls", text='-',
    ...     width=4, command=self.selected_y)
    """
    entry_label = tk.StringVar()
    entry_label.set(label)
    label = ttk.Label(frame, textvariable=entry_label)
    label.pack(side=tk.LEFT)
    entry_text = tk.StringVar()
    entry_text.set(text)
    entry = ttk.Entry(frame, textvariable=entry_text, **kwargs)
    if command is not None:
        entry.bind('<Return>', command)      # return
        entry.bind('<Key-Return>', command)  # return
        entry.bind('<FocusOut>', command)    # tab or click
    entry.pack(side=tk.LEFT)
    return entry_label, entry_text


def add_spinbox(frame, label="", values=[], command=None, **kwargs):
    """
    Add a left-aligned tk.Spinbox with a ttk.Label before.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears in front of the spinbox (default: "")
    values : list of str, optional
        The list of choices on the spinbox (default: [])
    command : function, optional
        Handler function to be bound to the spinbox for the event
        <<ComboboxSelected>> (default: None).
    **kwargs : option=value pairs, optional
        All other options will be passed to tk.Spinbox

    Returns
    -------
    tk.StringVar, tk.StringVar, tk.Spinbox
        variable for the text before the spinbox,
        variable for the text in the spinbox area,
        spinbox widget

    Examples
    --------
    >>> self.rowlev = ttk.Frame(self)
    >>> self.rowlev.pack(side=tk.TOP, fill=tk.X)
    >>> self.dlbl, self.dval, self.d = add_spinbox(
    ...     self.rowlev, label="dim", values=range(0,10),
    ...     command=self.spinned)
    """
    width = kwargs.pop('width', 1)
    sb_label = tk.StringVar()
    sb_label.set(label)
    label = ttk.Label(frame, textvariable=sb_label)
    label.pack(side=tk.LEFT)
    sb_val = tk.StringVar()
    if len(values) > 0:
        sb_val.set(str(values[0]))
    sb = tk.Spinbox(frame, values=values, command=command, width=width,
                    textvariable=sb_val, **kwargs)
    if command is not None:
        sb.bind('<Return>', command)      # return
        sb.bind('<Key-Return>', command)  # return
        sb.bind('<FocusOut>', command)    # tab or click
    sb.pack(side=tk.LEFT)
    return sb_label, sb_val, sb


# --------------------------------------------------------------------
# Contour plot panel
#

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
        # self                      = .!toplevel.!ncvmain.!scatterplot,
        # self.master               = .!toplevel.!ncvmain
        # self.master.master        = .!toplevel
        # self.master.master.master = .
        # toplevel is changing with each new window, e.g. .!toplevel2
        # first window has no top level
        if self.master.master.master is None:
            rot = self.master.master
        else:
            rot = self.master.master.master
        self.newwin = ttk.Button(self.rowwin, text="New Window",
                                 command=partial(ncvWin, self.fi, rot))
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


# --------------------------------------------------------------------
# Scatter plot panel
#

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
        # self                      = .!toplevel.!ncvmain.!scatterplot,
        # self.master               = .!toplevel.!ncvmain
        # self.master.master        = .!toplevel
        # self.master.master.master = .
        # toplevel is changing with each new window, e.g. .!toplevel2
        # first window has no top level
        if self.master.master.master is None:
            rot = self.master.master
        else:
            rot = self.master.master.master
        self.newwin = ttk.Button(self.rowwin, text="New Window",
                                 command=partial(ncvWin, self.fi, rot))
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


# --------------------------------------------------------------------
# Window with plot panels
#

class ncvMain(ttk.Frame):
    """
    New plotting window with different plotting panels.
    """

    #
    # Window setup
    #

    def __init__(self, fi, master=None, miss=np.nan, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=1)

        self.name   = 'ncvMain'
        self.fi     = fi      # netcdf file
        self.master = master  # master window = root
        self.root   = master  # root window
        self.miss   = master.miss
        self.time   = None    # datetime variable
        self.tname  = ''      # datetime variable name
        self.tvar   = ''      # datetime variable name in netcdf file
        self.dtime  = None    # decimal year
        self.maxdim = 0       # maximum number of dimensions of all variables
        self.cols   = []      # variable list

        # Analyse netcdf file
        self.analyse_netcdf()

        # Notebook for tabs for future plot types
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tab_scatter = ncvScatter(self)
        self.tab_contour = ncvContour(self)
        self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
        self.tabs.add(self.tab_contour, text=self.tab_contour.name)

    #
    # Methods
    #

    # analyse netcdf file
    def analyse_netcdf(self):
        import datetime as dt
        try:
            import cftime as cf
        except ModuleNotFoundError:
            import netCDF4 as cf
        # # search unlimited dimension
        # udim = None
        # for dd in self.fi.dimensions:
        #     if self.fi.dimensions[dd].isunlimited():
        #         udim = dd
        #         break
        # search for time variable
        self.time  = None
        self.tname = ''
        self.tvar  = ''
        self.dtime = None
        for vv in self.fi.variables:
            if ((vv.lower() == 'time') or (vv.lower() == 'datetime') or
                (vv.lower() == 'date')):
                self.tvar = vv
                if vv.lower() == 'datetime':
                    self.tname = 'date'
                else:
                    self.tname = 'datetime'
                try:
                    tunit = self.fi.variables[self.tvar].units
                except AttributeError:
                    tunit = ''
                try:
                    tcal = self.fi.variables[self.tvar].calendar
                except AttributeError:
                    tcal = 'standard'
                self.time = self.fi.variables[self.tvar][:]
                # time dimension "day as %Y%m%d.%f" from cdo.
                if ' as ' in tunit:
                    itunit = tunit.split()[2]
                    dtime = []
                    for tt in self.time:
                        stt = str(tt).split('.')
                        sstt = ('00'+stt[0])[-8:] + '.' + stt[1]
                        dtime.append(dt.datetime.strptime(sstt, itunit))
                    ntime = cf.date2num(dtime,
                                        'days since 0001-01-01 00:00:00')
                    self.dtime = cf.num2date(ntime,
                                             'days since 0001-01-01 00:00:00')
                else:
                    try:
                        self.dtime = cf.num2date(self.time, tunit,
                                                 calendar=tcal)
                    except ValueError:
                        self.dtime = None
                if self.dtime is not None:
                    ntime = len(self.dtime)
                    if (tcal == '360_day'):
                        ndays = [360.]*ntime
                    elif (tcal == '365_day'):
                        ndays = [365.]*ntime
                    elif (tcal == 'noleap'):
                        ndays = [365.]*ntime
                    elif (tcal == '366_day'):
                        ndays = [366.]*ntime
                    elif (tcal == 'all_leap'):
                        ndays = [366.]*ntime
                    else:
                        ndays = [ 365. +
                                  float((((t.year%4) == 0) &
                                         ((t.year%100) != 0)) |
                                        ((t.year%400) == 0))
                                  for t in self.dtime ]
                    self.dtime = np.array([
                        t.year +
                        (t.dayofyr-1 + t.hour / 24. +
                         t.minute / 1440 + t.second / 86400.) / ndays[i]
                        for i, t in enumerate(self.dtime) ])
                # make datetime variable
                try:
                    self.time = cf.num2date(
                        self.time, tunit, calendar=tcal,
                        only_use_cftime_datetimes=False,
                        only_use_python_datetimes=True)
                except TypeError:
                    self.time = cf.num2date(self.time, tunit,
                                            calendar=tcal)
                except ValueError:
                    # if not possible use decimal year
                    self.time = self.dtime
                break
        # construct different lists depending on number of dimensions
        if self.time is not None:
            addt = [
                self.tname + ' ' +
                str(tuple(zip_dim_name_length(self.fi.variables[self.tvar]))) ]
            self.cols  += addt
        ivars = []
        for vv in self.fi.variables:
            # ss = self.fi.variables[vv].shape
            ss = tuple(zip_dim_name_length(self.fi.variables[vv]))
            self.maxdim = max(self.maxdim, len(ss))
            ivars.append((vv, ss, len(ss)))
        self.cols  += sorted([ vv[0] + ' ' + str(vv[1]) for vv in ivars ])


# --------------------------------------------------------------------
# Secondary creation of new window with panels
#

class ncvWin(tk.Toplevel):
    """
    Call ncvMain for a new plotting window.
    """
    def __init__(self, fi, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.name = 'ncvWin'
        self.title("Secondary ncvue window")
        self.geometry('1000x800')
        self.miss = master.miss

        secondary_frame = ncvMain(fi, master=self)


# --------------------------------------------------------------------
# Calling function for creation of primary plotting window
#

def ncvue(ncfile, miss=np.nan):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    ncfile : str
        Name of netcdf file.
    """
    fi = nc.Dataset(ncfile, 'r')

    root = tk.Tk()
    root.name = 'root'
    root.title("ncvue "+ncfile)
    root.geometry('1000x800+100+100')
    root.miss = miss

    # 1st plotting window
    main_frame = ncvMain(fi, master=root)

    root.mainloop()

    fi.close()


# --------------------------------------------------------------------
# Script
#
if __name__ == "__main__":

    import argparse

    miss = np.nan
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
A minimal GUI for a quick view of netcdf files.""")
    hstr  = 'Set value to missing value (default: numpy.nan)'
    parser.add_argument('-m', '--miss', action='store', type=float,
                        default=miss, dest='miss',
                        metavar='missing_value', help=hstr)
    parser.add_argument('ncfile', nargs='?', default=None,
                        metavar='netcdf_file',
                        help='netcdf file')

    args   = parser.parse_args()
    miss   = args.miss
    ncfile = args.ncfile

    del parser, args

    # This must be before any other call to matplotlib
    # because it uses the TkAgg backend.
    # This means, do not use --pylab with ipython.
    ncvue(ncfile, miss=miss)
