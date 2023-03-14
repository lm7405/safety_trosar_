import requests
import json
from typing import Dict, Union, List, Any, Type
from enum import Enum
import urllib3
from pydantic import BaseModel


class METHOD(Enum):
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4


class PM_Content(BaseModel):
    id: str
    type1: str
    type2: str
    name: str
    description: str
    spec: str
    notes: str
    status: str
    createdAt: str

    def __getitem__(self, key):
        return getattr(self, key)


class PM(BaseModel):
    id: str
    createdAt: str
    name: str
    description: str
    pm_contents: List[PM_Content] = []

    def __getitem__(self, key) -> PM_Content:
        if isinstance(key, str):
            for pm_content in self.pm_contents:
                if pm_content.name == key:
                    return pm_content
        elif isinstance(key, int):
            return self.pm_contents[key]
        else:
            raise

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if isinstance(value, PM_Content):
                for pm_content in self.pm_contents:
                    if pm_content.name == key:
                        return pm_content
            else:
                raise
        elif isinstance(key, int):
            return self.pm_contents[key]
        else:
            raise

    def __iter__(self):
        return iter(self.pm_contents)

    def __delitem__(self, name):
        # Logic for deletion
        for obj in self.pm_contents:
            if obj.name == name:
                self.pm_contents.remove(obj)

    def __contains__(self, item):
        if isinstance(item, str):
            for obj in self.pm_contents:
                if obj.name == item:
                    return True
            return False
        else:
            raise

    @classmethod
    def parse_obj(cls: Type['PM'], obj: Any) -> 'PM':
        obj = cls._enforce_dict_if_root(obj)
        obj["pm_contents"] = []
        if not isinstance(obj, dict):
            try:
                obj = dict(obj)
            except (TypeError, ValueError):
                exc = TypeError(f'{cls.__name__} expected dict not {obj.__class__.__name__}')
                raise exc
        return cls(**obj)

    def add_content(self, pm_content: Union[PM_Content, dict, str]):
        if isinstance(pm_content, str):
            pm_content = json.loads(pm_content)
        if isinstance(pm_content, dict):
            pm_content = PM.parse_obj(pm_content)
        if isinstance(pm_content, PM_Content):
            self.pm_contents.append(pm_content)
        else:
            raise


class PM_List(BaseModel):
    pm_data: List[PM] = []

    def __getitem__(self, key) -> PM:
        if isinstance(key, str):
            for pm in self.pm_data:
                if pm.name == key:
                    return pm
        elif isinstance(key, int):
            return self.pm_data[key]
        else:
            raise

    def __iter__(self):
        return iter(self.pm_data)

    # def __next__(self):
    #     if self.position >= len(self.my_class):
    #         raise StopIteration
    #     item = self.my_class.get_data(self.position)
    #     self.position += 1
    #     # preprocess item
    #     # some mysterious code block
    #     return item

    def append(self, pm: Union[PM, Dict, str]):
        if isinstance(pm, str):
            raise
        if isinstance(pm, Dict):
            raise
        if isinstance(pm, PM):
            self.pm_data.append(pm)
        else:
            raise


class TrosarApi:
    __localhost: str
    __trosar_host: str
    NotConnectError = (
        ConnectionRefusedError,
        urllib3.exceptions.NewConnectionError,
        urllib3.exceptions.MaxRetryError,
        requests.exceptions.ConnectionError,
        requests.exceptions.InvalidURL,
        requests.exceptions.ReadTimeout,
    )

    def __init__(self, localhost=None, trosar_host=None):
        if localhost is not None and trosar_host is not None:
            self.init(localhost, trosar_host)

    def init(self, localhost, trosar_host):
        self.__localhost = localhost
        self.__trosar_host = trosar_host
        self.check_connection()

    def check_connection(self):
        method = METHOD.GET
        url = "/pm"
        self.request(method, url, timeout=1)

    @staticmethod
    def new_content(data):
        return PM_Content.parse_obj(data)

    def example(self):
        # return self.pm_search("")
        # return self.pm_new("테스트", "테스트설명")
        # return self.pm_update(5, "테스트PM3", "수정된 테스트설명")
        # return self.pm_delete(4)
        return self.pm_contents_read(1)
        # return self.pm_content_new(1, [content_class(["TROSAR안전성분석", "", "테스트입력", "테스트설명", "DC 12V", ""])])
        # return self.pm_content_update(6, 17, content_class("테스트타입2", "", "테스트입력", "테스트설명", "DC 12V", ""))
        # return self.pm_content_delete(6, 23)
        # return self.pm_content_fileUpload(6, 'safety_trosar/main.safety_trosar')

    # PM 관리 API
    def pm_search(self, key: str = None):
        # PM 목록/검색
        method = METHOD.GET
        url = "/pm"
        query = {}

        if key is not None:
            query["search"] = key

        response = self.request(method, url, query=query)
        pm_list_raw = response['pm']

        pm_list = PM_List()
        for pm_raw in pm_list_raw:
            pm = PM.parse_obj(pm_raw)
            pm_list.append(pm)

        return pm_list

    def pm_info(self, pm_id: int, type1: str = None, name: str = None, spec: str = None):
        # PM 상세정보
        method = METHOD.GET
        url = "/pm/" + str(pm_id)
        query = {}

        if type1 is not None:
            query["type1"] = type1
        if name is not None:
            query["name"] = name
        if spec is not None:
            query["spec"] = spec

        response = self.request(method, url, query=query)
        pm_raw = response['pm']
        pm = PM.parse_obj(pm_raw)

        return pm

    def pm_new(self, name: str, description: str):
        # PM 생성, 미완성
        method = METHOD.POST
        url = "/pm"
        json_ = {"name": name, "description": description}

        response = self.request(method, url, json_=json_)
        pm_raw = response['pm']
        pm = PM.parse_obj(pm_raw)

        return pm

    def pm_update(self, pm: PM):
        # PM 생성
        method = METHOD.PUT
        url = "/pm/" + pm.id
        json_ = {"name": pm.name, "description": pm.description}

        response = self.request(method, url, json_=json_)
        pm_raw = response['pm']
        pm = PM.parse_obj(pm_raw)

        return pm

    def pm_delete(self, pm_id: int):
        # PM 삭제
        method = METHOD.DELETE
        url = "/pm/" + str(pm_id)

        response = self.request(method, url)
        return response['success']

    def pm_contents_read(self, pm_id: int, type1: str = None, type2: str = None, name: str = None, spec: str = None) \
            -> List[PM_Content]:
        # PM 특성 정보 읽기
        method = METHOD.GET
        url = "/pm/" + str(pm_id) + "/content"
        query = {}
        if type1 is not None:
            query["type1"] = type1
        if type2 is not None:
            query["type2"] = type2
        if name is not None:
            query["name"] = name
        if spec is not None:
            query["spec"] = spec

        response = self.request(method, url, query=query)
        output_ = []
        if response['success'] is False:
            raise
        for content in response['content']:
            output_.append(PM_Content.parse_obj(content))
        return output_

    def pm_content_new(self, pm_id: int, contents: List[PM_Content]):
        # PM 특성 정보 생성
        method = METHOD.POST
        url = "/pm/" + str(pm_id) + '/content'
        json_ = {"content": []}
        for content in contents:
            pm_content_dict = content.dict()
            del pm_content_dict['id']
            json_["content"].append(pm_content_dict)

        response = self.request(method, url, json_=json_)
        if response['success'] is False:
            raise
        return response['success']

    def pm_content_update(self, pm_id: int, pm_content: PM_Content):
        # PM 특성 정보 수정
        method = METHOD.PUT
        url = "/pm/" + "content/" + str(pm_content.id)
        json_ = pm_content.dict()
        del json_["id"]

        response = self.request(method, url, json_=json_)
        if response['success'] is False:
            raise
        return response['success']

    def pm_content_delete(self, pm_id: int, content_id: int):
        # PM 특성 정보 삭제
        method = METHOD.DELETE
        url = "/pm/" + "content/" + str(content_id)

        response = self.request(method, url)
        if response['success'] is False:
            raise
        return response['success']

    def pm_content_fileUpload(self, pm_id: int, file):
        # PM 특성 파일 업로드
        method = METHOD.POST
        url = "/pm/" + str(pm_id) + "/content/file"
        files = {"file": file, "a": "a"}
        response_content_json = self.request(method, url, files=files)
        if response_content_json['success'] is False:
            raise
        return response_content_json['success']

    def pm_content_fileDownload(self, pm_id, file_path: str):
        url = file_path[1:]

        content = requests.get(self.__localhost + url).content

        file = content.decode('utf-8')
        json_ = json.loads(file)
        if 'success' in json_ and json_['success'] is False:
            raise Exception("Cannot download file: {}".format(json_['message']))

        return file

    # 플랫폼 로그인 API

    # PSM 데이터 관리

    # 내부 함수
    def request(self, method: METHOD, url: str, query=None, json_=None, files=None, timeout=1):
        url_ = self.__localhost + url

        if method == METHOD.GET:
            response = requests.get(url_, params=query, json=json_, files=files, timeout=timeout)
        elif method == METHOD.POST:
            response = requests.post(url_, params=query, json=json_, files=files, timeout=timeout)
        elif method == METHOD.PUT:
            response = requests.put(url_, params=query, json=json_, files=files, timeout=timeout)
        elif method == METHOD.DELETE:
            response = requests.delete(url_, params=query, data=json_, files=files, timeout=timeout)
        else:
            # method is invalid
            raise

        response_content_json_str = response.content.decode('utf-8')
        response_content_json = json.loads(response_content_json_str)

        return response_content_json


# 전역 객체
trosar_api = TrosarApi()
