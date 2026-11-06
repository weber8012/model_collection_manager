# -*- coding: utf-8 -*-


from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QLabel,
)


class YearMonthPicker(QWidget):
    """只選擇年份與月份的共用日期元件"""

    dateChanged = Signal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.minimum_date = QDate(2000, 1, 1)
        self.selected_date = None
        self.current_year = QDate.currentDate().year()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.date_input = QLineEdit()
        self.date_input.setReadOnly(True)
        self.date_input.setPlaceholderText("未設定")

        self.calendar_button = QPushButton("選擇")
        self.calendar_button.clicked.connect(
            self.open_picker
        )

        layout.addWidget(self.date_input)
        layout.addWidget(self.calendar_button)

    def setDate(self, date):
        """設定日期"""
        if date is None or not date.isValid():
            self.selected_date = None
            self.date_input.clear()
            return

        self.selected_date = QDate(
            date.year(), date.month(), 1
        )
        self.date_input.setText(
            self.selected_date.toString("yyyy-MM")
        )

    def date(self):
        """取得目前選擇的日期"""
        if self.selected_date is None:
            return self.minimum_date

        return self.selected_date

    def minimumDate(self):
        return self.minimum_date

    def open_picker(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("選擇年月")
        dialog.setMinimumWidth(320)

        layout = QVBoxLayout(dialog)

        navigation = QHBoxLayout()

        previous_button = QPushButton("上一年")
        next_button = QPushButton("下一年")
        year_label = QLabel()

        navigation.addWidget(previous_button)
        navigation.addWidget(year_label)
        navigation.addWidget(next_button)

        layout.addLayout(navigation)

        month_grid = QGridLayout()
        layout.addLayout(month_grid)

        year = (
            self.selected_date.year()
            if self.selected_date is not None
            else QDate.currentDate().year()
        )

        selected_month = (
            self.selected_date.month()
            if self.selected_date is not None
            else QDate.currentDate().month()
        )

        def update_year():
            year_label.setText(f"{year_holder[0]} 年")

        year_holder = [year]
        update_year()

        def change_year(offset):
            year_holder[0] += offset
            update_year()

        previous_button.clicked.connect(
            lambda: change_year(-1)
        )
        next_button.clicked.connect(
            lambda: change_year(1)
        )

        def select_month(month):
            self.setDate(
                QDate(year_holder[0], month, 1)
            )
            self.dateChanged.emit(self.selected_date)
            dialog.accept()

        for month in range(1, 13):
            button = QPushButton(f"{month} 月")
            row = (month - 1) // 3
            column = (month - 1) % 3

            if month == selected_month:
                button.setStyleSheet(
                    "font-weight: bold;"
                )

            button.clicked.connect(
                lambda checked=False, m=month:
                select_month(m)
            )

            month_grid.addWidget(
                button, row, column
            )

        dialog.exec()
