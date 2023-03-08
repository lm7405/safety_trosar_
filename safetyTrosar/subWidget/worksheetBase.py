# -*- coding: utf-8 -*-
from typing import Optional
from queue import Queue, Empty

import pandas as pd
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import uic
from safetyTrosar import config, raise_if_debug
from safetyTrosar.structure.qtableviewModel import *


class DownloadThread(QtCore.QThread):

    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, url):
        QtCore.QThread.__init__(self)
        self.url = url

    def run(self):
        pass


class PrintInfo(QtCore.QThread):
    label = None
    queue: Queue
    data_downloaded = QtCore.pyqtSignal(object)
    display_time = 9

    def __init__(self, queue, parent=None):
        self.queue = queue
        super().__init__(parent)

    def run(self):
        text = ""
        while text is not None:
            try:
                text = self.queue.get(block=True, timeout=self.display_time)
                self.label.setText(text)
            except Empty:
                self.label.setText("")
            except Exception as ex:
                print(ex)
                raise ex

    def set_label_info(self, label_info):
        self.label = label_info

    def __call__(self, text):
        self.queue.put(text)
        self.label.repaint()


# 화면을 띄우는데 사용되는 Class 선언
class WorksheetWidget(QWidget, uic.loadUiType(config.resource_path + "/widget.worksheet.ui")[0]):
    df_import_data: pd.DataFrame = None
    cell_offset: Optional[Tuple[str, str]] = None
    merged_cell_ranges: List[CellRange] = None

    toolButton_connect: QtWidgets.QToolButton
    toolButton_save: QtWidgets.QToolButton
    toolButton_insert_row: QtWidgets.QToolButton
    toolButton_delete_row: QtWidgets.QToolButton
    toolButton_export: QtWidgets.QToolButton
    toolButton_import: QtWidgets.QToolButton
    toolButton_undo: QtWidgets.QToolButton
    toolButton_redo: QtWidgets.QToolButton
    toolButton_copy: QtWidgets.QToolButton
    toolButton_paste: QtWidgets.QToolButton
    toolButton_refresh: QtWidgets.QToolButton
    comboBox_pm_list: QtWidgets.QComboBox
    toolButton_highlight: QtWidgets.QToolButton
    toolButton_filter: QtWidgets.QToolButton
    pushButton_save: QtWidgets.QPushButton
    pushButton_next: QtWidgets.QPushButton
    tableView: QtWidgets.QTableWidget
    label_info: QtWidgets.QLabel
    hide_temp_button: bool = True

    print_queue: Queue
    print_worker: PrintInfo

    def __init__(self, main_window, tab_widget, tab_name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.main_window = main_window
        self.tab_name = tab_name
        self.tab_widget = tab_widget

        self.tableview_manager = PandasTableViewMgr(self.tableView)

        self.init_action()
        self.init()

        if self.hide_temp_button:
            self.pushButton_temp.setParent(None)

        self.comboBox_pm_list.setParent(None)
        self.toolButton_filter.setParent(None)
        self.toolButton_highlight.setParent(None)

        self.toolButton_save.setEnabled(False)
        self.toolButton_insert_row.setEnabled(False)
        self.toolButton_delete_row.setEnabled(False)
        self.toolButton_export.setEnabled(False)
        self.toolButton_import.setEnabled(False)
        self.toolButton_undo.setEnabled(False)
        self.toolButton_redo.setEnabled(False)
        self.toolButton_copy.setEnabled(False)
        self.toolButton_paste.setEnabled(False)
        self.comboBox_pm_list.setEnabled(False)
        self.toolButton_highlight.setEnabled(False)
        self.toolButton_filter.setEnabled(False)

    def init_action(self):
        self.toolButton_save.clicked.connect(self.toolButton_save_clicked)
        self.toolButton_insert_row.clicked.connect(self.toolButton_insert_row_clicked)
        self.toolButton_delete_row.clicked.connect(self.toolButton_delete_row_clicked)
        self.toolButton_export.clicked.connect(self.toolButton_export_clicked)
        self.toolButton_import.clicked.connect(self.toolButton_import_clicked)
        self.toolButton_undo.clicked.connect(self.toolButton_undo_clicked)
        self.toolButton_redo.clicked.connect(self.toolButton_redo_clicked)
        self.toolButton_copy.clicked.connect(self.toolButton_copy_clicked)
        self.toolButton_paste.clicked.connect(self.toolButton_paste_clicked)
        self.toolButton_highlight.clicked.connect(self.toolButton_highlight_clicked)
        self.toolButton_filter.clicked.connect(self.toolButton_filter_clicked)
        self.pushButton_temp.clicked.connect(self.toolButton_temp_clicked)
        self.pushButton_next.clicked.connect(self.toolButton_next_clicked)

        # self.comboBox_pm_list.6

    def init(self):
        self.init_print_worker()
        self.tab_widget.addTab(self, self.tab_name)
        self.hide_tab()

    def init_print_worker(self):
        self.print_queue = Queue()
        self.print_worker = PrintInfo(queue=self.print_queue, parent=self)
        self.print_worker.label = self.label_info
        self.print_worker.start()

    def init_data(self, table: PandasTableData):
        self.tableview_manager.init_data(table_data=table)
        # self.tableview_manager.show_table()

    def index(self):
        index = self.tab_widget.indexOf(self)
        # index = [index for index in range(self.tab_widget.count()) if self.tab_name == self.tab_widget.tabText(index)]
        self.tab_widget.count()

        return index

    def setTabSelected(self):
        index = self.index()
        self.tab_widget.setCurrentIndex(index)

    def disable_toolbar(self, except_option=None):
        if except_option is None:
            except_option = {}
        target_button_dict = {
            "horizontalLayout_toolbar": self.horizontalLayout_toolbar,
            "toolButton_save": self.toolButton_save,
            "toolButton_insert_row": self.toolButton_insert_row,
            "toolButton_delete_row": self.toolButton_delete_row,
            "toolButton_export": self.toolButton_export,
            "toolButton_import": self.toolButton_import,
            "toolButton_undo": self.toolButton_undo,
            "toolButton_redo": self.toolButton_redo,
            "toolButton_copy": self.toolButton_copy,
            "toolButton_paste": self.toolButton_paste,
            "toolButton_refresh": self.toolButton_refresh,
            "comboBox_pm_list": self.comboBox_pm_list,
            "toolButton_filter": self.toolButton_filter,
            "toolButton_highlight": self.toolButton_highlight,
        }
        for name, widget in target_button_dict.items():
            if name not in except_option:
                widget.setParent(None)

    # 테스트 필요
    def getParent(self):
        return self.parent()

    def setTabVisible(self, bool_):
        self.tab_widget.setTabVisible(self.index(), bool_)

    def hide_tab(self):
        self.tab_widget.setTabVisible(self.index(), False)
        self.tab_widget.setCurrentIndex(0)

    def print_info(self, text: str):
        # self.label_info.setText(text)
        self.print_queue.put(text)

    # 이벤트 틀

    @raise_if_debug("print_info")
    def toolButton_save_clicked(self, _):
        self.print_info("saving...")
        self.safety_data.save_pm_server()
        self.print_info("saved!")

    @raise_if_debug("print_info")
    def toolButton_insert_row_clicked(self, _):
        self.tableview_manager.insert_row()

    @raise_if_debug("print_info")
    def toolButton_delete_row_clicked(self, _):
        self.tableview_manager.delete_row()

    @raise_if_debug("print_info")
    def toolButton_export_clicked(self, _):
        file_info = QFileDialog.getSaveFileName(self, 'Save file', './', "Excel Files (*.xlsx)")
        save_path = file_info[0]
        if save_path != "":
            self.tableview_manager.table_data.save_to_excel(path=save_path)

    @raise_if_debug("print_info")
    def toolButton_import_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_undo_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_redo_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_copy_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_paste_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_highlight_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_filter_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_next_clicked(self, _):
        raise

    @raise_if_debug("print_info")
    def toolButton_temp_clicked(self, _):
        raise
