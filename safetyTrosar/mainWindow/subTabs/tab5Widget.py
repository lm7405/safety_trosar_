from PyQt5 import QtWidgets
from typing import Tuple
from pandas import DataFrame
from openpyxl.worksheet.merge import MergedCellRange

from safetyTrosar import subWidget
from safetyTrosar.structure.safetyPmData import SafetyPmData


class TabSubWidget(subWidget.WorksheetWidget):
    safety_data: SafetyPmData
    TAB_NAME = "위험원 목록"

    def __init__(self, main_window, tab_widget: QtWidgets.QTabWidget):
        super().__init__(main_window, tab_widget, self.TAB_NAME)

        self.init_view()

    def init_data(self, safety_data: SafetyPmData):
        self.safety_data = safety_data
        table = safety_data.hazard_log.table
        if table.dataframe is None:
            self.generate_dataframe()
        self.tableview_manager.init_data(table_data=table)
        self.tableview_manager.show_table()

    def init_view(self):
        self.setTabVisible(False)
        self.toolButton_save.setEnabled(True)
        self.toolButton_export.setEnabled(True)
        self.pushButton_temp.setParent(self)
        self.tableView.setEnabled(True)

        self.pushButton_temp.setText("통계")
        self.pushButton_next.setText("완료")

    def generate_dataframe(self):
        hazop_table = self.safety_data.hazop_analysis.table
        hazard_list = []
        for i, item in hazop_table.dataframe.iterrows():
            if len(item[hazop_table.HAZARD_ID]) > 0:
                hazard_list.append(item)

        # sf_table = self.safety_data.hazop_analysis.info.severity_frequency.risk_table
        # data_list = []
        # for data in hazard_list:
        #     initial_risk = sf_table.get_risk_rank(severity=data.before_severity, frequency=data.before_frequency)
        #     if len(data.after_severity) == 0 or len(data.after_frequency) == 0:
        #         reduced_risk = "N/A"
        #     else:
        #         reduced_risk = sf_table.get_risk_rank(severity=data.after_severity, frequency=data.after_frequency)

        table = self.safety_data.hazard_log.table

        data_dict = {
            table.PM_ID: [],
            table.HAZARD_ID: [],
            table.FAILURE: [],
            table.EFFECT: [],
            table.INITIAL_RISK: [],
            table.SAFETY_MEASURES: [],
            table.REDUCE_RISK: [],
            table.STATUS: [],
            table.UPDATE_DATE: [],
            table.RESPONSIBILITY: [],
            table.EVIDENCE: [],
        }

        for item in hazard_list:
            data_dict[table.PM_ID].append(item[hazop_table.MODULE])
            data_dict[table.HAZARD_ID].append(item[hazop_table.HAZARD_ID])
            data_dict[table.FAILURE].append(item[hazop_table.BEFORE_FAULT_SITUATION])
            data_dict[table.EFFECT].append(item[hazop_table.CAUSE_EFFECT])
            data_dict[table.INITIAL_RISK].append("")
            data_dict[table.SAFETY_MEASURES].append(item[hazop_table.SAFETY_MEASURE])
            data_dict[table.REDUCE_RISK].append("")
            data_dict[table.STATUS].append("")
            data_dict[table.UPDATE_DATE].append("")
            data_dict[table.RESPONSIBILITY].append("")
            data_dict[table.EVIDENCE].append("")

        dataframe = DataFrame(data_dict)
        table.set_dataframe(dataframe)
        protect_column_name_list = ["PM 식별자", "위험원 식별자", "고장", "영향", "초기 위험도", "안전 대책", "저감된 위험도", "최종 수정일", "책임"]
        for i, name in enumerate(table.dataframe.columns):
            if name in protect_column_name_list:
                table.set_cell_protected(table.index_to_cell_range(0, i, len(table.dataframe.index), i))

    def toolButton_next_clicked(self, _):
        try:
            self.safety_data.save_pm_server()

        except Exception as ex:
            self.print_info(str(ex))
