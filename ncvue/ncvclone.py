#!/usr/bin/env python
"""
Clone window ncvMain.

Written  Matthias Cuntz, Nov-Dec 2020
"""
from __future__ import absolute_import, division, print_function
import tkinter as tk


__all__ = ['clone_ncvmain']


def clone_ncvmain(widget, fi, miss):
    # parent = widget.nametowidget(widget.winfo_parent())
    if widget.name != 'ncvMain':
        print('clone_ncvmain failed. Widget should be ncvMain.')
        print('widget.name is: ', widget.name)
        import sys
        sys.exit()

    self = tk.Toplevel()
    self.name = 'ncvClone'
    self.title("Secondary ncvue window")
    self.geometry('1000x800')
    self.miss = miss

    # https://stackoverflow.com/questions/46505982/is-there-a-way-to-clone-a-tkinter-widget
    cls = widget.__class__
    clone = cls(fi, master=self, miss=miss)
    for key in widget.configure():
        if key != 'class':
            clone.configure({key: widget.cget(key)})

    return clone
