import traceback

from rest_framework.views import exception_handler as drf_exception_handler

from core.logging_utils import append_error_log


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        detail = getattr(response, "data", None)
        append_error_log(f"API 错误: {detail!r}", exc)
        return response
    append_error_log("未处理的 API 异常", exc)
    return None
