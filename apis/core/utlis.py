from rest_framework.response import Response


def api_response(status, message, data=None, errors=None, http_status=200):
    """
    Generate a consistent API response format.

    :param status: 'success' or 'error'
    :param message: Descriptive message
    :param data: Data payload (optional)
    :param errors: Errors payload (optional)
    :param http_status: HTTP status code
    :return: Response object
    """
    response = {
        "status": status,
        "message": message,
        "data": data or {},
        "errors": errors or {},
    }
    return Response(response, status=http_status)
