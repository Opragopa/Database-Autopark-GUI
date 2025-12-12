from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDateEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import QDate
from validation import validate_route_name

class RouteForm(QDialog):
    def __init__(self, route_id=None, parent=None):
        super().__init__(parent)
        self.route_id = route_id
        self.setWindowTitle("Новый маршрут" if route_id is None else "Редактировать маршрут")
        self.setMinimumWidth(350)

        self.name_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        form = QFormLayout()
        form.addRow("Название маршрута:", self.name_edit)
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
        from db_utils import get_route_by_id
        route = get_route_by_id(self.route_id)
        if route:
            _, name, date = route
            self.name_edit.setText(name or "")
            if date:
                self.date_edit.setDate(QDate.fromString(str(date), "yyyy-MM-dd"))

    def save(self):
        name = self.name_edit.text().strip()
        if not validate_route_name(name):
            QMessageBox.warning(self, "Ошибка",
                "Название маршрута должно быть либо:\n"
                "• Простым названием (минимум 2 символа),\n"
                "• Или в формате 'Город-Город' с реальными городами РФ (например: Москва-Сочи)."
            )
            return

        date = self.date_edit.date().toString("yyyy-MM-dd")

        try:
            if self.route_id is None:
                from db_utils import insert_route
                insert_route(name, date)
            else:
                from db_utils import update_route
                update_route(self.route_id, name, date)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))