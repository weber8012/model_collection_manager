
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
    QDoubleSpinBox,
    QDialogButtonBox,
    QMessageBox,
    QTextEdit,
)

from repositories.product_repository import ProductRepository
from ui.widgets.year_month_picker import YearMonthPicker

class ProductPage(QWidget):
    """商品管理頁面"""

    TABLE_COLUMNS = [
        ("商品編號", "商品編號"),
        ("商品名稱", "商品名稱"),
        ("品牌", "模型品牌"),
        ("系列", "作品"),
        ("商品類型", "商品類型"),
        ("比例", "比例"),
        ("商品型號", "商品型號"),
        ("發售日期", "發售日期"),
        ("官方定價", "官方定價"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("商品管理")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel("管理模型與玩具的基本資料。")
        description.setObjectName("pageSubtitle")
        layout.addWidget(description)

        # 搜尋列
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋商品名稱、品牌或系列……")
        self.search_input.returnPressed.connect(self.search_products)

        search_button = QPushButton("搜尋")
        search_button.clicked.connect(self.search_products)

        reset_button = QPushButton("顯示全部")
        reset_button.clicked.connect(self.load_products)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(reset_button)

        layout.addLayout(search_layout)

        # 操作按鈕列
        button_layout = QHBoxLayout()

        add_button = QPushButton("新增商品")
        add_button.clicked.connect(self.add_product)

        edit_button = QPushButton("編輯選取商品")
        edit_button.clicked.connect(self.edit_product)

        delete_button = QPushButton("刪除選取商品")
        delete_button.clicked.connect(self.delete_product)

        refresh_button = QPushButton("重新載入")
        refresh_button.clicked.connect(self.load_products)

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)

        # 商品表格
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.TABLE_COLUMNS))
        self.table.setHorizontalHeaderLabels(
            [column[1] for column in self.TABLE_COLUMNS]
        )
        self.table.setColumnHidden(0, True)

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
            lambda row, column: self.edit_product()
        )

        layout.addWidget(self.table, 1)

        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #667085;")
        layout.addWidget(self.status_label)

    def load_products(self):
        """載入全部商品"""

        try:
            products = ProductRepository.get_all_products()
            self.show_products(products)
            self.status_label.setText(f"共 {len(products)} 筆商品")
        except Exception as error:
            QMessageBox.critical(
                self,
                "載入失敗",
                f"無法載入商品資料：\n{error}"
            )

    def search_products(self):
        """搜尋商品"""

        keyword = self.search_input.text().strip()

        if not keyword:
            self.load_products()
            return

        try:
            products = ProductRepository.search_products(keyword)
            self.show_products(products)
            self.status_label.setText(
                f"搜尋「{keyword}」：共 {len(products)} 筆"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "搜尋失敗",
                f"無法搜尋商品：\n{error}"
            )

    def show_products(self, products):
        """將商品資料顯示在表格"""

        self.table.setRowCount(0)

        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for column, (field, _) in enumerate(self.TABLE_COLUMNS):
                value = product.get(field)

                if value is None:
                    text = ""
                elif field == "官方定價":
                    text = f"{float(value):,.0f}"
                elif field == "發售日期":
                    text = str(value)[:7]
                else:
                    text = str(value)

                item = QTableWidgetItem(text)

                if field == "商品編號":
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(row, column, item)

    def get_selected_product_id(self):
        """取得目前選取的商品編號"""

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self,
                "尚未選取商品",
                "請先在表格中選取一筆商品。"
            )
            return None

        item = self.table.item(row, 0)

        if item is None:
            return None

        return int(item.text())

    def add_product(self):
        """新增商品"""

        dialog = ProductDialog(parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        try:
            product_id = ProductRepository.add_product(
                name=data["商品名稱"],
                brand=data["品牌"],
                series=data["系列"],
                manufacturer=data["製造商"],
                product_type=data["商品類型"],
                scale=data["比例"],
                model_number=data["商品型號"],
                release_date=data["發售日期"],
                msrp=data["官方定價"],
                image_path=data["商品圖片路徑"],
                memo=data["備註"],
            )

            self.load_products()
            self.status_label.setText(
                f"新增商品成功 {data['商品名稱']}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "新增失敗",
                f"無法新增商品：\n{error}"
            )

    def edit_product(self):
        """編輯選取的商品"""

        product_id = self.get_selected_product_id()

        if product_id is None:
            return

        try:
            product = ProductRepository.get_product_by_id(product_id)

            if product is None:
                QMessageBox.warning(
                    self, "找不到商品", "這筆商品可能已經被刪除。"
                )
                self.load_products()
                return

            dialog = ProductDialog(product=product, parent=self)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()
            success = ProductRepository.update_product(
                product_id,
                **data
            )

            if success:
                self.load_products()
                self.status_label.setText(
                    f"商品 {product['商品名稱']} 已更新"
                )
            else:
                QMessageBox.warning(
                    self, "修改失敗", "找不到指定商品，未完成修改。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "修改失敗",
                f"無法修改商品：\n{error}"
            )

    def delete_product(self):
        """刪除選取的商品"""

        product_id = self.get_selected_product_id()

        if product_id is None:
            return

        product = ProductRepository.get_product_by_id(product_id)

        if product is None:
            QMessageBox.warning(
                self, "找不到商品", "這筆商品可能已經被刪除。"
            )
            self.load_products()
            return

        answer = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除商品「{product['商品名稱']}」嗎？\n\n"
            "注意：資料庫設定會連帶刪除該商品的收藏與預購紀錄。",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            success = ProductRepository.delete_product(product_id)

            if success:
                self.load_products()
                self.status_label.setText(
                    f"商品 {product['商品名稱']} 已刪除"
                )
            else:
                QMessageBox.warning(
                    self, "刪除失敗", "找不到指定商品。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "刪除失敗",
                f"無法刪除商品：\n{error}"
            )

class ProductDialog(QDialog):
    """新增或編輯商品的對話視窗"""

    PRODUCT_TYPES = [
        "塑膠組裝模型",
        "完成品玩具",
        "可動人偶",
        "其他",
    ]

    def __init__(self, product=None, parent=None):
        super().__init__(parent)

        self.product = product
        self.setWindowTitle("編輯商品" if product else "新增商品")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.series_input = QLineEdit()
        self.manufacturer_input = QLineEdit()

        self.type_input = QComboBox()
        self.type_input.addItems(self.PRODUCT_TYPES)

        self.scale_input = QLineEdit()
        self.model_number_input = QLineEdit()
        self.release_date_input = YearMonthPicker()

        self.msrp_input = QDoubleSpinBox()
        self.msrp_input.setButtonSymbols(
            QDoubleSpinBox.ButtonSymbols.NoButtons
        )
        self.msrp_input.setRange(0, 999999999)
        self.msrp_input.setDecimals(0)
        self.msrp_input.setSpecialValueText("未設定")

        self.image_path_input = QLineEdit()
        self.memo_input = QTextEdit()
        self.memo_input.setMaximumHeight(90)

        form.addRow("商品名稱 *", self.name_input)
        form.addRow("模型品牌", self.brand_input)
        form.addRow("作品", self.series_input)
        form.addRow("製造商", self.manufacturer_input)
        form.addRow("商品類型", self.type_input)
        form.addRow("比例", self.scale_input)
        form.addRow("商品型號", self.model_number_input)
        form.addRow("發售日期", self.release_date_input)
        form.addRow("官方定價", self.msrp_input)
        form.addRow("商品圖片路徑", self.image_path_input)
        form.addRow("備註", self.memo_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if product:
            self.load_product(product)

    def load_product(self, product):
        """將既有商品資料填入表單"""

        self.name_input.setText(product.get("商品名稱") or "")
        self.brand_input.setText(product.get("品牌") or "")
        self.series_input.setText(product.get("系列") or "")
        self.manufacturer_input.setText(product.get("製造商") or "")

        product_type = product.get("商品類型") or "其他"
        index = self.type_input.findText(product_type)

        if index < 0:
            self.type_input.addItem(product_type)
            index = self.type_input.findText(product_type)

        self.type_input.setCurrentIndex(index)

        self.scale_input.setText(product.get("比例") or "")
        self.model_number_input.setText(product.get("商品型號") or "")

        release_date = product.get("發售日期")

        if release_date:
            date_value = QDate.fromString(
                str(release_date),
                "yyyy-MM-dd"
            )
            self.release_date_input.setDate(date_value)
        else:
            self.release_date_input.setDate(None)

        self.image_path_input.setText(product.get("商品圖片路徑") or "")
        self.memo_input.setPlainText(product.get("備註") or "")

        msrp = product.get("官方定價")

        if msrp is not None:
            self.msrp_input.setValue(float(msrp))

    def validate_and_accept(self):
        """檢查必要欄位"""

        if not self.name_input.text().strip():
            QMessageBox.warning(self, "資料不完整", "請輸入商品名稱。")
            self.name_input.setFocus()
            return

        self.accept()

    def get_data(self):
        """取得表單資料，欄位名稱對應資料庫"""

        msrp = self.msrp_input.value()

        return {
            "商品名稱": self.name_input.text().strip(),
            "品牌": self.brand_input.text().strip() or None,
            "系列": self.series_input.text().strip() or None,
            "製造商": self.manufacturer_input.text().strip() or None,
            "商品類型": self.type_input.currentText(),
            "比例": self.scale_input.text().strip() or None,
            "商品型號": self.model_number_input.text().strip() or None,
            "發售日期": (
                self.release_date_input.date().toString("yyyy-MM-dd")
                if self.release_date_input.date()
                != self.release_date_input.minimumDate()
                else None
            ),
            "官方定價": msrp if msrp > 0 else None,
            "商品圖片路徑": self.image_path_input.text().strip() or None,
            "備註": self.memo_input.toPlainText().strip() or None,
        }
