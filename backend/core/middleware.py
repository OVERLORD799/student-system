from core.logging_utils import append_error_log


class RequestErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            append_error_log(f"未捕获请求异常 {request.path}", exc)
            raise
