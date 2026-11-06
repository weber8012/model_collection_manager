
import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.paths import THEME_FILE, COMBOBOX_ARROW_FILE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("模型與玩具收藏管理系統")

    # 載入全域 QSS 樣式
    if THEME_FILE.exists():
        with open(THEME_FILE, "r", encoding="utf-8") as file:
            stylesheet = file.read()

        # 自動處理 SVG 相對路徑
        stylesheet = stylesheet.replace(
            'url("combobox_arrow.svg")',
            f'url("{COMBOBOX_ARROW_FILE.as_posix()}")'
        )

        app.setStyleSheet(stylesheet)
    else:
        print(f"找不到樣式檔案：{THEME_FILE}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
