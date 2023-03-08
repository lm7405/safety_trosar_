from PyQt5 import QtWidgets
from pandas import DataFrame

from safetyTrosar import PM_Content, trosar_api
from safetyTrosar import subWidget, raise_if_debug
from safetyTrosar.structure.safetyPmData import SafetyPmData, Requirements


class TabSubWidget(subWidget.WorksheetWidget):
    safety_data: SafetyPmData
    TAB_NAME = "요구사항"
    REQUIREMENTS_TYPE1 = [
        Requirements.Table.Type1.FUNCTION,
        Requirements.Table.Type1.INPUT,
        Requirements.Table.Type1.OUTPUT,
        Requirements.Table.Type1.ENVIRONMENT,
        Requirements.Table.Type1.STAKEHOLDER,
        Requirements.Table.Type1.PM,
        Requirements.Table.Type1.CONNECTION,
        Requirements.Table.Type1.STRUCTURE,
    ]

    def __init__(self, main_window, tab_widget: QtWidgets.QTabWidget):
        super().__init__(main_window, tab_widget, self.TAB_NAME)

        self.init_view()

    def init_data(self, safety_data: SafetyPmData):
        self.safety_data = safety_data
        table = safety_data.requirements.table
        if table.dataframe is None:
            self.generate_dataframe()

        self.tableview_manager.init_data(table_data=table)
        self.tableview_manager.show_table()

    def init_view(self):
        self.setTabVisible(False)
        self.toolButton_save.setEnabled(True)
        self.toolButton_export.setEnabled(True)
        self.tableView.setEnabled(True)

        self.disable_toolbar(except_option={"horizontalLayout_toolbar", "toolButton_save", "toolButton_export"})

    def generate_dataframe(self):
        project_info = self.safety_data.project.info
        pm_id = project_info.pm_id

        table = Requirements.Table
        TYPE1 = table.TYPE1
        TYPE2 = table.TYPE2
        NAME = table.NAME
        DESCRIPTION = table.DESCRIPTION
        SPEC = table.SPEC
        NOTES = table.NOTES
        STATUS = table.STATUS
        CREATED_AT = table.CREATED_AT

        dict_data = {
            TYPE1: [],
            TYPE2: [],
            NAME: [],
            DESCRIPTION: [],
            SPEC: [],
            NOTES: [],
            STATUS: [],
            CREATED_AT: [],
        }
        for type1 in self.REQUIREMENTS_TYPE1:
            content_data_list = trosar_api.pm_contents_read(pm_id=pm_id, type1=type1)
            for content_data in content_data_list:
                if content_data.type1 == type1:
                    dict_data[TYPE1].append(content_data.type1)
                    dict_data[TYPE2].append(content_data.type2)
                    dict_data[NAME].append(content_data.name)
                    dict_data[DESCRIPTION].append(content_data.description)
                    dict_data[SPEC].append(content_data.spec)
                    dict_data[NOTES].append(content_data.notes)
                    dict_data[STATUS].append(content_data.status)
                    dict_data[CREATED_AT].append(content_data.createdAt)

        dataframe = DataFrame(dict_data)
        self.safety_data.requirements.table.set_dataframe(dataframe)
        self.safety_data.requirements.table.set_cell_protected(
            cell_range=self.safety_data.requirements.table.index_to_cell_range(
                0, 0, len(dict_data[TYPE1]), len(self.safety_data.requirements.table.column_labels)
            )
        )

    @raise_if_debug("print_info")
    def toolButton_next_clicked(self, _):
        # 저장
        self.safety_data.save_pm_server()
        if self.is_worksheet_validity():
            # HAZOP 탭 생성 및 초기화
            hazop_widget = self.main_window.sub_tabs.hazop
            hazop_widget.init_data(safety_data=self.safety_data)
            hazop_widget.setTabVisible(True)
            hazop_widget.setTabSelected()

            # 그외 탭 끄기
            self.main_window.sub_tabs.safety_measure.setTabVisible(False)
            self.main_window.sub_tabs.hazard_log.setTabVisible(False)

    def is_worksheet_validity(self):
        if self.safety_data.requirements.table.dataframe.shape[0] == 0:
            self.print_info("적합한 요구사항이 없습니다.")
            return False
        if self.safety_data.requirements.table.dataframe.shape[0] == 0:
            self.print_info("적합한 요구사항이 없습니다.")
            return False
        return True
