
import sys

from ui.dashboard_page import DashboardPage
from ui.store_page import StorePage
from ui.storage_page import StoragePage
from ui.product_page import ProductPage
from ui.collection_page import CollectionPage
from ui.preorder_page import PreorderPage
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("模型與玩具收藏管理系統")
        self.resize(1200, 760)
        self.setMinimumSize(900, 600)

        self.init_ui()

    def init_ui(self):
        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左側導覽列
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 20)
        sidebar_layout.setSpacing(10)

        title = QLabel("模型收藏管理")
        title.setObjectName("app_title")
        title.setWordWrap(True)
        sidebar_layout.addWidget(title)

        subtitle = QLabel("MODEL COLLECTION")
        subtitle.setObjectName("app_subtitle")
        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addSpacing(24)

        # 內容區
        self.content_stack = QStackedWidget()

        # 頁面清單
        pages = [
            ("首頁儀表板", DashboardPage()),
            ("商品管理", ProductPage()),
            ("我的收藏", CollectionPage()),
            ("預購管理", PreorderPage()),
            ("收納管理", StoragePage()),
            ("店家管理", StorePage())
        ]

        self.nav_buttons = []

        for index, (page_name, page_widget) in enumerate(pages):
            button = QPushButton(page_name)
            button.setObjectName("nav_button")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, i=index: self.switch_page(i)
            )

            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)
            self.content_stack.addWidget(page_widget)

        sidebar_layout.addStretch()

        version_label = QLabel("版本 0.1.0")
        version_label.setObjectName("version_label")
        sidebar_layout.addWidget(version_label)

        # 加入主版面
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack, 1)

        # 樣式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F4F6F9;
            }

            #sidebar {
                background-color: #202B3C;
            }

            #app_title {
                color: #FFFFFF;
                font-size: 21px;
                font-weight: bold;
            }

            #app_subtitle {
                color: #AAB6C8;
                font-size: 10px;
                letter-spacing: 1px;
            }

            #nav_button {
                color: #DCE4EF;
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }

            #nav_button:hover {
                background-color: #344258;
            }

            #nav_button:checked {
                color: #FFFFFF;
                background-color: #4263A5;
                font-weight: bold;
            }

            #version_label {
                color: #AAB6C8;
                font-size: 11px;
            }

            #page_title {
                color: #202B3C;
                font-size: 26px;
                font-weight: bold;
            }

            #page_description {
                color: #667085;
                font-size: 14px;
            }

            #placeholder_card {
                background-color: #FFFFFF;
                border: 1px solid #E1E6ED;
                border-radius: 10px;
            }

            #placeholder_text {
                color: #667085;
                font-size: 15px;
            }
        """)

        self.switch_page(0)

    def create_placeholder_page(self, title_text, description_text):
        """建立尚未實作功能的暫時頁面"""

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(18)

        title = QLabel(title_text)
        title.setObjectName("page_title")
        layout.addWidget(title)

        description = QLabel(description_text)
        description.setObjectName("page_description")
        layout.addWidget(description)

        layout.addSpacing(12)

        card = QFrame()
        card.setObjectName("placeholder_card")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)

        message = QLabel(
            "此功能頁面尚未實作。\n"
            "後續將連接 SQLite 資料庫與 Repository。"
        )
        message.setObjectName("placeholder_text")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(message)
        layout.addWidget(card, 1)

        return page

    def switch_page(self, index):
        """切換頁面與導覽列狀態"""

        self.content_stack.setCurrentIndex(index)

        for button_index, button in enumerate(self.nav_buttons):
            button.setChecked(button_index == index)
