ncvue - A GUI to view netCDF files
==================================
..
  pandoc -f rst -o README.html -t html README.rst

A minimal GUI for a quick view of netCDF files. Aiming to be a drop-in
replacement for ncview_ and panoply_.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4459598.svg
   :target: https://doi.org/10.5281/zenodo.4459598
   :alt: Zenodo DOI

.. image:: https://badge.fury.io/py/ncvue.svg
   :target: https://badge.fury.io/py/ncvue
   :alt: PyPI version

.. image:: https://img.shields.io/conda/vn/conda-forge/ncvue.svg
   :target: https://anaconda.org/conda-forge/ncvue
   :alt: Conda version

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
   :target: https://github.com/mcuntz/ncvue/blob/master/LICENSE
   :alt: License

.. image:: https://github.com/mcuntz/ncvue/actions/workflows/main.yml/badge.svg?branch=main
   :target: https://github.com/mcuntz/ncvue/actions/workflows/main.yml
   :alt: Build status


About ncvue
-----------

``ncvue`` is a minimal GUI for a quick view of netCDF files. It is
aiming to be a drop-in replacement for ncview_ and panoply_, being
slightly more general than ncview targeting maps but providing
animations, zooming and panning capabilities unlike panoply. If
``ncvue`` is used with maps, it supports mostly structured grids, more
precisely the grids supported by cartopy_.

``ncvue`` is a Python script that can be called from within Python or
as a command line tool. It is not supposed to produce
publication-ready plots but rather provide a quick overview of the
netCDF file(s).

The complete documentation for ``ncvue`` is available from:

   https://mcuntz.github.io/ncvue/


Installation
------------

``ncvue`` is an application written in Python. If you have Python
installed, then the best is to install ``ncvue`` within the Python
universe. The easiest way to install ``ncvue`` is thence via `pip`:

.. code-block:: bash

   python -m pip install ncvue

or using Conda_:

.. code-block:: bash

   conda install -c conda-forge ncvue

``ncvue`` uses CustomTkinter_ if it is installed. CustomTkinter_ is
not on Conda_. ``ncvue`` can also use xarray_ to open netCDF files if
it is installed. If you also want to open multiple files with xarray
(`xarray.open_mfdataset`_), dask_ needs to be installed. One can
install CustomTkinter_ with pip on Conda_, which works well except for
Linux.

.. code-block:: bash

   python -m pip install dask xarray customtkinter

or:

.. code-block:: bash

   conda install -c conda-forge dask xarray
   python -m pip install customtkinter

Sometimes `tkinter` is not enabled in the system's Python version. One
has to do, for example, ``sudo apt install python3-tk`` on Linux or
``brew install python3 python-tk`` on macOS with Homebrew_.

We also provide standalone applications for macOS and Windows that
come with everything needed to run ``ncvue`` including Python:

  - macOS: `ncvue 6.4 Intel`_ and `ncvue 6.4 ARM`_ for Intel and ARM
    processors, resp., for macOS 15+ [Sequoia]
  - Windows: `ncvue 6.4`_

`ncvue > 5.0` is either for Intel processors or for Apple Silicon
(ARM) chips. The apps > v5.0 are notarized by Apple and might take a
short while on first opening.


Quick usage guide
-----------------

``ncvue`` can be run from the command line:

.. code-block:: bash

   ncvue
   ncvue netcdf_file.nc
   ncvue netcdf_file1.nc netcdf_file2.nc

A new netCDF file can be opened from within ``ncvue`` using the
buttons `Open File` or `Open xarray`.

One can also use xarray_ to open the netCDF file(s) using the command
line option `-x` or the button `Open xarray`:

.. code-block:: bash

   ncvue -x netcdf_file.nc
   ncvue -x netcdf_file1.nc netcdf_file2.nc

``ncvue`` either analyses the netCDF file itself looking for unlimited
dimensions, longitude, latitude, and treats datetime variables; or it
let's xarray_ do the job. The real difference between using or not
using xarray_ is in case of several input files: the files will be
opened as a single dataset with `xarray.open_mfdataset`_ if xarray_ is
used. The files will be combined by xarray's coordinates. This
requires dask_ to be installed. The files are treated like groups of a
single netCDF file if xarray is not used. This allows the comparison
of different files in scatter plots, for example.

One can set another missing value on the command line on top of the
`_FillValue` and `missing_value` attributes:

.. code-block:: bash

   ncvue -m '-9999' netcdf_file.nc

The command line option `-h` gives a quick usage message.

``ncvue`` can be called from within Python; the filenames have to be
given in a list then:

.. code-block:: python

   from ncvue import ncvue
   ncvue(['netcdf_file.nc'])

Note, ``ncvue`` uses the `TkAgg` backend of `matplotlib`. It must be
called before any other call to `matplotlib`. This also means that you
cannot launch it from `ipython --pylab`. It can be called from within
a standard `iPython`, though, or using `ipython --gui tk`.


General layout
^^^^^^^^^^^^^^

On opening, ``ncvue`` presents three panels for different plotting
types: Scatter or Line plots, Contour plots, and Maps. This is the
look in macOS light mode:

.. image:: https://mcuntz.github.io/ncvue/images/scatter_panel_light.png
   :width: 860 px
   :align: center
   :alt: Graphical documentation of ncvue layout

..
   :height: 462 px

All three panes are organised in this fashion: the plotting canvas,
the Matplotlib navigation toolbar and the pane, where one can choose
the plotting variables and dimensions, as well as plotting
options. You can always choose another panel on top, and open another,
identical window for the same netCDF file(s) with the button "New Window"
on the top right.

If CustomTkinter_ is installed, then the general layout looks like:

.. image:: https://mcuntz.github.io/ncvue/images/scatter_panel_light_ctk_screenshot.png
   :width: 507 px
   :align: center
   :alt: ncvue layout with CustomTkinter in light mode

or in dark mode:

.. image:: https://mcuntz.github.io/ncvue/images/scatter_panel_dark_ctk_screenshot.png
   :width: 507 px
   :align: center
   :alt: ncvue layout with CustomTkinter in dark mode

CustomTkinter_ does not work well with Conda_.


Map panel
^^^^^^^^^

If ``ncvue`` detects latitude and longitude variables with a size
greater than 1, it opens the Map panel by default. This is the Map
panel on macOS, describing all buttons, sliders, entry boxes,
spinboxes, and menus:

.. image:: https://mcuntz.github.io/ncvue/images/map_panel_light.png
   :width: 860 px
   :align: center
   :alt: Graphical documentation of Map panel

If it happens that the detection of latitudes and longitudes did not
work automatically, you can choose the correct variables manually. Or
you might also leave the latitudes and longitudes empty, which uses
then the indexes, and one can hence display the matrix within the
netCDF file(s). You might want to switch off the coastlines in this
case.

You might want to switch off the automatically detected "global"
option sometimes if your data is on a rotated grid, or if you want to
exclude some regions such as below minus -60 °S.

All dimensions can be set from 0 to the size of the dimension-1, to
"all", or to any of the arithmetic operators "mean", "std" (standard
deviation), "min", "max", "ptp" (point-to-point amplitude,
i.e. max-min), "sum", "median", "var" (variance).

Be aware that the underlying cartopy/matplotlib may (or may not) need
a long time to plot the data (with the pseudocolor 'mesh' option) if
you change the central longitude of the projection to anything else
than the central longitude of your data, which is automatically
detected if "central lon" is set to None. Setting "central lon" to the
central longitude of the input data normally eliminates the problem.


Scatter/Line panel
^^^^^^^^^^^^^^^^^^

If ``ncvue`` does not detect latitude and longitude variables with a
size greater than 1, it opens the Scatter/Line panel by default. This
is the Scatter/Line panel in macOS dark mode (Aqua look), describing
all buttons, sliders, entry boxes, spinboxes, and menus:

.. image:: https://mcuntz.github.io/ncvue/images/scatter_panel_dark.png
   :width: 860 px
   :align: center
   :alt: Graphical documentation of Scatter/Line panel

The default plot is a line plot with solid lines (line style 'ls' is
'-'). One can set line style 'ls' to None and set a marker symbol
(marker), e.g. 'o' for circles, to get a scatter plot. A large variety
of line styles, marker symbols, and color notations are
supported. They are listed in the tooltips that appear if you hove
longer than 0.5 s above an entry field.

``ncvue`` builds automatically a `datetime` variable from the time
axis. This is correctly interpreted by the underlying matplotlib_ also
when zooming or panning the axes. But it is also much slower than
using the index. Leaving `x` empty uses the index for the x-axis and
is very fast. Plotting a line plot with 52608 time points takes about
2.2 s on my MacBook Pro using the `datetime` variable and about 0.3 s
using the index (i.e. empty x-variable). This is especially true if
one plots multiple lines with 'all' entries from a specific
dimension. Plotting all 10 depths of soil water content for the 52608
time points, as in the example below, takes also about 0.3 s if using
the index as x-variable but more than 11.1 s when using the `datetime`
variable.

.. image:: https://mcuntz.github.io/ncvue/images/scatter_panel_dark_multiline_screenshot.png
   :width: 507 px
   :align: center
   :alt: Example of multiple lines in the Scatter/Line panel


Contour panel
^^^^^^^^^^^^^

The last panel provide by ``ncvue`` draws contour plots. This is the
Contour panel in macOS dark mode, describing all buttons, sliders,
entry boxes, spinboxes, and menus:

.. image:: https://mcuntz.github.io/ncvue/images/contour_panel_dark.png
   :width: 860 px
   :align: center
   :alt: Graphical documentation of Contour panel

This produces also either pseudocolor plots ('mesh' ticked) or filled
contour plots ('mesh' unticked) just as the Map panel but without any
map projection.


License
-------

``ncvue`` is distributed under the MIT License. See the LICENSE_ file
for details.

Copyright (c) 2020-2025 Matthias Cuntz

``ncvue`` uses CustomTkinter_ if installed. Otherwise it uses the
Azure_ 2.0 theme by rdbende_ on Linux and Windows.

Standalone applications are produced with `cx_Freeze`_, currently
maintained by `Marcelo Duarte`_.

The project structure of ``ncvue`` was very originally based on a
template_ provided by `Sebastian Müller`_ but has evolved
considerably since.

Different netCDF test files were provided by `Juliane Mai`_.

.. _Azure: https://github.com/rdbende/Azure-ttk-theme
.. _cartopy: https://scitools.org.uk/cartopy/docs/latest/
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _CustomTkinter: https://customtkinter.tomschimansky.com/
.. _cx_Freeze: https://cx-freeze.readthedocs.io/en/latest/
.. _Marcelo Duarte: https://github.com/marcelotduarte
.. _Homebrew: https://brew.sh
.. _LICENSE: https://github.com/mcuntz/ncvue/blob/main/LICENSE
.. _matplotlib: https://matplotlib.org/
.. _Juliane Mai: https://github.com/julemai
.. _Sebastian Müller: https://github.com/MuellerSeb
.. _dask: https://docs.dask.org/
.. _ncview: http://meteora.ucsd.edu/~pierce/ncview_home_page.html
.. _ncvue 6.4 ARM: https://www.macu.de/extra/ncvue-6.4-arm64.dmg
.. _ncvue 6.4 Intel: https://www.macu.de/extra/ncvue-6.4-intel.dmg
.. _ncvue 6.4: https://www.macu.de/extra/ncvue-6.4-win64.msi
.. _panoply: https://www.giss.nasa.gov/tools/panoply/
.. _rdbende: https://github.com/rdbende
.. _template: https://github.com/MuellerSeb/template
.. _xarray: https://docs.xarray.dev/
.. _xarray.open_mfdataset: https://docs.xarray.dev/en/stable/generated/xarray.open_mfdataset.html
