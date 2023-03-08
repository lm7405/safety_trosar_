import sys
from PyQt5 import uic, QtWidgets
from safetyTrosar import config


# 화면을 띄우는데 사용되는 Class 선언
class MainWindow(QtWidgets.QMainWindow, uic.loadUiType(config.resource_path + "/mainWindow.ui")[0]):
    from .subTabs import subTabs
    sub_tabs: subTabs.SubTabs

    def __init__(self):
        super().__init__()
        self.init_qt()
        self.init_action()

    def init_qt(self):
        # 내부 아이템들 연결
        self.setupUi(self)

        # tab 초기화
        from .subTabs import subTabs
        self.sub_tabs = subTabs.SubTabs(self, self.tabWidget)

    def init_action(self):
        pass


def show_main_window(argv):
    app = QtWidgets.QApplication(sys.argv)
    main_window_ = MainWindow()

    main_window_.show()
    app.exec_()
