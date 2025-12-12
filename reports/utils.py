import os
from openpyxl import Workbook

def export_to_txt(filename: str, headers: list, rows: list):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\t'.join(headers) + '\n')
        for row in rows:
            f.write('\t'.join(str(cell) for cell in row) + '\n')
    return os.path.abspath(filename)

def export_to_excel(filename: str, headers: list, rows: list):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(filename)
    return os.path.abspath(filename)