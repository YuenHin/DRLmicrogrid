import xlrd2 as xlrd
import xlwt
import numpy as np
from xlutils.copy import copy

'''
从EXCEL中读取数据的方法
path：表示文件路径
fromCol:表示起始的列
toCol；表示终止的列
fromRow:表示起始的行
toRow；表示终止的行
'''
def getDataFromExcel(path, fromCol, toCol, fromRow, toRow):
    path = xlrd.open_workbook(path)
    sheet = path.sheet_by_index(0)
    data = np.array([[sheet.cell_value(r, c) for c in range(fromCol, toCol)] for r in range(fromRow, toRow)])
    return data

def writeDatatoExcel(path, col, row, data):
    try:
        with xlrd.open_workbook(path, formatting_info=True) as wb:
            new_excel = copy(wb)

            ws = new_excel.get_sheet(0)
            for i in range(len(data)):
                ws.write(row + i, col, data[i])
            new_excel.save(path)
    except FileNotFoundError:
        # 创建工作簿
        wb = xlwt.Workbook(path)
        sh1 = wb.add_sheet('sheet')
        for i in range(len(data)):
            sh1.write(row + i, col, data[i])
        wb.save(path)


