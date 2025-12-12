import sys
import os

sys.path.append(os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from db import init_default_users
from login_dialog import LoginDialog
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    init_default_users()

    login_dialog = LoginDialog()
    if not login_dialog.exec():
        sys.exit(0)

    main_window = MainWindow(login_dialog.role)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()