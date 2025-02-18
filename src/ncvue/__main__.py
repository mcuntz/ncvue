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
  -x, --xarray          Use xarray to read input files


Example command line:
    ncvue MuSICA_out_2009.nc


:copyright: Copyright 2020- Matthias Cuntz, see AUTHORS.rst for details.
:license: MIT License, see LICENSE for details.

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Made ncvue a gui_script entry_point, May 2022, Matthias Cuntz
   * Include xarray to read input files, Feb 2025, Matthias Cuntz

"""
import numpy as np
from ncvue import ncvue


def main():
    import argparse

    miss = np.nan
    usex = False
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='A minimal GUI for a quick view of netcdf files.')
    hstr = 'Set value to missing value (default: numpy.nan)'
    parser.add_argument('-m', '--miss', action='store', type=float,
                        default=miss, dest='miss',
                        metavar='missing_value', help=hstr)
    hstr = 'Use xarray to read input files'
    parser.add_argument('-x', '--xarray', action='store_true',
                        default=usex, dest='usex', help=hstr)
    parser.add_argument('ncfile', nargs='*', default=None,
                        metavar='netcdf_file',
                        help='netcdf file')

    args = parser.parse_args()
    miss = args.miss
    usex = args.usex
    ncfile = args.ncfile

    del parser, args

    # if len(ncfile) == 0:
    #     ncfile = ncfile[0]
    # else:
    #     ncfile = ''

    # This must be before any other call to matplotlib
    # because it uses the TkAgg backend.
    # This means, do not use --pylab with ipython.
    ncvue(ncfile=ncfile, miss=miss, usex=usex)


if __name__ == "__main__":
    main()
