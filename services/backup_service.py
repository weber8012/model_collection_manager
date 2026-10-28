from pathlib import Path
from datetime import datetime
import shutil
import sqlite3
from contextlib import closing

from database.database import DATABASE_FILE


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIRECTORY = PROJECT_ROOT / "backup"


class BackupService:
    """SQLite 資料庫備份服務"""

    @staticmethod
    def get_backup_directory():
        """取得備份資料夾"""

        BACKUP_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True
        )

        return BACKUP_DIRECTORY

    
    @staticmethod
    def validate_database(database_path):
        """
        檢查指定檔案是否為有效的 SQLite 資料庫。
    
        Returns:
            tuple[bool, str]
        """
        from contextlib import closing
    
        database_path = Path(database_path)
    
        if not database_path.exists():
            return False, "找不到資料庫檔案。"
    
        if not database_path.is_file():
            return False, "指定的路徑不是檔案。"
    
        try:
            with closing(sqlite3.connect(database_path)) as connection:
                result = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()
    
            if not result:
                return False, "無法取得 SQLite 完整性檢查結果。"
    
            if result[0] != "ok":
                return False, (
                    f"SQLite 完整性檢查失敗：{result[0]}"
                )
    
            return True, "SQLite 資料庫檢查通過。"
    
        except sqlite3.DatabaseError as error:
            return False, (
                f"檔案不是有效的 SQLite 資料庫：{error}"
            )


    @staticmethod
    def create_backup():
        """
        建立目前資料庫的備份。

        Returns:
            Path: 備份檔案路徑
        """

        if not DATABASE_FILE.exists():
            raise FileNotFoundError(
                f"找不到目前資料庫：{DATABASE_FILE}"
            )

        # 先確認目前資料庫完整性
        valid, message = (
            BackupService.validate_database(DATABASE_FILE)
        )

        if not valid:
            raise RuntimeError(
                f"目前資料庫無法備份：{message}"
            )

        backup_directory = (
            BackupService.get_backup_directory()
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_file = (
            backup_directory
            / f"collection_{timestamp}.db"
        )

        # 避免同一秒建立同名檔案
        counter = 1

        while backup_file.exists():
            backup_file = (
                backup_directory
                / f"collection_{timestamp}_{counter}.db"
            )
            counter += 1

        shutil.copy2(
            DATABASE_FILE,
            backup_file
        )

        # 再驗證備份檔
        valid, message = (
            BackupService.validate_database(
                backup_file
            )
        )

        if not valid:
            try:
                backup_file.unlink()
            except OSError:
                pass

            raise RuntimeError(
                f"備份檔驗證失敗：{message}"
            )

        return backup_file

    @staticmethod
    def create_backup_from(database_path):
        """備份指定的 SQLite 資料庫。"""

        database_path = Path(database_path).resolve()

        if not database_path.is_file():
            raise FileNotFoundError(
                f"找不到要備份的資料庫：{database_path}"
            )

        valid, message = BackupService.validate_database(
            database_path
        )

        if not valid:
            raise RuntimeError(
                f"資料庫無法備份：{message}"
            )

        backup_directory = BackupService.get_backup_directory()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = (
            backup_directory / f"collection_{timestamp}.db"
        )

        counter = 1

        while backup_file.exists():
            backup_file = (
                backup_directory
                / f"collection_{timestamp}_{counter}.db"
            )
            counter += 1

        # 使用 SQLite Backup API 建立一致的資料庫副本
        with sqlite3.connect(database_path) as source:
            with sqlite3.connect(backup_file) as target:
                source.backup(target)

        valid, message = BackupService.validate_database(
            backup_file
        )

        if not valid:
            try:
                backup_file.unlink()
            except OSError:
                pass

            raise RuntimeError(
                f"備份檔驗證失敗：{message}"
            )

        return backup_file

    @staticmethod
    def get_backups():
        """
        取得所有資料庫備份。

        Returns:
            list[Path]
        """

        backup_directory = (
            BackupService.get_backup_directory()
        )

        backups = sorted(
            backup_directory.glob(
                "collection_*.db"
            ),
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        return backups

    @staticmethod
    def restore_backup(backup_path, database_path=None):
        """
        從指定備份還原資料庫。

        還原前先備份目前資料庫，並驗證來源備份。
        還原後若驗證失敗，嘗試恢復還原前的資料庫。

        Returns:
            tuple[bool, str]
        """

        backup_path = Path(backup_path).resolve()
        current_database = Path(
            database_path if database_path is not None else DATABASE_FILE
            ).resolve()
        if not backup_path.is_file():
            return False, "找不到指定的備份檔案。"

        if backup_path == current_database:
            return False, "不能將目前使用中的資料庫當作備份來源。"

        # 還原前驗證來源備份
        valid, message = BackupService.validate_database(
            backup_path
        )

        if not valid:
            return False, f"備份檔驗證失敗：{message}"

        # 檢查來源資料庫的外鍵
        
        try:
            with closing(sqlite3.connect(backup_path)) as connection:
                foreign_key_errors = connection.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
        
            if foreign_key_errors:
                return False, (
                    "備份檔存在外鍵違規，已取消還原。"
                )
        
        except sqlite3.DatabaseError as error:
            return False, f"無法檢查備份檔：{error}"

        # 先建立還原前的安全備份
        try:
            safety_backup = BackupService.create_backup_from(
                current_database
                )
        except Exception as error:
            return False, f"無法建立還原前安全備份，已取消還原：{error}"

        # 使用 SQLite Backup API 載入來源資料庫。
        # 不直接覆蓋檔案，避免一般檔案複製方式的風險。
        temporary_file = None

        try:
            import tempfile
            import os

            current_database.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            fd, temporary_name = tempfile.mkstemp(
                prefix="restore_",
                suffix=".db",
                dir=str(current_database.parent)
            )
            os.close(fd)
            temporary_file = Path(temporary_name)

            with closing(sqlite3.connect(backup_path)) as source:
                with closing(sqlite3.connect(temporary_file)) as target:
                    source.backup(target)

            valid, message = (
                BackupService.validate_database(
                    temporary_file
                )
            )

            if not valid:
                raise RuntimeError(
                    f"還原暫存檔驗證失敗：{message}"
                )

            # 以 SQLite Backup API 將暫存資料庫還原至目前資料庫。
            # 連線關閉後才進行完整性與外鍵檢查。
            with closing(sqlite3.connect(temporary_file)) as source:
                with closing(sqlite3.connect(current_database)) as target:
                    source.backup(target)

                    integrity = target.execute(
                        "PRAGMA integrity_check"
                        ).fetchone()

                    foreign_key_errors = target.execute(
                        "PRAGMA foreign_key_check"
                        ).fetchall()
            if not integrity or integrity[0] != "ok":
                raise RuntimeError(
                    f"還原後完整性檢查失敗：{integrity}"
                )

            if foreign_key_errors:
                raise RuntimeError(
                    "還原後發現外鍵違規。"
                )

            return True, (
                "資料庫還原成功。\n"
                f"還原來源：{backup_path}\n"
                f"還原前安全備份：{safety_backup}"
            )

        except Exception as error:
            # 還原失敗時，嘗試由安全備份恢復。
            try:
                with closing(sqlite3.connect(safety_backup)) as source:
                    with closing(sqlite3.connect(current_database)) as target:
                        source.backup(target)
                    return False, (
                    f"還原失敗，已嘗試恢復原資料庫。\n"
                    f"錯誤：{error}\n"
                    f"安全備份：{safety_backup}"
                )

            except Exception as recovery_error:
                return False, (
                    f"還原失敗：{error}\n"
                    f"自動恢復也失敗：{recovery_error}\n"
                    f"請保留安全備份：{safety_backup}"
                )

        finally:
            if temporary_file and temporary_file.exists():
                try:
                    temporary_file.unlink()
                except OSError:
                    pass




if __name__ == "__main__":
    print("=" * 60)
    print("資料庫備份服務測試")
    print("=" * 60)

    try:
        backup_file = (
            BackupService.create_backup()
        )

        print()
        print("備份成功")
        print(f"備份檔案：{backup_file}")

        print()
        print("目前備份清單：")

        backups = BackupService.get_backups()

        for backup in backups:
            print(f" - {backup}")

    except Exception as error:
        print()
        print("備份失敗")
        print(f"錯誤：{error}")