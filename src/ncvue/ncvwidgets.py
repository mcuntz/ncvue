#!/usr/bin/env python
"""
Widget functions.

Convenience functions for adding Tkinter widgets.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020-2023 Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   callurl
   Tooltip
   add_checkbutton
   add_combobox
   add_entry
   add_imagemenu
   add_menu
   add_scale
   add_spinbox
   add_tooltip
   Treeview

History
    * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
    * Added tooltips to all widgets with class Tooltip,
      Jan 2021, Matthias Cuntz
    * Added add_tooltip widget, Jan 2021, Matthias Cuntz
    * add_spinbox returns also label widget, Jan 2021, Matthias Cuntz
    * padlabel for add_entry to add space to previous widget,
      Jul 2023, Matthias Cuntz
    * labelwidth for add_entry to align columns with pack,
      Jul 2023, Matthias Cuntz
    * Replace tk constants with strings such as tk.LEFT with 'left',
      Jul 2023, Matthias Cuntz
    * Use Hovertip from local copy of tooltip.py, Jul 2023, Matthias Cuntz
    * Added Treeview class with optional horizontal and vertical scroolbars,
      Jul 2023, Matthias Cuntz
    * Added callurl function, Dec 2023, Matthias Cuntz

"""
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from .tooltip import Hovertip


__all__ = ['callurl', 'Tooltip',
           'add_checkbutton', 'add_combobox', 'add_entry',
           'add_imagemenu', 'add_menu', 'add_scale', 'add_spinbox',
           'add_tooltip',
           'Treeview']


# https://stackoverflow.com/questions/23482748/how-to-create-a-hyperlink-with-a-label-in-tkinter
def callurl(url):
    """
    Open url in external web browser

    Parameters
    ----------
    url : str
        html url

    Returns
    -------
    Opens *url* in external web browser

    Examples
    --------
    >>> opthead = ttk.Frame(self)
    >>> opthead.pack(side='top', fill='x')
    >>> optheadlabel1 = ttk.Label(opthead, text='Options for')
    >>> optheadlabel1.pack(side='left')
    >>> ttk.Style().configure('blue.TLabel', foreground='blue')
    >>> optheadlabel2 = ttk.Label(opthead, text='pandas.read_csv',
    ...                           style='blue.TLabel')
    >>> optheadlabel2.pack(side='left')
    >>> font = tkfont.Font(optheadlabel2, optheadlabel2.cget("font"))
    >>> font.configure(underline=True)
    >>> optheadlabel2.configure(font=font)
    >>> optheadlabel2.bind("<Button-1>",
    ...                    lambda e: callurl("https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html"))

    """
    webbrowser.open_new(url)


class Tooltip(Hovertip):
    """
    A tooltip that pops up when a mouse hovers over an anchor widget.

    This is a copy/extension of the class Hovertip of Python's
    idlelib/tooltip.py.
    In addition, it sets the foreground colour to see the tip also in
    macOS dark mode, and displays a textvariable rather than simple text
    so one can change the tip during run time.

    """
    def __init__(self, anchor_widget, text, hover_delay=1000):
        """
        Create a text tooltip with a mouse hover delay.
        anchor_widget: the widget next to which the tooltip will be shown
        text: tk.StringVar with text to display
        hover_delay: time to delay before showing the tooltip, in milliseconds
        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.

        """
        super(Tooltip, self).__init__(anchor_widget, text,
                                      hover_delay=hover_delay)

    def showcontents(self):
        # light yellow = #ffffe0
        label = tk.Label(self.tipwindow, textvariable=self.text,
                         background="#ffffe0", foreground="#000000",
                         justify='left', relief='flat', borderwidth=0,
                         padx=1, pady=1)
        label.pack()


def add_checkbutton(frame, label="", value=False, command=None, tooltip="",
                    **kwargs):
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
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the checkbutton (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Checkbutton

    Returns
    -------
    tk.StringVar, tk.BooleanVar
        variable for the text on the checkbutton,
        control variable tracking current state of checkbutton
    tk.StringVar
        variable for the text of the tooltip, if given.

    Examples
    --------
    >>> self.rowzxy = ttk.Frame(self)
    >>> self.rowzxy.pack(side='top', fill='x')
    >>> self.inv_xlbl, self.inv_x = add_checkbutton(
    ...     self.rowzxy, label="invert x", value=False, command=self.checked)

    """
    check_label = tk.StringVar()
    check_label.set(label)
    bvar = tk.BooleanVar(value=value)
    cb = ttk.Checkbutton(frame, variable=bvar, textvariable=check_label,
                         command=command, **kwargs)
    cb.pack(side='left', padx=3)
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        cbtip = Tooltip(cb, ttip)
        return check_label, bvar, ttip
    else:
        return check_label, bvar


def add_combobox(frame, label="", values=[], command=None, tooltip="",
                 **kwargs):
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
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the combobox (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Combobox

    Returns
    -------
    tk.StringVar, ttk.Combobox
        variable for the text before the combobox, combobox widget
    tk.StringVar
        variable for the text of the tooltip, if given.

    Examples
    --------
    >>> self.rowzxy = ttk.Frame(self)
    >>> self.rowzxy.pack(side='top', fill='x')
    >>> self.xlbl, self.x = add_combobox(
    ...     self.rowzxy, label="x", values=columns, command=self.selected)

    """
    width = kwargs.pop('width', 25)
    cb_label = tk.StringVar()
    cb_label.set(label)
    label = ttk.Label(frame, textvariable=cb_label)
    label.pack(side='left')
    cb = ttk.Combobox(frame, values=values, width=width, **kwargs)
    # long = len(max(values, key=len))
    # cb.configure(width=(max(20, long//2)))
    if command is not None:
        cb.bind("<<ComboboxSelected>>", command)
    cb.pack(side='left')
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        cbtip = Tooltip(cb, ttip)
        return cb_label, cb, ttip
    else:
        return cb_label, cb


def add_entry(frame, label="", text="", command=None, tooltip="",
              padlabel=0, labelwidth=None, **kwargs):
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
    command : function or list of functions, optional
        Handler function to be bound to the entry for the events
        '<FocusOut>', <Return>, '<Key-Return>', and <KP_Enter> (default: None).
        If list is given than command[0] is bound to '<FocusOut>' and
        command[1] is bound to the 3 events
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the entry (default: "" = no tooltip)
    padlabel : int, optional
        Prepend number of spaces to create distance other widgets (default: 0)
    labelwidth : int, optional
        If given, set width of Label
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Entry

    Returns
    -------
    tk.StringVar, tk.StringVar
        variable for the text before the entry,
        variable for the text in the entry area
    tk.StringVar
        variable for the text of the tooltip, if given.

    Examples
    --------
    >>> self.rowxyopt = ttk.Frame(self)
    >>> self.rowxyopt.pack(side='top', fill='x')
    >>> self.lslbl, self.ls = add_entry(
    ...     self.rowxyopt, label="ls", text='-',
    ...     width=4, command=self.selected_y)

    """
    entry_label = tk.StringVar()
    nlab = len(label) + padlabel
    lab = f'{label:>{nlab}s}'
    entry_label.set(lab)
    lkwargs = {'textvariable': entry_label}
    if labelwidth is not None:
        lkwargs.update({'width': labelwidth})
    label = ttk.Label(frame, **lkwargs)
    # print(label.configure())
    label.pack(side='left')
    entry_text = tk.StringVar()
    if text is None:
        tt = 'None'
    elif isinstance(text, bool):
        if text:
            tt = 'True'
        else:
            tt = 'False'
    else:
        tt = str(text)
    entry_text.set(tt)
    entry = ttk.Entry(frame, textvariable=entry_text, **kwargs)
    if command is not None:
        if isinstance(command, (list, tuple)):
            com0 = command[0]
            if len(command) > 1:
                com1 = command[1]
            else:
                com1 = command[0]
        else:
            com0 = command
            com1 = command
        entry.bind('<FocusOut>', com0)    # tab or click
        entry.bind('<Return>', com1)      # return
        entry.bind('<Key-Return>', com1)  # return
        entry.bind('<KP_Enter>', com1)    # return of numeric keypad
    entry.pack(side='left')
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        etip = Tooltip(entry, ttip)
        return entry_label, entry_text, ttip
    else:
        return entry_label, entry_text


def add_imagemenu(frame, label="", values=[], images=[], command=None,
                  tooltip="", **kwargs):
    """
    Add a left-aligned menu with menubuttons having text and images
    with a ttk.Label before.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears in front of the menu (default: "")
    values : list of str, optional
        The choices that will appear in the drop-down menu (default: [])
    images : list of str, optional
        The images before the choices that will appear in the drop-down menu
        (default: [])
    command : function, optional
        Handler function to be called if new menu entry chosen (default: None).
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the menu (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to the main ttk.Menubutton
    tk.StringVar
        variable for the text of the tooltip, if given.

    Returns
    -------
    tk.StringVar, ttk.Menubutton
        variable for the text before the menu, main tt.Menubutton widget

    Examples
    --------
    >>> self.rowcmap = ttk.Frame(self)
    >>> self.rowcmap.pack(side='top', fill='x')
    >>> self.cmaplbl, self.cmap = add_imagemenu(
    ...     self.rowcmap, label="cmap", values=self.cmaps,
    ...     images=self.imaps, command=self.selected_cmap)
    >>> self.cmap['text']  = 'RdYlBu'
    >>> self.cmap['image'] = self.imaps[self.cmaps.index('RdYlBu')]

    """
    from functools import partial
    estr  = 'Same number of values and images needed for add_imagemenu.'
    estr += ' values (' + str(len(values)) + '): ' + str(values)
    estr += ', images (' + str(len(images)) + '): ' + str(images)
    assert len(values) == len(images), estr
    mb_label = tk.StringVar()
    mb_label.set(label)
    label = ttk.Label(frame, textvariable=mb_label)
    label.pack(side='left')
    mb = ttk.Menubutton(frame, image=images[0], text=values[0],
                        compound='left')
    sb = tk.Menu(mb, tearoff=False)
    mb.config(menu=sb)
    for i, v in enumerate(values):
        sb.add_command(label=v, image=images[i], compound='left',
                       command=partial(command, v))
    mb.pack(side='left')
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        mbtip = Tooltip(mb, ttip)
        return mb_label, mb, ttip
    else:
        return mb_label, mb


def add_menu(frame, label="", values=[], command=None, tooltip="", **kwargs):
    """
    Add a left-aligned menu with menubuttons with a ttk.Label before.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears in front of the menu (default: "")
    values : list of str, optional
        The choices that will appear in the drop-down menu (default: [])
    command : function, optional
        Handler function to be called if new menu entry chosen (default: None).
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the menu (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to the main ttk.Menubutton
    tk.StringVar
        variable for the text of the tooltip, if given.

    Returns
    -------
    tk.StringVar, ttk.Menubutton
        variable for the text before the menu, main tt.Menubutton widget

    Examples
    --------
    >>> self.rowzxy = ttk.Frame(self)
    >>> self.rowzxy.pack(side='top', fill='x')
    >>> self.xlbl, self.x = add_combobox(
    ...     self.rowzxy, label="x", values=columns, command=self.selected)

    """
    from functools import partial
    mb_label = tk.StringVar()
    mb_label.set(label)
    label = ttk.Label(frame, textvariable=mb_label)
    label.pack(side='left')
    mb = ttk.Menubutton(frame, text=values[0], compound='left')
    sb = tk.Menu(mb, tearoff=False)
    mb.config(menu=sb)
    for i, v in enumerate(values):
        sb.add_command(label=v, compound='left',
                       command=partial(command, v))
    mb.pack(side='left')
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        mbtip = Tooltip(mb, ttip)
        return mb_label, mb, ttip
    else:
        return mb_label, mb


def add_scale(frame, label="", ini=0, tooltip="", **kwargs):
    """
    Add a left-aligned ttk.Scale with a ttk.Label before.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    label : str, optional
        Text that appears in front of the scale (default: "")
    ini : float, optional
        Initial value of scale (default: 0)
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the scale (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to ttk.Scale

    Returns
    -------
    tk.StringVar, tk.DoubleVar, ttk.Scale
        variable for the text before the scale,
        value of scale,
        scale widget
    tk.StringVar
        variable for the text of the tooltip, if given.

    Examples
    --------
    >>> self.rowzxy = ttk.Frame(self)
    >>> self.rowzxy.pack(side='top', fill='x')
    >>> self.xlbl, self.x = add_scale(
    ...     self.rowzxy, label="x", values=columns, command=self.selected)

    """
    s_label = tk.StringVar()
    s_label.set(label)
    label = ttk.Label(frame, textvariable=s_label)
    label.pack(side='left')
    s_val = tk.DoubleVar()
    s_val.set(ini)
    s = ttk.Scale(frame, variable=s_val, **kwargs)
    s.pack(side='left')
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        stip = Tooltip(s, ttip)
        return s_label, s_val, s, ttip
    else:
        return s_label, s_val, s


def add_spinbox(frame, label="", values=[], command=None, tooltip="",
                **kwargs):
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
        Handler function bound to
        <Return>, '<Key-Return>', <KP_Enter>, and '<FocusOut>' (default: None).
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the spinbox (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to tk.Spinbox

    Returns
    -------
    tk.StringVar, ttk.Label, tk.StringVar, tk.Spinbox
        variable for the text before the spinbox,
        label widget,
        variable for the text in the spinbox area,
        spinbox widget
    tk.StringVar
        variable for the text of the tooltip, if given.

    Examples
    --------
    >>> self.rowlev = ttk.Frame(self)
    >>> self.rowlev.pack(side='top', fill='x')
    >>> self.dlval, self.dl, self.dval, self.d = add_spinbox(
    ...     self.rowlev, label="dim", values=range(0,10),
    ...     command=self.spinned)

    """
    width = kwargs.pop('width', 1)
    sbl_val = tk.StringVar()
    sbl_val.set(label)
    sbl = ttk.Label(frame, textvariable=sbl_val)
    sbl.pack(side='left')
    sb_val = tk.StringVar()
    if len(values) > 0:
        sb_val.set(str(values[0]))
    sb = tk.Spinbox(frame, values=values, command=command, width=width,
                    textvariable=sb_val, **kwargs)
    if command is not None:
        sb.bind('<Return>', command)      # return
        sb.bind('<Key-Return>', command)  # return
        sb.bind('<KP_Enter>', command)    # return of numeric keypad
        sb.bind('<FocusOut>', command)    # tab or click
    sb.pack(side='left')
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        sbtip = Tooltip(sb, ttip)
        return sbl_val, sbl, sb_val, sb, ttip
    else:
        return sbl_val, sbl, sb_val, sb


def add_tooltip(frame, tooltip="", **kwargs):
    """
    Add a writeable tooltip to a widget using the class Tooltip.

    Parameters
    ----------
    frame : tk widget
        Parent widget
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the parent widget (default: "" = no tooltip)
    **kwargs : option=value pairs, optional
        All other options will be passed to tk.StringVar

    Returns
    -------
    tk.StringVar
        variable for the text of the tooltip.

    Examples
    --------
    >>> self.rowlev = ttk.Frame(self)
    >>> self.rowlev.pack(side='top', fill='x')
    >>> self.dlbl, self.dval, self.d = add_spinbox(
    ...     self.rowlev, label="dim", values=range(0,10),
    ...     command=self.spinned)
    >>> self.dtip = add_tooltip(self.d, 'Dimension')

    """
    ttip = tk.StringVar()
    ttip.set(tooltip)
    htip = Tooltip(frame, ttip)
    return ttip


# https://pythonassets.com/posts/scrollbar-in-tk-tkinter/
class Treeview(ttk.Frame):
    """
    Treeview class with optional horizontal and vertical scrollbars

    Examples
    --------
    Simple ttk.Treeview widget

    .. code-block:: python

       tree = Treeview(frame_widget)

    ttk.Treeview widget with vertical scrollbar

    .. code-block:: python

       tree = Treeview(frame_widget, yscroll=True)

    ttk.Treeview widget with vertical and horizontal scrollbars

    .. code-block:: python

       tree = Treeview(frame_widget, xscroll=True, yscroll=True)

    """
    def __init__(self, *args, xscroll=False, yscroll=False, **kwargs):
        super().__init__(*args, **kwargs)
        # scrollbars
        if xscroll:
            self.hscrollbar = ttk.Scrollbar(self, orient='horizontal')
        if yscroll:
            self.vscrollbar = ttk.Scrollbar(self, orient='vertical')
        # treeview
        self.tv = ttk.Treeview(self)
        # pack scrollbars and treeview together
        if xscroll:
            self.tv.config(xscrollcommand=self.hscrollbar.set)
            self.hscrollbar.config(command=self.tv.xview)
            self.hscrollbar.pack(side='bottom', fill='x')
        if yscroll:
            self.tv.config(yscrollcommand=self.vscrollbar.set)
            self.vscrollbar.config(command=self.tv.yview)
            self.vscrollbar.pack(side='right', fill='y')
        self.tv.pack()
        # convenience functions
        self.tag_configure = self.tv.tag_configure
        self.config = self.tv.config
        self.column = self.tv.column
        self.heading = self.tv.heading
        self.insert = self.tv.insert
