#!/usr/bin/env python
r'''
Make stand-alone version of ncvue with cx_Freeze.

On macOS, use minimal virtual environment
   if [[ "$(uname -m)" == "arm64" ]] ; then
       export OPENBLAS="$(brew --prefix openblas)"
       export HDF5_DIR="$(brew --prefix hdf5)"
       export GEOS_DIR="$(brew --prefix geos)"
       export GEOS_CONFIG="$(brew --prefix geos)/bin/geos-config"
   fi
   pyenv virtualenv 3.12.8 ncvue-install
   pyenv local ncvue-install
   # or:
   # pyenv virtualenv 3.12.8 ncvue-install-ctk
   # pyenv local ncvue-install-ctk
   pyenv rehash
   # requirements.txt includes dask and xarray
   python -m pip install -r requirements.txt
   # if ncvue-install-ctk
   # python -m pip install customtkinter
   python -m pip install -ve ./
   python -m pip install cx_freeze

On Windows, use conda-forge for everything because more up-to-date
    # Do not use mkl for smaller executable with PyInstaller/cx_Freeze
    conda create -n ncvue-install-ctk python=3.12
    conda activate ncvue-install-ctk
    conda install -c conda-forge nomkl cartopy
    conda install -c conda-forge scipy cython pykdtree cftime netcdf4 dask xarray
    python -m pip install customtkinter
    conda install -c conda-forge cx_Freeze
    
Have to install ncvue, e.g. in ncvue directory
    python -m pip install -ve .

Check in Windows Powershell
    $env:PYTHONPATH = "J:/prog/github/ncvue"
    ncvue
Executable for testing
    python cx_freeze_setup.py build
macOS app
    python cx_freeze_setup.py bdist_mac
macOS dmg
    python cx_freeze_setup.py bdist_dmg
Windows installer
    python cx_freeze_setup.py bdist_msi

'''
import os
import codecs
import re
import sys
import glob
import shutil
import pyproj

from cx_Freeze import setup, Executable


# find __version__
def _iread(*fparts):
    ''' Read file data. '''
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *fparts), 'r') as fp:
        return fp.read()


def _find_version(*file_paths):
    '''Find version without importing module.'''
    version_file = _iread(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


package   = 'ncvue'
doclines1 = 'A minimal GUI for a quick view of netcdf files'
doclines  = doclines1 + ', aiming to be a drop-in replacement'
doclines += ' for ncview and panoply.'
author    = 'Matthias Cuntz'
copyright = 'Copyright (c) 2020-2025 Matthias Cuntz - mc (at) macu (dot) de'

version = _find_version('src/' + package, '_version.py')

script        = 'src/ncvue/__main__.py'
packages      = ['scipy', 'cftime', 'netCDF4']  # others detected automatically
excludes      = ['pyflakes', 'mccabe', 'pycodestyle', 'flake8',  # flake8
                 'gtk', 'PyQt4', 'PyQt5', 'wx']                  # matplotlib
includes      = []
# no need to include images and themes because ncvue gets installed as module
# include_files = [('ncvue/images', 'images'), ('ncvue/themes', 'themes')]
# since pyproj v9.1
include_files = [(pyproj.datadir.get_data_dir(), 'Library/share/proj')]

if sys.platform == 'win32':
    base = 'Win32GUI'
    exe  = 'ncvue.exe'
    icon = 'src/ncvue/images/ncvue_icon.ico'
    msvcr = True
    shortcutname = 'ncvue'
    shortcutdir  = 'ProgramMenuFolder'
elif sys.platform == 'darwin':
    base = None
    exe  = 'ncvue'
    icon = 'docs/images/ncvue_icon.icns'
    msvcr = False
    shortcutname = 'ncvue'
    shortcutdir  = None
else:
    base = None
    exe  = 'ncvue'
    icon = 'src/ncvue/images/ncvue_icon.ico'
    msvcr = False
    shortcutname = 'ncvue'
    shortcutdir  = None

build_exe_options = {'packages': packages,
                     'excludes': excludes,
                     'includes': includes,
                     'include_files': include_files,
                     'include_msvcr': msvcr}

executables = [Executable(script,
                          target_name=exe,
                          copyright=copyright,
                          base=base,
                          icon=icon,
                          shortcut_name=shortcutname,
                          shortcut_dir=shortcutdir)]

# Check codesign
#     spctl -a -t exec -vvv build/ncvue.app
bdist_mac_options = {
    'iconfile': icon,
    'bundle_name': package,
    # Create certificate
    #     https://developer.apple.com/help/account/create-certificates/create-developer-id-certificates
    # Check ID (Team ID is in parenthesis)
    #     security find-identity -p codesigning -v
    'codesign_identity': 'MATTHIAS OSKAR CUNTZ (R5T7LWQ224)',
    'codesign_options': 'runtime',  # Ensure codesign uses 'hardened runtime'
    'codesign_verify': True,  # Get more verbose logging for codesign
    'spctl_assess': False,  # rejects codesign because not notarized yet
    'plist_items': [('NSPrincipalClass', 'NSApplication'),
                    ('NSHighResolutionCapable', True)]
}

# Install intermediate certificates as in answer of FrostyBagg on
#     https://forums.developer.apple.com/forums/thread/86161
# Do not change the trust settings.
#     xcrun notarytool submit ncvue-5.1.dev1.dmg --keychain-profile "notarytool-password" --wait
# Check codesign
#     spctl -a -t open -vvv --context context:primary-signature build/ncvue-5.1.dev1.dmg
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
    'install_icon': icon}
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

setup(name=package,
      version=version,
      description=doclines,
      options={'build_exe': build_exe_options,
               'bdist_mac': bdist_mac_options,
               'bdist_dmg': bdist_dmg_options,
               'bdist_msi': bdist_msi_options},
      executables=executables,
      )
