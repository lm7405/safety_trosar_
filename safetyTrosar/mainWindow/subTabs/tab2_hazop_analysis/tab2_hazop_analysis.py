# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QTableWidget, QFileDialog
from .hazop_sheet import HazopSheet
from .hazop_structure import *
from .hazop_excel import generate_from_data
from safetyTrosar.tool.trosarApi import trosar_api
import json


class qtc_hazop_analysis_tab:
    hazop_work_data: hazop_work_data

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.hazop_sheet = HazopSheet(main_window, hazop_work_data)
        self.main_window.splitter.setStretchFactor(1, 1)

        self.init_action()

    def init_action(self):
        self.main_window.toolButton_hazop_save.clicked.connect(self.button_hazop_save_clicked)
        self.main_window.toolButton_hazop_insert_row.clicked.connect(self.button_hazop_insert_row_clicked)
        self.main_window.toolButton_hazop_delete_row.clicked.connect(self.button_hazop_delete_row_clicked)
        self.main_window.toolButton_hazop_export.clicked.connect(self.button_hazop_export_clicked)
        self.main_window.toolButton_hazop_undo.clicked.connect(self.button_hazop_undo_clicked)
        self.main_window.toolButton_hazop_redo.clicked.connect(self.button_hazop_redo_clicked)
        # self.mainWindow.toolButton_hazop_copy.clicked.connect(self.button_hazop_copy_clicked)
        # self.mainWindow.toolButton_hazop_paste.clicked.connect(self.button_hazop_paste_clicked)

    def button_hazop_save_clicked(self):
        self.hazop_work_data.root_node = self.hazop_sheet.root_node
        save_data = self.hazop_work_data.export()
        save_data_text = str(save_data)

        pm_data = self.hazop_work_data.pm_data
        pm_id = pm_data["id"]
        pm_content_data = self.hazop_work_data.pm_contents_hazard_work_data
        pm_content_id = pm_content_data.id
        pm_content_data.description = save_data_text

        trosar_api.pm_content_update(pm_id, pm_content_id, pm_content_data)

    def button_hazop_insert_row_clicked(self):
        focused_widget = self.main_window.focusWidget()
        if isinstance(focused_widget, QTableWidget):
            selected_node_list = self.hazop_sheet.get_selected_node_list()
            if selected_node_list is None or len(selected_node_list) == 0:
                return False

        else:
            return False

        self.hazop_sheet.save_current_root_node()
        for selected_node in selected_node_list:
            parent_node = selected_node.parent
            if parent_node is not None:
                selected_node.insert_row()
                self.hazop_sheet.refresh()

                # row, column = selected_node.get_sheet_index()
                # row += selected_node.get_row_count()
                # self.hazop_sheet.insert_row(row, column)

    def button_hazop_delete_row_clicked(self):
        focused_widget = self.main_window.focusWidget()
        if isinstance(focused_widget, QTableWidget):
            selected_node_list = self.hazop_sheet.get_selected_node_list()
            if selected_node_list is None or len(selected_node_list) == 0:
                return False
        else:
            return False

        self.hazop_sheet.save_current_root_node()
        for selected_node in selected_node_list:
            parent_node = selected_node.parent
            if parent_node is not None:
                # row, column = selected_node.get_sheet_index()
                # self.hazop_sheet.remove_row(row, column)

                selected_node.remove_row()
                self.hazop_sheet.refresh()

    def button_hazop_export_clicked(self):
        file_name = QFileDialog.getSaveFileName(self.main_window, caption='Export file', filter="Excel File (*.xlsx)")
        splitted = file_name[0].split('.')
        if splitted[-1] != "xlsx":
            file_name = (file_name[0] + ".xlsx", )
        generate_from_data(self.hazop_work_data.root_node, file_name[0])

    def button_hazop_import_clicked(self):
        pass

    def button_hazop_undo_clicked(self):
        self.hazop_sheet.load_old_root_node()

    def button_hazop_redo_clicked(self):
        self.hazop_sheet.reload_undo_root_node()

    def button_hazop_copy_clicked(self):
        self.hazop_sheet.copy()

    def button_hazop_paste_clicked(self):
        self.hazop_sheet.paste()

    def start_tab(self, hazop_work_data_: hazop_work_data):
        self.hazop_work_data = hazop_work_data_
        self.init_view()
        self.main_window.tabWidget.setTabVisible(1, True)
        self.main_window.tabWidget.setCurrentIndex(1)

    def init_view(self):
        if len(self.hazop_work_data.pm_contents_hazard_work_data.description) > 0:
            if self.build_tree_from_previous_work() is False:
                raise
        else:
            if self.build_tree_from_requirement_data() is False:
                raise
        self.hazop_sheet.init(self.hazop_work_data.root_node)

    def build_tree_from_previous_work(self):
        guideword = self.hazop_work_data.guideword
        pm_data = self.hazop_work_data.pm_data
        pm_contents = self.hazop_work_data.pm_contents_requirements_data
        description_text = self.hazop_work_data.pm_contents_hazard_work_data.description
        description_text = description_text.replace("\'", "\"")
        description = json.loads(description_text)

        pm_name = pm_data["name"]

        root_node = tree_node(tree_node.empty_key)
        self.hazop_work_data.root_node = root_node
        root_node.import_data(description["root"]["child_list"])

        return True

    def build_tree_from_requirement_data(self):
        guideword = self.hazop_work_data.guideword
        pm_data = self.hazop_work_data.pm_data
        pm_contents = self.hazop_work_data.pm_contents_requirements_data

        pm_name = pm_data["name"]

        style_readonly = ["readonly"]
        root_node = tree_node(tree_node.empty_key)
        root_node.add_child(pm_name, style=style_readonly)
        self.hazop_work_data.root_node = root_node
        for function_data in pm_contents["기능"]:
            function_name = function_data.name
            root_node.add([pm_name], function_name, style=style_readonly)

            hazard_factor = [function_name]
            for item in pm_contents["입력"]:
                hazard_factor.append(item.name)
            for item in pm_contents["출력"]:
                hazard_factor.append(item.name)
            for item in pm_contents["환경"]:
                hazard_factor.append(item.name)
            for item in pm_contents["사용자"]:
                hazard_factor.append(item.name)

            for key1, value1 in guideword.items():
                root_node.add([pm_name, function_name], key1, style=style_readonly)
                for key2, value2 in value1.items():
                    root_node.add([pm_name, function_name, key1], key2, style=style_readonly)
                    root_node.add([pm_name, function_name, key1, key2], value2, style=style_readonly)
                    root_node.add([pm_name, function_name, key1, key2, value2], tree_node.empty_key)
                    for item in hazard_factor:
                        root_node.add([pm_name, function_name, key1, key2, value2, tree_node.empty_key],
                                      item, style=style_readonly)
        return True


if __name__ == "__main__":
    from safetyTrosar.main_window.main_window import show_main_window
    show_main_window()
