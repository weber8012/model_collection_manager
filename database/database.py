
import sqlite3

from utils.paths import DATABASE_FILE, SCHEMA_FILE


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
# 資料庫完整性檢查
# ============================================================

def check_database_integrity():
    with get_connection() as connection:

        # 檢查資料庫完整性
        integrity_results = connection.execute(
            "PRAGMA integrity_check"
        ).fetchall()

        # 檢查外鍵關聯
        foreign_key_results = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

    print("\n=== SQLite 完整性檢查 ===")

    for row in integrity_results:
        print("資料庫檢查：", row[0])

    if not foreign_key_results:
        print("外鍵檢查：通過")
    else:
        print("外鍵檢查：發現問題")

        for row in foreign_key_results:
            print(tuple(row))


# ============================================================
# 測試入口
# ============================================================

if __name__ == "__main__":
    initialize_database()
    check_database_integrity()
