#!/usr/bin/env python
"""
Widget functions for ncvue.

Convenience functions for adding Tkinter widgets.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de

Released under the MIT License; see LICENSE file for details.

History:

* Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
* Added tooltips to all widgets with class Tooltip, Jan 2021, Matthias Cuntz
* Added add_tooltip widget, Jan 2021, Matthias Cuntz
* add_spinbox returns also label widget, Jan 2021, Matthias Cuntz

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   Tooltip
   add_checkbutton
   add_combobox
   add_entry
   add_imagemenu
   add_menu
   add_scale
   add_spinbox
   add_tooltip
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
from idlelib.tooltip import Hovertip


__all__ = ['Tooltip',
           'add_checkbutton', 'add_combobox', 'add_entry',
           'add_imagemenu', 'add_menu', 'add_scale', 'add_spinbox',
           'add_tooltip']


class Tooltip(Hovertip):
    """
    A tooltip that pops up when a mouse hovers over an anchor widget.

    This is a copy of the class Hovertip of Python's idlelib/tooltip.py.
    In addition, it sets the foreground colour to see the tip also in
    macOS dark mode, and displays a textvariable rather than simple text
    so one can change the tip during run time.
    """
    def __init__(self, anchor_widget, text, hover_delay=1000):
        """Create a text tooltip with a mouse hover delay.
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
                         justify=tk.LEFT, relief=tk.FLAT, borderwidth=0,
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
    if tooltip:
        ttip = tk.StringVar()
        ttip.set(tooltip)
        cbtip = Tooltip(cb, ttip)
        return cb_label, cb, ttip
    else:
        return cb_label, cb


def add_entry(frame, label="", text="", command=None, tooltip="", **kwargs):
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
        <Return>, '<Key-Return>', <KP_Enter>, and '<FocusOut>' (default: None).
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the entry (default: "" = no tooltip)
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
        entry.bind('<KP_Enter>', command)    # return of numeric keypad
        entry.bind('<FocusOut>', command)    # tab or click
    entry.pack(side=tk.LEFT)
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
    >>> self.rowcmap.pack(side=tk.TOP, fill=tk.X)
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
    label.pack(side=tk.LEFT)
    mb = ttk.Menubutton(frame, image=images[0], text=values[0],
                        compound=tk.LEFT)
    sb = tk.Menu(mb, tearoff=False)
    mb.config(menu=sb)
    for i, v in enumerate(values):
        sb.add_command(label=v, image=images[i], compound=tk.LEFT,
                       command=partial(command, v))
    mb.pack(side=tk.LEFT)
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
    >>> self.rowzxy.pack(side=tk.TOP, fill=tk.X)
    >>> self.xlbl, self.x = add_combobox(
    ...     self.rowzxy, label="x", values=columns, command=self.selected)
    """
    from functools import partial
    mb_label = tk.StringVar()
    mb_label.set(label)
    label = ttk.Label(frame, textvariable=mb_label)
    label.pack(side=tk.LEFT)
    mb = ttk.Menubutton(frame, text=values[0], compound=tk.LEFT)
    sb = tk.Menu(mb, tearoff=False)
    mb.config(menu=sb)
    for i, v in enumerate(values):
        sb.add_command(label=v, compound=tk.LEFT,
                       command=partial(command, v))
    mb.pack(side=tk.LEFT)
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
    >>> self.rowzxy.pack(side=tk.TOP, fill=tk.X)
    >>> self.xlbl, self.x = add_scale(
    ...     self.rowzxy, label="x", values=columns, command=self.selected)
    """
    s_label = tk.StringVar()
    s_label.set(label)
    label = ttk.Label(frame, textvariable=s_label)
    label.pack(side=tk.LEFT)
    s_val = tk.DoubleVar()
    s_val.set(ini)
    s = ttk.Scale(frame, variable=s_val, **kwargs)
    s.pack(side=tk.LEFT)
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
    >>> self.rowlev.pack(side=tk.TOP, fill=tk.X)
    >>> self.dlval, self.dl, self.dval, self.d = add_spinbox(
    ...     self.rowlev, label="dim", values=range(0,10),
    ...     command=self.spinned)
    """
    width = kwargs.pop('width', 1)
    sbl_val = tk.StringVar()
    sbl_val.set(label)
    sbl = ttk.Label(frame, textvariable=sbl_val)
    sbl.pack(side=tk.LEFT)
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
    sb.pack(side=tk.LEFT)
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
    >>> self.rowlev.pack(side=tk.TOP, fill=tk.X)
    >>> self.dlbl, self.dval, self.d = add_spinbox(
    ...     self.rowlev, label="dim", values=range(0,10),
    ...     command=self.spinned)
    >>> self.dtip = add_tooltip(self.d, 'Dimension')
    """
    ttip = tk.StringVar()
    ttip.set(tooltip)
    htip = Tooltip(frame, ttip)
    return ttip
