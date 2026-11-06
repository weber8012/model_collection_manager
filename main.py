
import sys
import subprocess
from pathlib import Path

from database.database import initialize_database


def main():
    # 初始化資料庫
    initialize_database()

    # PyInstaller 打包版本
    if getattr(sys, "frozen", False):

        from run_app import main as run_gui

        run_gui()

    # 開發環境
    else:
        project_root = Path(__file__).resolve().parent
        app_script = project_root / "run_app.py"

        # 使用獨立程序啟動 GUI
        subprocess.Popen(
            [sys.executable, str(app_script)],
            cwd=str(project_root)
        )

        print("桌面程式已啟動。")


if __name__ == "__main__":
    main()
