from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from typing import List


class QTreeViewModel:
    qtreeview_item_selectionChanged_super: callable

    def __init__(self, qtreeview: QTreeView):
        self.qtreeview = qtreeview

        self.init_tree()
        self.init_action()

    def init_tree(self):
        self.qtreeview.setModel(QStandardItemModel())
        self.qtreeview.setExpandsOnDoubleClick(True)

    def init_action(self):
        self.qtreeview.selectionModel().selectionChanged.connect(self.qtreeview_item_selectionChanged)
        self.qtreeview.setEditTriggers(QTreeView.NoEditTriggers)

    def set_super_action(self, function: callable):
        self.qtreeview_item_selectionChanged_super = function

    # 선택 아이템이 바뀌었을 경우 상세정보란에 반영
    def qtreeview_item_selectionChanged(self, selected, deselected):
        if selected.indexes():
            selected_index = selected.indexes()[0]
            model = self.qtreeview.model()
            selected_item_key = model.data(selected_index)
            parent_index = selected_index.parent()
            parent_item_key = model.data(parent_index)

            if parent_item_key is None:
                pm_name = selected_item_key
                hazard_work_name = None
            else:
                pm_name = parent_item_key
                hazard_work_name = selected_item_key

            self.qtreeview_item_selectionChanged_super(pm_name, hazard_work_name)

    def set_data(self, tree_data_root: "TreeDataRoot"):
        model = self.qtreeview.model()
        model.removeRows(0, model.rowCount())

        model.setHorizontalHeaderLabels(tree_data_root.header)
        self.qtreeview.setColumnWidth(0, 120)
        self.qtreeview.setColumnWidth(1, 85)
        self.qtreeview.setColumnWidth(2, 20)

        for tree_data in tree_data_root.child:
            self.add_tree_item(tree_data)

    def add_tree_item(self, tree_data: "TreeData", parent: QStandardItem = None):
        line = []

        for i, text in enumerate(tree_data.data):
            line.append(QStandardItem(text))
        if parent is None:
            model = self.qtreeview.model()
            model.appendRow(line)
        else:
            parent.appendRow(line)

        for child_tree_data in tree_data.child:
            self.add_tree_item(child_tree_data, line[0])

    def get_item_index(self):
        raise

    def remove_item(self):
        raise


class TreeData:
    def __init__(self, data: List[str] = None):
        if data is None:
            self.data = []
        else:
            self.data = data
        self.child: List[TreeData] = []

    def set_data(self, data: List[str]):
        self.data = data

    def add_child(self, tree_data: "TreeData"):
        self.child.append(tree_data)

    def __getitem__(self, index: int):
        return self.child[index]


class TreeDataRoot:
    def __init__(self, header: List[str]):
        super().__init__()
        self.header = header
        self.data = []
        self.child = []

    def add_child(self, tree_data: "TreeData"):
        self.child.append(tree_data)

    def __getitem__(self, index: int):
        return self.child[index]
