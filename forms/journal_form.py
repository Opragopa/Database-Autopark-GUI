from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QPushButton, QHBoxLayout,
    QMessageBox, QVBoxLayout, QDateTimeEdit
)

from db_utils import get_all_cars_for_combo, get_all_routes_for_combo, check_car_returned


class JournalForm(QDialog):
    def __init__(self, journal_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать рейс" if journal_id else "Новый рейс")
        self.journal_id = journal_id
        self.setMinimumWidth(400)

        self.time_out_edit = QDateTimeEdit()
        self.time_out_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_out_edit.setCalendarPopup(True)

        self.time_in_edit = QDateTimeEdit()
        self.time_in_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_in_edit.setCalendarPopup(True)
        self.time_in_edit.setDateTime(QDateTime.currentDateTime())

        self.car_combo = QComboBox()
        self.route_combo = QComboBox()

        cars = get_all_cars_for_combo()
        routes = get_all_routes_for_combo()

        self.car_ids = [cid for cid, _ in cars]
        self.route_ids = [rid for rid, _ in routes]

        self.car_combo.addItems([f"{num} (ID: {cid})" for cid, num in cars])
        self.route_combo.addItems([f"{name} (ID: {rid})" for rid, name in routes])

        self.car_ids = [cid for cid, _ in cars]
        self.route_ids = [rid for rid, _ in routes]

        form = QFormLayout()
        form.addRow("Время выезда:", self.time_out_edit)
        form.addRow("Время возвращения:", self.time_in_edit)
        form.addRow("Автомобиль:", self.car_combo)
        form.addRow("Маршрут:", self.route_combo)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.reject)

        if journal_id:
            self.load_data()

    def load_data(self):
        pass

    def save(self):
        time_out = self.time_out_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        time_in_str = self.time_in_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        time_in = time_in_str if time_in_str != "2000-01-01 00:00:00" else None

        car_index = self.car_combo.currentIndex()
        route_index = self.route_combo.currentIndex()
        auto_id = self.car_ids[car_index]
        route_id = self.route_ids[route_index]

        if not check_car_returned(auto_id):
            QMessageBox.warning(self, "Ошибка", f"Автомобиль с ID {auto_id} ещё не вернулся в парк!")
            return

        from db_utils import insert_journal, update_journal
        try:
            if self.journal_id is None:
                insert_journal(time_out, time_in, auto_id, route_id)
            else:
                update_journal(self.journal_id, time_out, time_in, auto_id, route_id)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))