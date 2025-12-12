from PySide6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLineEdit
)
from validation import validate_russian_plate

class CarForm(QDialog):
    def __init__(self, car_id=None, parent=None):
        super().__init__(parent)
        self.car_id = car_id
        self.setWindowTitle("Новый автомобиль" if car_id is None else "Редактировать автомобиль")
        self.setMinimumWidth(400)

        self.num_edit = QLineEdit()
        self.num_edit.textChanged.connect(self.auto_upper)
        self.color_combo = QComboBox()
        self.mark_combo = QComboBox()
        self.driver_combo = QComboBox()

        colors = ["Белый", "Чёрный", "Серый", "Синий", "Красный", "Зелёный",
                  "Жёлтый", "Оранжевый", "Фиолетовый", "Коричневый", "Бежевый", "Серебристый"]
        self.color_combo.addItems(colors)

        brands = ["Форд", "Мерседес", "Газель", "ВАЗ", "Тойота", "Хендай", "Шкода", "БМВ",
                  "Ауди", "Киа", "Рено", "Ниссан", "Митсубиси", "Лада", "УАЗ", "КамАЗ"]
        self.mark_combo.addItems(brands)

        from db_utils import get_all_drivers_for_select
        drivers = get_all_drivers_for_select()
        self.driver_ids = [0]
        self.driver_combo.addItem("— не назначен —")
        for did, name in drivers:
            self.driver_ids.append(did)
            self.driver_combo.addItem(name)

        form = QFormLayout()
        form.addRow("Номер:", self.num_edit)
        form.addRow("Цвет:", self.color_combo)
        form.addRow("Марка:", self.mark_combo)
        form.addRow("Водитель:", self.driver_combo)

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

        if car_id:
            self.load_data()

    def auto_upper(self):
        cursor = self.num_edit.cursorPosition()
        text = self.num_edit.text()
        self.num_edit.setText(text.upper())
        self.num_edit.setCursorPosition(cursor)

    def load_data(self):
        from db_utils import get_car_by_id
        car = get_car_by_id(self.car_id)
        if car:
            _, num, color, mark, pid, _ = car
            self.num_edit.setText(num or "")
            self.color_combo.setCurrentText(color or "Белый")
            self.mark_combo.setCurrentText(mark or "Форд")
            try:
                idx = self.driver_ids.index(pid) if pid else 0
                self.driver_combo.setCurrentIndex(idx)
            except ValueError:
                self.driver_combo.setCurrentIndex(0)

    def save(self):
        num = self.num_edit.text().strip()
        if not validate_russian_plate(num):
            QMessageBox.warning(self, "Ошибка",
                "Номер должен быть в формате А123БВ.\n"
                "Разрешённые буквы: А, В, Е, К, М, Н, О, Р, С, Т, У, Х"
            )
            return

        color = self.color_combo.currentText()
        mark = self.mark_combo.currentText()
        driver_id = self.driver_ids[self.driver_combo.currentIndex()]

        try:
            if self.car_id is None:
                from db_utils import insert_car
                insert_car(num, color, mark, driver_id or None)
            else:
                from db_utils import update_car
                update_car(self.car_id, num, color, mark, driver_id or None)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))