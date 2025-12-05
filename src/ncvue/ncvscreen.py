#!/usr/bin/env python
"""
ncvscreen class for screen size and resolution

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2025- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   ncvScreen

History
   * Written Nov 2025 by Matthias Cuntz (mc (at) macu (dot) de)
   * Add get/set_window_geometry from idle, Nov 2025, Matthias Cuntz
   * Get size from fullscreen window to deal with multiple monitors,
     Nov 2025, Matthias Cuntz

"""
import platform
import re
import tkinter
try:
    import customtkinter
    ihavectk = True
except ModuleNotFoundError:
    ihavectk = False


__all__ = ['ncvScreen']


class ncvScreen(object):
    """
    Set window sizes and resolution

    """

    def __init__(self, top, **kwargs):

        self.ihavectk = ihavectk
        self.os = platform.system()  # Windows, Darwin, Linux

        # Get the monitor's size
        # if (self.os == 'Darwin') or (self.os == 'Windows'):
        if self.os == 'Darwin':
            # total width of all monitors if not on macOS
            self.width = top.winfo_screenwidth()
            self.height = top.winfo_screenheight()  # includes title bar
        elif self.os == 'Windows':
            wm_state = top.wm_state()
            top.wm_state('zoomed')  # make fullscreen
            self.width, self.height, x, y = self.get_window_geometry(top)
            top.wm_state(wm_state)
            top.update()
        else:
            wm_state = top.wm_state()
            try:
                top.wm_state('zoomed')  # make fullscreen
                self.width, self.height, x, y = self.get_window_geometry(top)
            except tkinter.TclError:
                self.width = min(top.winfo_screenwidth(), 1618)
                self.height = min(top.winfo_screenheight(), 1000)
                # if ihavectk:
                #     top.wm_attributes('-fullscreen', True)
                #     self.width, self.height, x, y = self.get_window_geometry(top)
                # else:
                #     self.width, self.height = top.maxsize()
            top.wm_state(wm_state)
            top.update()
        # print('winfo', self.width, self.height,
        #       top.winfo_screenwidth(), top.winfo_screenheight())

        # result of top.winfo_fpixels('1i') on development screen
        self.dpi_default = 72.
        self.dpi = top.winfo_fpixels('1i')

    #
    # DPI scaling
    #
    def scale(self, x):
        '''
        Scales *x* by current dpi over dpi of development screen

        '''
        return int(x * self.dpi / self.dpi_default)

    #
    # Window size getter and setter (from idle)
    #
    def get_window_geometry(self, top):
        geom = top.wm_geometry()
        m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        return tuple(map(int, m.groups()))


    def set_window_geometry(self, top, geometry):
        top.wm_geometry("{:d}x{:d}+{:d}+{:d}".format(*geometry))

    #
    # Window sizes
    #
    def standard_window_size(self):
        '''
        Set xsize, ysize, xoffset, yoffset of standard window

        '''
        if self.height < 800:
            ysize = self.height
        else:
            ysize = max(4 * self.height // 5, 800)
        yoffset = 0

        if self.width < 1000:
            xsize = self.width
            xoffset = 0
        else:
            xsize = max(2 * self.width // 5, 1000)
            xoffset = self.width // 5
            if ((xsize + xoffset) > self.width) or (xsize == 1000):
                xoffset = (self.width - xsize) // 2

        # ysize = 1200
        # xsize = int(1.5 * ysize)
        return xsize, ysize, xoffset, yoffset

    def secondary_window_size(self):
        '''
        Set xsize, ysize, xoffset, yoffset of secondary window

        '''
        xsize, ysize, xoffset, yoffset = self.standard_window_size()
        
        xoffset += 50
        if (xsize + xoffset) > self.width:
            xoffset = self.width - xsize

        return xsize, ysize, xoffset, yoffset
