# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

_mido_hidden = collect_submodules('mido')
_mido_datas  = collect_data_files('mido')
_src_hidden  = collect_submodules('src')

a = Analysis(
    ['playSong_clean.py'],
    pathex=[],
    binaries=[],
    datas=_mido_datas,
    hiddenimports=['keyboard'] + _mido_hidden + _src_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy', 'pandas', 'matplotlib', 'scipy', 'PIL', 'Pillow',
        'pytest', 'unittest', 'doctest', 'pdb', 'profile', 'cProfile',
        'email', 'html', 'http', 'urllib', 'xmlrpc',
        'turtle', 'curses', 'readline', 'rlcompleter',
        'multiprocessing', 'concurrent', 'asyncio',
        'distutils', 'setuptools', 'pkg_resources',
        'sqlite3', 'lib2to3', 'argparse', 'optparse',
        'logging.handlers', 'logging.config',
        'xml', 'xmllib', 'xml.etree', 'xml.dom', 'xml.sax', 'xml.parsers',
        'bz2', 'lzma',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='playSong_clean',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
