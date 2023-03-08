from datetime import datetime
from pandas import DataFrame
from safetyTrosar import SafetyPmData, GuideWordPandasTable, SeverityFrequency, TreeDataRoot, TreeData
from safetyTrosar import PM_Content, trosar_api, PM_List
from safetyTrosar.structure.safetyPmData import PM_CONTENT_TYPE1_NAME, NEW_PROJECT_NAME


def get_pm_tree_root(pm_list: PM_List) -> TreeDataRoot:
    column_label = ["이름", "수정일시"]
    root = TreeDataRoot(header=column_label)
    for pm in pm_list:
        new_node = TreeData(data=[pm.name, pm.createdAt])
        root.add_child(new_node)
        for contents in pm:
            new_child_node = TreeData(data=[contents.name])
            new_node.add_child(new_child_node)

    return root


def new_project_content() -> PM_Content:
    now = datetime.now()
    now_text = now.strftime("%Y-%m-%dT%H:%M:%S.") + str(now.microsecond) + "Z"
    new_pm_content = PM_Content(
        id=-1,
        type1=PM_CONTENT_TYPE1_NAME,
        type2="HAZOP",
        name=NEW_PROJECT_NAME,
        description=NEW_PROJECT_NAME,
        spec="",
        notes="",
        status="-",
        createdAt=now_text
    )

    return new_pm_content


def load_pm_list() -> PM_List:
    searched_pm_list = trosar_api.pm_search()
    pm_list = PM_List()
    for pm_data in searched_pm_list:
        pm_id = pm_data.id
        pm_contents = trosar_api.pm_contents_read(
            pm_id,
            type1=PM_CONTENT_TYPE1_NAME  # TODO
        )
        pm_list.append(pm_data)
        for pm_content in pm_contents:
            pm_list[pm_data.name].add_content(pm_content)
        new_pm_content = new_project_content()
        pm_list[pm_data.name].add_content(new_pm_content)
    return pm_list


def temp_default_guideword():
    # 가이드워드를 생성하는 모의 코드
    guideword = {
        "부정": {
            "No": "명령이 실행되지 않는 상태"
        },
        "정량적 변형": {
            "More": "수량의 비정상 증가",
            "Less": "수량의 비정상 감소"
        },
        "정성적 변형": {
            "As well as": "기대하지 않은 동작 수행",
            "Part of": "완전한 수행을 하지 못함"
        },
        "대체": {
            "Reverse": "목적과 상반되는 결과 수행",
            "Other than": "목적과 다른 결과 수행"
        },
        "시간": {
            "Early": "예상시간보다 일찍 발생",
            "Late": "예상시간보다 늦게 발생"
        },
        "명령 또는 흐름": {
            "Before": "예상순서보다 일찍 발생",
            "After": "예상순서보다 늦게 발생"
        }
    }
    TYPE = GuideWordPandasTable.TYPE
    WORD = GuideWordPandasTable.WORD
    DESCRIPTION = GuideWordPandasTable.DESCRIPTION

    dict_output = {
        TYPE: [],
        WORD: [],
        DESCRIPTION: []
    }
    for key, value in guideword.items():
        for key2, description in value.items():
            dict_output[TYPE].append(key)
            dict_output[WORD].append(key2)
            dict_output[DESCRIPTION].append(description)
    return dict_output


# severity_frequency = self.safety_data.hazop_analysis.info.severity_frequency
def init_data_(severity_frequency: SeverityFrequency):
    def set_risk_data(sf_data_: SeverityFrequency):
        data_list = [
            ["빈번한 발생", "0", "", "10E-3 이상"],
            ["종종 발생", "1", "", "10E-4 < ~ 10E-3"],
            ["가끔 발생", "2", "", "10E-6 < ~ 10E-4"],
            ["미약함", "3", "", "10E-8 < ~ 10E-6"],
            ["거의 없음", "4", "", "10E-9 < ~ 10E-8"],
            ["전혀 없음", "5", "", "10E-9 이하"]
        ]
        column_labels = ["name", "rank", "description", "quantitative"]

        dataframe_data = {}
        for i, label in enumerate(column_labels):
            dataframe_data[label] = []
            for data in data_list:
                dataframe_data[label].append(data[i])
        dataframe = DataFrame(dataframe_data)
        sf_data_.frequency_table.set_dataframe(dataframe)

        data_list = [
            ["치명적 위험", "A", "인명의 사망 및 시스템의 손실", "사망 사고, 30분 이상 지연"],
            ["중대한 위험", "B", "인명 부상 및 시스템 고장", "인명 부상, 10-30분 지연"],
            ["중요하지 않은 위험", "C", "시스템의 고장으로 정지 및 운행에 지장", "10분이하 지연"],
            ["사소한 위험", "D", "고장으로 유지보수 필요, 시스템 정상 운행 가능", "정상 운행 가능"],
            ["정상", "E", "", ""]
        ]
        column_labels = ["name", "rank", "description", "quantitative"]

        dataframe_data = {}
        for i, label in enumerate(column_labels):
            dataframe_data[label] = []
            for data in data_list:
                dataframe_data[label].append(data[i])
        dataframe = DataFrame(dataframe_data)
        sf_data_.severity_table.set_dataframe(dataframe)

        data_list = [
            ["Intolerable", "I", "허용 불가능한 위험", "N", "A0, B0, C0, D0, A1, B1, C1, D2, D3"],
            ["Undesirable", "U", "불가피한 경우 허용 가능한 위험", "Y", "E0, D1, D2, C2, C3, B3, B4"],
            ["Tolerable", "T", "허용 가능한 위험", "Y", "A1, A2, B3, C4, D5"],
            ["Negligible", "N", "무시할 수 있는 위험", "Y", "A3, A4, A5, B4, B5, C5"],
        ]
        column_labels = ["name", "rank", "description", "permit", "target"]

        dataframe_data = {}
        for i, label in enumerate(column_labels):
            dataframe_data[label] = []
            for data in data_list:
                dataframe_data[label].append(data[i])
        dataframe = DataFrame(dataframe_data)
        sf_data_.risk_table.set_dataframe(dataframe)

        data_list = [
            ["U", "I", "I", "I", "I", ],
            ["T", "U", "I", "I", "I", ],
            ["T", "U", "U", "I", "I", ],
            ["N", "T", "U", "U", "I", ],
            ["N", "N", "T", "U", "U", ],
            ["N", "N", "N", "T", "T", ],
        ]
        column_labels = ["E", "D", "C", "B", "A"]

        dataframe_data = {}
        for i, label in enumerate(column_labels):
            dataframe_data[label] = []
            for data in data_list:
                dataframe_data[label].append(data[i])
        dataframe = DataFrame(dataframe_data)
        sf_data_.risk_matrix.set_dataframe(dataframe)

    set_risk_data(severity_frequency)

    cell_range = severity_frequency.frequency_table.index_to_cell_range(0, 0, 10, 10)
    severity_frequency.frequency_table.set_cell_protected(cell_range)
    severity_frequency.severity_table.set_cell_protected(cell_range)
    severity_frequency.risk_table.set_cell_protected(cell_range)
    severity_frequency.risk_matrix.set_cell_protected(cell_range)
