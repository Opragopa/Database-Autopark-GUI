from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
)

from db_utils import call_distribute_bonuses
from reports.utils import export_to_excel, export_to_txt
from table_utils import NumericQTableWidgetItem


class BonusReport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        form = QFormLayout()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        self.bonus_amount = QLineEdit("10000")
        self.start_date.setDate(QDate(2024, 1, 1))
        self.end_date.setDate(QDate.currentDate())
        form.addRow("Начало периода:", self.start_date)
        form.addRow("Конец периода:", self.end_date)
        form.addRow("Общий бонус (RUB):", self.bonus_amount)
        self.layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Сформировать отчёт")
        self.export_xls = QPushButton("Экспорт в Excel")
        self.export_txt = QPushButton("Экспорт в TXT")
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.export_xls)
        btn_layout.addWidget(self.export_txt)
        self.layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Имя", "Фамилия", "Отчество",
            "Рейсов", "Лучшее время (сек)", "Бонус (RUB)", "Доля (%)"
        ])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.run_btn.clicked.connect(self.run_report)
        self.export_xls.clicked.connect(self.export_excel)
        self.export_txt.clicked.connect(self.export_text)

        self.report_data = []

    def run_report(self):
        try:
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            bonus = float(self.bonus_amount.text())
            self.report_data = call_distribute_bonuses(start, end, bonus)
            self.table.setRowCount(len(self.report_data))
            for i, row in enumerate(self.report_data):
                self.table.setItem(i, 0, NumericQTableWidgetItem(row[0]))  # ID
                for j in range(1, 8):
                    self.table.setItem(i, j, QTableWidgetItem(str(row[j]) if row[j] is not None else ""))

            self.table.setRowCount(len(self.report_data))
            for i, row in enumerate(self.report_data):
                for j, val in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(val) if val is not None else ""))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчёт:\n{str(e)}")

    def export_excel(self):
        if not self.report_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        try:
            path = export_to_excel("bonus_report.xlsx", [
                "ID", "Имя", "Фамилия", "Отчество",
                "Рейсов", "Лучшее время (сек)", "Бонус (RUB)", "Доля (%)"
            ], self.report_data)
            QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить Excel:\n{str(e)}")

    def export_text(self):
        if not self.report_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        try:
            path = export_to_txt("bonus_report.txt", [
                "ID", "Имя", "Фамилия", "Отчество",
                "Рейсов", "Лучшее время (сек)", "Бонус (RUB)", "Доля (%)"
            ], self.report_data)
            QMessageBox.information(self, "Успех", f"Отчёт сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить TXT:\n{str(e)}")