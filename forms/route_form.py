from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDateEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QDate
from db_utils import get_all_cities_list, insert_route, update_route, get_route_by_id

class RouteForm(QDialog):
    def __init__(self, route_id=None, parent=None):
        super().__init__(parent)
        self.route_id = route_id
        self.setWindowTitle("Новый маршрут" if route_id is None else "Редактировать маршрут")
        self.setMinimumWidth(400)

        self.from_combo = QComboBox()
        self.to_combo = QComboBox()

        cities = get_all_cities_list()
        self.from_combo.addItems([""] + cities)
        self.to_combo.addItems([""] + cities)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        form = QFormLayout()
        form.addRow("Город отправления:", self.from_combo)
        form.addRow("Город назначения:", self.to_combo)
        form.addRow("Дата:", self.date_edit)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.reject)

        if route_id:
            self.load_data()

    def load_data(self):
        from_db = get_route_by_id(self.route_id)
        if from_db:
            name = from_db[1]
            date = from_db[2]
            parts = name.split("-")
            if len(parts) == 2:
                self.from_combo.setCurrentText(parts[0].strip())
                self.to_combo.setCurrentText(parts[1].strip())
            else:
                parts = name.split("—")
                if len(parts) == 2:
                    self.from_combo.setCurrentText(parts[0].strip())
                    self.to_combo.setCurrentText(parts[1].strip())
                else:
                    self.from_combo.setCurrentText("")
                    self.to_combo.setCurrentText("")

            if date:
                self.date_edit.setDate(QDate.fromString(str(date), "yyyy-MM-dd"))

    def save(self):
        from_city = self.from_combo.currentText().strip()
        to_city = self.to_combo.currentText().strip()
        date = self.date_edit.date().toString("yyyy-MM-dd")

        if not from_city or not to_city:
            QMessageBox.warning(self, "Ошибка", "Выберите оба города!")
            return

        route_name = f"{from_city}-{to_city}"

        try:
            if self.route_id is None:
                insert_route(route_name, date)
            else:
                update_route(self.route_id, route_name, date)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))