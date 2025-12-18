# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['main.py', 'gui.py', 'host.py', 'client.py', 'relay_host.py', 'relay_client.py', 'relay_server.py', 'config.py', 'screen_capture.py', 'input_control.py', 'favorites.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.scrolledtext', 'tkinter.simpledialog', 'PIL', 'PIL.Image', 'PIL.ImageGrab', 'PIL.ImageTk', 'pynput', 'pynput.mouse', 'pynput.keyboard'],
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
    name='EdafDesk',
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

# Mac için .app bundle oluştur
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='EdafDesk.app',
        icon=None,
        bundle_identifier='com.edaf.edafdesk',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
