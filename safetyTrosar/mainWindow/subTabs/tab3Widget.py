from PyQt5 import QtWidgets
from typing import Tuple, List
from openpyxl.worksheet.merge import CellRange
from openpyxl.utils.cell import get_column_letter
from pandas import DataFrame
import numpy as np

from safetyTrosar.subWidget import WorksheetWidget
from safetyTrosar import SafetyPmData, HazopAnalysis, raise_if_debug, Requirements


class TabSubWidget(WorksheetWidget):
    safety_data: SafetyPmData
    TAB_NAME = "HAZOP 분석"

    def __init__(self, main_window, tab_widget: QtWidgets.QTabWidget):
        super().__init__(main_window, tab_widget, self.TAB_NAME)

        self.init_view()

    def init_data(self, safety_data: SafetyPmData):

        self.safety_data = safety_data

        table = safety_data.hazop_analysis.table
        if table.dataframe is None:
            self.generate_dataframe()

        combobox_delegate = [
            (9, ["A", "B", "C", "D", "E"]), (10, ["0", "1", "2", "3", "4", "5"]),
            (16, ["A", "B", "C", "D", "E"]), (17, ["0", "1", "2", "3", "4", "5"]),
        ]

        self.tableview_manager.init_data(table_data=table, combobox_delegate=combobox_delegate)
        self.tableview_manager.show_table()

    def init_view(self):
        self.setTabVisible(False)
        self.toolButton_save.setEnabled(True)
        self.toolButton_export.setEnabled(True)
        self.tableView.setEnabled(True)

    @raise_if_debug("print_info")
    def toolButton_next_clicked(self, _):
        self.safety_data.save_pm_server()
        if self.is_worksheet_validity() is True:
            # 안전대책 탭 성성 및 초기화
            measure_widget = self.main_window.sub_tabs.safety_measure
            measure_widget.init_data(safety_data=self.safety_data)
            measure_widget.setTabVisible(True)
            measure_widget.setTabSelected()

            # 그외 탭 끄기
            self.main_window.sub_tabs.hazard_log.setTabVisible(False)

    def generate_dataframe(self):
        requirement_table = self.safety_data.requirements.table
        pm_req = None
        func_req_list = []
        other_req_list = []

        def is_func(req):
            if req[Requirements.Table.TYPE1] == Requirements.Table.Type1.FUNCTION:
                return True
            return False

        def is_req(req):
            if req[Requirements.Table.TYPE1] in [
                Requirements.Table.Type1.FUNCTION,
                Requirements.Table.Type1.INPUT,
                Requirements.Table.Type1.OUTPUT,
                Requirements.Table.Type1.ENVIRONMENT,
                Requirements.Table.Type1.STAKEHOLDER,
            ]:
                return True
            return False

        def is_pm(req):
            if req[Requirements.Table.TYPE1] == Requirements.Table.Type1.PM:
                return True
            return False

        def index_to_cell_range(start_row, start_column, end_row, end_column):
            start_cell = index_to_cell_letter(start_row, start_column)
            end_cell = index_to_cell_letter(end_row, end_column)
            range_string = start_cell + ':' + end_cell

            return CellRange(range_string)

        def index_to_cell_letter(row_, column_):
            string = get_column_letter(column_ + 1) + str(row_ + 1)
            return string

        # TODO Later: 요구사항을 식별하는 방법 정의된 후 수정할 것
        for index, requirement in requirement_table.dataframe.iterrows():
            if is_func(requirement):
                func_req_list.append(requirement)
            if is_req(requirement):
                other_req_list.append(requirement)
            if is_pm(requirement):
                pm_req = requirement
        if len(func_req_list) is 0:
            raise Exception("기능 요구사항이 없습니다.")
        if pm_req is None:
            raise Exception("PM이 정보가 없습니다.")

        guideword = self.safety_data.hazop_analysis.info.guide_word_table

        merged_cell_ranges: List[CellRange] = []

        row = 0
        column = 0

        MODULE = HazopAnalysis.Table.MODULE
        FUNCTION = HazopAnalysis.Table.FUNCTION
        GUIDEWORD_TYPE = HazopAnalysis.Table.GUIDEWORD_TYPE
        GUIDEWORD_WORD = HazopAnalysis.Table.GUIDEWORD_WORD
        GUIDEWORD_DESCRIPTION = HazopAnalysis.Table.GUIDEWORD_DESCRIPTION
        ITEM = HazopAnalysis.Table.ITEM

        hazop_table = self.safety_data.hazop_analysis.table
        hazop_table.init_dataframe()

        row0 = row
        column0 = column
        for i_func, func_req in enumerate(func_req_list):
            row1 = row
            column1 = column + 1
            for i_other, other_req in enumerate(other_req_list):
                row2 = row
                column2 = column + 2
                for i_guide, guideword_data in guideword.dataframe.iterrows():
                    dataframe = DataFrame({
                        MODULE: [pm_req[Requirements.Table.NAME]],
                        FUNCTION: [func_req[Requirements.Table.NAME]],
                        GUIDEWORD_TYPE: [guideword_data[guideword.TYPE]],
                        GUIDEWORD_WORD: [guideword_data[guideword.WORD]],
                        GUIDEWORD_DESCRIPTION: [guideword_data[guideword.DESCRIPTION]],
                        ITEM: [other_req[Requirements.Table.TYPE1] + ': ' + other_req[Requirements.Table.NAME]],
                    }, columns=hazop_table.dataframe.columns, )
                    hazop_table.set_dataframe(hazop_table.dataframe.append(dataframe, ignore_index=True))  # .reset_index(drop=True)
                    row += 1

                merged_cell_ranges.append(index_to_cell_range(row2, column2, row - 1, column2))
                # merged_cell_ranges.append(index_to_cell_range(row2, column2 + 1, row - 1, column2 + 1))
                # merged_cell_ranges.append(index_to_cell_range(row2, column2 + 2, row - 1, column2 + 2))
                # merged_cell_ranges.append(index_to_cell_range(row2, column2 + 3, row - 1, column2 + 3))
            merged_cell_ranges.append(index_to_cell_range(row1, column1, row - 1, column1))
        merged_cell_ranges.append(index_to_cell_range(row0, column0, row - 1, column0))

        hazop_table.merged_cell_ranges = merged_cell_ranges

        hazop_table.dataframe.fillna("", inplace=True)
        protect_name_list = ["모듈", "항목(기능)", "Guide Word\n유형", "Guide Word\n단어", "Guide Word\n설명", "위험 원인\n위험원"]
        for i, name in enumerate(hazop_table.get_shown_header()):
            if name in protect_name_list:
                hazop_table.set_cell_protected(hazop_table.index_to_cell_range(0, i, len(hazop_table.dataframe.index), i))

    def is_worksheet_validity(self):
        return True
        table = self.safety_data.hazop_analysis.table
        column_name_list = list(table.column_labels.keys())
        column_name_list.remove("description")

        # N/A 또는 완결이 될 때 까지 작성이 되었는지 확인
        for i, data in enumerate(data_list):
            for column_name in column_name_list:
                text = data.__getattribute__(column_name)
                if text in table.NON_AVAILABLE_TEXT_LIST:
                    break
                elif len(text) > 0:
                    pass
                else:
                    self.print_info(str(i) + "번째 줄이 작성되지 않았습니다.")
                    return False

        # N/A가 이상한 곳에 있지 않은지 확인
        NA_ACCEPTABLE_LIST = ["before_fault_situation", "cause_effect", "before_effect_and_result", "hazard_id",
                              "safety_measure", "after_fault_situation"]
        for label in NA_ACCEPTABLE_LIST:
            column_name_list.remove(label)
        for i, data in enumerate(data_list):
            for column_name in column_name_list:
                text = data.__getattribute__(column_name)
                if len(text) == 0:
                    break
                elif text in table.NON_AVAILABLE_TEXT_LIST:
                    self.print_info(str(i) + "번째 줄의 N/A가 비정상적으로 사용되었습니다.")
                    return False

        # S, F를 올바르게 작성 했는지 확인
        s_set = set()
        f_set = set()
        for data in self.safety_data.hazop_analysis.info.severity_frequency.severity_table.data_list:
            s_set.add(data.rank)
        for data in self.safety_data.hazop_analysis.info.severity_frequency.frequency_table.data_list:
            f_set.add(data.rank)

        for i, data in enumerate(data_list):
            if len(data.before_severity) > 0:
                if data.before_severity not in s_set:
                    self.print_info(str(i) + "번째 줄의 대책 전 S가 정의되지 않았습니다.")
            if len(data.after_severity) > 0:
                if data.after_severity not in s_set:
                    self.print_info(str(i) + "번째 줄의 대책 후 S가 정의되지 않았습니다.")
            if len(data.before_frequency) > 0:
                if data.before_frequency not in s_set:
                    self.print_info(str(i) + "번째 줄의 대책 전 F가 정의되지 않았습니다.")
            if len(data.after_frequency) > 0:
                if data.after_frequency not in s_set:
                    self.print_info(str(i) + "번째 줄의 대책 후 F가 정의되지 않았습니다.")

        # 위험원 식별자가 중복되지 않았는지 확인
        hazard_id_set = set()
        for i, data in enumerate(data_list):
            if len(data.hazard_id) > 0 and data.hazard_id not in table.NON_AVAILABLE_TEXT_LIST:
                if data.hazard_id not in hazard_id_set:
                    hazard_id_set.add(data.hazard_id)
                else:
                    self.print_info(str(i) + "번째 줄의 위험원 식별자가 중복됩니다.")
                    return False

        # 위험원 식별자 및 안전 대책 유무가 정상적인지 확인
        for i, data in enumerate(data_list):
            if len(data.before_frequency) > 0:
                s = data.before_severity
                f = data.before_frequency
                risk_table = self.safety_data.hazop_analysis.info.severity_frequency.risk_table
                r = risk_table.get_risk_rank(s, f)
                if risk_table.is_permit(r):
                    if len(data.hazard_id) == 0 and len(data.safety_measure) == 0:
                        pass
                    else:
                        self.print_info(str(i) + "번째 줄은 위험하지 않지만 위험원 식별자/안전대책이 작성되었습니다.")
                else:
                    if len(data.hazard_id) == 0 or data.hazard_id in table.NON_AVAILABLE_TEXT_LIST:
                        self.print_info(str(i) + "번째 줄은 위험하지만 위험원 식별자가 작성되지 않았습니다.")
                        return False
                    elif len(data.safety_measure) == 0 or data.safety_measure in table.NON_AVAILABLE_TEXT_LIST:
                        self.print_info(str(i) + "번째 줄은 위험하지만 안전대책이 작성되지 않았습니다.")
                        return False
                    elif len(data.safety_measure_type) == 0 or data.safety_measure_type in table.NON_AVAILABLE_TEXT_LIST:
                        self.print_info(str(i) + "번째 줄의 안전대책 분류가 작성되지 않았습니다.")
                        return False
        return True
