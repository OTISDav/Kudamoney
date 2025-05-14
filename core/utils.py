from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, APIException):
        response.data['status_code'] = response.status_code
        if hasattr(exc, 'detail'):
            response.data['message'] = exc.detail
        else:
            response.data['message'] = str(exc)
    return response