#!/usr/bin/env python
"""
usage: ncvue [-h] [-m missing_value] [netcdf_file]

A minimal GUI for a quick view of netcdf files.

positional arguments:
  netcdf_file           netcdf file

optional arguments:
  -h, --help            show this help message and exit
  -m missing_value, --miss missing_value
                        Set value to missing value (default: numpy.nan)


Example command line:
    ncvue MuSICA_out_2009.nc

:copyright: Copyright 2020-2022 Matthias Cuntz, see AUTHORS.md for details.
:license: MIT License, see LICENSE for details.

History
    * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
    * Made ncvue a gui_script entry_point, May 2022, Matthias Cuntz

"""
import numpy as np
from ncvue import ncvue


def main():
    import argparse

    miss = np.nan
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
A minimal GUI for a quick view of netcdf files.""")
    hstr  = 'Set value to missing value (default: numpy.nan)'
    parser.add_argument('-m', '--miss', action='store', type=float,
                        default=miss, dest='miss',
                        metavar='missing_value', help=hstr)
    parser.add_argument('ncfile', nargs='*', default=None,
                        metavar='netcdf_file',
                        help='netcdf file')

    args   = parser.parse_args()
    miss   = args.miss
    ncfile = args.ncfile

    del parser, args

    if len(ncfile) > 0:
        ncfile = ncfile[0]
    else:
        ncfile = ''

    # This must be before any other call to matplotlib
    # because it uses the TkAgg backend.
    # This means, do not use --pylab with ipython.
    ncvue(ncfile=ncfile, miss=miss)


if __name__ == "__main__":
    main()
