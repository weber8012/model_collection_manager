
# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

PROJECT_ROOT = Path(r"D:\model_collection_manager")

datas = [
    (
        str(PROJECT_ROOT / "database" / "schema.sql"),
        "database"
    ),
    (
        str(PROJECT_ROOT / "ui" / "styles" / "theme.qss"),
        "ui/styles"
    ),
    (
        str(PROJECT_ROOT / "ui" / "styles" / "combobox_arrow.svg"),
        "ui/styles"
    ),
]

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
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
    [],
    exclude_binaries=True,
    name="model_collection_manager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="model_collection_manager",
)
