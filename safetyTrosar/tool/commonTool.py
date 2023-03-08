from PyQt5.QtWidgets import QMessageBox


# 클래스 공용 변수, 활용예: https://wikidocs.net/168367
class SharedAttribute:
    def __init__(self, initial_value=None) :
        self.value = initial_value
        self._name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.value is None :
            raise AttributeError(f"{ self._name} was never set ")
        return self.value

    def __set__(self, instance, new_value):
        self.value = new_value

    def __set_name__(self, owner, name):
        self._name = name


def clone_dictionary(dict_: dict):
    output = {}
    for key, value in dict_.items():
        if type(value) in [int, float, str, tuple]:
            output[key] = value
        if type(value) is dict:
            output[key] = clone_dictionary(value)
        elif type(value) is list:
            output[key] = clone_list(value)
        else:
            raise
    return output


def clone_list(list_: list):
    output = []
    for item in list_:
        if type(item) in [int, float, str, tuple]:
            output.append(item)
        if type(item) is dict:
            output.append(clone_dictionary(item))
        elif type(item) is list:
            output.append(clone_list(item))
        else:
            raise
    return output


def message_box(text: str, parent=None):
    return QMessageBox.question(parent, 'Message', text,
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


class SingletonInstance:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance


from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QEvent


class CheckBoxDelegate_(QtWidgets.QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        '''
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''

        checked = index.data()  # .toBool()
        # checked = str(index.data())
        check_box_style_option = QtWidgets.QStyleOptionButton()

        if Qt.ItemIsEditable & index.flags().__index__() > 0:
            check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtWidgets.QStyle.State_On
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)

        check_box_style_option.state |= QtWidgets.QStyle.State_Enabled

        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        # print('Check Box editor Event detected : ')
        if not (Qt.ItemIsEditable & index.flags().__index__()) > 0:
            return False

        # print('Check Box editor Event detected : passed first check')
        # Do not change the checkbox-state
        if event.type() == QEvent.MouseButtonPress:
            return False
        if event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.MouseButtonDblClick:
            if event.button() != Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData(self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        # print('SetModelData')
        newValue = not bool(index.data())
        # print('New Value : {0}'.format(newValue))
        model.setData(index, newValue, Qt.EditRole)

    def getCheckBoxRect(self, option):
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint(option.rect.x() +
                                        option.rect.width() / 2 -
                                        check_box_rect.width() / 2,
                                        option.rect.y() +
                                        option.rect.height() / 2 -
                                        check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())
