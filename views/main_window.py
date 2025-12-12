from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QLabel, QWidget, QVBoxLayout

from forms.cars_view import CarsView
from forms.drivers_view import DriversView
from forms.journal_view import JournalView
from forms.routes_view import RoutesView
from reports.bonus_report import BonusReport
from reports.route_time_report import RouteTimeReport


class MainWindow(QMainWindow):
    def __init__(self, role: str):
        super().__init__()
        self.role = role
        self.setWindowTitle(f"Автопарк — {'Администратор' if role == 'admin' else 'Пользователь'}")
        self.resize(1000, 700)

        # Меню
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        # СПРАВОЧНИКИ
        ref_menu = menubar.addMenu("СПРАВОЧНИКИ")
        ref_menu.addAction("Водители", self.show_drivers)
        ref_menu.addAction("Автомобили", self.show_cars)
        ref_menu.addAction("Маршруты", self.show_routes)

        # ЖУРНАЛЫ
        journal_menu = menubar.addMenu("ЖУРНАЛЫ")
        journal_menu.addAction("Журнал рейсов", self.show_journal)

        # ОТЧЁТЫ
        report_menu = menubar.addMenu("ОТЧЁТЫ")
        report_menu.addAction("Бонусы водителям", self.show_bonus_report)
        report_menu.addAction("Среднее время по маршрутам", self.show_route_time_report)

        if self.role != 'admin':
            pass

        central = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("Добро пожаловать в систему управления автопарком!"))
        central.setLayout(layout)
        self.setCentralWidget(central)

    def show_drivers(self):
        self.drivers_view = DriversView(self.role)
        self.setCentralWidget(self.drivers_view)

    def show_cars(self):
        self.cars_view = CarsView(self.role)
        self.setCentralWidget(self.cars_view)

    def show_routes(self):
        self.routes_view = RoutesView(self.role)
        self.setCentralWidget(self.routes_view)

    def show_journal(self):
        self.journal_view = JournalView(self.role)
        self.setCentralWidget(self.journal_view)

    def show_bonus_report(self):
        self.bonus_report = BonusReport()
        self.setCentralWidget(self.bonus_report)

    def show_route_time_report(self):
        self.route_report = RouteTimeReport()
        self.setCentralWidget(self.route_report)

    def msg(self, text):
        QMessageBox.information(self, "В разработке", f"Форма «{text}» будет реализована далее.")