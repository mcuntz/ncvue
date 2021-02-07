# -*- mode: python ; coding: utf-8 -*-

# Use pyinstaller:
#   pyinstaller --onedir --windowed ncvue_exe.spec

# Test app:
#   dist\ncvue\ncvue.exe

# Create icon:
#   see ncvue_app.spec

# Create app:
#   Use conda-forge for everything because more up-to-date
#   Try to avoid mkl by using numpy from conda-forge and scipy from pip
#   https://github.com/pyinstaller/pyinstaller/issues/2270
#     conda install -c conda-forge blas numpy openblas pandas netcdf4 matplotlib cython pyshp six pykdtree
#     pip install scipy
#     conda install -c conda-forge shapely
#     conda install -c conda-forge cartopy
#     pip install ncvue
#   Install newest version of PyInstaller (5.0a2)
#     conda install -c conda-forge pyinstaller
#     pip install --upgrade https://github.com/pyinstaller/pyinstaller/tarball/develop
#     pyinstaller --onedir --windowed .\ncvue_exe.spec
#   # Using UPX (copy into C:\ProgramData, i.e. path without space): https://upx.github.io/
#   #   pyinstaller --onedir --windowed --upx-dir='C:\ProgramData\upx-3.96-win64\' .\ncvue_exe.spec
#   Change icon of dist\ncvue\ncvue.exe with ResourceHacker
#      http://www.angusj.com/resourcehacker/

# Clean icon cache
#   # Before Win-10 
#   ie4uinit.exe -ClearIconCache
#   # For Windows 10, use
#   ie4uinit.exe -show

# Create Installer:
#   https://helpdeskgeek.com/free-tools-review/4-tools-to-create-windows-installer-packages/

block_cipher = None

a = Analysis(['../bin/ncvue'],
             pathex=['.'],
             binaries=[],
             datas=[('../ncvue/images', 'images')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=True,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

# # manually remove mkl libraries
# # https://github.com/pyinstaller/pyinstaller/issues/2270
# def remove_from_list(input, keys):
#     outlist = []
#     for item in input:
#         name, _, _ = item
#         flag = 0
#         for key_word in keys:
#             if name.find(key_word) > -1:
#                 flag = 1
#         if flag != 1:
#             outlist.append(item)
#     return outlist

# rmlibs = ['mkl', 'libopenblas']
# a.binaries = remove_from_list(a.binaries, rmlibs)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ncvue',
          icon='../ncvue/images/ncvue_icon.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)

app = COLLECT(exe,
              a.binaries,
              a.zipfiles,
              a.datas,
              strip=False,
              upx=True,
              upx_exclude=[],
              name='ncvue',)
