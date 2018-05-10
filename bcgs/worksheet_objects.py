from openpyxl import Workbook, worksheet

class WorkbookManager(object):
    # if we need more we can add them
    _col_letters = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N', 'M', 'O', 'P')

    def __init__(self, workbook: worksheet.worksheet.Worksheet):
        self._wb = workbook
        self._widths = {}

    @property
    def title(self):
        return self._wb.title

    @title.setter
    def title(self, value):
        self._wb.title = value

    def append(self, row):
        for idx, value in enumerate(row):
            length = len(str(value))
            letter = self._col_letters[idx]
            if length > self._widths.get(letter, 0):
                self._widths[letter] = length
                self._wb.column_dimensions[letter].width = length

        self._wb.append(row)