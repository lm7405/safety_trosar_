import sys
from typing import Union, List
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem


def print_merged_cells(table_widget):
    class Cell(object):
        row: int
        column: int

        def __init__(self, row: int, column: int, cell_string: Union[None, str] = None):
            self.row = row
            self.column = column

            if cell_string is not None:
                self.row, self.column = self.string_to_coordinates(cell_string)

        @staticmethod
        def string_to_coordinates(s):
            row_number = None
            column_number = None
            column_letters = ''

            for char in s:
                if not (char.isupper() or char.isdigit()):
                    raise ValueError("Input string must contain only uppercase letters and digits")
                if char.isdigit():
                    row_number = int(column_letters + char)
                    break
                else:
                    column_letters += char

            for letter in column_letters:
                column_number = column_number * 26 + (ord(letter) - ord('A') + 1)
            return column_number, row_number

    class CellRange(object):
        top_left_cell: Cell
        row_span: int
        column_span: int

        def __init__(self, top_left_cell: Cell, row_span: int, column_span: int):
            self.top_left_cell = top_left_cell
            self.row_span = row_span
            self.column_span = column_span

        def __contains__(self, item: Cell):
            if not isinstance(item, Cell):
                raise TypeError("item must be a Cell object")
            row_in_range = (self.top_left_cell.row <= item.row <= self.top_left_cell.row + self.row_span - 1)
            col_in_range = (
                        self.top_left_cell.column <= item.column <= self.top_left_cell.column + self.column_span - 1)
            return row_in_range and col_in_range

    class MergedCellRanges(object):
        __data__: List[CellRange] = []

        def append(self, item: CellRange):
            if not isinstance(item, CellRange):
                raise TypeError("item must be a CellRange")
            self.__data__.append(item)

        def __contains__(self, item: Cell):
            if not isinstance(item, Cell):
                raise TypeError("item must be a CellRange")
            for item_ in self.__data__:
                if item in item_:
                    return True
            return False

        def __getitem__(self, index: int):
            return self.__data__[index]

        def insert_row(self, row, column):
            # TODO: need test
            # call after insert row on qTableWidget
            column_i = 0
            cell = Cell(row, column_i)
            for cell_range in self:
                if cell in cell_range:
                    cell_range.row_span += 1
                    table_widget.setSpan(
                        cell_range.top_left_cell.row,
                        cell_range.top_left_cell.column,
                        cell_range.row_span,
                        cell_range.column_span
                    )
                column_i += cell_range.column_span - 1

                if column_i >= column:
                    break
                cell = Cell(row, column)

    merged_ranges: MergedCellRanges = MergedCellRanges()
    for row_ in range(table_widget.rowCount()):
        for column_ in range(table_widget.columnCount()):
            top_left_cell_ = Cell(row=row_, column=column_)
            row_span_ = table_widget.rowSpan(row_, column_)
            column_span_ = table_widget.columnSpan(row_, column_)

            if row_span_ > 1 or column_span_ > 1:
                if top_left_cell_ not in merged_ranges:
                    merged_ranges.append(CellRange(top_left_cell_, row_span_, column_span_))
    return merged_ranges


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle('QTableWidget Example')
        self.resize(600, 400)

        # Create a QTableWidget object and set the number of rows and columns
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(10)
        self.table_widget.setColumnCount(5)

        # hide the row and column headers
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)

        # Set the table headers
        headers = ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5']
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Add the QTableWidget to the main window
        self.setCentralWidget(self.table_widget)

        # test code
        self.table_widget.setItem(0, 0, QTableWidgetItem('Apple'))
        self.table_widget.setItem(0, 1, QTableWidgetItem('Banana'))
        self.table_widget.setItem(1, 0, QTableWidgetItem('Orange'))
        self.table_widget.setItem(1, 1, QTableWidgetItem('Grape'))
        self.table_widget.setSpan(0, 0, 2, 2)
        print_merged_cells(self.table_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())