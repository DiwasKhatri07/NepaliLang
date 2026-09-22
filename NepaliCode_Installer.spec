# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NepaliCode All-in-One Installer
Creates a standalone installer like Python's setup.exe
"""

block_cipher = None

a = Analysis(
    ['NepaliLang_Setup.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('stdlib', 'stdlib'),
        ('examples', 'examples'),
        ('docs', 'docs'),
        ('vscode-extension', 'vscode-extension'),
        ('assets', 'assets'),
        ('main.py', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'win32com.client',
        'winreg',
        'ctypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NepaliCode_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)