# -*- mode: python ; coding: utf-8 -*-

# 设置资源文件列表 - 确保打包时包含所有必要的图标和资源
datas = [
    # 包含图标文件夹中的所有文件
    ('generated_icons/*.ico', 'generated_icons'),
    ('generated_icons/*.png', 'generated_icons'),
    # 包含lib文件夹中的必要文件
    ('lib/*', 'lib'),
]

a = Analysis(
    ['apkeditor_main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ApkEditor',
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
    icon=['generated_icons\\tag.ico'],
)
