# -*- coding: utf-8 -*-


from enum import Enum
from typing import Tuple
import copy
from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from PyQt5.QtCore import Qt, QPoint, QItemSelectionModel
from .hazop_structure import *


class SELECTION_TYPE(Enum):
    NOT_SELECTED = 0
    UNIDENTIFIED = 1

    SINGLE_CELL = 2
    VERTICAL_LINE_CELL = 3
    HORIZONTAL_LINE_CELL = 4
    BOX_CELL = 5

    ROW = 6
    COLUMN = 7


class HazopSheet:
    hazop_table_view: any
    headerLabels: list
    root_node: tree_node
    change_event_flag: bool
    old_root_node_list = []
    undo_root_node_list = []
    hazop_work_data_: hazop_work_data

    def __init__(self, main_window, hazop_work_data__):
        self.hazop_table_view = main_window.hazop_table_view
        self.super = main_window
        self.hazop_work_data_ = hazop_work_data__

        self.init_action(main_window)
        self.change_event_flag = True

    def init_action(self, main_window):
        self.hazop_table_view.itemChanged.connect(self.item_changed)
        pass

    def init(self, root_node: tree_node):
        self.root_node = root_node
        self.headerLabels = [
            "모듈", "항목(기능)", "가이드워드-유형", "가이드워드-단어", "가이드워드-설명", "기능이상현상", "위험원",
            "대책전-위험현상", "대책전-영향범위및결과",
            "대책전-S", "대책전-F", "안전대책", "안전대책-분류",
            "대책후-기능이상현상", "대책후-영향범위및결과", "대책후-S", "대책후-F", "세부조치내용"
        ]
        self.refresh()
        self.save_current_root_node()

    def item_changed(self, item):
        if self.change_event_flag:
            selected_item = item
            index_row = self.hazop_table_view.row(selected_item)
            index_column = self.hazop_table_view.column(selected_item)
            selected_node = self.root_node.get_node_from_index(index_row, index_column)
            selected_node.pm_data = selected_item.text()
            self.save_current_root_node()
            # print(str(index_row) + ", " + str(index_column) + ": " + selected_item.text())

    def generate_table_from_tree(self, node, row, column):
        text = node.pm_data
        style = node.style

        if column >= 0:
            self.set_cell_data(row, column, text, style, node.get_row_count())
        if len(node.child_list) > 0:
            # 자식이 있다면 순회
            for child_node in node.child_list:
                self.generate_table_from_tree(child_node, row, column + 1)
                row += child_node.get_row_count()
        else:
            # 자식이 없다면 공백 노드 생성
            self.generate_table_from_none(row, column + 1)

    def generate_table_from_none(self, row, column):
        column_count = len(self.headerLabels)
        if column >= column_count:
            return False

        self.set_cell_data(row, column, tree_node.empty_key)
        self.generate_table_from_none(row, column + 1)

    def set_cell_data(self, row, column, text: str, style=None, rowSpanCount=None):
        column_count = len(self.headerLabels)
        if column >= column_count:
            return False

        if column >= 0:
            item = QTableWidgetItem(text)
            self.hazop_table_view.setItem(row, column, item)
            if rowSpanCount is not None:
                self.hazop_table_view.setSpan(row, column, rowSpanCount, 1)
            if style is not None:
                if "readonly" in style:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def get_cell_data(self, row, column):
        return self.hazop_table_view.model().index(row, column).pm_data()

    def get_selected_node_list(self):
        selected_items = self.hazop_table_view.selectedItems()
        if len(selected_items) == 0:
            return None

        selected_node_list = []
        for selected_item in selected_items:
            index_row = self.hazop_table_view.row(selected_item)
            index_column = self.hazop_table_view.column(selected_item)
            selected_node = self.root_node.get_node_from_index(index_row, index_column)
            selected_node_list.append(selected_node)

        return selected_node_list

    def get_selected_node(self):
        selected_items = self.hazop_table_view.selectedItems()
        if len(selected_items) == 0:
            return None

        index_row = self.hazop_table_view.row(selected_items[0])
        index_column = self.hazop_table_view.column(selected_items[0])
        selected_node = self.root_node.get_node_from_index(index_row, index_column)

        return selected_node

    def refresh(self):
        self.hazop_table_view.model().removeRows(0, self.hazop_table_view.model().rowCount())
        max_height = self.root_node.get_row_count()
        self.hazop_table_view.setRowCount(max_height)
        self.hazop_table_view.setColumnCount(len(self.headerLabels))
        self.hazop_table_view.setHorizontalHeaderLabels(self.headerLabels)
        self.hazop_table_view.resizeColumnsToContents()

        self.change_event_flag = False
        self.generate_table_from_tree(self.root_node, 0, -1)
        self.change_event_flag = True

        self.hazop_table_view.resizeRowsToContents()

    def save_current_root_node(self):
        root_node_deep_copied = copy.deepcopy(self.root_node)
        self.old_root_node_list.append(root_node_deep_copied)
        if len(self.old_root_node_list) >= 10:
            del self.old_root_node_list[0]
        while len(self.undo_root_node_list) > 0:
            del self.undo_root_node_list[0]

    def load_old_root_node(self):
        if len(self.old_root_node_list) > 0:
            self.root_node = self.old_root_node_list.pop()
            self.save_root_node_to_parent()
            self.undo_root_node_list.append(copy.deepcopy(self.root_node))
            self.refresh()

    def reload_undo_root_node(self):
        if len(self.undo_root_node_list) > 0:
            self.root_node = self.undo_root_node_list.pop()
            self.save_root_node_to_parent()
            self.refresh()

            root_node_deep_copied = copy.deepcopy(self.root_node)
            self.old_root_node_list.append(root_node_deep_copied)
            if len(self.old_root_node_list) >= 10:
                del self.old_root_node_list[0]

    def save_root_node_to_parent(self):
        self.hazop_work_data_.root_node = self.root_node

    class SelectedClass:
        selection_type: SELECTION_TYPE
        selected_cell_list: list
        selected_row_list: list
        selected_column_list: list
        selected_box_info: Tuple[QPoint, QPoint]
        selected_item_list: List[QTableWidgetItem]

        def __init__(self, selectionModel: QItemSelectionModel):
            self.selected_row_list = selectionModel.selectedRows()
            self.selected_column_list = selectionModel.selectedColumns()
            self.selected_item_list = selectionModel.selectedIndexes()

            if len(self.selected_item_list) == 1:
                self.selection_type = SELECTION_TYPE.SINGLE_CELL

            elif len(self.selected_item_list) == 0:
                self.selection_type = SELECTION_TYPE.NOT_SELECTED

            elif len(self.selected_row_list) > 0 and len(self.selected_column_list) > 0:
                self.selection_type = SELECTION_TYPE.UNIDENTIFIED

            elif len(self.selected_row_list) > 0:
                selected_row_index_num = []
                for selected_row_qitem in self.selected_row_list:
                    selected_row_index_num.append(selected_row_qitem.row())
                for selected_qitem in self.selected_item_list:
                    if selected_qitem.row() not in selected_row_index_num:
                        self.selection_type = SELECTION_TYPE.UNIDENTIFIED
                if not hasattr(self, 'selection_type'):
                    self.selection_type = SELECTION_TYPE.ROW

            elif len(self.selected_column_list) > 0:
                selected_row_index_num = []
                for selected_column_qitem in self.selected_column_list:
                    selected_row_index_num.append(selected_column_qitem.column())
                for selected_qitem in self.selected_item_list:
                    if selected_qitem.column() not in selected_row_index_num:
                        self.selection_type = SELECTION_TYPE.UNIDENTIFIED
                if not hasattr(self, 'selection_type'):
                    self.selection_type = SELECTION_TYPE.COLUMN

            else:
                self.selected_item_list.sort(key=lambda x: x.row() * 100 + x.column())
                start_row = self.selected_item_list[0].row()
                start_column = self.selected_item_list[0].column()
                end_row = self.selected_item_list[-1].row()
                end_column = self.selected_item_list[-1].column()
                if (end_row - start_row + 1) * (end_column - start_column + 1) == len(self.selected_item_list):
                    for item in self.selected_item_list:
                        if not (start_row <= item.row() <= end_row and start_column <= item.column() <= end_column):
                            self.selection_type = SELECTION_TYPE.UNIDENTIFIED
                    if not hasattr(self, 'selection_type'):
                        if start_row == end_row:
                            self.selection_type = SELECTION_TYPE.HORIZONTAL_LINE_CELL
                        elif start_column == end_column:
                            self.selection_type = SELECTION_TYPE.VERTICAL_LINE_CELL
                        else:
                            self.selection_type = SELECTION_TYPE.BOX_CELL
                else:
                    self.selection_type = SELECTION_TYPE.UNIDENTIFIED

    def paste(self):
        clipboard = QApplication.clipboard()
        copy_text = clipboard.text()

        def get_quotation_text(text, start_index, end_index):
            cell_text = text[start_index:end_index]
            if text[start_index] == '"' and text[end_index - 1] == '"':
                cell_text = cell_text[1:-1].replace('""', '"')
            return cell_text

        def from_excel_text(text: str):
            try:
                output = []
                output_row = []
                start_index = 0
                double_quotation_marks_count = 0
                if text[-1] == "\n":
                    text = text[:-1]
                for i in range(len(text)):
                    if double_quotation_marks_count % 2 == 0:
                        if text[i] == "\t":
                            cell_text = get_quotation_text(text, start_index, i)
                            output_row.append(cell_text)
                            start_index = i + 1
                        elif text[i] == "\n":
                            cell_text = get_quotation_text(text, start_index, i)
                            output_row.append(cell_text)
                            start_index = i + 1
                            output.append(output_row)
                            output_row = []
                    if text[i] == '"':
                        double_quotation_marks_count += 1
                if double_quotation_marks_count % 2 == 0:
                    if start_index != len(text):
                        cell_text = get_quotation_text(text, start_index, -1)
                        output_row.append(cell_text)
                        output.append(output_row)
                return output
            except:
                return [[]]

        copy_data = from_excel_text(copy_text)

        selected_items = self.hazop_table_view.selectedItems()
        if len(selected_items) == 0:
            return None

        index_row = self.hazop_table_view.row(selected_items[0])
        index_column = self.hazop_table_view.column(selected_items[0])

        if self.check_area(index_row, index_column, len(copy_data[0]), len(copy_data)):
            print()
        else:
            print("Invalid Paste Area")

    def check_area(self, start_row, start_column, row_count, column_count):
        for row in range(start_row, start_row + row_count):
            for column in range(start_column, start_column + column_count):
                if self.get_cell_data(row, column) is None:
                    return False
        return True

    def copy(self):
        selected_class = self.SelectedClass(self.hazop_table_view.selectionModel())
        if selected_class.selection_type in [SELECTION_TYPE.NOT_SELECTED]:
            pass
        elif selected_class.selection_type in [SELECTION_TYPE.COLUMN, SELECTION_TYPE.ROW, SELECTION_TYPE.UNIDENTIFIED]:
            print("Invalid Copy Range")
        else:
            def to_excel_text(text: str):
                if text is None:
                    return ""
                if "\n" in text or "\t" in text:
                    if '"' in text:
                        text = text.replace('"', '""')
                    text = '"' + text + '"'
                return text
            copy_text = ""
            previous_row = -1
            tmp_list = []
            for single_item in selected_class.selected_item_list:
                tmp_list.append(single_item.row())
            for single_item in selected_class.selected_item_list:
                cell_text = self.get_cell_data(single_item.row(), single_item.column())
                if previous_row == -1:
                    previous_row = single_item.row()
                    copy_text += to_excel_text(cell_text)
                elif previous_row == single_item.row():
                    copy_text += "\t" + to_excel_text(cell_text)
                elif previous_row + 1 == single_item.row():
                    previous_row += 1
                    copy_text += "\n" + to_excel_text(cell_text)
                else:
                    raise
            clipboard = QApplication.clipboard()
            clipboard.setText(copy_text)
