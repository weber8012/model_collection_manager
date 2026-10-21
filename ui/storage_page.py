
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
    QDialogButtonBox,
    QMessageBox,
    QTextEdit,
)

from repositories.storage_repository import StorageRepository


class StorageDialog(QDialog):
    """新增或編輯收納位置"""

    def __init__(self, location=None, parent=None):
        super().__init__(parent)

        self.location = location
        self.setWindowTitle(
            "編輯收納位置" if location else "新增收納位置"
        )
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "例如：A 櫃、A-1 層、展示櫃"
        )

        self.parent_input = QComboBox()
        self.parent_input.addItem("無（最上層）", None)

        self.locations = StorageRepository.get_all_locations()

        current_id = (
            location.get("位置編號") if location else None
        )

        for item in self.locations:
            location_id = item["位置編號"]

            # 不允許選擇自己當作上層位置
            if current_id is not None and location_id == current_id:
                continue

            self.parent_input.addItem(
                item["位置名稱"],
                location_id
            )

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(90)

        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(0, 999999)
        self.capacity_input.setSpecialValueText("未設定")

        form.addRow("位置名稱 *", self.name_input)
        form.addRow("上層位置", self.parent_input)
        form.addRow("位置描述", self.description_input)
        form.addRow("收納容量", self.capacity_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if location:
            self.load_location(location)

    def load_location(self, location):
        self.name_input.setText(
            location.get("位置名稱") or ""
        )

        self.set_combo_data(
            self.parent_input,
            location.get("上層位置編號")
        )

        self.description_input.setPlainText(
            location.get("位置描述") or ""
        )

        capacity = location.get("收納容量")
        if capacity is not None:
            self.capacity_input.setValue(int(capacity))

    @staticmethod
    def set_combo_data(combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def validate_and_accept(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "資料不完整",
                "請輸入收納位置名稱。"
            )
            return

        parent_id = self.parent_input.currentData()
        current_id = (
            self.location.get("位置編號")
            if self.location else None
        )

        # 避免將自己的後代設為上層，造成階層循環
        if current_id is not None and parent_id is not None:
            try:
                descendants = StorageRepository.get_location_tree()
                descendant_ids = self.collect_descendant_ids(
                    descendants, current_id
                )

                if parent_id in descendant_ids:
                    QMessageBox.warning(
                        self,
                        "階層設定錯誤",
                        "不能將子位置或後代位置設為自己的上層位置。"
                    )
                    return
            except Exception:
                # 若無法判斷階層，後續仍由 Repository 處理
                pass

        self.accept()

    @staticmethod
    def collect_descendant_ids(tree, parent_id):
        """從位置樹中找出指定位置的所有後代編號"""
        result = set()

        def walk(node, found_parent=False):
            if isinstance(node, dict):
                node_id = node.get("位置編號")
                now_found = found_parent or node_id == parent_id

                if found_parent and node_id is not None:
                    result.add(node_id)

                for value in node.values():
                    if isinstance(value, (list, dict)):
                        walk(value, now_found)

            elif isinstance(node, (list, tuple)):
                for child in node:
                    walk(child, found_parent)

        walk(tree)
        return result

    def get_data(self):
        capacity = self.capacity_input.value()

        return {
            "位置名稱": self.name_input.text().strip(),
            "上層位置編號": self.parent_input.currentData(),
            "位置描述": (
                self.description_input.toPlainText().strip() or None
            ),
            "收納容量": capacity if capacity > 0 else None,
        }


class StoragePage(QWidget):
    """收納位置管理頁面"""

    COLUMNS = [
        ("位置編號", "位置編號"),
        ("位置名稱", "位置名稱"),
        ("上層位置編號", "上層位置編號"),
        ("位置描述", "位置描述"),
        ("收納容量", "收納容量"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_locations()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("收納管理")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #202B3C;"
        )
        layout.addWidget(title)

        description = QLabel(
            "管理櫃子、層架、抽屜與其他收藏收納位置。"
        )
        description.setStyleSheet("color: #667085;")
        layout.addWidget(description)

        # 搜尋
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "搜尋位置名稱或描述……"
        )
        self.search_input.returnPressed.connect(
            self.search_locations
        )

        search_button = QPushButton("搜尋")
        search_button.clicked.connect(self.search_locations)

        show_all_button = QPushButton("顯示全部")
        show_all_button.clicked.connect(self.load_locations)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(show_all_button)
        layout.addLayout(search_layout)

        # 操作按鈕
        button_layout = QHBoxLayout()

        add_button = QPushButton("新增位置")
        add_button.clicked.connect(self.add_location)

        edit_button = QPushButton("編輯位置")
        edit_button.clicked.connect(self.edit_location)

        delete_button = QPushButton("刪除位置")
        delete_button.clicked.connect(self.delete_location)

        view_items_button = QPushButton("查看位置內收藏")
        view_items_button.clicked.connect(self.view_items)

        refresh_button = QPushButton("重新載入")
        refresh_button.clicked.connect(self.load_locations)

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(view_items_button)
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)
        layout.addLayout(button_layout)

        self.statistics_label = QLabel("收納統計：載入中")
        self.statistics_label.setStyleSheet(
            "font-size: 13px; color: #475467;"
        )
        layout.addWidget(self.statistics_label)

        # 位置表格
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
            lambda row, column: self.edit_location()
        )

        layout.addWidget(self.table, 1)

        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #667085;")
        layout.addWidget(self.status_label)

    def load_locations(self):
        try:
            locations = StorageRepository.get_all_locations()
            self.show_locations(locations)
            self.update_statistics(locations)
            self.status_label.setText(
                f"共 {len(locations)} 個收納位置"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "載入失敗",
                f"無法載入收納位置：\n{error}"
            )

    def search_locations(self):
        keyword = self.search_input.text().strip()

        if not keyword:
            self.load_locations()
            return

        try:
            locations = StorageRepository.get_all_locations()

            matched = [
                location
                for location in locations
                if keyword.lower() in str(
                    location.get("位置名稱") or ""
                ).lower()
                or keyword.lower() in str(
                    location.get("位置描述") or ""
                ).lower()
            ]

            self.show_locations(matched)
            self.update_statistics(matched)
            self.status_label.setText(
                f"搜尋「{keyword}」：共 {len(matched)} 個位置"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "搜尋失敗",
                f"無法搜尋收納位置：\n{error}"
            )

    def show_locations(self, locations):
        self.table.setRowCount(0)

        for location in locations:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for column, (field, _) in enumerate(self.COLUMNS):
                value = location.get(field)

                if value is None:
                    text = ""
                else:
                    text = str(value)

                cell = QTableWidgetItem(text)

                if field in ("位置編號", "上層位置編號", "收納容量"):
                    cell.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(row, column, cell)

    def update_statistics(self, locations):
        root_count = sum(
            1 for location in locations
            if location.get("上層位置編號") is None
        )

        capacity_count = sum(
            1 for location in locations
            if location.get("收納容量") is not None
        )

        self.statistics_label.setText(
            f"位置總數：{len(locations)}　"
            f"最上層位置：{root_count}　"
            f"已設定容量：{capacity_count}"
        )

    def get_selected_location(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self,
                "尚未選取",
                "請先在表格中選取一個收納位置。"
            )
            return None

        cell = self.table.item(row, 0)

        if cell is None:
            return None

        location_id = int(cell.text())
        return StorageRepository.get_location_by_id(location_id)

    def add_location(self):
        try:
            dialog = StorageDialog(parent=self)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()

            location_id = StorageRepository.add_location(
                name=data["位置名稱"],
                parent_id=data["上層位置編號"],
                description=data["位置描述"],
                capacity=data["收納容量"],
            )

            self.load_locations()
            self.status_label.setText(
                f"新增位置成功，編號：{location_id}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "新增失敗",
                f"無法新增收納位置：\n{error}"
            )

    def edit_location(self):
        location = self.get_selected_location()

        if location is None:
            return

        try:
            dialog = StorageDialog(
                location=location,
                parent=self
            )

            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()

            success = StorageRepository.update_location(
                location["位置編號"],
                **data
            )

            if success:
                self.load_locations()
                self.status_label.setText(
                    f"位置 {location['位置編號']} 已更新"
                )
            else:
                QMessageBox.warning(
                    self,
                    "修改失敗",
                    "找不到指定的收納位置。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "修改失敗",
                f"無法修改收納位置：\n{error}"
            )

    def delete_location(self):
        location = self.get_selected_location()

        if location is None:
            return

        location_id = location["位置編號"]
        location_name = location["位置名稱"]

        answer = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除「{location_name}」嗎？\n\n"
            "依目前資料庫外鍵設定，持有品的收納位置與"
            "子位置的上層位置可能會被設為未指定。",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            success = StorageRepository.delete_location(
                location_id
            )

            if success:
                self.load_locations()
                self.status_label.setText(
                    f"位置 {location_id} 已刪除"
                )
            else:
                QMessageBox.warning(
                    self,
                    "刪除失敗",
                    "找不到指定的收納位置。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "刪除失敗",
                f"無法刪除收納位置：\n{error}"
            )

    def view_items(self):
        location = self.get_selected_location()

        if location is None:
            return

        try:
            items = StorageRepository.get_items_in_location(
                location["位置編號"]
            )

            if not items:
                QMessageBox.information(
                    self,
                    f"{location['位置名稱']}：收藏清單",
                    "這個位置目前沒有收藏商品。"
                )
                return

            lines = []

            for item in items:
                product_name = (
                    item.get("商品名稱")
                    or item.get("品牌")
                    or "未命名商品"
                )
                quantity = item.get("數量", 1)

                lines.append(
                    f"• {product_name}（數量：{quantity}）"
                )

            QMessageBox.information(
                self,
                f"{location['位置名稱']}：收藏清單",
                "\n".join(lines)
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "查詢失敗",
                f"無法查詢位置內的收藏：\n{error}"
            )
