Installation
============

``ncvue`` is an application written in Python. If you have Python
installed, then the best is to install ``ncvue`` within the Python
universe. The easiest way to install ``ncvue`` is thence via `pip` if
you have cartopy_ already installed:

.. code-block:: bash

   pip install ncvue

`Cartopy` can, however, be more elaborate to install_. The easiest way
to install `Cartopy` or directly ``ncvue`` is by using Conda_. After
having installed, for example, Miniconda_:

.. code-block:: bash

   conda install -c conda-forge ncvue

Binary distributions
--------------------

We also provide standalone macOS and Windows applications that come
with everything needed to run ``ncvue`` including Python:

- `macOS app`_ (macOS > 10.13, High Sierra on Intel)
- `Windows executable`_ (Windows 10)

The macOS app should work from macOS 10.13 (High Sierra) onward on
Intel processors. There is no standalone application for macOS on
Apple Silicon (M1) chips because I do not have a paid Apple
Developer ID. The installation via `pip` works, though.

A dialog box might pop up on macOS saying that the ``ncvue.app`` is
from an unidentified developer. This is because ``ncvue`` is an
open-source software.  Depending on the macOS version, it offers to
open it anyway. In later versions of macOS, this option is only given
if you right-click (or control-click) on the ``ncvue.app`` and choose
`Open`. You only have to do this once. It will open like any other
application the next times.

Building from source
--------------------

If you want to install ``ncvue`` from source, you first have to
install the dependencies listed below and you can then install
``ncvue`` using `pip`:

.. code-block:: bash

   pip install ncvue

The latest version of ``ncvue`` can be installed from source:

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   pip install .

You can use the `\-\-user` option with `pip install` if you do not
have proper privileges to install Python packages (and you are not
using a virtual environment).

You probably also have to run the Command prompt or the Powershell
Prompt as Administrator (Right click > More > Run as administrator) on
Windows to install Python packages.

You can also simply clone the repository and add it to your
`PYTHONPATH`. In this case, add the `bin` directory to your `PATH` as
well (`bash`/`zsh` example):

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   export PYTHONPATH=${PYTHONPATH}:${PWD}
   export PATH=${PATH}:${PWD}/bin

Dependencies
------------

``ncvue`` uses the packages :mod:`numpy`, :mod:`netCDF4`,
:mod:`matplotlib`, and cartopy_. The first three packages are easily
installed with `pip` from PyPI. `Cartopy` can, however, be more
elaborate to install_. It basically uses Python wrappers to
C++/C-libraries that must be installed first.

Windows
^^^^^^^

On **Windows**, one can install `cartopy` with Conda_ from
`conda-forge`. We recommend then to install also all other
dependencies for ``ncvue``:

.. code-block:: bash

   conda install -c conda-forge ncvue

macOS
^^^^^

On **macOS**, one can use exactly the same procedure with Conda_ as
for Windows (see above). Or one can use homebrew_ to install the
Cartographic Projections Library `proj` and the Geometry Engine
`geos`:

.. code-block:: bash

   # uncomment next line if homebrew is not installed
   # /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install geos
   brew install proj

``ncvue`` and its prerequisites are then installed via pip (from cartopy install_):

.. code-block:: bash

   # HOMEBREW_PREFIX environment variable should be set after installing homebrew.
   # Make sure it is /usr/local or /opt/homebrew.
   if [[ "$(uname -m)" == "arm64" ]] ; then
       export OPENBLAS="$(brew --prefix openblas)"
       export HDF5_DIR="$(brew --prefix hdf5)"
       export GEOS_DIR="$(brew --prefix geos)"
       export GEOS_CONFIG="$(brew --prefix geos)/bin/geos-config"
   fi
   pyenv virtualenv 3.12.1 pystd
   pyenv rehash
   pyenv global pystd
   pyenv rehash
   pip install numpy scipy matplotlib netcdf4 pykdtree
   pip install --upgrade cython pyshp six
   # shapely needs to be built from source to link to geos.
   # Uninstall it if already installed
   [[ -z $(python -m pip freeze | grep shapely) ]] && \
       python -m pip uninstall -y shapely
   python -m pip install shapely --no-binary shapely
   # gdal needs to know the installed gdal version
   python -m pip install GDAL==$(gdal-config --version) \
       --global-option=build_ext --global-option="-I${HOMEBREW_PREFIX}/include"
   python -m pip install cartopy

One can then install ``ncvue``, eventually:

.. code-block:: bash

   pip install ncvue

It is possible that your Python version installed with pyenv_ might
clash with Apple's Tcl/Tk library. This gives in the best case a
deprecation warning like:

.. code-block::

   DEPRECATION WARNING: The system version of Tk is deprecated and
   may be removed in a future release. Please don't rely on it.
   Set TK_SILENCE_DEPRECATION=1 to suppress this warning.

You have to install `tcl-tk` from homebrew_ first and then reinstall Python
(example with Python version 3.12.1):

.. code-block:: bash

   brew install tcl-tk
   pyenv uninstall 3.12.1
   pyenv rehash
   env PYTHON_CONFIGURE_OPTS=" \
       --with-tcltk-includes='-I${HOMEBREW_PREFIX}/opt/tcl-tk/include' \
       --with-tcltk-libs='-L${HOMEBREW_PREFIX}/opt/tcl-tk/lib -ltcl8.6 -ltk8.6' \
       --enable-optimizations --enable-framework=${HOME}/Library/Frameworks" \
       CFLAGS="-I$(brew --prefix xz)/include" \
       LDFLAGS="-L$(brew --prefix xz)/lib" \
       PKG_CONFIG_PATH="$(brew --prefix xz)/lib/pkgconfig" \
       pyenv install 3.12.1
   pyenv rehash

Note that `tcl-tk` is keg-only in homebrew_. `env` in the command
above allows using the homebrew version with Python while not
interfering with the macOS provided Tcl/Tk installation.

Linux
^^^^^

On **Linux**, one can also use exactly the same procedure with Conda_
as for Windows (see above):

Instead of conda, one can also install the C++/C-libraries with `apt`
or `apt-get` (Ubuntu):

.. code-block:: bash

   sudo apt-get install libproj-dev proj-data proj-bin libgeos++-dev

or any other package manager such as homebrew_.

The Python packages are then installed as for macOS (see above):

.. code-block:: bash

   pip install numpy scipy matplotlib netcdf4 pykdtree
   pip install --upgrade cython pyshp six
   # shapely needs to be built from source to link to geos. If it is already
   # installed, uninstall it:
   [[ -z $(pip freeze | grep shapely) ]] && pip uninstall -y shapely
   pip install shapely --no-binary shapely
   pip install cartopy
   pip install ncvue

``ncvue`` uses the "themed Tk" ("ttk") functionality of Tk 8.5. Linux
users might need to update their (very old) Tk installations.

.. _Anaconda: https://www.anaconda.com/products/individual
.. _cartopy: https://scitools.org.uk/cartopy/docs/latest/
.. _install: https://scitools.org.uk/cartopy/docs/latest/installing.html
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _homebrew: https://brew.sh/
.. _macOS app: http://www.macu.de/extra/ncvue-4.0.dmg
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Miniforge: https://github.com/conda-forge/miniforge
.. _netcdf4: https://unidata.github.io/netcdf4-python/netCDF4/index.html
.. _pyenv: https://github.com/pyenv/pyenv
.. _Sebastian Müller: https://github.com/MuellerSeb
.. _Windows executable: http://www.macu.de/extra/ncvue-3.7-amd64.msi
