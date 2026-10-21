
import sys
import subprocess
from pathlib import Path

from database.database import initialize_database


def main():
    initialize_database()

    # 使用目前 Spyder 所使用的 Python 解譯器，
    # 以獨立程序啟動桌面視窗。
    project_root = Path(__file__).resolve().parent
    app_script = project_root / "run_app.py"

    subprocess.Popen(
        [sys.executable, str(app_script)],
        cwd=str(project_root)
    )

    print("桌面程式已啟動。")


if __name__ == "__main__":
    main()
