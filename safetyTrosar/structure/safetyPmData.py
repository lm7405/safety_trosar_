from typing import Dict, List, Any, TypeVar, Tuple, ClassVar
from collections import OrderedDict
from pydantic import BaseModel
from datetime import datetime
import json
from io import StringIO

from safetyTrosar.tool.trosarApi import trosar_api, PM, PM_Content
from safetyTrosar.structure.qtableviewModel import PandasTableData


# Step 1) Make Project
class Project(BaseModel):
    class Info(BaseModel):
        pm_id: str = None
        pm_name: str = None
        project_id: str = None
        project_name: str = None
        project_type1: str = None
        project_type2: str = None
        project_version: str = None
        project_status: str = None

        def import_pm(self, pm: PM, pm_content: PM_Content):
            self.pm_id = pm.id
            self.pm_name = pm.name
            self.project_id = pm_content.id
            self.project_name = pm_content.name
            self.project_type1 = pm_content.type1
            self.project_type2 = pm_content.type2
            self.project_status = pm_content.status
            self.project_version = pm_content.createdAt

        def export_pm_content(self):
            pm_content = PM_Content(
                id=self.project_id,
                type1=self.project_type1,
                type2=self.project_type2,
                name=self.project_name,
                description="",
                spec="",
                notes="",
                status=self.project_status,
                createdAt=self.project_version
            )
            return pm_content

    info: Info = None

    def init(self):
        self.info = self.Info()


# Step 2) Check Requirements
class Requirements(BaseModel):
    class Info(BaseModel):
        version: Any = ""

    class Table(PandasTableData):
        TYPE1: ClassVar[str] = "type1"
        TYPE2: ClassVar[str] = "type2"
        NAME: ClassVar[str] = "name"
        DESCRIPTION: ClassVar[str] = "description"
        SPEC: ClassVar[str] = "spec"
        NOTES: ClassVar[str] = "notes"
        STATUS: ClassVar[str] = "status"
        CREATED_AT: ClassVar[str] = "createdAt"

        class Type1(object):
            FUNCTION: ClassVar[str] = "??????"
            INPUT: ClassVar[str] = "??????"
            OUTPUT: ClassVar[str] = "??????"
            ENVIRONMENT: ClassVar[str] = "??????"
            STAKEHOLDER: ClassVar[str] = "?????????"
            PM: ClassVar[str] = "pm"
            CONNECTION: ClassVar[str] = "??????"
            STRUCTURE: ClassVar[str] = "??????"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (TYPE1, "??????1"),
            (TYPE2, "??????2"),
            (NAME, "??????"),
            (DESCRIPTION, "??????"),
            (SPEC, "??????"),
            (NOTES, "??????"),
            (STATUS, "??????"),
            (CREATED_AT, "???????????????"),
        ]

    info: Info = None
    table: Table = None

    def init(self):
        self.info = self.Info()
        self.table = self.Table()


class GuideWordPandasTable(PandasTableData):
    TYPE: ClassVar[str] = "type"
    WORD: ClassVar[str] = "word"
    DESCRIPTION: ClassVar[str] = "description"

    TYPE_: ClassVar[str] = "??????"
    WORD_: ClassVar[str] = "???????????????"
    DESCRIPTION_: ClassVar[str] = "??????"

    column_labels: ClassVar[List[Tuple[str, str]]] = [
        (TYPE, "??????"),
        (WORD, "???????????????"),
        (DESCRIPTION, "??????"),
    ]


class SeverityFrequency(BaseModel):
    class SeverityPandasTable(PandasTableData):
        NAME: ClassVar[str] = "name"
        RANK: ClassVar[str] = "rank"
        DESCRIPTION: ClassVar[str] = "description"
        QUANTITATIVE: ClassVar[str] = "quantitative"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (NAME, "?????????"),
            (RANK, "??????"),
            (DESCRIPTION, "??????"),
            (QUANTITATIVE, "??????"),
        ]

    class FrequencyPandasTable(PandasTableData):
        NAME: ClassVar[str] = "name"
        RANK: ClassVar[str] = "rank"
        DESCRIPTION: ClassVar[str] = "description"
        QUANTITATIVE: ClassVar[str] = "quantitative"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (NAME, "?????? ??????"),
            (RANK, "??????"),
            (DESCRIPTION, "??????"),
            (QUANTITATIVE, "??????"),
        ]

    class RiskPandasTable(PandasTableData):
        NAME: ClassVar[str] = "name"
        RANK: ClassVar[str] = "rank"
        DESCRIPTION: ClassVar[str] = "description"
        PERMIT: ClassVar[str] = "permit"
        TARGET: ClassVar[str] = "target"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (NAME, "??????"),
            (RANK, "??????"),
            (DESCRIPTION, "??????"),
            (PERMIT, "?????? ??????"),
            (TARGET, "??????(??????)")
        ]

        def get_risk_rank(self, severity: str, frequency: str):
            if len(frequency) == 0 or len(severity) == 0:
                return ""
                raise Exception("?????? ?????? ???????????? ???????????? ???????????????.")
            sf_str = frequency + severity
            for index, row in self.dataframe.iterrows():
                if sf_str in row[self.TARGET]:
                    return row[self.RANK]
            return ""
            raise Exception("???????????? ?????? ?????? ?????? ?????????(" + sf_str + ")??? ?????????????????????.")

        def is_permit(self, rank: str):
            for i, row in self.dataframe.iterrows():
                if row[self.RANK] == rank:
                    if row[self.PERMIT] == 'Y':
                        return True
                    else:
                        return False
            raise Exception("????????? ????????? ?????? ???????????? ?????? ??? ????????????.")

    class RiskMatrix(PandasTableData):
        A: ClassVar[str] = 'A'
        B: ClassVar[str] = 'B'
        C: ClassVar[str] = 'C'
        D: ClassVar[str] = 'D'
        E: ClassVar[str] = 'E'

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (E, 'E'),
            (D, 'D'),
            (C, 'C'),
            (B, 'B'),
            (A, 'A'),
        ]

    severity_table: SeverityPandasTable = None
    frequency_table: FrequencyPandasTable = None
    risk_table: RiskPandasTable = None
    risk_matrix: RiskMatrix = None

    def init(self):
        self.severity_table = self.SeverityPandasTable()
        self.frequency_table = self.FrequencyPandasTable()
        self.risk_table = self.RiskPandasTable()
        self.risk_matrix = self.RiskMatrix()


# step 3) Hazop Analysis
class HazopAnalysis(BaseModel):
    class Info(BaseModel):
        guide_word_table: GuideWordPandasTable = None
        severity_frequency: SeverityFrequency = None

        def init(self):
            self.guide_word_table = GuideWordPandasTable()
            self.severity_frequency = SeverityFrequency()
            self.severity_frequency.init()

    class Table(PandasTableData):
        MODULE: ClassVar[str] = "module"
        FUNCTION: ClassVar[str] = "function"
        ITEM: ClassVar[str] = "item"
        GUIDEWORD_TYPE: ClassVar[str] = "guideword_type"
        GUIDEWORD_WORD: ClassVar[str] = "guideword_word"
        GUIDEWORD_DESCRIPTION: ClassVar[str] = "guideword_description"
        BEFORE_FAULT_SITUATION: ClassVar[str] = "before_fault_situation"
        # CAUSE_FAULT: ClassVar[str] = "cause_fault"
        CAUSE_EFFECT: ClassVar[str] = "cause_effect"
        BEFORE_EFFECT_AND_RESULT: ClassVar[str] = "before_effect_and_result"
        BEFORE_SEVERITY: ClassVar[str] = "before_severity"
        BEFORE_FREQUENCY: ClassVar[str] = "before_frequency"
        HAZARD_ID: ClassVar[str] = "hazard_id"
        SAFETY_MEASURE: ClassVar[str] = "safety_measure"
        SAFETY_MEASURE_TYPE: ClassVar[str] = "safety_measure_type"
        AFTER_FAULT_SITUATION: ClassVar[str] = "after_fault_situation"
        AFTER_EFFECT_AND_RESULT: ClassVar[str] = "after_effect_and_result"
        AFTER_SEVERITY: ClassVar[str] = "after_severity"
        AFTER_FREQUENCY: ClassVar[str] = "after_frequency"
        DESCRIPTION: ClassVar[str] = "description"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (MODULE, "??????"),
            (FUNCTION, "??????"),
            (ITEM, "??????"),
            (GUIDEWORD_TYPE, "Guide Word\n??????"),
            (GUIDEWORD_WORD, "Guide Word\n??????"),
            (GUIDEWORD_DESCRIPTION, "Guide Word\n??????"),
            (BEFORE_FAULT_SITUATION, "?????? ?????? ??????"),
            # (CAUSE_FAULT, "?????? ??????\n?????????"),
            (CAUSE_EFFECT, "?????? ??????\n?????? ??????"),
            (BEFORE_EFFECT_AND_RESULT, "?????? ?????? ??? ??????"),
            (BEFORE_SEVERITY, "?????? ???\nS"),
            (BEFORE_FREQUENCY, "?????? ???\nF"),
            (HAZARD_ID, "????????? ?????????"),
            (SAFETY_MEASURE, "????????????"),
            (SAFETY_MEASURE_TYPE, "????????????\n??????"),
            (AFTER_FAULT_SITUATION, "?????? ???\n?????? ?????? ??????"),
            (AFTER_EFFECT_AND_RESULT, "?????? ???\n?????? ?????? ??? ??????"),
            (AFTER_SEVERITY, "?????? ???\nS"),
            (AFTER_FREQUENCY, "?????? ???\nF"),
            (DESCRIPTION, "??????????????????"),
        ]

    info: Info = None
    table: Table = None

    def init(self):
        self.info = self.Info()
        self.table = self.Table()
        self.info.init()


# Step 4) Check Safety Measure
class SafetyMeasure(BaseModel):
    class Info(BaseModel):
        any_: str = None

    class PandasTable(PandasTableData):
        NAME: ClassVar[str] = "name"
        DESCRIPTION: ClassVar[str] = "description"
        SAFETY_REQUIREMENTS: ClassVar[str] = "safety_requirements"
        HAZARD_ID: ClassVar[str] = "hazard_id"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            # "id": "???????????? ID",
            (NAME, "??????"),
            (DESCRIPTION, "??????"),
            (SAFETY_REQUIREMENTS, "?????? ????????????"),
            (HAZARD_ID, "????????? ?????????"),
            # "version": "??????"
        ]

    info: Info = None
    table: PandasTable = None

    def init(self):
        self.info = self.Info()
        self.table = self.PandasTable()


# Step 5) Write Hazard Log
class HazardLog(BaseModel):
    class Info(BaseModel):
        pass

    class PandasTable(PandasTableData):
        PM_ID: ClassVar[str] = "pm_id"
        HAZARD_ID: ClassVar[str] = "hazard_id"
        FAILURE: ClassVar[str] = "failure"
        EFFECT: ClassVar[str] = "effect"
        INITIAL_RISK: ClassVar[str] = "initial_risk"
        SAFETY_MEASURES: ClassVar[str] = "safety_measures"
        REDUCE_RISK: ClassVar[str] = "reduced_risk"
        EVIDENCE: ClassVar[str] = "evidence"
        STATUS: ClassVar[str] = "status"
        UPDATE_DATE: ClassVar[str] = "update_date"
        RESPONSIBILITY: ClassVar[str] = "responsibility"

        column_labels: ClassVar[List[Tuple[str, str]]] = [
            (PM_ID, "PM ?????????"),
            (HAZARD_ID, "????????? ?????????"),
            (FAILURE, "??????"),
            (EFFECT, "??????"),
            (INITIAL_RISK, "?????? ?????????"),
            (SAFETY_MEASURES, "?????? ??????"),
            (REDUCE_RISK, "????????? ?????????"),
            (STATUS, "??????"),
            (UPDATE_DATE, "?????? ?????????"),
            (RESPONSIBILITY, "??????"),
            (EVIDENCE, "??????"),
        ]

    info: Info = None
    table: PandasTable = None

    def init(self):
        self.info = self.Info()
        self.table = self.PandasTable()


PM_CONTENT_TYPE1_NAME = "SafetyTrosar PM Data"
PM_CONTENT_TYPE2_NAME = "HAZOP_FILE"
NEW_PROJECT_NAME = "??? ??????"
HAZOP_WORK_NAME = "HAZOP"


# pm??? ???????????? ??????
class SafetyPmData(BaseModel):
    project: Project = None
    requirements: Requirements = None
    hazop_analysis: HazopAnalysis = None
    safety_measures: SafetyMeasure = None
    hazard_log: HazardLog = None
    Model = TypeVar('Model', bound='BaseModel')

    class Config:
        arbitrary_types_allowed = True

    def init(self):
        self.project = Project()
        self.requirements = Requirements()
        self.hazop_analysis = HazopAnalysis()
        self.safety_measures = SafetyMeasure()
        self.hazard_log = HazardLog()

        self.project.init()
        self.requirements.init()
        self.hazop_analysis.init()
        self.safety_measures.init()
        self.hazard_log.init()

    def save_pm_server(self):
        project_info = self.project.info
        pm_id = self.project.info.pm_id
        merged_description = {}

        if self.project.info.project_id is None:
            raise Exception("SafetyData.Project.Info is not initialize")

        now = datetime.now()
        now_text = now.strftime("%Y-%m-%dT%H:%M:%S.") + str(now.microsecond) + "Z"
        project_info.project_version = now_text

        def add_new_pm_content():
            pm_content = project_info.export_pm_content()
            if pm_content.id == "-1":
                trosar_api.pm_content_new(pm_id=pm_id, contents=[pm_content])
                pm_content_list = trosar_api.pm_contents_read(
                    pm_id=pm_id,
                    type1=pm_content.type1,
                    type2=pm_content.type2,
                    name=pm_content.name
                )
                project_info.project_id = pm_content_list[-1].id

        def save_to_file():
            # ?????? ??????
            path = project_info.project_name + "." + PM_CONTENT_TYPE2_NAME
            safety_pm_dict = self.dict()
            # ????????????, ??????????????? ????????? ??????
            if 'Model' in safety_pm_dict:
                del safety_pm_dict['Model']
            json_ = json.dumps(safety_pm_dict, ensure_ascii=False)
            file = StringIO(json_)
            file.name = path
            file.seek(0)

            result = trosar_api.pm_content_fileUpload(pm_id, file)
            if result is False:
                raise Exception("safetyPmData: PM ????????? ?????????????????????.")
            # os.remove(path)

            # description ????????????
            json_file = trosar_api.pm_contents_read(
                pm_id=pm_id,
                type1="??????",
                type2=PM_CONTENT_TYPE2_NAME,
                spec=path
            )
            newest_file_pm_content = None
            for content in json_file:
                if content.type2 == "." + PM_CONTENT_TYPE2_NAME:
                    if newest_file_pm_content is None:
                        newest_file_pm_content = content
                    else:
                        if newest_file_pm_content.spec < content.spec:
                            trosar_api.pm_content_delete(pm_id=pm_id, content_id=newest_file_pm_content.id)
                            newest_file_pm_content = content
                        else:
                            trosar_api.pm_content_delete(pm_id=pm_id, content_id=content.id)

            # api_result = trosarApi.pm_content_fileUpload(pm_id, path)
            if newest_file_pm_content is not None:
                file_url_path = newest_file_pm_content.spec
                file_content_id = newest_file_pm_content.id

                merged_description["path"] = file_url_path
                merged_description["id"] = file_content_id
            else:
                raise Exception("pm ?????? ?????? ??????")

        def update_pm_content():
            # pm_content ????????????
            pm_content = project_info.export_pm_content()
            pm_content.description = json.dumps(merged_description)

            trosar_api.pm_content_update(pm_id=pm_id, pm_content=pm_content)

        add_new_pm_content()
        save_to_file()
        update_pm_content()

        return project_info.project_id, json.dumps(merged_description)

    @classmethod
    def load_pm_server(cls, pm: "PM", pm_content: PM_Content):
        pm_content = trosar_api.pm_contents_read(
            pm_id=pm.id, type1=pm_content.type1, type2=pm_content.type2, name=pm_content.name
        )[0]
        description_ = pm_content.description
        json_ = json.loads(description_)
        safety_trosar_data_str = trosar_api.pm_content_fileDownload(
            pm_id=pm.id,
            file_path=json_["path"]
        )
        safety_trosar_data_dict = json.loads(safety_trosar_data_str)

        return cls.parse_obj(safety_trosar_data_dict)
