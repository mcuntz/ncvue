#!/usr/bin/env python
"""
Make stand-alone version of ncvue with cx_Freeze.

On macOS, use minimal virtual environment
    pyenv virtualenv 3.8.9 install-ncvue
    pyenv rehash
    pyenv local install-ncvue
    pip install --upgrade cython numpy pyshp six
    isshapely=$(pip freeze | grep shapely)
    if [[ -z ${isshapely} ]] ; then pip uninstall -y shapely ; fi
    pip install shapely --no-binary shapely
    pip install scipy
    pip install matplotlib
    pip install pykdtree
    pip install netcdf4
    pip install cartopy
    pip install flake8  # for Emacs
    pip install cx_Freeze
    # libtiff.5.dylib version of PIL too old for pyproj -> use current from homebrew
    mv ~/.pyenv/versions/3.8.9/envs/install-ncvue/lib/python3.8/site-packages/PIL/.dylibs/libtiff.5.dylib \
       ~/.pyenv/versions/3.8.9/envs/install-ncvue/lib/python3.8/site-packages/PIL/.dylibs/libtiff.5.dylib.save
    \cp /usr/local/lib/libtiff.5.dylib \
        ~/.pyenv/versions/3.8.9/envs/install-ncvue/lib/python3.8/site-packages/PIL/.dylibs/libtiff.5.dylib

On Windows, use conda-forge for everything because more up-to-date
    # Do not use mkl for smaller executable with PyInstaller
    conda install -c conda-forge nomkl cartopy
    conda install -c conda-forge scipy cython pykdtree netcdf4
    conda install -c conda-forge cx_Freeze
    # pip install ncvue

Executable for testing
    python cx_freeze_setup.py build
macOS app
    python cx_freeze_setup.py bdist_mac
macOS dmg
    python cx_freeze_setup.py bdist_dmg
Windows installer
    python.exe cx_freeze_setup.py bdist_msi
"""
from __future__ import division, absolute_import, print_function
import os
import codecs
import re
import sys
import glob
import shutil

from cx_Freeze import setup, Executable
from cx_Freeze.dist import build as _build


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


# special build for macOS
# https://stackoverflow.com/questions/17806485/execute-a-python-script-post-install-using-distutils-setuptools
def _post_build_mac(exedir):
    adir = glob.glob(exedir + '/lib/*/.dylibs')
    for aa in adir:
        print('rm -r', aa)
        shutil.rmtree(aa)


def _post_build_win(exedir):
    adir = glob.glob(exedir + '/lib/**/*.dll', recursive=True)
    for aa in adir:
        if not os.path.exists(exedir + '/' + os.path.basename(aa)):
            print('cp ', aa, exedir)
            shutil.copy2(aa, exedir)


class build(_build):
    def run(self):
        _build.run(self)
        if sys.platform == 'win32':
            self.execute(_post_build_win, (self.build_exe,),
                         msg="Post-build on Windows")
        elif sys.platform == 'darwin':
            self.execute(_post_build_mac, (self.build_exe,),
                         msg="Post-build on macOS")
        else:
            pass


package   = 'ncvue'
doclines1 = 'A minimal GUI for a quick view of netcdf files.'
doclines  = doclines1 + ' Aiming to be a drop-in replacement'
doclines += ' for ncview and panoply.'
author    = 'Matthias Cuntz'
copyright = 'Copyright (c) 2020-2021 Matthias Cuntz - mc (at) macu (dot) de'

version = _find_version(package, 'version.py')

script        = 'bin/ncvue'
packages      = ['scipy', 'netCDF4']  # others detected automatically
excludes      = ['pyflakes', 'mccabe', 'pycodestyle', 'flake8',  # flake8
                 'gtk', 'PyQt4', 'PyQt5', 'wx']                  # matplotlib
includes      = []
# no need to include images and themes because ncvue gets installed as module
# include_files = [('ncvue/images', 'images'), ('ncvue/themes', 'themes')]
include_files = []

if sys.platform == 'win32':
    base = 'Win32GUI'
    exe  = 'ncvue.exe'
    icon = 'ncvue/images/ncvue_icon.ico'
    msvcr = True
elif sys.platform == 'darwin':
    base = None
    exe  = 'ncvue'
    icon = 'docs/images/ncvue_icon.icns'
    msvcr = False
else:
    base = None
    exe  = 'ncvue'
    icon = 'ncvue/images/ncvue_icon.ico'
    msvcr = False

build_exe_options = {'packages': packages,
                     'excludes': excludes,
                     'includes': includes,
                     'include_files': include_files,
                     'include_msvcr': msvcr}

executables = [Executable(script,
                          target_name=exe,
                          copyright=copyright,
                          base=base,
                          icon=icon)]

bdist_mac_options = {
    'iconfile': icon,
    'bundle_name': package,
    'plist_items': [('NSPrincipalClass', 'NSApplication'),
                    ('NSHighResolutionCapable', True)]
}

bdist_dmg_options = {
    'applications_shortcut': True
}

bdist_msi_options = {
    'add_to_path': True,
    'all_users': True,
    'data': {'ProgId': [('Prog.Id', None, None, doclines1,
                         'IconId', None)]},
    'summary_data': {'author': author,
                     'comments': doclines1,
                     'keywords': 'netcdf maps view GUI cartopy'},
    'install_icon': icon,}
#    'extensions': [{'extension': 'nc',  # open / view netcdf files (.nc)
#                    'verb': 'open',
#                    'executable': exe,
#                    'context': 'Open with ncvue'},
#                   {'extension': 'nc',
#                    'verb': 'view',
#                    'executable': exe,
#                    'context': 'View with ncvue'},
#                   {'extension': 'nc4',  # open / view netcdf files (.nc4)
#                    'verb': 'open',
#                    'executable': exe,
#                    'context': 'Open with ncvue'},
#                   {'extension': 'nc4',
#                    'verb': 'view',
#                    'executable': exe,
#                    'context': 'View with ncvue'}]
#}

setup(name        = package,
      version     = version,
      description = doclines,
      cmdclass    = {'build': build},
      options     = {'build_exe': build_exe_options,
                     'bdist_mac': bdist_mac_options,
                     'bdist_dmg': bdist_dmg_options,
                     'bdist_msi': bdist_msi_options},
      executables = executables,
      )