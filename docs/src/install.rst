Installation
============

The easiest way to install ``ncvue`` is via `pip` if you have cartopy_
installed already:

.. code-block:: bash

   pip install ncvue

`Cartopy` can, however, be more elaborate to install_. The easiest way to install
`Cartopy` is by Conda_ and then installing ``ncvue`` by `pip`:

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

You would need an Anaconda_ or Miniconda_ environment for this, of course.

Support of `conda-forge` will be added in one of the next minor releases of ``ncvue``.

Building from source
--------------------

If you want to install ``ncvue`` from source, you first have to install the
dependencies listed below and you can then install ``ncvue`` using `pip`:

.. code-block:: bash

   pip install ncvue

The latest version of ``ncvue`` can be installed from source:

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   pip install .

You can use the `\-\-user` option with `pip install` if you do not have proper
privileges to install Python packages (and you are not using a virtual
environment).

You can also simply clone the repository and add it to your `PYTHONPATH`. In
this case, add the `bin` directory to your `PATH` as well (bash/zsh example):

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   export PYTHONPATH=${PYTHONPATH}:${PWD}
   export PATH=${PATH}:${PWD}/bin

Dependencies
------------

``ncvue`` uses the packages :mod:`numpy`, :mod:`netCDF4`, :mod:`matplotlib`, and
cartopy_. The first three packages are easily installed with `pip` from
PyPI:

.. code-block:: bash

   pip install numpy netcdf4 matplotlib

`Cartopy` can, however, be more elaborate to install_. It basically uses Python
wrappers to C++/C-libraries that must be installed first.

On **Windows**, one can use either the unofficial binaries of Christoph Gohlke
(https://www.lfd.uci.edu/~gohlke/pythonlibs/) or install `cartopy` with Conda_
from `conda-forge` (see above).

On **macOS**, one can use homebrew_ to install the Cartographic Projections
Library `proj` and the Geometry Engine `geos`:

.. code-block:: bash

   brew install proj geos

On Ubuntu **Linux**, this can be done with `apt-get`:

.. code-block:: bash

   sudo apt-get install libproj-dev proj-data proj-bin
   sudo apt-get install libgeos++-dev

The remaining Python packages can then be installed with `pip` (from Cartopy install_):

.. code-block:: bash

   pip install --upgrade cython pyshp six
   # shapely needs to be built from source to link to geos. If it is already
   # installed, uninstall it by: pip uninstall shapely
   pip install shapely --no-binary shapely

I also recommend to install the fast kd-tree implementation `pykdtree`:

.. code-block:: bash

   pip install pykdtree

Now, eventually, you can install `cartopy` with `pip`:

.. code-block:: bash

   pip install cartopy

``ncvue`` uses the "themed Tk" ("ttk") functionality of Tk 8.5. It hence needs
Python 2.7 or Python 3.1 or later. Linux users might need to update their (very
old) Tk installations.

Summary
-------

To install ``ncvue`` on **Windows**, install Anaconda_ and the binary of `Cartopy` of Christoph Gohlke
(https://www.lfd.uci.edu/~gohlke/pythonlibs/). Then install ``ncvue`` via pip:

.. code-block:: bash

   pip.exe install ncvue

To install ``ncvue`` on **macOS**, use Anaconda_ and install ``ncvue`` with `pip`

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

or install from source:

.. code-block:: bash

   pip install numpy netcdf4 matplotlib
   # uncomment next line if homebrew is not installed
   # /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
   brew install proj geos
   pip install --upgrade cython pyshp six
   # uncomment next line if shapely is already installed
   # pip uninstall shapely
   pip install shapely --no-binary shapely
   pip install pykdtree
   pip install cartopy
   pip install ncvue

To install ``ncvue`` on **Linux**, use Anaconda_ and install ``ncvue`` with `pip`

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

or install from source:

.. code-block:: bash

   pip install numpy netcdf4 matplotlib
   sudo apt-get install libproj-dev proj-data proj-bin
   sudo apt-get install libgeos++-dev
   pip install --upgrade cython pyshp six
   # uncomment next line if shapely is already installed
   # pip uninstall shapely
   pip install shapely --no-binary shapely
   pip install pykdtree
   pip install cartopy
   pip install ncvue

.. _Anaconda: https://www.anaconda.com/products/individual
.. _cartopy: https://scitools.org.uk/cartopy/docs/latest/
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _homebrew: https://brew.sh/
.. _install: https://scitools.org.uk/cartopy/docs/latest/installing.html
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _netcdf4: https://unidata.github.io/netcdf4-python/netCDF4/index.html
