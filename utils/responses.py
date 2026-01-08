from rest_framework.response import Response

class APIResponse:
    @staticmethod
    def success(data=None, message="Success"):
        """
        Standard success response
        """
        return Response({
            "hasError": False,
            "errorCode": -1,
            "message": message,
            "data": data or {}
        })

    @staticmethod
    def failure(message="Something went wrong", error_code=1000, data=None, status_code=400):
        """
        Standard failure response
        """
        return Response({
            "hasError": True,
            "errorCode": error_code,
            "message": message,
            "data": data or {}
        }, status=status_code)
