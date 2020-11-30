# ncvue -- A GUI to view netCDF files
<!-- pandoc -f gfm -o README.html -t html README.md -->

A minimal GUI for a quick view of netCDF files.
Aiming to be a drop-in replacement for ncview.

<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3893705.svg)](https://doi.org/10.5281/zenodo.3893705) -->
[![PyPI version](https://badge.fury.io/py/ncvue.svg)](https://badge.fury.io/py/ncvue)
[![License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/mcuntz/ncvue/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/mcuntz/ncvue.svg?branch=master)](https://travis-ci.org/mcuntz/ncvue)
[![Coverage Status](https://coveralls.io/repos/github/mcuntz/ncvue/badge.svg?branch=master)](https://coveralls.io/github/mcuntz/ncvue?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ncvue/badge/?version=latest)](https://ncvue.readthedocs.io/en/latest/?badge=latest)

## About ncvue

*ncvue* is a minimal GUI for a quick view of netCDF files. It is aiming to be a
drop-in replacement for ncview, being slightly more general than
[ncview](http://meteora.ucsd.edu/~pierce/ncview_home_page.html), which targets
maps.

*ncvue* is a Python script that can be called from the Python and as a command
line tool.


## Documentation

The complete documentation for *ncvue* is available from Read The Docs.

   http://ncvue.readthedocs.org/en/latest/


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
before any other call to `matplotlib`. This means also that you cannot launch it
in `iPython` that was called with `--pylab`. But it can be called in normal
`iPython`.


## Installation

The easiest way to install is via `pip`:

```bash
    pip install ncvue
```
	
See the [installation instructions](http://ncvue.readthedocs.io/en/latest/install.html)
in the [documentation](http://ncvue.readthedocs.io) for more information.


## Requirements:

- [NumPy](https://www.numpy.org)
- [netcdf4](https://unidata.github.io/netcdf4-python/netCDF4/index.html)
- [matplotlib](https://matplotlib.org/)

*ncvue* uses the "themed Tk" ("ttk") functionality of Tk 8.5. It hence needs Python 2.7 or Python 3.1 or later. Linux users might need to update their (very old) Tk installations.


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

More information is available in the
[Contributing](http://ncvue.readthedocs.org/en/latest/contributing.html)
guidelines.
