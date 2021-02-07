Installation
============

``ncvue`` is an application written in Python. If you have Python installed,
then the best is to install ``ncvue`` within the Python universe. The easiest
way to install ``ncvue`` is thence via `pip` if you have cartopy_ installed
already:

.. code-block:: bash

   pip install ncvue

`Cartopy` can, however, be more elaborate to install_. The easiest way to
install `Cartopy` is by using conda_ and then installing ``ncvue`` by `pip`.
After installing, for example, Miniconda_:

.. code-block:: bash

   conda install -c conda-forge cartopy
   pip install ncvue

Support of `conda-forge` will be added in one of the next minor releases of ``ncvue``.

Binary distributions
--------------------

We also provide a standalone macOS app_ and a Windows executable_ that come with
everything needed to run ``ncvue`` including Python. The macOS app should work
from macOS 10.13 (High Sierra) onward. It is, however, only tested on macOS
10.15 (Catalina).

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
PyPI. `Cartopy` can, however, be more elaborate to install_. It basically uses Python
wrappers to C++/C-libraries that must be installed first.

Windows
^^^^^^^

On **Windows**, one can install `cartopy` with conda_ from `conda-forge`. We
recommend then to install also all other dependencies for ``ncvue`` with conda
before installing ``ncvue`` with `pip` (`pip` will otherwise install the second
lot of packages):

.. code-block:: bash

   conda install -c conda-forge cartopy
   conda install -c conda-forge scipy cython pykdtree netcdf4
   pip install ncvue

macOS
^^^^^

On **macOS**, one can use exactly the same procedure with conda_ as for Windows
(see above). Or one can use homebrew_ to install the Cartographic Projections
Library `proj` and the Geometry Engine `geos`:

.. code-block:: bash

   # uncomment next line if homebrew is not installed
   # /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
   brew install proj geos

``ncvue`` and its prerequisites are then installed via pip (from Cartopy install_):

.. code-block:: bash

   pip install numpy scipy matplotlib netcdf4 pykdtree
   pip install --upgrade cython pyshp six
   # shapely needs to be built from source to link to geos. If it is already
   # installed, uninstall it by: pip uninstall shapely
   pip install shapely --no-binary shapely
   pip install cartopy
   pip install ncvue

It is possible that your Python version installed with pyenv_ might clash
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

Linux
^^^^^

On **Linux**, one can also use exactly the same procedure with conda_ as for Windows
(see above). Or one can install the C++/C-libraries with `apt-get` (Ubuntu):

.. code-block:: bash

   sudo apt-get install libproj-dev proj-data proj-bin libgeos++-dev

or any other package manager such as homebrew_.

The Python packages are then installed as for macOS (see above):

.. code-block:: bash

   pip install numpy scipy matplotlib netcdf4 pykdtree
   pip install --upgrade cython pyshp six
   # shapely needs to be built from source to link to geos. If it is already
   # installed, uninstall it by: pip uninstall shapely
   pip install shapely --no-binary shapely
   pip install cartopy
   pip install ncvue

``ncvue`` uses the "themed Tk" ("ttk") functionality of Tk 8.5. It hence needs
Python 2.7 or Python 3.1 or later. Linux users might need to update their (very
old) Tk installations.

.. _Anaconda: https://www.anaconda.com/products/individual
.. _app: http://www.macu.de/extra/ncvue.dmg
.. _cartopy: https://scitools.org.uk/cartopy/docs/latest/
.. _conda: https://docs.conda.io/projects/conda/en/latest/
.. _executable: http://www.macu.de/extra/ncvue.msi
.. _homebrew: https://brew.sh/
.. _install: https://scitools.org.uk/cartopy/docs/latest/installing.html
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Miniforge: https://github.com/conda-forge/miniforge
.. _netcdf4: https://unidata.github.io/netcdf4-python/netCDF4/index.html
.. _pyenv: https://github.com/pyenv/pyenv
