
from pathlib import Path
import sqlite3
import tempfile
import gc
from contextlib import closing

from services.backup_service import BackupService


def create_test_database(database_path, product_name):
    """建立獨立的測試資料庫。"""

    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("""
            CREATE TABLE test_products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        connection.execute(
            "INSERT INTO test_products (name) VALUES (?)",
            (product_name,)
        )

        connection.commit()

def get_test_product_name(database_path):
    """讀取測試資料庫中的商品名稱。"""

    with closing(sqlite3.connect(database_path)) as connection:
        row = connection.execute(
            "SELECT name FROM test_products ORDER BY id LIMIT 1"
        ).fetchone()

    return row[0] if row else None

def create_sqlite_backup(source_path, backup_path):
    """使用 SQLite Backup API 建立獨立備份。"""

    with closing(sqlite3.connect(source_path)) as source:
        with closing(sqlite3.connect(backup_path)) as target:
            source.backup(target)

def main():
    print("=" * 60)
    print("正式還原服務：隔離測試")
    print("=" * 60)

    with tempfile.TemporaryDirectory(
        prefix="collection_restore_service_test_"
    ) as temp_directory:

        temp_path = Path(temp_directory)

        test_database = temp_path / "test_collection.db"
        source_backup = temp_path / "source_backup.db"

        # 測試 1：建立目前的測試資料庫
        create_test_database(
            test_database,
            "還原前的測試商品"
        )

        assert (
            get_test_product_name(test_database)
            == "還原前的測試商品"
        )
        print("\n[測試 1] 建立測試資料庫：通過")

        # 測試 2：建立要還原的備份
        source_database = temp_path / "source_database.db"

        create_test_database(
            source_database,
            "備份中的測試商品"
        )

        create_sqlite_backup(
            source_database,
            source_backup
        )

        valid, message = BackupService.validate_database(
            source_backup
        )

        assert valid, message
        print("[測試 2] 建立有效的來源備份：通過")

        # 測試 3：呼叫正式還原方法，但指定測試資料庫
        success, message = BackupService.restore_backup(
            source_backup,
            database_path=test_database
        )

        print("\n[測試 3] 正式還原服務")
        print(message)

        assert success, message
        print("通過")

        # 測試 4：確認資料確實還原
        restored_name = get_test_product_name(test_database)

        print("\n[測試 4] 驗證還原後資料")
        print("實際資料：", restored_name)

        assert restored_name == "備份中的測試商品"
        print("通過")

        # 測試 5：確認還原前安全備份已建立
        safety_backup = None

        for line in message.splitlines():
            if line.startswith("還原前安全備份："):
                safety_backup = Path(
                    line.split("：", 1)[1].strip()
                )
                break

        print("\n[測試 5] 驗證安全備份")

        assert safety_backup is not None, (
            "還原成功訊息中找不到安全備份路徑。"
        )
        assert safety_backup.is_file(), (
            f"安全備份檔不存在：{safety_backup}"
        )

        valid, validation_message = (
            BackupService.validate_database(safety_backup)
        )

        assert valid, validation_message

        safety_name = get_test_product_name(safety_backup)
        assert safety_name == "還原前的測試商品"

        print("安全備份資料：", safety_name)
        print("通過")

        # 測試 6：檢查還原後的 SQLite 完整性與外鍵
        with closing(sqlite3.connect(test_database)) as connection:
            integrity = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()
        
            foreign_key_errors = connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()
        assert integrity and integrity[0] == "ok"
        assert not foreign_key_errors

        print("\n[測試 6] 完整性與外鍵檢查：通過")

        # 清理前釋放物件引用
        del integrity
        del foreign_key_errors
        gc.collect()

    print("\n" + "=" * 60)
    print("正式還原服務的隔離測試全部通過。")
    print("測試資料庫已自動清理。")
    print("=" * 60)


if __name__ == "__main__":
    main()
