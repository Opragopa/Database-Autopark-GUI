from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
)

from db_utils import get_all_cars, delete_car
from forms.car_form import CarForm
from table_utils import NumericQTableWidgetItem


class CarsView(QWidget):
    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.role = role
        layout = QVBoxLayout()

        if self.role == 'admin':
            btn_layout = QHBoxLayout()
            self.add_btn = QPushButton("Добавить")
            self.del_btn = QPushButton("Удалить")
            btn_layout.addWidget(self.add_btn)
            btn_layout.addWidget(self.del_btn)
            layout.addLayout(btn_layout)
            self.add_btn.clicked.connect(self.add_car)
            self.del_btn.clicked.connect(self.delete_car)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Номер", "Цвет", "Марка", "Водитель ID", "Водитель"])
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        if self.role == 'admin':
            self.table.doubleClicked.connect(self.edit_car)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        cars = get_all_cars()
        self.table.setRowCount(len(cars))
        for i, (id_, num, color, mark, pid, driver) in enumerate(cars):
            self.table.setItem(i, 0, NumericQTableWidgetItem(id_))
            self.table.setItem(i, 1, QTableWidgetItem(num or ""))
            self.table.setItem(i, 2, QTableWidgetItem(color or ""))
            self.table.setItem(i, 3, QTableWidgetItem(mark or ""))
            self.table.setItem(i, 4, NumericQTableWidgetItem(pid) if pid else QTableWidgetItem(""))
            self.table.setItem(i, 5, QTableWidgetItem(driver or ""))
        self.table.resizeColumnsToContents()

    def add_car(self):
        form = CarForm()
        if form.exec():
            self.load_data()

    def edit_car(self):
        row = self.table.currentRow()
        if row >= 0:
            car_id = int(self.table.item(row, 0).text())
            form = CarForm(car_id)
            if form.exec():
                self.load_data()

    def delete_car(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите автомобиль")
            return
        car_id = int(self.table.item(row, 0).text())
        try:
            delete_car(car_id)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Невозможно удалить авто:\n{str(e)}")