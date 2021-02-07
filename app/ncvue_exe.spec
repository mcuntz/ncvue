# -*- mode: python ; coding: utf-8 -*-

#   Use pyinstaller
#     pyinstaller --onedir --windowed ncvue_exe.spec

# Test app:
#   open dist/ncvue.app/

# Windows blurry text:
#   https://stackoverflow.com/questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp

# conda install -c conda-forge numpy netcdf4 matplotlib
# conda install -c conda-forge cython pyshp six scipy pykdtree
# conda install -c conda-forge shapely
# conda install -c conda-forge cartopy
# pip install ncvue

# conda install -c conda-forge pyinstaller
# pip install --upgrade https://github.com/pyinstaller/pyinstaller/tarball/develop
# pyinstaller --onedir --windowed .\ncvue_exe.spec
# pyinstaller --onedir --windowed --upx-dir='C:\ProgramData\upx-3.96-win64\' .\ncvue_exe.spec

# http://www.angusj.com/resourcehacker/

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

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ncvue',
		  icon='../docs/images/ncvue_icon.ico',
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
