from typing import Tuple
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from functools import wraps
from pandas import DataFrame

from safetyTrosar import QTreeViewModel, SafetyPmData
from safetyTrosar import PM_List
from safetyTrosar import message_box, raise_if_debug, trosar_api, debug
from safetyTrosar.subWidget import riskTable
from safetyTrosar.structure.safetyPmData import NEW_PROJECT_NAME, HAZOP_WORK_NAME
from .tab1Function import temp_default_guideword, init_data_, load_pm_list, new_project_content, get_pm_tree_root


class ProjectWidget:
    qtreeview_model: "QTreeViewModel"
    project_info_widget: "ProjectInfoWidget"

    def __init__(self, main_window):
        # 기본 변수 연결
        self.main_window = main_window

        # qt designer 항목 연결
        self.qt_widget = main_window.start_tab

        # 초기화
        self.init_qt()
        self.init_link()

    def init_qt(self):
        self.main_window.tabWidget.setTabVisible(1, False)
        self.main_window.start_tab_splitter.setStretchFactor(1, 100)
        self.main_window.start_tab_splitter.setStretchFactor(2, 1)

        self.main_window.comboBox.addItem(HAZOP_WORK_NAME)
        self.main_window.comboBox.setEnabled(True)

        self.qtreeview_model = QTreeViewModel(self.main_window.start_tab_pm_tree_view)
        self.project_info_widget = ProjectInfoWidget(self.main_window, self.qtreeview_model)

    def init_link(self):
        # start_tab_pm_tree_view 에서 선택, 더블클릭 시 액션 지정
        self.qtreeview_model.set_super_action(self.project_info_widget.qtreeview_selectionChanged)


print_function: callable = print


def set_function(func: callable):
    global print_function
    print_function = func


def print_info_(text):
    global print_function
    print_function(text)


def clicked_decorator(success_text, fail_text):
    def decorator(func: callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                output = func(self, *args, **kwargs)
                self.print_info(success_text)
                return output
            except Exception as ex:
                self.print_info(fail_text)
                if debug:
                    import traceback
                    traceback.print_exc()
                    # raise ex
                return None
        return wrapper
    return decorator


class ProjectInfoWidget:
    pm_data_list: PM_List = []
    selected: Tuple[str, str] = (None, None)
    work_info_changed_flag: bool = False
    safety_data: SafetyPmData

    def __init__(self, main_window, qtreeview_model_: QTreeViewModel):
        # 기본 변수 연결
        self.main_window = main_window
        self.qtreeview_model = qtreeview_model_

        # qt designer 항목 연결
        self.groupBox_pm_info = self.main_window.groupBox_pm_info
        self.groupBox_hazard_work_info = self.main_window.groupBox_hazard_work_info

        self.lineEdit_pm_name = self.main_window.lineEdit_pm_name
        self.lineEdit_pm_date = self.main_window.lineEdit_pm_date

        self.lineEdit_work_name = self.main_window.lineEdit_work_name
        # self.lineEdit_work_type = self.main_window.lineEdit_work_type
        self.lineEdit_work_date = self.main_window.lineEdit_work_date
        self.lineEdit_guideword = self.main_window.lineEdit_guideword
        self.lineEdit_sf = self.main_window.lineEdit_sf
        self.lineEdit_progress = self.main_window.lineEdit_progress

        self.pushButton_save = self.main_window.pushButton_save
        self.pushButton_delete = self.main_window.pushButton_delete
        self.pushButton_next = self.main_window.pushButton_next
        self.toolButton_sf = self.main_window.toolButton_sf

        self.label_info = self.main_window.label_info
        self.comboBox = self.main_window.comboBox
        # self.toolButton_guide_word = self.main_window.toolButton_guide_word

        set_function(self.print_info)

        # 초기화 호출
        self.init_action()
        try:
            self.refresh_server_connection()
            self.reload_qtreeview()
        except:
            pass
        self.update_selected(None, None)

    def print_info(self, text: str):
        self.label_info.setText(text)

    def init_action(self):
        # 버튼 동작 지정
        self.main_window.toolButton_refresh_connection.clicked.connect(self.button_refresh_clicked)
        self.pushButton_save.clicked.connect(self.button_save_clicked)
        self.pushButton_delete.clicked.connect(self.button_delete_clicked)
        self.pushButton_next.clicked.connect(self.button_next_clicked)
        # self.toolButton_guide_word.clicked.connect(self.toolButton_guide_word_clicked)
        self.toolButton_sf.clicked.connect(self.toolButton_sf_clicked)

        self.lineEdit_work_name.textChanged.connect(lambda: self.setWorkInfoChangedFlag())
        self.comboBox.currentIndexChanged.connect(lambda: self.setWorkInfoChangedFlag())
        self.lineEdit_work_date.textChanged.connect(lambda: self.setWorkInfoChangedFlag())
        self.lineEdit_guideword.textChanged.connect(lambda: self.setWorkInfoChangedFlag())
        self.lineEdit_sf.textChanged.connect(lambda: self.setWorkInfoChangedFlag())
        self.lineEdit_progress.textChanged.connect(lambda: self.setWorkInfoChangedFlag())

    @raise_if_debug(print_info_)
    @clicked_decorator("", "PM API 서버 오류")
    def button_refresh_clicked(self, _):
        self.refresh_server_connection()
        self.reload_qtreeview()
        self.update_selected(None, None)

    @raise_if_debug(print_info_)
    @clicked_decorator("위헙원 작업 저장 완료", "위헙원 작업 삭제 실패")
    def button_save_clicked(self, _):
        self.save_pm_content()

    @raise_if_debug(print_info_)
    @clicked_decorator("위헙원 작업 삭제 성공", "위헙원 작업 삭제 실패")
    def button_delete_clicked(self, _):
        try:
            pm_name, pm_content_name = self.selected
            pm_id = self.pm_data_list[pm_name].id
            content_id = self.pm_data_list[pm_name][pm_content_name].id

            # pm 서버의 작업정보 삭제
            trosar_api.pm_content_delete(pm_id, content_id)
            # pm 목록 재확인  #TODO
            self.reload_qtreeview()
            # 선택 항목 유지
            self.update_selected(pm_name, None)
            self.print_info("위헙원 작업 삭제 성공")
        except Exception as ex:
            self.print_info("위헙원 작업 삭제 성공")
            if debug:
                raise ex

    @raise_if_debug(print_info_)
    @clicked_decorator("", "요구사항 탭 생성 오류")
    def button_next_clicked(self, _):
        if self.is_leave_without_change():
            # 요구사항 탭 전환
            requirements_widget = self.main_window.sub_tabs.requirements
            requirements_widget.init_data(safety_data=self.safety_data)
            requirements_widget.setTabVisible(True)
            requirements_widget.setTabSelected()

            # 그외 탭 끄기  # TODO-작업한 항목이 있으면 같이 띄울까?
            self.main_window.sub_tabs.hazop.setTabVisible(False)
            self.main_window.sub_tabs.safety_measure.setTabVisible(False)
            self.main_window.sub_tabs.hazard_log.setTabVisible(False)

    @raise_if_debug(print_info_)  # TODO-보류
    def toolButton_guide_word_clicked(self):
        raise

    @raise_if_debug(print_info_)  # TODO
    @clicked_decorator("", "심각도/빈도 적용 오류")
    def toolButton_sf_clicked(self):
        output = riskTable.show_window(self.main_window, self.safety_data)

    def reload_qtreeview(self):
        self.pm_data_list = load_pm_list()
        self.qtreeview_model.set_data(get_pm_tree_root(self.pm_data_list))

    def refresh_server_connection(self):
        self.main_window.toolButton_refresh_connection.setEnabled(False)
        self.main_window.lineEdit_connection_status.setText("Connecting...")
        self.main_window.lineEdit_connection_status.repaint()
        try:
            localhost_ = self.main_window.lineEdit_localhost.text()
            trosar_host_ = self.main_window.lineEdit_trosar_server.text()

            trosar_api.init(localhost_, trosar_host_)
            self.main_window.lineEdit_connection_status.setText("Connected")
            self.main_window.toolButton_refresh_connection.setEnabled(True)

        except trosar_api.NotConnectError:
            # 서버에 연결 실패
            self.main_window.lineEdit_connection_status.setText("Error: PM 서버에 연결할 수 없습니다.")

            # PM 데이터 초기화 및 PM 트리 초기화
            self.pm_data_list = PM_List()
            self.qtreeview_model.set_data(get_pm_tree_root(self.pm_data_list))
            self.main_window.toolButton_refresh_connection.setEnabled(True)
            return False

        except Exception as ex:
            # 식별되지 않은 오류
            self.main_window.lineEdit_connection_status.setText("Error: 통신 중 오류가 발생했습니다.")
            self.main_window.toolButton_refresh_connection.setEnabled(True)
            raise ex

    @raise_if_debug(print_info_)
    @clicked_decorator("", "정보 불러오기 중 오류 발생")
    def qtreeview_selectionChanged(self, pm_name, pm_content_name=None):
        if self.is_leave_without_change():
            # safety data 로드
            self.safety_data = SafetyPmData()
            if pm_content_name is not None:
                if pm_content_name != NEW_PROJECT_NAME:
                    pm_content = self.pm_data_list[pm_name][pm_content_name]
                    pm = self.pm_data_list[pm_name]
                    self.safety_data = SafetyPmData.load_pm_server(pm, pm_content)
                else:
                    self.safety_data.init()
            self.setWorkInfoChangedFlag(False)
            self.update_selected(pm_name, pm_content_name)
        else:
            # cancel change
            pass

    def setWorkInfoChangedFlag(self, flag=True):
        self.work_info_changed_flag = flag
        self.pushButton_save.setEnabled(flag)

    def save_pm_content(self):
        pm_name, pm_content_name = self.selected

        # TODO: 가이드워드 불러와야함
        # TODO: 위험원분석 불러와야함

        def is_save_valid():
            new_name = self.main_window.lineEdit_work_name.text()
            if len(new_name) == 0:
                self.print_info("위험원 분석 작업 명칭이 미입력되었습니다.")
                return False
            if new_name == NEW_PROJECT_NAME:
                self.print_info('"{}"은 위험원 분석 작업 명칭으로 쓸 수 없습니다.'.format(NEW_PROJECT_NAME))
                return False
            if new_name in self.pm_data_list[pm_name]:
                if self.pm_data_list[pm_name][new_name].createdAt != self.main_window.lineEdit_work_date.text():
                    self.print_info("위험원 분석 작업 명칭이 중복되었습니다.")
                    return False
            return True

        if is_save_valid():
            work_name = self.main_window.lineEdit_work_name.text()
            # pm_content 업데이트
            pm_content = self.pm_data_list[pm_name][pm_content_name]
            pm_content.name = work_name
            pm_content.type2 = self.comboBox.currentText()

            pm = self.pm_data_list[pm_name]

            if pm_content.id == "-1":        # 새 작업일 경우
                self.safety_data.project.info.import_pm(pm, pm_content)
                severity_frequency = self.safety_data.hazop_analysis.info.severity_frequency
                # TODO: 임시코드
                init_data_(severity_frequency)
                guideword_dataframe = DataFrame(temp_default_guideword())
                self.safety_data.hazop_analysis.info.guide_word_table.set_dataframe(guideword_dataframe)
                new_id, new_description = self.safety_data.save_pm_server()
                pm_content.id = new_id
                pm_content.description = new_description
                self.safety_data.load_pm_server(pm, pm_content)

                new_item = new_project_content()
                self.pm_data_list[pm_name].add_content(new_item)
                # self.qtreeview_model.add_tree_item(tree_data=TreeData(new_item), pm_name=pm_name)
                self.reload_qtreeview()
            else:
                new_pm_content = self.safety_data.save_pm_server()
                pm_content.description = new_pm_content.description
                # self.qtreeview_model.modify_tree_item(tree_data=TreeData(new_item), pm_name=pm_name)
                self.reload_qtreeview()
            self.update_selected(pm_name, work_name)
            self.setWorkInfoChangedFlag(False)

            return True

        return False

    def update_selected(self, pm_name, pm_content_name):
        self.selected = (pm_name, pm_content_name)
        # self.qtreeview_model.set_selected()

        self.refresh_view()

    def refresh_view(self):
        def refresh_pm_info():
            pm_name = self.selected[0]
            if pm_name is None:
                self.groupBox_pm_info.setEnabled(False)
                self.lineEdit_pm_name.setText("")
                self.lineEdit_pm_date.setText("")
            elif pm_name is not None:
                pm = self.pm_data_list[pm_name]
                self.groupBox_pm_info.setEnabled(True)
                self.lineEdit_pm_name.setText(pm.name)
                self.lineEdit_pm_date.setText(pm.createdAt)

        def refresh_pm_content():
            pm_name = self.selected[0]
            pm_content_name = self.selected[1]
            if pm_content_name is None:
                self.groupBox_hazard_work_info.setEnabled(False)
                self.lineEdit_work_name.setText("")
                self.set_hazard_work_combobox(HAZOP_WORK_NAME)
                self.lineEdit_work_date.setText("")
                self.lineEdit_guideword.setText("")
                self.lineEdit_sf.setText("")
                self.lineEdit_progress.setText("")

                self.pushButton_save.setEnabled(False)
                self.pushButton_delete.setEnabled(False)
                self.pushButton_next.setEnabled(False)
                self.toolButton_sf.setEnabled(False)
            else:
                pm_content = self.pm_data_list[pm_name][pm_content_name]
                self.groupBox_hazard_work_info.setEnabled(True)
                self.lineEdit_work_name.setText(pm_content_name)
                self.set_hazard_work_combobox(pm_content.type2)
                self.lineEdit_work_date.setText(pm_content.createdAt)
                self.lineEdit_guideword.setText("Default")
                self.lineEdit_sf.setText("Default")
                self.lineEdit_progress.setText(pm_content.status)

                self.lineEdit_work_name.setReadOnly(False)
                self.pushButton_save.setEnabled(False)
                self.pushButton_delete.setEnabled(True)
                self.pushButton_next.setEnabled(True)
                self.toolButton_sf.setEnabled(True)
                # self.toolButton_guide_word.setEnabled(False)

                if pm_content.name == NEW_PROJECT_NAME:
                    self.pushButton_delete.setEnabled(False)
                    self.pushButton_next.setEnabled(False)

        refresh_pm_info()
        refresh_pm_content()
        self.setWorkInfoChangedFlag(False)

    def set_hazard_work_combobox(self, text: str):
        index = self.comboBox.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.comboBox.setCurrentIndex(index)
            return True
        else:
            return False

    def is_leave_without_change(self):
        if self.work_info_changed_flag is True:
            if message_box(text="Leave without Apply Change?", parent=self.main_window) == QMessageBox.No:
                return False
            else:
                self.setWorkInfoChangedFlag(False)
        return True
