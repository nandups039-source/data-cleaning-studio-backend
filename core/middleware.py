# config/middleware.py
from django.conf import settings
from django.http import JsonResponse
from utils.exceptions import InvalidCandidateException
from utils.logger import log_error, log_info

class CandidateValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.expected_candidate_id = settings.X_CANDIDATE_ID

    def __call__(self, request):
        try:
            candidate_id = request.headers.get("X-Candidate-Id")

            if not candidate_id:
                log_error("Missing X-Candidate-Id header")
                raise InvalidCandidateException()

            if candidate_id != self.expected_candidate_id:
                log_error(
                    "Invalid candidate ID received",
                    extra={"received_candidate_id": candidate_id}
                )
                raise InvalidCandidateException()

            log_info(
                "Candidate ID validated successfully",
                extra={"candidate_id": candidate_id}
            )
            return self.get_response(request)

        except InvalidCandidateException as e:
            # Use JsonResponse here for middleware
            return JsonResponse({
                "hasError": True,
                "errorCode": e.detail.get("errorCode", 1002),
                "message": e.detail.get("message", "Something went wrong"),
                "data": {}
            }, status=e.status_code)
