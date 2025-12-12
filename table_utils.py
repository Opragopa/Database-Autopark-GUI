from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt

class NumericQTableWidgetItem(QTableWidgetItem):
    """
    Элемент таблицы, который сортируется как число (int/float), а не как строка.
    """
    def __init__(self, value):
        super().__init__(str(value))
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if isinstance(value, (int, float)):
            self.value = value
        else:
            self.value = 0

    def __lt__(self, other):
        if isinstance(other, NumericQTableWidgetItem):
            return self.value < other.value
        return super().__lt__(other)