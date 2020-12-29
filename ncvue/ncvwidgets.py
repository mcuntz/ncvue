#!/usr/bin/env python
"""
Widget functions for ncvue.

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


__all__ = ['add_checkbutton', 'add_combobox', 'add_entry',
           'add_imagemenu', 'add_spinbox']


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


def add_imagemenu(frame, label="", values=[], images=[], command=None,
                  **kwargs):
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
    **kwargs : option=value pairs, optional
        All other options will be passed to the main ttk.Menubutton

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
    estr  = 'Same number of values and images needed for add_imagemenu.'
    estr += ' values (' + str(len(values)) + '): ' + str(values)
    estr += ', images (' + str(len(images)) + '): ' + str(images)
    assert len(values) == len(images), estr
    width = kwargs.pop('width', 25)
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
    return mb_label, mb


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
