from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
)
from validation import validate_name_part

class DriverForm(QDialog):
    def __init__(self, driver_id=None, parent=None):
        super().__init__(parent)
        self.driver_id = driver_id
        self.setWindowTitle("Новый водитель" if driver_id is None else "Редактировать водителя")
        self.setMinimumWidth(300)

        self.first_edit = QLineEdit()
        self.last_edit = QLineEdit()
        self.father_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Имя:", self.first_edit)
        form.addRow("Фамилия:", self.last_edit)
        form.addRow("Отчество:", self.father_edit)

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

        if driver_id:
            self.load_data()

    def load_data(self):
        from db_utils import get_driver_by_id
        driver = get_driver_by_id(self.driver_id)
        if driver:
            _, first, last, father = driver
            self.first_edit.setText(first or "")
            self.last_edit.setText(last or "")
            self.father_edit.setText(father or "")

    def save(self):
        first = self.first_edit.text().strip()
        last = self.last_edit.text().strip()
        father = self.father_edit.text().strip()

        if not last or not validate_name_part(last, "last"):
            QMessageBox.warning(self, "Ошибка", "Фамилия должна быть реальной русской фамилией")
            return

        if first and not validate_name_part(first, "first"):
            QMessageBox.warning(self, "Ошибка", "Имя должно быть реальным русским именем")
            return

        if father and not validate_name_part(father, "father"):
            QMessageBox.warning(self, "Ошибка", "Отчество должно быть реальным русским отчеством")
            return

        try:
            if self.driver_id is None:
                from db_utils import insert_driver
                insert_driver(first, last, father)
            else:
                from db_utils import update_driver
                update_driver(self.driver_id, first, last, father)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))