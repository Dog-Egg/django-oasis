class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        handle_error = getattr(request, "_oasis_handle_error", None)
        if handle_error is not None:
            return handle_error(exception, request)
