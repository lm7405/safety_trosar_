# -*- coding: utf-8 -*-


from typing import List, Union, Dict
from safetyTrosar.tool.trosarApi import PM_Content


class tree_node:
    empty_key = ""
    header: str
    data: str
    child_list: Union[List["tree_node"], None]
    parent: Union["tree_node", None]
    style: List[str]
    row_count: int

    def __init__(
            self,
            str_data: Union[str],
            parent: "tree_node" = None,
            child_data: Union[str, dict, list, None] = None,
            style: Union[List[str], None] = None,
            row_count: int = 1
    ):
        if str_data is None:
            raise
        if style is None:
            style = []
        self.data = str_data
        self.child_list = []
        self.parent = parent
        self.style = style[:]
        if child_data is not None:
            self.add_child(child_data)
        self.row_count = row_count

    def add_child(self, data: Union[str, list, dict, None], style: List[str] = None):
        if isinstance(data, str):
            new_child = tree_node(data, self, style=style)
            self.child_list.append(new_child)
        elif isinstance(data, dict):
            for key, value in data.items():
                new_child = tree_node(key, self, value, style)
                self.child_list.append(new_child)
        elif isinstance(data, list):
            for list_item in data:
                self.add_child(list_item)
        else:
            raise
        row_count = 0
        for child in self.child_list:
            row_count += child.get_row_count()
        self.add_parent_row_count(row_count - self.row_count)
        self.row_count = row_count
        if row_count != self.get_row_count():
            raise

    def insert_row(self):
        self.parent.add_child(tree_node.empty_key)
        for i, child in enumerate(self.parent.child_list):
            if child == self:
                new_child_list = self.parent.child_list[:i + 1] + \
                                 [self.parent.child_list[-1]] + \
                                 self.parent.child_list[i + 1:-1]
                self.parent.child_list = new_child_list
                break

    def __del__(self):
        if hasattr(self, 'parent') and self.parent is not None:
            self.parent.remove_row_parent(self)
            del self.parent
        if hasattr(self, 'child_list') and self.child_list is not None:
            for child in self.child_list:
                child.parent = None
                child.__del__()
            del self.child_list

    def remove_row(self):
        self.__del__()

    def remove_row_parent(self, delete_target_node):
        if self.parent is None:
            self.row_count -= delete_target_node.get_row_count()
            if delete_target_node in self.child_list:
                i = self.child_list.index(delete_target_node)
                del self.child_list[i]
                if len(self.child_list) == 0:
                    pass
        else:
            if delete_target_node in self.child_list:
                i = self.child_list.index(delete_target_node)
                del self.child_list[i]
            if len(self.child_list) == 0:
                self.parent.remove_row_parent(self)
                del self.child_list
                del self.parent
            else:
                self.row_count -= delete_target_node.row_count
                self.parent.remove_row_parent(delete_target_node)

    def remove_row_child(self):
        for child in self.child_list:
            child.remove_row_child()
        del self.child_list
        del self.parent

    def add_parent_row_count(self, added_height):
        parent = self.parent
        if parent is not None:
            parent.row_count += added_height
            if parent.parent is not None:
                parent.add_parent_row_count(added_height)

    def get_first_child(self):
        if len(self.child_list) == 0:
            self.add_child(tree_node.empty_key)
        return self.child_list[0]

    def get_last_child(self):
        if len(self.child_list) == 0:
            self.add_child(tree_node.empty_key)
        return self.child_list[-1]

    def add(self, path: List[str], data: Union[str, list, dict, None], style: List[str] = None):
        if len(path) == 0:
            self.add_child(data, style)
            return True
        else:
            target = path[0]
            if len(self.child_list) > 0:
                found_child = next(x for x in self.child_list if x.data == target)
            else:
                found_child = None

            if found_child is not None:
                found_child.add(path[1:], data, style)
            else:
                return False

    def get_row_count(self):
        debug = True
        if not debug:
            return self.row_count
        else:
            if len(self.child_list) == 0:
                return 1
            else:
                row_count = 0
                for child in self.child_list:
                    row_count += child.get_row_count()
                return row_count

    def export_data(self):
        data = {
            "data": self.data,
            "child_list": [x.export_data() for x in self.child_list],
            "style": self.style,
        }
        return data

    def import_data(self, child_list_data):
        for child_data in child_list_data:
            self.add_child(child_data["data"], child_data["style"])
            # new_node = tree_node(child_data["data"], self, style=child_data["style"])
            self.get_last_child().import_data(child_data["child_list"])
            # self.child_list.append(new_node)

    def get_node_from_index(self, row, col):
        if col == -1:
            if self.get_row_count() > row:
                return self
            else:
                raise
        if len(self.child_list) == 0:
            self.add_child(self.empty_key)
        for child in self.child_list:
            row_count = child.get_row_count()
            if row < row_count:
                return child.get_node_from_index(row, col - 1)
            else:
                row -= row_count

        raise

    def get_sheet_index(self, target=None):
        # 최상위 root 에 대한 동작
        if self.parent is None:
            row = 0
            col = -1
        else:
            row, col = self.parent.get_sheet_index(self)
            col += 1

        # 자녀 노드 중 target 탐색
        if target is not None:
            for child in self.child_list:
                if child == target:
                    return row, col
                else:
                    row += child.get_row_count()
        else:
            pass

        return row, col


class hazop_work_data:
    pm_data: any
    pm_contents_requirements_data: Dict[str, List[PM_Content]]
    pm_contents_hazard_work_data: PM_Content
    guideword: any
    sf: any
    header: any
    root_node: tree_node

    def __init__(self, pm_data, pm_requirements_contents_data, pm_hazard_work_data, guideword, sf, header):
        self.pm_data = pm_data
        self.pm_contents_requirements_data = pm_requirements_contents_data
        self.pm_contents_hazard_work_data = pm_hazard_work_data
        self.guideword = guideword
        self.sf = sf
        self.header = header

    def export(self):
        output = {
            "pm_data": self.pm_data,
            "pm_contents_requirements_data": {},
            "guideword": self.guideword,
            "sf": self.sf,
            "header": self.header,
            "root": self.root_node.export_data()
        }
        for key, value in self.pm_contents_requirements_data.items():
            output["pm_contents_requirements_data"][key] = []
            for item in value:
                output["pm_contents_requirements_data"][key].append(item.export())
        return output
