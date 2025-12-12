from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
)

from db_utils import get_all_routes, delete_route
from forms.route_form import RouteForm
from table_utils import NumericQTableWidgetItem


class RoutesView(QWidget):
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
            self.add_btn.clicked.connect(self.add_route)
            self.del_btn.clicked.connect(self.delete_route)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Дата"])
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        if self.role == 'admin':
            self.table.doubleClicked.connect(self.edit_route)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        routes = get_all_routes()
        self.table.setRowCount(len(routes))
        for i, (id_, name, date) in enumerate(routes):
            self.table.setItem(i, 0, NumericQTableWidgetItem(id_))
            self.table.setItem(i, 1, QTableWidgetItem(name or ""))
            self.table.setItem(i, 2, QTableWidgetItem(str(date) if date else ""))
        self.table.resizeColumnsToContents()

    def add_route(self):
        form = RouteForm()
        if form.exec():
            self.load_data()

    def edit_route(self):
        row = self.table.currentRow()
        if row >= 0:
            route_id = int(self.table.item(row, 0).text())
            form = RouteForm(route_id)
            if form.exec():
                self.load_data()

    def delete_route(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите маршрут")
            return
        route_id = int(self.table.item(row, 0).text())
        try:
            delete_route(route_id)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Невозможно удалить маршрут:\n{str(e)}")