Installation
============

``ncvue`` is an application written in Python. If you have Python installed,
 then the best is to install ``ncvue`` within the Python universe. The easiest
 way to install ``ncvue`` is thence via `pip` if you have cartopy_ installed
 already:

.. code-block:: bash

   pip install ncvue

`Cartopy` can, however, be more elaborate to install_. The easiest way to
install `Cartopy` is by using Conda_ and then installing ``ncvue`` by `pip`.
After installing, for example, Miniconda_:

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

or using directly the community-led Miniforge_:

.. code-block:: bash

   conda install cartopy
   pip install ncvue

Support of `conda-forge` will be added in one of the next minor releases of ``ncvue``.

Binary distribution
-------------------

We provide a macOS app_, which should work from macOS 10.13 (High
Sierra) onward. It is, however, only tested on macOS 10.15 (Catalina). Drop me
a message if it does not work on newer operating systems.

A Windows application is in the making ;-)

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

You probably also have to run the Command prompt or the Powershell Prompt as
Administrator (Right click > More > Run as administrator) on Windows to install
Python packages.

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

   sudo apt-get install libproj-dev proj-data proj-bin libgeos++-dev

The remaining Python packages can then be installed with `pip` (from Cartopy install_):

.. code-block:: bash

   pip install --upgrade cython pyshp six scipy
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


It is also possible that your Python version installed with pyenv_ might clash
with Apple's Tcl/Tk library. This gives in the best case a deprecation warning
like:

.. code-block::

   DEPRECATION WARNING: The system version of Tk is deprecated and
   may be removed in a future release. Please don't rely on it.
   Set TK_SILENCE_DEPRECATION=1 to suppress this warning.

You have to install `tcl-tk` from homebrew_ first and then reinstall Python
(example with Python version 3.8.3):

.. code-block:: bash

   brew install tcl-tk
   pyenv uninstall 3.8.3
   pyenv rehash
   env PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/usr/local/opt/tcl-tk/include' \
       --with-tcltk-libs='-L/usr/local/opt/tcl-tk/lib -ltcl8.6 -ltk8.6' \
       --enable-framework" pyenv install 3.8.3
   pyenv rehash

Note that `tcl-tk` is keg-only in homebrew_. `env` in the command above allows
using the homebrew version with Python while not interfering with the macOS
provided Tcl/Tk installation.


Summary
-------

Windows
^^^^^^^

To install ``ncvue`` on Windows, install Anaconda_, run the Anaconda Prompt as
administrator, install cartopy_ from conda_forge and ``ncvue`` via pip:

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

macOS
^^^^^

To install ``ncvue`` on macOS, either use the macOS app_, or use Anaconda_,
install cartopy_ from conda_forge and install ``ncvue`` with `pip`:

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

or install everything from source:

.. code-block:: bash

   pip install numpy netcdf4 matplotlib
   # uncomment next line if homebrew is not installed
   # /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
   brew install proj geos
   pip install --upgrade cython pyshp six scipy
   # uncomment next line if shapely is already installed
   # pip uninstall shapely
   pip install shapely --no-binary shapely
   pip install pykdtree
   pip install cartopy
   pip install ncvue

Linux
^^^^^

To install ``ncvue`` on Linux, either use Anaconda_, install cartopy_ from
conda_forge and install ``ncvue`` with `pip`:

.. code-block:: bash

   conda install -c conda-forge cartopy
   conda install netcdf4
   pip install ncvue

or install everything from source:

.. code-block:: bash

   pip install numpy netcdf4 matplotlib
   sudo apt-get install libproj-dev proj-data proj-bin
   sudo apt-get install libgeos++-dev
   pip install --upgrade cython pyshp six scipy
   # uncomment next line if shapely is already installed
   # pip uninstall shapely
   pip install shapely --no-binary shapely
   pip install pykdtree
   pip install cartopy
   pip install ncvue

.. _Anaconda: https://www.anaconda.com/products/individual
.. _app: http://www.macu.de/extra/ncvue.dmg
.. _cartopy: https://scitools.org.uk/cartopy/docs/latest/
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _homebrew: https://brew.sh/
.. _install: https://scitools.org.uk/cartopy/docs/latest/installing.html
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Miniforge: https://github.com/conda-forge/miniforge
.. _netcdf4: https://unidata.github.io/netcdf4-python/netCDF4/index.html
.. _pyenv: https://github.com/pyenv/pyenv
