
from pathlib import Path
import sqlite3


# ============================================================
# 路徑設定
# ============================================================

# 專案根目錄
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# SQL 結構檔案
SCHEMA_FILE = PROJECT_ROOT / "database" / "schema.sql"

# SQLite 資料庫檔案
DATABASE_FILE = PROJECT_ROOT / "data" / "collection.db"


# ============================================================
# 取得資料庫連線
# ============================================================

def get_connection():
    """建立 SQLite 連線，並啟用外鍵約束。"""

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_FILE)

    # 啟用外鍵約束
    connection.execute("PRAGMA foreign_keys = ON")

    # 查詢結果可使用欄位名稱取得資料
    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# 初始化資料庫
# ============================================================

def initialize_database():
    """讀取 schema.sql 並建立資料表。"""

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"找不到資料庫結構檔案：{SCHEMA_FILE}"
        )

    schema_sql = SCHEMA_FILE.read_text(
        encoding="utf-8"
    )

    with get_connection() as connection:
        connection.executescript(schema_sql)

    print("資料庫初始化完成。")
    print(f"資料庫位置：{DATABASE_FILE}")


# ============================================================
# 測試入口
# ============================================================

if __name__ == "__main__":
    initialize_database()
