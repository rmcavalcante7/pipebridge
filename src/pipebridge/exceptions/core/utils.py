import inspect
from typing import Tuple


def getExceptionContext(obj: object) -> Tuple[str, str]:
    """
    Extract class and method name for exception context.

    :param obj: object = Instance
    :return: tuple[str, str]
    """
    class_name = obj.__class__.__name__
    method_name = inspect.currentframe().f_back.f_code.co_name  # type: ignore

    return class_name, method_name
