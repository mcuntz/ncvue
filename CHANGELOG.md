# Changelog

All notable changes after its initial development up to November 2020 (v1.0)
are documented in this file.

### v1.4 (Dec 2020)
    - Use unlimited dimension instead of first dimension in Scatter and Contour
      panels as default for 'all'.
    - Use slice function rather than numpy.take to extract slices of arrays.
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
    - Open new window without helper class ncvWin to avoid circular import when
      modularised.

### v1.0 (Nov 2020)
    - Initial release on PyPI.
    - Scatter and Contour plot panels.
