from pathlib import Path


project_root = Path(SPECPATH)

a = Analysis(
    [str(project_root / "build_entrypoint.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[(str(project_root / "templates"), "templates")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="create-python-app",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
