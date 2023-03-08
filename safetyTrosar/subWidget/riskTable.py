# -*- coding: utf-8 -*-

from typing import Optional, Tuple, List
import pandas as pd
from pandas import DataFrame
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from openpyxl.worksheet.merge import CellRange

from safetyTrosar import config
from safetyTrosar import SafetyPmData, PandasTableViewMgr, SeverityFrequency


# 화면을 띄우는데 사용되는 Class 선언
class RiskWindow(QDialog, uic.loadUiType(config.resource_path + "/subWidget.risk_table.ui")[0]):
    df_import_data: pd.DataFrame = None
    cell_offset: Optional[Tuple[str, str]] = None
    merged_cell_ranges: List[CellRange] = None

    def __init__(self, main_window, safety_data: "SafetyPmData", output: List, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.output = output
        self.main_window = main_window
        self.safety_data = safety_data

        self.qtableview_frequency = PandasTableViewMgr(self.tableView_3)
        self.qtableview_severity = PandasTableViewMgr(self.tableView_4)
        self.qtableview_risk = PandasTableViewMgr(self.tableView_6)
        self.qtableview_risk_matrix = PandasTableViewMgr(self.tableView_5)

        self.init_action()
        self.init_data()

        self.output.append("Modified")

    def init_action(self):
        pass

    def init_data(self):
        def set_risk_data(sf_data_: SeverityFrequency):
            data_list = [
                ["빈번한 발생", "0", "", "10E-3 이상"],
                ["종종 발생", "1", "", "10E-4 < ~ 10E-3"],
                ["가끔 발생", "2", "", "10E-6 < ~ 10E-4"],
                ["미약함", "3", "", "10E-8 < ~ 10E-6"],
                ["거의 없음", "4", "", "10E-9 < ~ 10E-8"],
                ["전혀 없음", "5", "", "10E-9 이하"]
            ]
            column_labels = ["발생 빈도", "등급", "설명", "기준"]

            dataframe_data = {}
            for i, label in enumerate(column_labels):
                dataframe_data[label] = []
                for data in data_list:
                    dataframe_data[label].append(data[i])
            dataframe = DataFrame(dataframe_data)
            sf_data_.frequency_table.set_dataframe(dataframe)

            data_list = [
                ["치명적 위험", "A", "인명의 사망 및 시스템의 손실", "사망 사고, 30분 이상 지연"],
                ["중대한 위험", "B", "인명 부상 및 시스템 고장", "인명 부상, 10-30분 지연"],
                ["중요하지 않은 위험", "C", "시스템의 고장으로 정지 및 운행에 지장", "10분이하 지연"],
                ["사소한 위험", "D", "고장으로 유지보수 필요, 시스템 정상 운행 가능", "정상 운행 가능"],
                ["정상", "E", "", ""]
            ]
            column_labels = ["위험성", "등급", "설명", "기준"]

            dataframe_data = {}
            for i, label in enumerate(column_labels):
                dataframe_data[label] = []
                for data in data_list:
                    dataframe_data[label].append(data[i])
            dataframe = DataFrame(dataframe_data)
            sf_data_.severity_table.set_dataframe(dataframe)

            data_list = [
                ["Intolerable", "I", "허용 불가능한 위험", "N", "A2, A3, A4, A5, B3, B4, B5, C4, C5, D5"],
                ["Undesirable", "U", "불가피한 경우 허용 가능한 위험", "Y", "A1, B1, B2, C2, C3, D3, D4, E5"],
                ["Tolerable", "T", "허용 가능한 위험", "Y", "A0, B0, C1, D2, E3, E4"],
                ["Negligible", "N", "무시할 수 있는 위험", "Y", "C0, D0, D1, E0, E1, E2"],
            ]
            column_labels = ["명칭", "등급", "설명", "허용 여부", "대상(임시)"]

            dataframe_data = {}
            for i, label in enumerate(column_labels):
                dataframe_data[label] = []
                for data in data_list:
                    dataframe_data[label].append(data[i])
            dataframe = DataFrame(dataframe_data)
            sf_data_.risk_table.set_dataframe(dataframe)

            data_list = [
                ["U", "I", "I", "I", "I", ],
                ["T", "U", "I", "I", "I", ],
                ["T", "U", "U", "I", "I", ],
                ["N", "T", "U", "U", "I", ],
                ["N", "N", "T", "U", "U", ],
                ["N", "N", "N", "T", "T", ],
            ]
            column_labels = ["E", "D", "C", "B", "A"]

            dataframe_data = {}
            for i, label in enumerate(column_labels):
                dataframe_data[label] = []
                for data in data_list:
                    dataframe_data[label].append(data[i])
            dataframe = DataFrame(dataframe_data)
            sf_data_.risk_matrix.set_dataframe(dataframe)

        sf_data = self.safety_data.hazop_analysis.info.severity_frequency
        set_risk_data(sf_data)
        self.qtableview_frequency.init_data(sf_data.frequency_table)
        self.qtableview_severity.init_data(sf_data.severity_table)
        self.qtableview_risk.init_data(sf_data.risk_table)
        self.qtableview_risk_matrix.init_data(sf_data.risk_matrix)

        cell_range = self.qtableview_frequency.table_data.index_to_cell_range(0, 0, 10, 10)
        self.qtableview_frequency.table_data.set_cell_protected(cell_range)
        self.qtableview_severity.table_data.set_cell_protected(cell_range)
        self.qtableview_risk.table_data.set_cell_protected(cell_range)
        self.qtableview_risk_matrix.table_data.set_cell_protected(cell_range)


def show_window(main_window, safety_data: "SafetyPmData"):
    output: List[PandasTableViewMgr] = []

    sub_window = RiskWindow(main_window, safety_data, output)
    # dialog.safety_trosar.setupUi(dialog)
    sub_window.exec_()

    if len(output) > 0:
        return output[-1]
    else:
        return None
