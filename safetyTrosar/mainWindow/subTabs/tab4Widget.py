from PyQt5 import QtWidgets
from typing import Tuple
from pandas import DataFrame
from openpyxl.worksheet.merge import MergedCellRange

from safetyTrosar import subWidget
from safetyTrosar.structure.safetyPmData import SafetyPmData


class TabSubWidget(subWidget.WorksheetWidget):
    safety_data: SafetyPmData
    TAB_NAME = "안전대책"

    def __init__(self, main_window, tab_widget: QtWidgets.QTabWidget):
        super().__init__(main_window, tab_widget, self.TAB_NAME)

        self.init_view()

    def init_data(self, safety_data: SafetyPmData):
        self.safety_data = safety_data
        table = safety_data.safety_measures.table
        if True or table.dataframe is None:
            self.generate_dataframe()
        self.tableview_manager.init_data(table_data=table)
        self.tableview_manager.show_table()

    def init_view(self):
        self.setTabVisible(False)
        self.toolButton_save.setEnabled(True)
        self.toolButton_export.setEnabled(True)
        self.tableView.setEnabled(True)

    def generate_dataframe(self):
        hazop_table = self.safety_data.hazop_analysis.table
        measure_data = {}
        for i, data in hazop_table.dataframe.iterrows():
            if len(data[hazop_table.HAZARD_ID]) > 0:
                if data[hazop_table.SAFETY_MEASURE] not in measure_data:
                    measure_data[data[hazop_table.SAFETY_MEASURE]] = []
                measure_data[data[hazop_table.SAFETY_MEASURE]].append(data[hazop_table.HAZARD_ID])

        safety_table = self.safety_data.safety_measures.table
        data_dict = {
            safety_table.NAME: [],
            safety_table.DESCRIPTION: [],
            safety_table.SAFETY_REQUIREMENTS: [],
            safety_table.HAZARD_ID: []
        }
        for key, value in measure_data.items():
            data_dict[safety_table.NAME].append(key)
            data_dict[safety_table.DESCRIPTION].append("")
            data_dict[safety_table.SAFETY_REQUIREMENTS].append("")
            data_dict[safety_table.HAZARD_ID].append(value)

        dataframe = DataFrame(data_dict)

        safety_table.set_dataframe(dataframe)
        protect_column_name_list = ["이름", "위험원 ID"]
        for i, name in enumerate(safety_table.dataframe.columns):
            if name in protect_column_name_list:
                safety_table.set_cell_protected(safety_table.index_to_cell_range(0, i, len(safety_table.dataframe.index), i))

    def toolButton_next_clicked(self):
        try:
            self.safety_data.save_pm_server()
            if self.is_worksheet_validity() is True:
                # 위험원 목록 탭 성성 및 초기화
                hazard_log = self.main_window.sub_tabs.hazard_log
                hazard_log.init_data(safety_data=self.safety_data)
                hazard_log.setTabVisible(True)
                hazard_log.setTabSelected()

        except Exception as ex:
            self.print_info(str(ex))

    def is_worksheet_validity(self):
        return True
        table = self.safety_data.safety_measures.table
        for data in table.data_list:
            if len(data.safety_requirements) == 0:
                return False
            elif len(data.description) == 0:
                return False
        return True
