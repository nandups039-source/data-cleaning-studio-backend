# config/exceptions.py
import logging
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class BaseAPIException(APIException):
    """
    Standard API error response:
    {
        hasError: true,
        errorCode: <int>,
        message: <string>
    }
    """
    status_code = 400
    error_code = 1000
    default_message = "Something went wrong."

    def __init__(self, message=None, *, log_message=None):
        self.detail = {
            "hasError": True,
            "errorCode": self.error_code,
            "message": message or self.default_message
        }

        if log_message:
            logger.warning(log_message)

        super().__init__(self.detail)


class InvalidCandidateException(BaseAPIException):
    status_code = 403
    error_code = 1002
    default_message = "Invalid candidate."