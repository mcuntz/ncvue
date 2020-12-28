==========
Quickstart
==========

# ncvue -- A GUI to view netCDF files
<!-- pandoc -f gfm -o README.html -t html README.md -->

A minimal GUI for a quick view of netCDF files.
Aiming to be a drop-in replacement for ncview.

<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3893705.svg)](https://doi.org/10.5281/zenodo.3893705) -->
[![PyPI version](https://badge.fury.io/py/ncvue.svg)](https://badge.fury.io/py/ncvue)
[![License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/mcuntz/ncvue/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/mcuntz/ncvue.svg?branch=master)](https://travis-ci.org/mcuntz/ncvue)

## About ncvue

*ncvue* is a minimal GUI for a quick view of netCDF files. It is aiming to be a
drop-in replacement for
[ncview](http://meteora.ucsd.edu/~pierce/ncview_home_page.html), being slightly
more general than ncview, which targets maps.

*ncvue* is a Python script that can be called from within Python and as a command
line tool.


## Quick usage guide

Try it on the command line as:

```bash
    ncvue netcdf_file.nc
```

or from within Python:

```python
    from ncvue import ncvue
    ncvue('netcdf_file.nc')
```

Note that *ncvue* uses the `TkAgg` backend of `matplotlib`. It must be called
before any other call to `matplotlib`. This also means that you cannot launch it
from within `iPython` if it was launched with `--pylab`. It can be called from
within a standard `iPython`.


## Installation - NOT YET ON PyPI

The easiest way to install is via `pip`:

```bash
    pip install ncvue
```

The latest version of `ncvue` can be installed from source:

```bash
    git clone https://github.com/mcuntz/ncvue.git
    cd ncvue
    pip install .
```

Users without proper privileges can append the `--user` flag to
``pip`` either while installing from the Python Package Index (PyPI):

```bash
    pip install ncvue --user
```

or from the top *ncvue* directory:

```bash
    git clone https://github.com/mcuntz/ncvue.git
    cd ncvue
    pip install . --user
```

One can download the repository and add it to `PYTHONPATH` as well as the `bin`
directory to `PATH`:
```bash
    git clone https://github.com/mcuntz/ncvue.git
    cd ncvue
    export PYTHONPATH=${PYTHONPATH}:${PWD}
    export PATH=${PATH}:${PWD}/bin
```

*ncvue* uses the packages :mod:`numpy`,
[netCDF4](https://unidata.github.io/netcdf4-python/netCDF4/index.html), and
:mod:`matplotlib`, which are installed automatically if `pip` is used or should
be installed before setting up *ncvue*.

*ncvue* uses the "themed Tk" ("ttk") functionality of Tk 8.5. It hence needs
Python 2.7 or Python 3.1 or later. Linux users might need to update their (very
old) Tk installations.


## License

*ncvue* is distributed under the MIT License.  
See the [LICENSE](https://github.com/mcuntz/ncvue/LICENSE) file for details.

Copyright (c) 2020 Matthias Cuntz

The project structure is based on a
[template](https://github.com/MuellerSeb/template) provided by [Sebastian
Müller](https://github.com/MuellerSeb).


## Contributing to ncvue

Users are welcome to submit bug reports, feature requests, and code
contributions to this project through GitHub.
