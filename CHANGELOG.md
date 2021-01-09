# Changelog

All notable changes after its initial development up to November 2020 (v1.0)
are documented in this file.

### v2.1 (Jan 2021)
    - Variable names are now separated by SEPCHAR=chr(6) because netcdf
      variable names can have spaces, parentheses, brackets, etc.
    - Map panel is only chosen first if either lon or lat have more than one
      grid cell.
    - Central longitude is now calculated in 0-360 range but set in -180 to 180
      range. Seems to be more stable for grids that are missing for example the
      southern hemisphere.
    - Catch a few errors if variable is for example a simple string (e.g.
      vegetation type, basin name or similar).

### v2.0 (Jan 2021)
    - Added Map panel.
    - Assure 2-digit month and day and 4 digit year in time unit.
    - Added return on numeric keyboard to key bindings.
    - Changed layout so that dimensions are below variable selection
      spinboxes.
    - Transpose array by default in Contour panel so that first dimension
      (time) is on x-axis (col) because contourf/pcolormesh use (row,col).
    - Common arithmetic operations on axes: mean, std, min, max, ptp, sum,
      median, var.
    - General get_slice function for x, y, y2, and z.
    - Only activate valid dimensions for chosen variable, disable others.
    - Axis labels are now the long_name attribute then the standard_name
      attribute and only if both are missing the variable name.

### v1.4 (Dec 2020)
    - Colorbar menu with images of colorbars. 
    - Use unlimited dimension instead of first dimension in Scatter and Contour
      panels as default for 'all'.
    - Use slice function rather than numpy.take to extract slices of arrays,
      i.e. reads only the current slice from disk.
    - Enhanced documentation with automatic API generation.

### v1.3 (Dec 2020)
    - Use zmin/zmax to fix colorbar for different dimensions in Contour panel.
    - Optional grid lines in Contour panel.
    - Possibility to invert x-axis in Scatter/Line panel.
    - Rename Scatter to Scatter/Line.
    - Use build instead of cibuildwheel to make pure Python wheels.

### v1.2 (Dec 2020)
    - Put common methods in ncvmethods (first arg is self).
    - Make lists of labels, spinboxes and values of dimensions
      rather than exhaustive lists of if/elif statements.

### v1.1 (Dec 2020)
    - Modularised ncvue to have utilities and different panels in individual
      files.
    - Open new window without helper class ncvWin to avoid circular import
      when modularised.

### v1.0 (Nov 2020)
    - Initial release on PyPI.
    - Scatter and Contour plot panels.
