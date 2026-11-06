
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
    QDialogButtonBox,
    QMessageBox,
)

from repositories.store_repository import StoreRepository

class StorePage(QWidget):
    """店家管理頁面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_stores()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("店家管理")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel(
            "管理購買與預購店家，供預購紀錄選取使用。"
        )
        description.setObjectName("pageSubtitle")
        layout.addWidget(description)

        # 搜尋列
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "輸入店家名稱搜尋……"
        )
        self.search_input.returnPressed.connect(
            self.search_stores
        )

        search_button = QPushButton("搜尋")
        search_button.clicked.connect(self.search_stores)

        show_all_button = QPushButton("顯示全部")
        show_all_button.clicked.connect(self.load_stores)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(show_all_button)

        layout.addLayout(search_layout)

        # 操作按鈕
        button_layout = QHBoxLayout()

        add_button = QPushButton("新增店家")
        add_button.clicked.connect(self.add_store)

        edit_button = QPushButton("編輯店家")
        edit_button.clicked.connect(self.edit_store)

        delete_button = QPushButton("刪除店家")
        delete_button.clicked.connect(self.delete_store)

        refresh_button = QPushButton("重新載入")
        refresh_button.clicked.connect(self.load_stores)

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)

        self.statistics_label = QLabel("店家統計：載入中")
        self.statistics_label.setStyleSheet(
            "font-size: 13px; color: #475467;"
        )
        layout.addWidget(self.statistics_label)

        # 店家表格
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(
            ["店家編號", "店家名稱"]
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
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )

        self.table.cellDoubleClicked.connect(
            lambda row, column: self.edit_store()
        )

        layout.addWidget(self.table, 1)

        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #667085;")
        layout.addWidget(self.status_label)

    def load_stores(self):
        """載入全部店家"""

        try:
            stores = StoreRepository.get_all_stores()
            self.show_stores(stores)
            self.update_statistics(stores)
            self.status_label.setText(
                f"共 {len(stores)} 家店家"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "載入失敗",
                f"無法載入店家資料：\n{error}"
            )

    def search_stores(self):
        """搜尋店家"""

        keyword = self.search_input.text().strip()

        if not keyword:
            self.load_stores()
            return

        try:
            stores = StoreRepository.search_stores(keyword)
            self.show_stores(stores)
            self.update_statistics(stores)
            self.status_label.setText(
                f"搜尋「{keyword}」：共 {len(stores)} 家店家"
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "搜尋失敗",
                f"無法搜尋店家：\n{error}"
            )

    def show_stores(self, stores):
        self.table.setRowCount(0)

        for store in stores:
            row = self.table.rowCount()
            self.table.insertRow(row)

            store_id = QTableWidgetItem(
                str(store["店家編號"])
            )
            store_id.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            store_name = QTableWidgetItem(
                store["店家名稱"]
            )

            self.table.setItem(row, 0, store_id)
            self.table.setItem(row, 1, store_name)

    def update_statistics(self, stores):
        self.statistics_label.setText(
            f"店家數量：{len(stores)}"
        )

    def get_selected_store(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self,
                "尚未選取",
                "請先在表格中選取一家店家。"
            )
            return None

        id_cell = self.table.item(row, 0)

        if id_cell is None:
            return None

        store_id = int(id_cell.text())
        return StoreRepository.get_store_by_id(store_id)

    def add_store(self):
        dialog = StoreDialog(parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name = dialog.get_name()

        try:
            store_id = StoreRepository.add_store(name)
            self.load_stores()
            self.status_label.setText(
                f"新增店家成功 {name}"
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "新增失敗",
                "無法新增店家。\n\n"
                "可能原因：店家名稱已存在，或資料庫發生錯誤。\n\n"
                f"詳細訊息：{error}"
            )

    def edit_store(self):
        store = self.get_selected_store()

        if store is None:
            return

        dialog = StoreDialog(store=store, parent=self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name = dialog.get_name()

        try:
            success = StoreRepository.update_store(
                store["店家編號"],
                name
            )

            if success:
                self.load_stores()
                self.status_label.setText(
                    f"店家 {store['店家名稱']} 已更新"
                )
            else:
                QMessageBox.warning(
                    self,
                    "修改失敗",
                    "找不到指定的店家。"
                )

        except Exception as error:
            QMessageBox.warning(
                self,
                "修改失敗",
                "無法修改店家。\n\n"
                "請確認新名稱沒有與其他店家重複。\n\n"
                f"詳細訊息：{error}"
            )

    def delete_store(self):
        store = self.get_selected_store()

        if store is None:
            return

        store_id = store["店家編號"]
        store_name = store["店家名稱"]

        answer = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除店家「{store_name}」嗎？\n\n"
            "既有預購紀錄的店家欄位會依資料庫設定改為未指定。",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            success = StoreRepository.delete_store(store_id)

            if success:
                self.load_stores()
                self.status_label.setText(
                    f"店家 {store_name} 已刪除"
                )
            else:
                QMessageBox.warning(
                    self,
                    "刪除失敗",
                    "找不到指定的店家。"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "刪除失敗",
                f"無法刪除店家：\n{error}"
            )

class StoreDialog(QDialog):
    """新增或編輯店家"""

    def __init__(self, store=None, parent=None):
        super().__init__(parent)

        self.store = store
        self.setWindowTitle(
            "編輯店家" if store else "新增店家"
        )
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "請輸入店家名稱"
        )

        form.addRow("店家名稱 *", self.name_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        if store:
            self.name_input.setText(
                store.get("店家名稱") or ""
            )

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "資料不完整",
                "請輸入店家名稱。"
            )
            return

        self.accept()

    def get_name(self):
        return self.name_input.text().strip()
