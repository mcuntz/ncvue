# -*- mode: python ; coding: utf-8 -*-

# Used by script ./ncvue2app

# Create icon:
#   - Export PDF in Keynote from docs/images/ncvue_icon.key
#   - Export PNG in Preview ncvue_icon.pdf
#   - Make magenta transparent
#     outfile=docs/images/ncvue_icon.png
#     infile=~/Desktop/ncvue_icon.png
#     color=$( convert ${infile} -format "%[pixel:p{0,0}]" info:- )
#     convert ${infile} -alpha off -bordercolor ${color} -border 1 \
#         \( +clone -fuzz 30% -fill none -floodfill +0+0 ${color} \
#         -alpha extract -geometry 200% -blur 0x0.5 \
#         -morphology erode square:1 -geometry 50% \) \
#         -compose CopyOpacity -composite -shave 1 ${outfile}
#   - png to icns
#     image2icns docs/images/ncvue_icon.png
#   - png to ico
#     convert docs/images/ncvue_icon.png \
#         -define icon:auto-resize="256,128,96,64,48,32,16" \
#         ncvue/images/ncvue_icon.ico
#     convert docs/images/ncvue_icon.png \
#          -resize 512 ncvue/images/ncvue_icon.png
#   - clean up: docs/images/ncvue_icon.pdf ~/Desktop/ncvue_icon.png

# Create app:
#   Had to recompile bootloader in pyinstaller to get dark mode working
#   https://github.com/pyinstaller/pyinstaller/issues/4886
#     git clone https://github.com/pyinstaller/pyinstaller.git
#     cd pyinstaller/bootloader/
#     export MACOSX_DEPLOYMENT_TARGET=10.13
#     export CFLAGS=-mmacosx-version-min=10.13
#     export CPPFLAGS=-mmacosx-version-min=10.13
#     export LDFLAGS=-mmacosx-version-min=10.13
#     export LINKFLAGS=-mmacosx-version-min=10.13
#     python ./waf all
#     cd ..
#     pip install .
#   Check in output of
#     otool -l /Users/cuntz/.pyenv/versions/3.8.6/lib/python3.8/site-packages/pyinstaller/bootloader/Darwin-64bit/run
#   that LC_VERSION_MIN_MACOSX is >= 10.13
#     cmd LC_VERSION_MIN_MACOSX
#     cmdsize 16
#     version 10.13
#     sdk 10.15.4
#   Use pyinstaller
#     pyinstaller --onefile --windowed ncvue_app.spec

# Test app:
#   open dist/ncvue.app/

# Windows blurry text:
#   https://stackoverflow.com/questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp

block_cipher = None

a = Analysis(['../bin/ncvue'],
             pathex=['.'],
             binaries=[],
             datas=[('../ncvue/images', 'images')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ncvue',
          debug=False,
          strip=False,
          upx=True,
          console=True)

app = BUNDLE(exe,
             a.binaries,
             a.zipfiles,
             a.datas,
             strip=False,
             upx=True,
             name='ncvue.app',
             icon='../docs/images/ncvue_icon.icns',
             bundle_identifier=None,
             info_plist={'NSPrincipalClass': 'NSApplication',
                         'NSHighResolutionCapable': True},)
