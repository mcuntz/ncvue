ncvue -- A GUI to view netCDF files
===================================
..
  pandoc -f rst -o README.html -t html README.rst

A minimal GUI for a quick view of netCDF files.
Aiming to be a drop-in replacement for ncview.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3893705.svg
   :alt: Zenodo DOI
   :target: https://doi.org/10.5281/zenodo.3893705

.. image:: https://badge.fury.io/py/ncvue.svg
   :alt: PyPI version
   :target: https://badge.fury.io/py/ncvue

.. image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat
   :alt: License
   :target: https://github.com/mcuntz/ncvue/blob/master/LICENSE

.. image:: https://travis-ci.org/mcuntz/ncvue.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/mcuntz/ncvue

.. image:: https://readthedocs.org/projects/ncvue/badge/?version=latest
   :alt: Documentation status
   :target: https://ncvue.readthedocs.io/en/latest/?badge=latest

About ncvue
-----------

``ncvue`` is a minimal GUI for a quick view of netCDF files. It is aiming to be
a drop-in replacement for `ncview`_, being slightly more general than `ncview`,
which targets maps.

.. _ncview http://meteora.ucsd.edu/~pierce/ncview_home_page.html

``ncvue`` is a Python script that can be called from within Python and as a command
line tool.

Documentation - NOT YET ON ReadTheDocs
--------------------------------------

The complete documentation for ``ncvue`` is available from Read The Docs.

   http://ncvue.readthedocs.org/en/latest/


Quick usage guide
-----------------

Try it on the command line as:

.. code-block:: bash

   ncvue netcdf_file.nc

or from within Python:

.. code-block:: python

   from ncvue import ncvue
   ncvue('netcdf_file.nc')

Note that ``ncvue`` uses the `TkAgg` backend of `matplotlib`. It must be called
before any other call to `matplotlib`. This also means that you cannot launch it
from within `iPython` if it was launched with `--pylab`. It can be called from
within a standard `iPython`.


Installation - NOT YET ON PyPI
------------------------------

The easiest way to install is via `pip`:

.. code-block:: bash

   pip install ncvue


The latest version of `ncvue` can be installed from source:

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   pip install .

Users without proper privileges can append the `--user` flag to
``pip`` either while installing from the Python Package Index (PyPI):

.. code-block:: bash

   pip install ncvue --user

or from the top ``ncvue`` directory:

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   pip install . --user

One can download the repository and add it to `PYTHONPATH` as well as the `bin`
directory to `PATH`:

.. code-block:: bash

   git clone https://github.com/mcuntz/ncvue.git
   cd ncvue
   export PYTHONPATH=${PYTHONPATH}:${PWD}
   export PATH=${PATH}:${PWD}/bin

``ncvue`` uses the packages :mod:`numpy`,
[netCDF4](https://unidata.github.io/netcdf4-python/netCDF4/index.html),
:mod:`matplotlib`, and :mod:`cartopy`, which are installed automatically if
`pip` is used or should be installed before setting up ``ncvue``.

``ncvue`` uses the "themed Tk" ("ttk") functionality of Tk 8.5. It hence needs
Python 2.7 or Python 3.1 or later. Linux users might need to update their (very
old) Tk installations.

License
-------

``ncvue`` is distributed under the MIT License. See the `LICENSE`_ file for
details.

.. _LICENSE: https://github.com/mcuntz/ncvue/LICENSE

Copyright (c) 2020-2021 Matthias Cuntz

The project structure is based on a `template`_ provided by `Sebastian Müller`_.

.. _template: https://github.com/MuellerSeb/template
.. _Sebastian Müller: https://github.com/MuellerSeb

Contributing to ncvue
---------------------

Users are welcome to submit bug reports, feature requests, and code
contributions to this project through GitHub.
