
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QDialogButtonBox,
    QMessageBox,
    QTextEdit,
    QDateEdit,
)

from repositories.collection_repository import CollectionRepository
from repositories.product_repository import ProductRepository
from repositories.storage_repository import StorageRepository


class CollectionDialog(QDialog):
    """新增或編輯持有品的對話視窗"""

    STATUSES = ["未開始", "製作中", "已完成", "展示中", "已收納"]
    CONDITIONS = ["全新", "良好", "輕微瑕疵", "損壞"]

    def __init__(self, item=None, parent=None):
        super().__init__(parent)

        self.item = item
        self.setWindowTitle("編輯持有品" if item else "新增持有品")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # 商品下拉選單
        self.product_input = QComboBox()
        self.products = ProductRepository.get_all_products()

        for product in self.products:
            self.product_input.addItem(
                product["商品名稱"],
                product["商品編號"]
            )

        # 收藏狀態
        self.status_input = QComboBox()
        self.status_input.addItems(self.STATUSES)

        # 商品狀況
        self.condition_input = QComboBox()
        self.condition_input.addItems(self.CONDITIONS)

        # 購買日期
        self.purchase_date_input = QDateEdit()
        self.purchase_date_input.setCalendarPopup(True)
        self.purchase_date_input.setDisplayFormat("yyyy-MM-dd")
        self.purchase_date_input.setSpecialValueText("未設定")
        self.purchase_date_input.setMinimumDate(
            self.purchase_date_input.minimumDate()
        )
        self.purchase_date_input.setDate(
            self.purchase_date_input.minimumDate()
        )

        # 購買價格
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setRange(0, 999999999)
        self.purchase_price_input.setDecimals(2)
        self.purchase_price_input.setSpecialValueText("未設定")

        # 數量
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 999999)

        # 是否開封、是否完成組裝
        self.opened_input = QComboBox()
        self.opened_input.addItem("未開封", 0)
        self.opened_input.addItem("已開封", 1)

        self.completed_input = QComboBox()
        self.completed_input.addItem("未完成組裝", 0)
        self.completed_input.addItem("已完成組裝", 1)

        # 收納位置
        self.location_input = QComboBox()
        self.location_input.addItem("未指定", None)

        self.locations = StorageRepository.get_all_locations()

        for location in self.locations:
            self.location_input.addItem(
                location["位置名稱"],
                location["位置編號"]
            )

        # 備註
        self.memo_input = QTextEdit()
        self.memo_input.setMaximumHeight(90)

        form.addRow("商品 *", self.product_input)
        form.addRow("收藏狀態", self.status_input)
        form.addRow("商品狀況", self.condition_input)
        form.addRow("購買日期", self.purchase_date_input)
        form.addRow("購買單價", self.purchase_price_input)
        form.addRow("數量", self.quantity_input)
        form.addRow("開封狀態", self.opened_input)
        form.addRow("組裝狀態", self.completed_input)
        form.addRow("收納位置", self.location_input)
        form.addRow("備註", self.memo_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if item:
            self.load_item(item)

    def load_item(self, item):
        """將既有持有品資料填入表單"""

        self.set_combo_data(
            self.product_input, item.get("商品編號")
        )
        self.set_combo_text(
            self.status_input, item.get("收藏狀態")
        )
        self.set_combo_text(
            self.condition_input, item.get("商品狀況")
        )

        purchase_date = item.get("購買日期")

        if purchase_date:
            from PySide6.QtCore import QDate

            date_value = QDate.fromString(
                purchase_date, "yyyy-MM-dd"
            )

            if date_value.isValid():
                self.purchase_date_input.setDate(date_value)

        price = item.get("購買單價")

        if price is not None:
            self.purchase_price_input.setValue(float(price))

        self.quantity_input.setValue(
            int(item.get("數量") or 1)
        )

        self.set_combo_data(
            self.opened_input, item.get("是否開封", 0)
        )
        self.set_combo_data(
            self.completed_input,
            item.get("是否完成組裝", 0)
        )
        self.set_combo_data(
            self.location_input,
            item.get("收納位置編號")
        )

        self.memo_input.setPlainText(item.get("備註") or "")

    @staticmethod
    def set_combo_data(combo, value):
        index = combo.findData(value)

        if index >= 0:
            combo.setCurrentIndex(index)

    @staticmethod
    def set_combo_text(combo, value):
        if value is None:
            return

        index = combo.findText(str(value))

        if index >= 0:
            combo.setCurrentIndex(index)

    def validate_and_accept(self):
        if self.product_input.currentIndex() < 0:
            QMessageBox.warning(
                self,
                "缺少商品",
                "目前沒有可選擇的商品，請先到商品管理新增商品。"
            )
            return

        self.accept()

    def get_data(self):
        """取得準備寫入資料庫的欄位"""

        purchase_date = None

        if self.purchase_date_input.date() != (
            self.purchase_date_input.minimumDate()
        ):
            purchase_date = (
                self.purchase_date_input.date().toString("yyyy-MM-dd")
            )

        price = self.purchase_price_input.value()

        return {
            "商品編號": self.product_input.currentData(),
            "收藏狀態": self.status_input.currentText(),
            "商品狀況": self.condition_input.currentText(),
            "購買日期": purchase_date,
            "購買單價": price if price > 0 else None,
            "數量": self.quantity_input.value(),
            "是否開封": self.opened_input.currentData(),
            "是否完成組裝": self.completed_input.currentData(),
            "收納位置編號": self.location_input.currentData(),
            "備註": self.memo_input.toPlainText().strip() or None,
        }


class CollectionPage(QWidget):
    """我的收藏管理頁面"""

    COLUMNS = [
        ("持有品編號", "持有品編號"),
        ("商品名稱", "商品名稱"),
        ("收藏狀態", "收藏狀態"),
        ("商品狀況", "商品狀況"),
        ("購買單價", "購買單價"),
        ("數量", "數量"),
        ("是否開封", "是否開封"),
        ("是否完成組裝", "是否完成組裝"),
        ("位置名稱", "收納位置"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_items()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("我的收藏")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #202B3C;"
        )
        layout.addWidget(title)

        description = QLabel(
            "管理持有品、開封狀態、組裝進度與收納位置。"
        )
        description.setStyleSheet("color: #667085;")
        layout.addWidget(description)

        # 搜尋列
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "搜尋商品名稱、品牌或備註……"
        )
        self.search_input.returnPressed.connect(self.search_items)

        search_button = QPushButton("搜尋")
        search_button.clicked.connect(self.search_items)

        reset_button = QPushButton("顯示全部")
        reset_button.clicked.connect(self.load_items)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(reset_button)

        layout.addLayout(search_layout)

        # 操作按鈕
        button_layout = QHBoxLayout()

        add_button = QPushButton("新增持有品")
        add_button.clicked.connect(self.add_item)

        edit_button = QPushButton("編輯持有品")
        edit_button.clicked.connect(self.edit_item)

        delete_button = QPushButton("刪除持有品")
        delete_button.clicked.connect(self.delete_item)

        refresh_button = QPushButton("重新載入")
        refresh_button.clicked.connect(self.load_items)

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)

        # 統計列
        self.statistics_label = QLabel("收藏統計：載入中")
        self.statistics_label.setStyleSheet(
            "font-size: 13px; color: #475467;"
        )
        layout.addWidget(self.statistics_label)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(
            [column[1] for column in self.COLUMNS]
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

        self.table.cellDoubleClicked.connect(
            lambda row, column: self.edit_item()
        )

        layout.addWidget(self.table, 1)

        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #667085;")
        layout.addWidget(self.status_label)

    def load_items(self):
        """載入全部持有品"""

        try:
            items = CollectionRepository.get_all_items()
            self.show_items(items)
            self.update_statistics()
            self.status_label.setText(f"共 {len(items)} 筆持有紀錄")
        except Exception as error:
            QMessageBox.critical(
                self, "載入失敗", f"無法載入收藏資料：\n{error}"
            )

    def search_items(self):
        """搜尋持有品"""

        keyword = self.search_input.text().strip()

        if not keyword:
            self.load_items()
            return

        try:
            items = CollectionRepository.search_items(keyword)
            self.show_items(items)
            self.status_label.setText(
                f"搜尋「{keyword}」：共 {len(items)} 筆"
            )
        except Exception as error:
            QMessageBox.critical(
                self, "搜尋失敗", f"無法搜尋收藏：\n{error}"
            )

    def show_items(self, items):
        self.table.setRowCount(0)

        for item_data in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for column, (field, _) in enumerate(self.COLUMNS):
                value = item_data.get(field)

                if field == "是否開封":
                    text = "已開封" if value else "未開封"
                elif field == "是否完成組裝":
                    text = "已完成" if value else "未完成"
                elif value is None:
                    text = ""
                else:
                    text = str(value)

                item = QTableWidgetItem(text)

                if field in ("持有品編號", "數量"):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(row, column, item)

    def update_statistics(self):
        """更新收藏統計"""

        stats = CollectionRepository.get_statistics()

        self.statistics_label.setText(
            f"持有紀錄：{stats.get('總筆數', stats.get('持有品數', 0))}　"
            f"總數量：{stats.get('總數量', 0)}　"
            f"未開始：{stats.get('未開始數', 0)}　"
            f"製作中：{stats.get('製作中數', 0)}　"
            f"已完成組裝：{stats.get('已完成組裝數', 0)}"
        )

    def get_selected_item_id(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self, "尚未選取", "請先在表格中選取一筆持有品。"
            )
            return None

        cell = self.table.item(row, 0)

        if cell is None:
            return None

        return int(cell.text())

    def add_item(self):
        try:
            products = ProductRepository.get_all_products()

            if not products:
                QMessageBox.information(
                    self,
                    "沒有商品",
                    "請先到「商品管理」新增商品，再建立收藏。"
                )
                return

            dialog = CollectionDialog(parent=self)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()

            item_id = CollectionRepository.add_item(
                product_id=data["商品編號"],
                status=data["收藏狀態"],
                condition=data["商品狀況"],
                purchase_date=data["購買日期"],
                purchase_price=data["購買單價"],
                quantity=data["數量"],
                is_opened=data["是否開封"],
                is_completed=data["是否完成組裝"],
                storage_location_id=data["收納位置編號"],
                memo=data["備註"],
            )

            self.load_items()
            self.status_label.setText(
                f"新增持有品成功，編號：{item_id}"
            )

        except Exception as error:
            QMessageBox.critical(
                self, "新增失敗", f"無法新增持有品：\n{error}"
            )

    def edit_item(self):
        item_id = self.get_selected_item_id()

        if item_id is None:
            return

        try:
            item_data = CollectionRepository.get_item_by_id(item_id)

            if item_data is None:
                QMessageBox.warning(
                    self, "找不到資料", "該持有品可能已被刪除。"
                )
                self.load_items()
                return

            dialog = CollectionDialog(item=item_data, parent=self)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()
            success = CollectionRepository.update_item(
                item_id, **data
            )

            if success:
                self.load_items()
                self.status_label.setText(
                    f"持有品 {item_id} 已更新"
                )
            else:
                QMessageBox.warning(
                    self, "修改失敗", "找不到指定的持有品。"
                )

        except Exception as error:
            QMessageBox.critical(
                self, "修改失敗", f"無法修改持有品：\n{error}"
            )

    def delete_item(self):
        item_id = self.get_selected_item_id()

        if item_id is None:
            return

        answer = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除持有品編號 {item_id} 嗎？\n"
            "這只會刪除持有紀錄，不會刪除商品主檔。",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            success = CollectionRepository.delete_item(item_id)

            if success:
                self.load_items()
                self.status_label.setText(
                    f"持有品 {item_id} 已刪除"
                )
            else:
                QMessageBox.warning(
                    self, "刪除失敗", "找不到指定的持有品。"
                )

        except Exception as error:
            QMessageBox.critical(
                self, "刪除失敗", f"無法刪除持有品：\n{error}"
            )
