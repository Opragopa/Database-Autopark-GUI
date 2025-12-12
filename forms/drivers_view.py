from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
)

from db_utils import get_all_drivers, delete_driver
from forms.driver_form import DriverForm
from table_utils import NumericQTableWidgetItem


class DriversView(QWidget):
    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.role = role
        layout = QVBoxLayout()

        if self.role == 'admin':
            button_layout = QHBoxLayout()
            self.add_btn = QPushButton("Добавить")
            self.delete_btn = QPushButton("Удалить")
            button_layout.addWidget(self.add_btn)
            button_layout.addWidget(self.delete_btn)
            layout.addLayout(button_layout)
            self.add_btn.clicked.connect(self.add_driver)
            self.delete_btn.clicked.connect(self.delete_driver)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Фамилия", "Отчество"])
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        if self.role == 'admin':
            self.table.doubleClicked.connect(self.edit_driver)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        drivers = get_all_drivers()
        self.table.setRowCount(len(drivers))
        for i, (id_, first, last, father) in enumerate(drivers):
            self.table.setItem(i, 0, NumericQTableWidgetItem(id_))
            self.table.setItem(i, 1, QTableWidgetItem(first or ""))
            self.table.setItem(i, 2, QTableWidgetItem(last or ""))
            self.table.setItem(i, 3, QTableWidgetItem(father or ""))
        self.table.resizeColumnsToContents()

    def add_driver(self):
        form = DriverForm()
        if form.exec():
            self.load_data()

    def edit_driver(self):
        row = self.table.currentRow()
        if row >= 0:
            driver_id = int(self.table.item(row, 0).text())
            form = DriverForm(driver_id)
            if form.exec():
                self.load_data()

    def delete_driver(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите водителя для удаления")
            return
        driver_id = int(self.table.item(row, 0).text())
        try:
            delete_driver(driver_id)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Невозможно удалить водителя:\n{str(e)}")