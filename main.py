import sys
import os

# Добавляем текущую директорию в путь поиска модулей
sys.path.append(os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from db import init_default_users
from login_dialog import LoginDialog
from views.main_window import MainWindow

def main():
    # ЕДИНСТВЕННЫЙ QApplication — создаётся здесь
    app = QApplication(sys.argv)

    # Инициализация пользователей (если их ещё нет)
    init_default_users()

    # Авторизация
    login_dialog = LoginDialog()
    if not login_dialog.exec():
        sys.exit(0)

    # Запуск главного окна
    main_window = MainWindow(login_dialog.role)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()