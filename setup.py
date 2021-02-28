#!/usr/bin/env python
"""
ncvue: A minimal GUI for a quick view of netcdf files.
       Aiming to be a drop-in replacement for ncview and panoply.
"""
from __future__ import division, absolute_import, print_function
import os
import codecs
import re

from setuptools import setup, find_packages


# find __version__

def _iread(*fparts):
    """ Read file data. """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *fparts), "r") as fp:
        return fp.read()


def _find_version(*file_paths):
    """Find version without importing module."""
    version_file = _iread(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# setup

package   = "ncvue"
doclines  = "A minimal GUI for a quick view of netcdf files."
doclines += " Aiming to be a drop-in replacement for ncview and panoply."
readme    = open("README.rst").read()

author = "Matthias Cuntz"
email  = "mc@macu.de"

version = _find_version(package, "version.py")

scripts = [os.path.join('bin', f) for f in os.listdir('bin')]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Atmospheric Science",
    "Topic :: Scientific/Engineering :: Hydrology",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Software Development",
    "Topic :: Utilities",
]

setup(
    name                 = package,
    version              = version,
    maintainer           = author,
    maintainer_email     = email,
    description          = doclines,
    long_description     = readme,
    long_description_content_type = "text/x-rst",
    author               = author,
    author_email         = email,
    url                  = "https://github.com/mcuntz/"+package,
    license              = "MIT",
    classifiers          = classifiers,
    platforms            = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
    package_data         = {package: ['ncvue/images/*.png']},
    include_package_data = True,
    install_requires     = ["numpy", "scipy", "netcdf4", "matplotlib",
                            "pykdtree", "cartopy"],
    extras_require       = {},
    packages             = find_packages(include=[package, package+'.*']),
    scripts              = scripts,
)
