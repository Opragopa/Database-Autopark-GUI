from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox
)
from db_utils import get_routes_avg_time
from reports.utils import export_to_excel, export_to_txt
from table_utils import NumericQTableWidgetItem


class RouteTimeReport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Сформировать отчёт")
        self.export_xls = QPushButton("Экспорт в Excel")
        self.export_txt = QPushButton("Экспорт в TXT")
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.export_xls)
        btn_layout.addWidget(self.export_txt)
        self.layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Маршрут", "Среднее время (мин)"])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.run_btn.clicked.connect(self.run_report)
        self.export_xls.clicked.connect(self.export_excel)
        self.export_txt.clicked.connect(self.export_text)

        self.report_data = []

    def run_report(self):
        try:
            self.report_data = get_routes_avg_time()
            self.table.setRowCount(len(self.report_data))
            for i, row in enumerate(self.report_data):
                self.table.setItem(i, 0, NumericQTableWidgetItem(row[0]))  # ID
                for j in range(1, 8):
                    self.table.setItem(i, j, QTableWidgetItem(str(row[j]) if row[j] is not None else ""))
            self.table.setRowCount(len(self.report_data))
            for i, (route, avg) in enumerate(self.report_data):
                self.table.setItem(i, 0, QTableWidgetItem(route))
                self.table.setItem(i, 1, QTableWidgetItem(str(avg)))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные:\n{str(e)}")

    def export_excel(self):
        if not self.report_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        path = export_to_excel("route_avg_time.xlsx", ["Маршрут", "Среднее время (мин)"], self.report_data)
        QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{path}")

    def export_text(self):
        if not self.report_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        path = export_to_txt("route_avg_time.txt", ["Маршрут", "Среднее время (мин)"], self.report_data)
        QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{path}")