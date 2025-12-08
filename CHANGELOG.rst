Changelog
---------

v6.4.1 (Dec 2025)
  - Finetuned size without CustomTkinter.
  - Set window size on Linux systems that do not support
    state('zoomed') on tkinter windows.

v6.4 (Dec 2025)
   - Draw canvas as last element so that UI controls are displayed as
     long as possible.
   - Get size from fullscreen window to deal with multiple monitors.

v6.3 (Nov 2025)
   - Deduce datetime in xlim and ylim in Scatter panel.

v6.2 (Nov 2025)
   - Use screen size to determine window sizes.
   - Bugfix for setting axes limits.
   - Add xlim, ylim, and y2lim options.

v6.1 (Mar 2025)
   - Windows installer.
   - Correct logic to check for new file.
   - macOS installers with or without CustomTkinter on Intel and ARM64.

v6.0 (Mar 2025)
   - Set delay for tooltips from 1 s to 0.5 s.
   - Use exclusively `add_*` for widget creation.
   - Remove delay in `ncvmap`.
   - Add `analyse_netcdf_xarray`.
   - New utility functions `xzip_dim_name_length`, `get_standard_name`,
     and `get_units` used in `ncvmethods`.
   - Add xarray support for reading files.
   - Use f-strings for most string operations.
   - New widgets `add_button` and `add_label`.
   - Increased number of digits in coordinate formatters.

v5.1 (Dec 2024)
   - Use ncvue-specific theme with customtkinter.
   - Update images for new matplotlib cmaps.
   - Bugfix: file not updated in all tabs when opened with file dialog
     in one tab with CustomTkinter.
   - Bugfix: dimensions not shown when file opened with file dialog.
   - Updated documentation.

v5.0 (Dec 2024)
   - Use CustomTkinter if installed.
   - Add Quit button.
   - Correct datetime formatting in coordinate printing.
   - Move from token to trusted publisher on PyPI.

v4.4.3 (Jul 2024)
   - Use `draw_idle` instead of `draw` in map update method for
     faster animation.
   - Change formatting of file string for multiple files.

v4.4.2 (Jul 2024)
   - Use `matplotlib.colormaps[name]` instead of
     `matplotlib.colormaps.get_cmap(name)` to work with
     matplotlib >= v3.9.0.

v4.4.1 (Feb 2024)
   - Move themes and images back to src/ncvue.

v4.4 (Feb 2024)
   - Added borders, rivers, and lakes checkbuttons in map.
   - Bugfix: formatted string used wrong data type in `analyse_netcdf`.
   - Move themes and images directories from src/ncvue to src directory.

v4.3 (Jan 2024)
   - Added conda and continuous integration badges.
   - Allow multiple netcdf files.
   - Squeeze output in `get_slice_miss` only if more than 1 dimension.

v4.2 (Jan 2024)
   - Updated versions of github actions.
   - Changed to sphinx_book_theme for documentation.
   - Use local copy of `tooltip.py` from idle.
   - Allow groups in netcdf files.
   - Made ``ncvue`` work with newer matplotlib versions, updating
     colormaps and using matplotlib.pyplot.style 'seaborn-v0_8-dark'.
   - Made ``ncvue`` work with newer Tcl/Tk versions (ttk.Style.theme_use).

v4.1.2 (Jun 2022)
   - Made ``ncvue`` a gui_script entry_point, so it can be called by
     `python -m ncvue`.
   - Bumped minimum Python version to 3.7 because of proj4.

v4.1.1 (Nov 2021)
   - Added package_data to `setup.cfg`.

v4.1 (Nov 2021)
   - Add final routines `add_cyclic` and `has_cyclic` committed to cartopy
     v0.20.1.
   - Added `ncvue` to conda-forge.
   - Added `scripts` in [options] section in `setup.cfg`.

v4.0 (Oct 2021)
   - Move to new pip structure using `pyproject.toml`.
   - Versioning with `setuptools_scm`.
   - Move to src directory structure.
   - Move to Github actions.

v3.8 (Oct 2021)
   - Work with files without an unlimited (time) dimension.
   - Removed bug in detection of lon/lat.
   - Identify lon/lat also by axis attributes x/y or X/Y.
   - Do not default the unlimited dimension to 'all' if no lon/lat were found.

v3.7 (Sep 2021)
   - Use Azure theme v2.0 on Linux and Sun Valley theme v1.0 on Windows from
     rdbende (https://github.com/rdbende).
   - Does not provide standalone package (no installer) on macOS with Apple
     Silicon (M1) chip anymore (no paid Apple Developer ID).

v3.6 (Jun 2021)
   - Separate variables and dimensions by space again but deal with space in
     variable names.
   - Use cx_Freeze to make standalone apps.
   - Font size 13 on Windows in plot panel.

v3.5.1 (Jun 2021)
   - Set labelling of second y-axis to the right explicitly, which needs to be
     done with newer Matplotlib versions.

v3.5 (Jun 2021)
   - Uses different themes on different operating systems.
   - New add_cyclic function used as submitted to Cartopy.

v3.4 (May 2021)
   - Works in ipython and jupyter notebooks. Adapted documentation accordingly.
   - Added license to documentation.
   - Change separator character to unit separator (ASCII 31).
   - Print correct coordinates and values on plotting window.
   - Set time axis to numpy's datetime64 format.
   - Moved from Matplotlib style `seaborn-darkgrid` to `seaborn-dark`.
   - Grid is drawn by hand in contour plot. Set automatic grid to False:
     `self.axes.grid(False)`.

v3.3.1 (Feb 2021)
   - Better installation instructions for all platforms.
   - Dropped claim of Python 2 support, which was not given.

v3.3 (Feb 2021)
   - Main window disappears if closed even if called from within Python.
   - Added Windows Installer for ncvue standalone program.
   - Added standalone app for macOS.

v3.2 (Jan 2021)
   - Added 'Open File' button to switch between files.
   - Separated Tk() and Toplevel() to communicate via Tk() between windows.
   - Externalise analysis of netcdf file for open file button.
   - Allow finding images path in standalone applications using pyinstaller.

v3.1 (Jan 2021)
   - Include `ncvue/images/*.png` in PyPI wheel.

v3.0 (Jan 2021)
   - Moved from ReadTheDocs to Github Pages for documentation.
   - Added tooltips to all selectors, entries, menus.
   - Variable names are now separated by SEPCHAR=chr(6) because netcdf variable
     names can have spaces, parentheses, brackets, etc.
   - Map panel is only chosen first if either lon or lat have more than one
     grid cell.
   - Central longitude is now calculated in 0-360 range but set in -180 to 180
     range. Seems to be more stable for grids that are missing for example the
     southern hemisphere.
   - Catch a few errors if variable is for example a simple string (e.g.
     vegetation type, basin name or similar).

v2.0 (Jan 2021)
   - Added Map panel.
   - Assure 2-digit month and day and 4 digit year in time unit.
   - Added return on numeric keyboard to key bindings.
   - Changed layout so that dimensions are below variable selection spinboxes.
   - Transpose array by default in Contour panel so that first dimension (time)
     is on x-axis (col) because contourf/pcolormesh use (row,col).
   - Common arithmetic operations on axes: mean, std, min, max, ptp, sum,
     median, var.
   - General get_slice function for x, y, y2, and z.
   - Only activate valid dimensions for chosen variable, disable others.
   - Axis labels are now the long_name attribute then the standard_name
     attribute and only if both are missing the variable name.

v1.4 (Dec 2020)
   - Colorbar menu with images of colorbars.
   - Use unlimited dimension instead of first dimension in Scatter and Contour
     panels as default for 'all'.
   - Use slice function rather than numpy.take to extract slices of arrays,
     i.e. reads only the current slice from disk.
   - Enhanced documentation with automatic API generation.

v1.3 (Dec 2020)
   - Use zmin/zmax to fix colorbar for different dimensions in Contour panel.
   - Optional grid lines in Contour panel.
   - Possibility to invert x-axis in Scatter/Line panel.
   - Rename Scatter to Scatter/Line.
   - Use build instead of cibuildwheel to make pure Python wheels.

v1.2 (Dec 2020)
   - Put common methods in ncvmethods (first arg is self).
   - Make lists of labels, spinboxes and values of dimensions rather than
     exhaustive lists of if/elif statements.

v1.1 (Dec 2020)
   - Modularised ncvue to have utilities and different panels in individual
     files.
   - Open new window without helper class ncvWin to avoid circular import when
     modularised.

v1.0 (Nov 2020)
   - Initial release on Github.
   - Scatter and Contour plot panels.
