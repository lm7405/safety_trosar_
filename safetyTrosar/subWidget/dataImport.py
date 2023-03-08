# -*- coding: utf-8 -*-

from typing import Optional
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QDialog, QPlainTextEdit
from PyQt5 import uic
from openpyxl import load_workbook
from openpyxl.worksheet.merge import CellRange
from safetyTrosar import config
from safetyTrosar.structure.qtableviewModel import *


# 화면을 띄우는데 사용되는 Class 선언
class DataImportWindow(QDialog, uic.loadUiType(config.resource_path + "/subWidget.data_import.ui")[0]):
    df_import_data: pd.DataFrame = None
    cell_offset: Optional[Tuple[str, str]] = None
    merged_cell_ranges: List[CellRange] = None

    def __init__(self, main_window, output: List, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.output = output
        self.debug = main_window.debug
        self.main_window = main_window

        self.toolButton_browse = self.toolButton_browse
        self.toolButton_refresh = self.toolButton_refresh
        self.toolButton_ok = self.toolButton_ok
        self.toolButton_cancel = self.toolButton_cancel

        self.qtableview_model = QTableViewModel(self.tableView_mapping)
        self.plainTextEdit_excelPath: QPlainTextEdit = self.plainTextEdit_excelPath
        self.plainTextEdit_startCell: QPlainTextEdit = self.plainTextEdit_startCell
        self.plainTextEdit_headerRow: QPlainTextEdit = self.plainTextEdit_headerRow

        self.init_action()

    def init_action(self):
        self.toolButton_browse.clicked.connect(self.toolButton_browse_clicked)
        self.toolButton_refresh.clicked.connect(self.toolButton_refresh_clicked)
        self.toolButton_ok.clicked.connect(self.toolButton_ok_clicked)
        self.toolButton_cancel.clicked.connect(self.toolButton_cancel_clicked)

    def import_excel(self, file_name):
        pass

    def toolButton_browse_clicked(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
        self.plainTextEdit_excelPath.setPlainText(file_name[0])
        self.toolButton_refresh_clicked(alert=False)

    def toolButton_refresh_clicked(self, alert=True):
        try:
            self.read_excel()
            if self.df_import_data is not None:
                self.qtableview_model.init_data(
                    dataframe=self.df_import_data,
                    cell_offset=self.cell_offset,
                    merged_cell_ranges=self.merged_cell_ranges
                )
        except Exception as ex:
            if alert is True:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage(str(ex))
            else:
                if self.debug is True:
                    raise ex
                else:
                    print(str(__class__) + ": " + str(ex))

    def toolButton_ok_clicked(self):
        if self.df_import_data is not None:
            self.output.append(self.qtableview_model)
        self.close()

    def toolButton_cancel_clicked(self):
        self.close()

    def read_excel(self):
        # 입력 값 읽기
        file_name = self.plainTextEdit_excelPath.toPlainText()
        start_cell_text = self.plainTextEdit_startCell.toPlainText()
        header_row_text = self.plainTextEdit_headerRow.toPlainText()

        # 입력 값이 비어있을 경우 기본 값 로드
        if start_cell_text == '':
            start_cell_text = self.plainTextEdit_startCell.placeholderText()
        if header_row_text == '':
            header_row_text = self.plainTextEdit_headerRow.placeholderText()

        # 입력 값(start_cell) 파싱 및 유효성 검사. 실패 시 에러
        start_cell_index = index_from_string(start_cell_text)
        if start_cell_index is not None:
            start_cell_row = start_cell_index[0]
            start_cell_column = start_cell_index[1]
        else:
            raise Exception("Invalid \"Start Cell\"")

        # 입력 값(header_row) 유효성 검사. 실패 시 에러
        if header_row_text.isdigit():
            header_row = int(header_row_text)
        else:
            raise Exception("Invalid \"Multiple Header\"")

        # 입력 값(file_name) 유효성 검사. 실패 시 에러
        try:
            sheet_index = 0
            # openpyxl 엑셀 읽기(merged cell 확인)
            wb = load_workbook(filename=file_name)
            ws = wb.worksheets[sheet_index]
            self.merged_cell_ranges = ws.merged_cell_ranges

            # pandas 엑셀 읽기
            self.df_import_data = pd.read_excel(
                file_name,
                sheet_name=sheet_index,
                header=list(range(0, header_row)),
                index_col=None,
                skiprows=start_cell_row,
                keep_default_na=False,
            )
            self.df_import_data = self.df_import_data.iloc[:, start_cell_column:]
            self.cell_offset = (start_cell_row + header_row, start_cell_column)
        except Exception as ex:
            if self.debug is True:
                raise ex
            else:
                print(str(__class__) + ": " + str(ex))
            raise Exception("Cannot read \"Excel File\"")


def show_window(main_window):
    output: List[QTableViewModel] = []

    sub_window = DataImportWindow(main_window, output)
    # dialog.safety_trosar.setupUi(dialog)
    sub_window.exec_()

    if len(output) > 0:
        return output[-1]
    else:
        return None
