# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path.cwd()
src_dir = project_root / "ai" / "src"

datas = [
    (str(project_root / "ai" / "assets"), "assets"),
    (str(project_root / "ai" / "Free"), "Free"),
]


a = Analysis(
    [str(src_dir / "Main.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name="Mario remake",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name="Mario remake.app",
    icon=str(project_root / "ai" / "assets" / "images" / "mario_remake.icns"),
    bundle_identifier="com.quoczai22.marioremake",
)
