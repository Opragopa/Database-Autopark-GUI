from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QLayout
)

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.role = None

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        layout.addWidget(self.login_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Войти")
        self.cancel_button = QPushButton("Отмена")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        layout.setSizeConstraint(QLayout.SetFixedSize)  # ← автоматический фиксированный размер

        self.ok_button.clicked.connect(self.handle_login)
        self.cancel_button.clicked.connect(self.reject)

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text()
        from auth import authenticate
        role = authenticate(login, password)

        if role:
            self.role = role
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")