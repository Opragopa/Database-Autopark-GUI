from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox
)
from db_utils import get_routes_avg_time


class RouteTimeReport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Сформировать отчёт")
        self.export_xls = QPushButton("Экспорт в Excel")
        self.export_txt = QPushButton("Экспорт в TXT")
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.export_xls)
        btn_layout.addWidget(self.export_txt)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Маршрут", "Среднее время (мин)"])
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.run_btn.clicked.connect(self.run_report)
        self.export_xls.clicked.connect(self.export_excel)
        self.export_txt.clicked.connect(self.export_text)

        self.report_data = []

    def run_report(self):
        """Формирует отчёт со средним временем по маршрутам."""
        try:
            data = get_routes_avg_time()
            if not data:
                QMessageBox.information(self, "Информация", "Нет данных для отображения.\nУбедитесь, что в журнале есть завершённые рейсы.")
                self.table.setRowCount(0)
                self.report_data = []
                return

            safe_data = []
            for item in data:
                if isinstance(item, (tuple, list)) and len(item) >= 2:
                    route = str(item[0]) if item[0] is not None else "Неизвестный маршрут"
                    avg_time = float(item[1]) if item[1] is not None else 0.0
                    safe_data.append((route, avg_time))

            self.report_data = safe_data
            self.table.setRowCount(len(safe_data))
            for i, (route, avg) in enumerate(safe_data):
                self.table.setItem(i, 0, QTableWidgetItem(route))
                self.table.setItem(i, 1, QTableWidgetItem(f"{avg:.2f}"))
            self.table.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка при формировании отчёта",
                f"Не удалось загрузить данные:\n{str(e)}\n\n"
                "Возможные причины:\n"
                "• В журнале нет завершённых рейсов (нет time_in)\n"
                "• Ошибка в данных маршрутов"
            )
            self.table.setRowCount(0)
            self.report_data = []

    def export_excel(self):
        if not self.report_data:
            QMessageBox.warning(self, "Экспорт", "Нет данных для экспорта.")
            return
        try:
            from reports.utils import export_to_excel
            path = export_to_excel(
                "route_avg_time.xlsx",
                ["Маршрут", "Среднее время (мин)"],
                self.report_data
            )
            QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось сохранить Excel:\n{str(e)}")

    def export_text(self):
        if not self.report_data:
            QMessageBox.warning(self, "Экспорт", "Нет данных для экспорта.")
            return
        try:
            from reports.utils import export_to_txt
            path = export_to_txt(
                "route_avg_time.txt",
                ["Маршрут", "Среднее время (мин)"],
                self.report_data
            )
            QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось сохранить TXT:\n{str(e)}")