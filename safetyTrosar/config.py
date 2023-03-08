# http://daplus.net/python-__init__-py%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%98%EC%97%AC-%EC%A0%84%EC%97%AD-%EB%B3%80%EC%88%98%EB%A5%BC-%EC%A0%95%EC%9D%98-%ED%95%A0-%EC%88%98-%EC%9E%88%EC%8A%B5%EB%8B%88%EA%B9%8C/

import os as __os


# Path 관련
# https://schulwin.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%97%90%EC%84%9C-%ED%8C%8C%EC%9D%BC%EA%B3%BC-%EB%94%94%EB%A0%89%ED%86%A0%EB%A6%AC-%EA%B2%BD%EB%A1%9C-%EB%8B%A4%EB%A3%A8%EA%B8%B0
import os.path

# pyrcc5
# "D:\Source\Python\safety trosar\safetyTrosar\resource\resources.qrc" > "D:\Source\Python\safety trosar\resource.py"
__path = __os.path.dirname(__os.path.abspath(__file__))
resource_path = __path + "/resource"
run_path = __path


def get_abs_path(relative_path):
    return os.path.join(__path, relative_path)


# 설정값 관련
def init_config():
    raise
