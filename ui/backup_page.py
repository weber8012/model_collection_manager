# 資料庫備份與還原管理頁面。


from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QMessageBox,
    QFrame,
)

from services.backup_service import BackupService


class BackupPage(QWidget):
    """資料庫備份與還原管理頁面。"""

    def __init__(self):
        super().__init__()

        self.init_ui()
        self.refresh_backups()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        # 頁面標題
        title = QLabel("備份與還原")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        description = QLabel(
            "管理收藏資料庫的備份，並在需要時還原資料。"
        )

        description.setObjectName("pageSubtitle")
        layout.addWidget(description)

        # 操作按鈕
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.create_backup_button = QPushButton("立即建立備份")
        self.create_backup_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.create_backup_button.clicked.connect(
            self.create_backup
        )
        button_layout.addWidget(self.create_backup_button)

        self.refresh_button = QPushButton("重新整理清單")
        self.refresh_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.refresh_button.clicked.connect(
            self.refresh_backups
        )
        button_layout.addWidget(self.refresh_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 備份清單卡片
        card = QFrame()
        card.setObjectName("placeholder_card")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        list_title = QLabel("可用的備份檔案")
        list_title.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #202B3C;"
        )
        card_layout.addWidget(list_title)

        self.backup_list = QListWidget()
        self.backup_list.setMinimumHeight(260)
        self.backup_list.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        card_layout.addWidget(self.backup_list)

        self.backup_info = QLabel("請選擇一個備份檔案。")
        self.backup_info.setWordWrap(True)
        self.backup_info.setStyleSheet("color: #667085;")
        card_layout.addWidget(self.backup_info)

        # 還原按鈕
        restore_layout = QHBoxLayout()
        restore_layout.addStretch()

        self.restore_button = QPushButton("還原選取的備份")
        self.restore_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.restore_button.clicked.connect(
            self.restore_backup
        )
        restore_layout.addWidget(self.restore_button)

        card_layout.addLayout(restore_layout)
        layout.addWidget(card, 1)

        self.backup_list.currentItemChanged.connect(
            self.update_backup_info
        )


    def refresh_backups(self):
        """重新載入備份清單。"""

        self.backup_list.clear()

        try:
            backups = BackupService.get_backups()

            valid_count = 0
            invalid_count = 0

            for backup_path in backups:
                path = Path(backup_path)

                valid, message = (
                    BackupService.validate_database(path)
                )

                if valid:
                    display_text = (
                        f"{path.name} [有效]"
                    )
                    valid_count += 1
                else:
                    display_text = (
                        f"{path.name} [無效：{message}]"
                    )
                    invalid_count += 1

                self.backup_list.addItem(display_text)

                item = self.backup_list.item(
                    self.backup_list.count() - 1
                )

                # 保存原始備份路徑，避免顯示文字影響還原
                item.setData(
                    Qt.ItemDataRole.UserRole,
                    str(path)
                )

                # 保存驗證結果
                item.setData(
                    Qt.ItemDataRole.UserRole + 1,
                    valid
                )

            self.backup_info.setText(
                f"有效備份：{valid_count} 個\n"
                f"無效備份：{invalid_count} 個"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "讀取備份失敗",
                f"無法讀取備份清單：\n{error}",
            )


    def update_backup_info(self, current_item, previous_item):
        """顯示所選備份檔案的資訊。"""

        if current_item is None:
            self.backup_info.setText(
                "請選擇一個備份檔案。"
            )
            return

        backup_path = Path(current_item.text())

        if backup_path.exists():
            size_kb = backup_path.stat().st_size / 1024

            self.backup_info.setText(
                f"檔案：{backup_path.name}\n"
                f"大小：{size_kb:.2f} KB\n"
                f"位置：{backup_path}"
            )
        else:
            self.backup_info.setText(
                f"找不到備份檔案：{backup_path}"
            )

    def create_backup(self):
        """建立目前資料庫的備份。"""

        self.create_backup_button.setEnabled(False)

        try:
            backup_path = BackupService.create_backup()

            QMessageBox.information(
                self,
                "備份完成",
                f"資料庫備份已建立：\n{backup_path}",
            )

            self.refresh_backups()

        except Exception as error:
            QMessageBox.critical(
                self,
                "備份失敗",
                f"無法建立資料庫備份：\n{error}",
            )

        finally:
            self.create_backup_button.setEnabled(True)

    def restore_backup(self):
        """還原使用者選取的備份。"""

        selected_item = self.backup_list.currentItem()

        if selected_item is None:
            QMessageBox.warning(
                self,
                "還原失敗",
                "請先選擇備份檔案。",
            )
            return

        backup_path = Path(
            selected_item.data(Qt.ItemDataRole.UserRole)
        )
        if not backup_path.is_file():
            QMessageBox.warning(
                self,
                "備份檔案不存在",
                f"找不到指定的備份檔案：\n{backup_path}",
            )
            self.refresh_backups()
            return

        answer = QMessageBox.warning(
            self,
            "確認還原資料庫",
            "還原會以備份中的資料取代目前的資料。\n\n"
            "系統會先建立目前資料庫的安全備份。\n"
            "請確認你選取的是正確的備份檔案。\n\n"
            f"準備還原：\n{backup_path.name}\n\n"
            "確定要繼續嗎？",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.restore_button.setEnabled(False)

        try:
            success, message = BackupService.restore_backup(
                backup_path
            )

            if success:
                QMessageBox.information(
                    self,
                    "還原完成",
                    f"{message}\n\n"
                    "建議重新啟動程式，"
                    "讓所有頁面重新載入資料。",
                )
                self.refresh_backups()

            else:
                QMessageBox.critical(
                    self,
                    "還原失敗",
                    message,
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "還原失敗",
                f"還原資料庫時發生錯誤：\n{error}",
            )

        finally:
            self.restore_button.setEnabled(True)
