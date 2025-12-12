from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from db_utils import fetch_journal_with_details, delete_journal
from forms.journal_form import JournalForm
from table_utils import NumericQTableWidgetItem  # ← ИМПОРТ

class JournalView(QWidget):
    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.role = role
        self.layout = QVBoxLayout()

        if self.role == 'admin':
            button_layout = QHBoxLayout()
            self.add_button = QPushButton("Добавить")
            self.delete_button = QPushButton("Удалить")
            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.delete_button)
            self.layout.addLayout(button_layout)
            self.add_button.clicked.connect(self.add_record)
            self.delete_button.clicked.connect(self.delete_record)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Выезд", "Возвращение", "Авто", "Водитель", "Маршрут"
        ])
        self.table.setSortingEnabled(True)  # ← разрешить сортировку
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        if self.role == 'admin':
            self.table.doubleClicked.connect(self.edit_record)

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self):
        data = fetch_journal_with_details()
        self.table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            self.table.setItem(row_idx, 0, NumericQTableWidgetItem(row[0]))
            for col_idx in range(1, 6):
                item = QTableWidgetItem(str(row[col_idx]) if row[col_idx] is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()

    def add_record(self):
        form = JournalForm()
        if form.exec():
            self.load_data()

    def edit_record(self):
        if not self.role == 'admin':
            return
        selected = self.table.currentRow()
        if selected < 0:
            return
        journal_id = int(self.table.item(selected, 0).text())
        form = JournalForm(journal_id=journal_id)
        if form.exec():
            self.load_data()

    def delete_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return
        journal_id = int(self.table.item(selected, 0).text())
        try:
            delete_journal(journal_id)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))