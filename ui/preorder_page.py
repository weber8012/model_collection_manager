
from PySide6.QtCore import Qt, QDate
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

from repositories.preorder_repository import PreorderRepository
from repositories.product_repository import ProductRepository
from repositories.store_repository import StoreRepository


class PreorderDialog(QDialog):
    """新增或編輯預購資料"""

    PREORDER_STATUSES = [
        "預購中", "已到貨", "已取消"
    ]

    PAYMENT_STATUSES = [
        "未付款", "部分付款", "已付款"
    ]

    def __init__(self, preorder=None, parent=None):
        super().__init__(parent)

        self.preorder = preorder
        self.setWindowTitle(
            "編輯預購" if preorder else "新增預購"
        )
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # 商品
        self.product_input = QComboBox()
        products = ProductRepository.get_all_products()

        for product in products:
            self.product_input.addItem(
                product["商品名稱"],
                product["商品編號"]
            )

        # 預購店家
        self.store_input = QComboBox()
        self.store_input.addItem("未指定", None)

        stores = StoreRepository.get_all_stores()

        for store in stores:
            self.store_input.addItem(
                store["店家名稱"],
                store["店家編號"]
            )

        # 日期欄位：允許不設定
        self.preorder_date_input = self.create_date_input()
        self.release_date_input = self.create_date_input()
        self.arrival_date_input = self.create_date_input()

        # 數量
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 999999)
        self.quantity_input.setValue(1)

        # 金額
        self.price_input = self.create_money_input()
        self.deposit_input = self.create_money_input()
        self.shipping_input = self.create_money_input()
        self.paid_balance_input = self.create_money_input()

        # 預購狀態
        self.preorder_status_input = QComboBox()
        self.preorder_status_input.addItems(
            self.PREORDER_STATUSES
        )

        # 付款狀態
        self.payment_status_input = QComboBox()
        self.payment_status_input.addItems(
            self.PAYMENT_STATUSES
        )

        # 訂單編號與備註
        self.order_number_input = QLineEdit()
        self.memo_input = QTextEdit()
        self.memo_input.setMaximumHeight(80)

        form.addRow("商品 *", self.product_input)
        form.addRow("預購店家", self.store_input)
        form.addRow("預購日期", self.preorder_date_input)
        form.addRow("預計發售日期", self.release_date_input)
        form.addRow("預計到貨日期", self.arrival_date_input)
        form.addRow("預購數量", self.quantity_input)
        form.addRow("預購單價", self.price_input)
        form.addRow("訂金", self.deposit_input)
        form.addRow("運費", self.shipping_input)
        form.addRow("已付尾款", self.paid_balance_input)
        form.addRow("預購狀態", self.preorder_status_input)
        form.addRow("付款狀態", self.payment_status_input)
        form.addRow("訂單編號", self.order_number_input)
        form.addRow("備註", self.memo_input)

        layout.addLayout(form)

        self.total_label = QLabel("預估總額：請輸入單價與數量")
        self.total_label.setStyleSheet(
            "font-weight: bold; color: #475467;"
        )
        layout.addWidget(self.total_label)

        # 即時更新預估總額
        self.price_input.valueChanged.connect(
            self.update_total_preview
        )
        self.quantity_input.valueChanged.connect(
            self.update_total_preview
        )
        self.shipping_input.valueChanged.connect(
            self.update_total_preview
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if preorder:
            self.load_preorder(preorder)

        self.update_total_preview()

    @staticmethod
    def create_date_input():
        widget = QDateEdit()
        widget.setCalendarPopup(True)
        widget.setDisplayFormat("yyyy-MM-dd")
        widget.setSpecialValueText("未設定")
        widget.setMinimumDate(QDate(2000, 1, 1))
        widget.setDate(widget.minimumDate())
        return widget

    @staticmethod
    def create_money_input():
        widget = QDoubleSpinBox()
        widget.setRange(0, 999999999)
        widget.setDecimals(2)
        return widget

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

    def load_preorder(self, preorder):
        """將既有預購資料填入表單"""

        self.set_combo_data(
            self.product_input,
            preorder.get("商品編號")
        )
        self.set_combo_data(
            self.store_input,
            preorder.get("店家編號")
        )

        date_fields = [
            ("預購日期", self.preorder_date_input),
            ("預計發售日期", self.release_date_input),
            ("預計到貨日期", self.arrival_date_input),
        ]

        for field, widget in date_fields:
            value = preorder.get(field)
            if value:
                date_value = QDate.fromString(
                    str(value), "yyyy-MM-dd"
                )
                if date_value.isValid():
                    widget.setDate(date_value)

        self.quantity_input.setValue(
            int(preorder.get("預購數量") or 1)
        )

        money_fields = [
            ("預購單價", self.price_input),
            ("訂金", self.deposit_input),
            ("運費", self.shipping_input),
            ("已付尾款", self.paid_balance_input),
        ]

        for field, widget in money_fields:
            value = preorder.get(field)
            if value is not None:
                widget.setValue(float(value))

        self.set_combo_text(
            self.preorder_status_input,
            preorder.get("預購狀態")
        )
        self.set_combo_text(
            self.payment_status_input,
            preorder.get("付款狀態")
        )

        self.order_number_input.setText(
            preorder.get("訂單編號") or ""
        )
        self.memo_input.setPlainText(
            preorder.get("備註") or ""
        )

    def read_date(self, widget):
        if widget.date() == widget.minimumDate():
            return None
        return widget.date().toString("yyyy-MM-dd")

    def update_total_preview(self):
        total = (
            self.price_input.value()
            * self.quantity_input.value()
            + self.shipping_input.value()
        )

        self.total_label.setText(
            f"預估總額（單價 × 數量 + 運費）：{total:,.2f}"
        )

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
        return {
            "商品編號": self.product_input.currentData(),
            "店家編號": self.store_input.currentData(),
            "預購日期": self.read_date(
                self.preorder_date_input
            ),
            "預計發售日期": self.read_date(
                self.release_date_input
            ),
            "預計到貨日期": self.read_date(
                self.arrival_date_input
            ),
            "預購數量": self.quantity_input.value(),
            "預購單價": self.price_input.value(),
            "訂金": self.deposit_input.value(),
            "運費": self.shipping_input.value(),
            "已付尾款": self.paid_balance_input.value(),
            "預購狀態": self.preorder_status_input.currentText(),
            "付款狀態": self.payment_status_input.currentText(),
            "訂單編號": (
                self.order_number_input.text().strip() or None
            ),
            "備註": self.memo_input.toPlainText().strip() or None,
        }


class PreorderPage(QWidget):
    """預購管理頁面"""

    COLUMNS = [
        ("預購編號", "編號"),
        ("商品名稱", "商品名稱"),
        ("店家名稱", "預購店家"),
        ("預購數量", "數量"),
        ("預購單價", "單價"),
        ("預計到貨日期", "預計到貨"),
        ("預購狀態", "預購狀態"),
        ("付款狀態", "付款狀態"),
        ("訂單編號", "訂單編號"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_preorders()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("預購管理")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #202B3C;"
        )
        layout.addWidget(title)

        description = QLabel(
            "追蹤預購商品、到貨日期、付款進度與剩餘金額。"
        )
        description.setStyleSheet("color: #667085;")
        layout.addWidget(description)

        # 搜尋
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "搜尋商品、店家或訂單編號……"
        )
        self.search_input.returnPressed.connect(
            self.search_preorders
        )

        search_button = QPushButton("搜尋")
        search_button.clicked.connect(self.search_preorders)

        show_all_button = QPushButton("顯示全部")
        show_all_button.clicked.connect(self.load_preorders)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(show_all_button)
        layout.addLayout(search_layout)

        # 操作按鈕
        button_layout = QHBoxLayout()

        add_button = QPushButton("新增預購")
        add_button.clicked.connect(self.add_preorder)

        edit_button = QPushButton("編輯預購")
        edit_button.clicked.connect(self.edit_preorder)

        delete_button = QPushButton("刪除預購")
        delete_button.clicked.connect(self.delete_preorder)

        refresh_button = QPushButton("重新載入")
        refresh_button.clicked.connect(self.load_preorders)

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        self.statistics_label = QLabel("預購統計：載入中")
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
            lambda row, column: self.edit_preorder()
        )

        layout.addWidget(self.table, 1)

        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #667085;")
        layout.addWidget(self.status_label)

    def load_preorders(self):
        try:
            preorders = PreorderRepository.get_all_preorders()
            self.show_preorders(preorders)
            self.update_statistics(preorders)
            self.status_label.setText(
                f"共 {len(preorders)} 筆預購紀錄"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "載入失敗",
                f"無法載入預購資料：\n{error}"
            )

    def search_preorders(self):
        keyword = self.search_input.text().strip()

        if not keyword:
            self.load_preorders()
            return

        try:
            preorders = PreorderRepository.search_preorders(keyword)
            self.show_preorders(preorders)
            self.update_statistics(preorders)
            self.status_label.setText(
                f"搜尋「{keyword}」：共 {len(preorders)} 筆"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "搜尋失敗",
                f"無法搜尋預購資料：\n{error}"
            )

    def show_preorders(self, preorders):
        self.table.setRowCount(0)

        for preorder in preorders:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for column, (field, _) in enumerate(self.COLUMNS):
                value = preorder.get(field)

                if value is None:
                    text = ""
                elif field == "預購單價":
                    text = f"{float(value):,.2f}"
                else:
                    text = str(value)

                cell = QTableWidgetItem(text)

                if field in ("預購編號", "預購數量"):
                    cell.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(row, column, cell)

    def update_statistics(self, preorders):
        """根據目前清單計算預購金額統計"""

        total_amount = 0.0
        paid_amount = 0.0
        remaining_amount = 0.0

        for preorder in preorders:
            preorder_id = preorder.get("預購編號")

            if preorder_id is None:
                continue

            total = PreorderRepository.calculate_total(preorder_id)
            paid = PreorderRepository.calculate_paid_amount(
                preorder_id
            )
            remaining = (
                PreorderRepository.calculate_remaining_amount(
                    preorder_id
                )
            )

            total_amount += float(total or 0)
            paid_amount += float(paid or 0)
            remaining_amount += float(remaining or 0)

        self.statistics_label.setText(
            f"總金額：{total_amount:,.2f}　"
            f"已付款：{paid_amount:,.2f}　"
            f"剩餘金額：{remaining_amount:,.2f}"
        )

    def get_selected_preorder_id(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self,
                "尚未選取",
                "請先在表格中選取一筆預購紀錄。"
            )
            return None

        cell = self.table.item(row, 0)

        if cell is None:
            return None

        return int(cell.text())

    def add_preorder(self):
        try:
            if not ProductRepository.get_all_products():
                QMessageBox.information(
                    self,
                    "沒有商品",
                    "請先到「商品管理」新增商品。"
                )
                return

            dialog = PreorderDialog(parent=self)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()

            preorder_id = PreorderRepository.add_preorder(
                product_id=data["商品編號"],
                store_id=data["店家編號"],
                preorder_date=data["預購日期"],
                expected_release_date=data["預計發售日期"],
                expected_arrival_date=data["預計到貨日期"],
                quantity=data["預購數量"],
                preorder_price=data["預購單價"],
                deposit=data["訂金"],
                shipping_fee=data["運費"],
                paid_balance=data["已付尾款"],
                preorder_status=data["預購狀態"],
                payment_status=data["付款狀態"],
                order_number=data["訂單編號"],
                memo=data["備註"],
            )

            self.load_preorders()
            self.status_label.setText(
                f"新增預購成功，編號：{preorder_id}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "新增失敗",
                f"無法新增預購：\n{error}"
            )

    def edit_preorder(self):
        preorder_id = self.get_selected_preorder_id()

        if preorder_id is None:
            return

        try:
            preorder = PreorderRepository.get_preorder_by_id(
                preorder_id
            )

            if preorder is None:
                QMessageBox.warning(
                    self,
                    "找不到資料",
                    "該預購紀錄可能已被刪除。"
                )
                self.load_preorders()
                return

            dialog = PreorderDialog(
                preorder=preorder,
                parent=self
            )

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()

            # Repository 的 update_preorder 使用中文欄位名稱
            success = PreorderRepository.update_preorder(
                preorder_id,
                **data
            )

            if success:
                self.load_preorders()
                self.status_label.setText(
                    f"預購 {preorder_id} 已更新"
                )
            else:
                QMessageBox.warning(
                    self,
                    "修改失敗",
                    "找不到指定的預購紀錄。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "修改失敗",
                f"無法修改預購：\n{error}"
            )

    def delete_preorder(self):
        preorder_id = self.get_selected_preorder_id()

        if preorder_id is None:
            return

        answer = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除預購編號 {preorder_id} 嗎？",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            success = PreorderRepository.delete_preorder(
                preorder_id
            )

            if success:
                self.load_preorders()
                self.status_label.setText(
                    f"預購 {preorder_id} 已刪除"
                )
            else:
                QMessageBox.warning(
                    self,
                    "刪除失敗",
                    "找不到指定的預購紀錄。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "刪除失敗",
                f"無法刪除預購：\n{error}"
            )
