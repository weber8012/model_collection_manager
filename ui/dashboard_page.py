
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QMessageBox,
)

from repositories.product_repository import ProductRepository
from repositories.collection_repository import CollectionRepository
from repositories.preorder_repository import PreorderRepository
from repositories.storage_repository import StorageRepository


class DashboardPage(QWidget):
    """首頁統計儀表板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        # 標題
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel("首頁儀表板")
        title.setStyleSheet(
            "font-size: 28px; "
            "font-weight: bold; "
            "color: #202B3C;"
        )

        subtitle = QLabel(
            "查看商品、收藏、預購與收納的整體狀況。"
        )
        subtitle.setStyleSheet(
            "font-size: 13px; color: #667085;"
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        refresh_button = QPushButton("重新整理")
        refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_button)

        layout.addLayout(header_layout)

        # 統計卡片區域
        grid = QGridLayout()
        grid.setSpacing(16)

        self.cards = {}

        card_definitions = [
            ("商品種類", "商品資料庫中的商品筆數"),
            ("收藏紀錄", "我的收藏紀錄筆數"),
            ("持有總數", "所有收藏紀錄的數量合計"),
            ("已完成組裝", "已標記完成組裝的收藏紀錄"),
            ("未開始", "收藏狀態為未開始的紀錄"),
            ("製作中", "收藏狀態為製作中的紀錄"),
            ("預購筆數", "目前登記的預購紀錄"),
            ("預購中", "狀態為預購中的紀錄"),
            ("未付款", "付款狀態為未付款的紀錄"),
            ("收納位置", "已建立的收納位置數"),
            ("已指定位置", "已指定收納位置的持有數量"),
        ]

        for index, (name, description) in enumerate(
            card_definitions
        ):
            card = self.create_stat_card(
                name, description
            )

            row = index // 3
            column = index % 3

            grid.addWidget(card, row, column)

        layout.addLayout(grid)

        # 說明區域
        note = QFrame()
        note.setStyleSheet(
            "QFrame {"
            "background-color: #F2F4F7;"
            "border-radius: 8px;"
            "}"
        )

        note_layout = QVBoxLayout(note)

        note_title = QLabel("使用說明")
        note_title.setStyleSheet(
            "font-size: 15px; "
            "font-weight: bold; "
            "color: #344054;"
        )

        note_text = QLabel(
            "本頁數字來自目前的 SQLite 資料庫。"
            "新增、修改或刪除資料後，按下「重新整理」"
            "即可重新計算。"
        )
        note_text.setWordWrap(True)
        note_text.setStyleSheet(
            "font-size: 13px; color: #475467;"
        )

        note_layout.addWidget(note_title)
        note_layout.addWidget(note_text)

        layout.addWidget(note)
        layout.addStretch()

    def create_stat_card(self, name, description):
        card = QFrame()
        card.setMinimumHeight(125)
        card.setStyleSheet(
            "QFrame {"
            "background-color: #FFFFFF;"
            "border: 1px solid #E4E7EC;"
            "border-radius: 10px;"
            "}"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        name_label = QLabel(name)
        name_label.setStyleSheet(
            "font-size: 14px; "
            "font-weight: bold; "
            "color: #475467;"
            "border: none;"
        )

        value_label = QLabel("—")
        value_label.setStyleSheet(
            "font-size: 30px; "
            "font-weight: bold; "
            "color: #175CD3;"
            "border: none;"
        )

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(
            "font-size: 11px; "
            "color: #667085;"
            "border: none;"
        )

        card_layout.addWidget(name_label)
        card_layout.addWidget(value_label)
        card_layout.addWidget(description_label)

        self.cards[name] = value_label

        return card

    def refresh_data(self):
        """重新讀取資料並更新統計"""

        try:
            products = ProductRepository.get_all_products()

            collection_stats = (
                CollectionRepository.get_statistics()
            )

            collection_items = (
                CollectionRepository.get_all_items()
            )

            preorders = (
                PreorderRepository.get_all_preorders()
            )

            locations = (
                StorageRepository.get_all_locations()
            )

            # 商品統計
            product_count = len(products)

            # 收藏統計
            collection_count = collection_stats.get(
                "總筆數",
                collection_stats.get("持有品數", 0)
            )

            total_quantity = collection_stats.get(
                "總數量", 0
            )

            unstarted_count = collection_stats.get(
                "未開始數", 0
            )

            in_progress_count = collection_stats.get(
                "製作中數", 0
            )

            completed_count = collection_stats.get(
                "已完成組裝數", 0
            )

            # 預購統計
            preorder_count = len(preorders)

            active_preorders = sum(
                1 for item in preorders
                if item.get("預購狀態") == "預購中"
            )

            unpaid_count = sum(
                1 for item in preorders
                if item.get("付款狀態") == "未付款"
            )

            # 收納統計
            location_count = len(locations)

            stored_quantity = sum(
                int(item.get("數量") or 0)
                for item in collection_items
                if item.get("收納位置編號") is not None
            )

            # 更新畫面
            values = {
                "商品種類": product_count,
                "收藏紀錄": collection_count,
                "持有總數": total_quantity,
                "已完成組裝": completed_count,
                "未開始": unstarted_count,
                "製作中": in_progress_count,
                "預購筆數": preorder_count,
                "預購中": active_preorders,
                "未付款": unpaid_count,
                "收納位置": location_count,
                "已指定位置": stored_quantity,
            }

            for name, value in values.items():
                self.cards[name].setText(
                    f"{int(value or 0):,}"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "統計資料載入失敗",
                "無法取得完整的儀表板資料。\n\n"
                f"錯誤訊息：{error}"
            )
