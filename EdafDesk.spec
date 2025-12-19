# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'client',
        'host', 
        'config',
        'gui',
        'screen_capture',
        'input_control',
        'relay_client',
        'relay_host',
        'relay_server',
        'favorites',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.simpledialog',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageGrab',
        'pynput',
        'pynput.mouse',
        'pynput.keyboard',
        'socket',
        'threading',
        'base64',
        'zlib',
        'json',
        'struct',
        'platform',
        'subprocess',
        'tempfile',
        'os',
        'io',
        'time'
    ],
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
    icon='NONE',
)

# macOS için .app bundle oluştur
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
