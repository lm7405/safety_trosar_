import traceback
from inspect import signature
from functools import wraps


def raise_if_debug(print_func: callable = print):
    def decorator(func: callable):
        @wraps(func)
        def wrapper_function(*args, **kwargs):  # 파라미터 패킹 - https://kukuta.tistory.com/318
            try:
                sig = signature(func)
                if len(sig.parameters) != len(args):
                    print("At function {}, number of args is not correct. expect {}, called {}".format(
                        func.__name__, len(sig.parameters), len(args)))
                    result = func(*args[:len(sig.parameters)], **kwargs)  # 파라미터 언패킹
                else:
                    result = func(*args, **kwargs)  # 파라미터 언패킹
                return result

            except Exception as ex:
                traceback.print_exc()
                print_func_ = print_func
                if isinstance(print_func_, str):
                    print_func_ = getattr(args[0], print_func_)
                # if hasattr(args[0], "print_info"):
                #     print_func_ = getattr(args[0], "print_info")
                sig = signature(print_func_)
                if len(sig.parameters) is 1:
                    # print_func_("{}: {}".format(func.__name__, str(ex)))
                    pass
                elif len(sig.parameters) is 2:
                    # print_func_(args[0], "{}: {}".format(func.__name__, str(ex)))
                    pass
                else:
                    raise
                print("{}: {}".format(func.__name__, str(ex)))

                from safetyTrosar import debug
                if debug is True:
                    raise ex
        return wrapper_function
    return decorator
