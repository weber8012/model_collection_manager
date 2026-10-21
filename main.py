
import sys

from PySide6.QtWidgets import QApplication

from database.database import initialize_database
from ui.main_window import MainWindow


def main():
    # 確保資料庫與資料表已初始化
    initialize_database()

    app = QApplication(sys.argv)
    app.setApplicationName("模型與玩具收藏管理系統")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
