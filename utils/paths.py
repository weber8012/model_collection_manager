# -*- coding: utf-8 -*-


from pathlib import Path
import sys


# ============================================================
# 路徑管理
# ============================================================

# 是否為 PyInstaller 打包版本
IS_FROZEN = getattr(sys, "frozen", False)


# ============================================================
# 程式資源路徑
# ============================================================

if IS_FROZEN:
    # PyInstaller 內部資源目錄
    RESOURCE_ROOT = Path(sys._MEIPASS)
else:
    # 開發環境專案根目錄
    RESOURCE_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# 應用程式資料路徑
# ============================================================

if IS_FROZEN:
    # 正式版：EXE 所在目錄
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    # 開發版：專案根目錄
    APP_ROOT = RESOURCE_ROOT


# ============================================================
# SQLite 資料庫
# ============================================================

DATABASE_FILE = APP_ROOT / "data" / "collection.db"


# ============================================================
# SQL 結構檔案
# ============================================================

SCHEMA_FILE = RESOURCE_ROOT / "database" / "schema.sql"


# ============================================================
# 備份目錄
# ============================================================

BACKUP_DIRECTORY = APP_ROOT / "backup"


# ============================================================
# UI 資源
# ============================================================

UI_DIRECTORY = RESOURCE_ROOT / "ui"

STYLE_DIRECTORY = UI_DIRECTORY / "styles"

THEME_FILE = STYLE_DIRECTORY / "theme.qss"

COMBOBOX_ARROW_FILE = STYLE_DIRECTORY / "combobox_arrow.svg"
