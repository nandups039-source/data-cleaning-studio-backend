# document_processor/views.py
from rest_framework.views import APIView
from rest_framework import status
from document_processor.serializers import DocumentSerializer
from utils.helper import dict_to_snake_case
from utils.logger import log_error
from utils.responses import APIResponse
from .services.document_utils import DocumentUtils


class FetchRawView(APIView):
    """Fetch raw records from LumiCore"""
    def get(self, request):
        utils = DocumentUtils()
        raw_data = utils.fetch()

        if not raw_data or "records" not in raw_data:
            log_error("Failed to fetch raw data from LumiCore API", extra={"raw_data": raw_data})
            return APIResponse.failure(
                message="Something went wrong",
                error_code=1001,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return APIResponse.success({
            "batchId": raw_data.get("batch_id"),
            "records": raw_data.get("records", [])
        })


class CleanDataView(APIView):
    """Normalize & deduplicate edited raw data"""
    def post(self, request):
        batch_id = request.data.get("batchId")
        records = request.data.get("records")

        if not batch_id or not records:
            log_error("Missing batch_id or records in request", extra=request.data)
            return APIResponse.failure(
                message="batch_id and records are required",
                error_code=1002,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        utils = DocumentUtils()
        normalized = utils.normalize(records)
        cleaned = utils.validate_and_deduplicate(normalized)

        return APIResponse.success({
            "batchId": batch_id,
            "cleanedItems": cleaned
        })


class SubmitCleanView(APIView):
    """Validate and submit cleaned records to LumiCore"""
    def post(self, request):
        batch_id = request.data.get("batchId")
        items = request.data.get("cleanedItems")
        cleaned_items = [dict_to_snake_case(item) for item in items]

        if not batch_id or not cleaned_items:
            log_error("Missing batch_id or cleaned_items in request", extra=request.data)
            return APIResponse.failure(
                message="batch and cleaned_items are required",
                error_code=1003,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate each cleaned record
        invalid_records = []
        for idx, rec in enumerate(cleaned_items, start=1):
            serializer = DocumentSerializer(data=rec)
            if not serializer.is_valid():
                invalid_records.append({
                    "index": idx,
                    "doc_id": rec.get("doc_id"),
                    "errors": serializer.errors
                })

        if invalid_records:
            log_error(f"Validation failed for {len(invalid_records)} records", extra=invalid_records)
            return APIResponse.failure(
                message="Some records are invalid",
                error_code=1004,
                data={"invalid_records": invalid_records},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        utils = DocumentUtils()
        result = utils.submit(batch_id, cleaned_items)

        if not result:
            log_error(f"Failed to submit cleaned data for batch {batch_id}", extra={"cleaned_items": cleaned_items})
            return APIResponse.failure(
                message="Server is unavailable, please try again later",
                error_code=1005,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return APIResponse.success(result, message="Submission successful")
