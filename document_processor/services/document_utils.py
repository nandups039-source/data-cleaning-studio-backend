import requests
import time
import re
from datetime import datetime
from django.conf import settings

from utils.helper import dict_to_camel_case

from .constants import (
    CANDIDATE_NAME,
    FIELD_MAP,
    DATE_FORMATS,
    DEFAULT_BATCH,
    RETRIES,
)

from utils.logger import log_error, log_info, log_warning


class DocumentUtils:
    def __init__(
        self,
        base_url=settings.LUMICORE_BASE_URL,
        candidate_id=settings.X_CANDIDATE_ID,
    ):
        self.base_url = base_url
        self.candidate_id = candidate_id

    # ---------------- FETCH ---------------- #
    def fetch(self, batch=DEFAULT_BATCH, retries=RETRIES, backoff=1):
        """Fetch data from API with retries & exponential backoff"""
        url = f"{self.base_url}/api/data?batch={batch}"
        headers = {"X-Candidate-Id": self.candidate_id}
        log_info(f"Fetching data from LumiCore API, batch={batch}")

        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=5)
                response.raise_for_status()
                log_info(f"Successfully fetched data on attempt {attempt + 1}")
                return response.json()
            except requests.RequestException as e:
                log_warning(f"Fetch attempt {attempt + 1} failed: {e}")
                time.sleep(backoff * (2 ** attempt))

        log_error("Failed to fetch data after retries")
        return None

    # ---------------- NORMALIZATION ---------------- #
    @staticmethod
    def get_field(data, keys):
        """Get first valid value from possible keys, including nested keys"""
        for key in keys:
            if "." in key:
                value = data
                for part in key.split("."):
                    value = value.get(part) if isinstance(value, dict) else None
                if value not in [None, "", "N/A"]:
                    return value
            else:
                if key in data and data[key] not in [None, "", "N/A"]:
                    return data[key]
        return None

    @staticmethod
    def parse_date(value):
        """Parse all possible date formats into ISO format"""
        if not value:
            return None

        value_str = str(value).strip()

        for fmt in DATE_FORMATS:
            try:
                dt = datetime.strptime(value_str, fmt)
                return dt.date().isoformat()
            except Exception:
                continue

        # Compact format YYYYMMDD
        if re.match(r"^\d{8}$", value_str):
            try:
                return datetime.strptime(value_str, "%Y%m%d").date().isoformat()
            except Exception:
                pass

        log_warning(f"Unable to parse date '{value_str}', dropping value")
        return None

    @staticmethod
    def parse_amount(value):
        """Convert amount strings like 'AED 5200' to float"""
        if value in [None, "", "N/A"]:
            return None

        if isinstance(value, str):
            value = re.sub(r"[^\d.]", "", value)

        try:
            return float(value)
        except Exception as e:
            log_warning(f"Unable to parse amount '{value}': {e}")
            return None

    def normalize(self, raw_records):
        """Normalize all raw records into standard schema"""
        normalized = []

        for record in raw_records:
            norm = {
                "doc_id": self.get_field(record, FIELD_MAP["doc_id"]),
                "type": self.get_field(record, FIELD_MAP["type"]),
                "counterparty": self.get_field(record, FIELD_MAP["counterparty"]),
                "project": self.get_field(record, FIELD_MAP["project"]),
                "expiry_date": self.parse_date(
                    self.get_field(record, FIELD_MAP["expiry_date"])
                ),
                "amount": self.parse_amount(
                    self.get_field(record, FIELD_MAP["amount"])
                ),
            }

            log_info(f"Normalized record: {norm}")
            normalized.append(norm)

        log_info(f"Total records normalized: {len(normalized)}")
        return normalized

    # ---------------- VALIDATION & DEDUPLICATION ---------------- #
    def validate_and_deduplicate(self, normalized_records):
        """
        Remove duplicates.
        DO NOT validate required fields here.
        Missing fields are allowed for UI display.
        """
        seen = set()
        valid_records = []

        log_info(f"Normalized records received: {len(normalized_records)}")

        for rec in normalized_records:
            doc_id = rec.get("doc_id")

            if not doc_id:
                log_warning("Record skipped due to missing doc_id")
                continue

            if doc_id in seen:
                log_warning(f"Duplicate record skipped: {doc_id}")
                continue

            seen.add(doc_id)

            valid_records.append(dict_to_camel_case({
                "doc_id": doc_id,
                "type": rec.get("type"),
                "counterparty": rec.get("counterparty"),
                "project": rec.get("project"),
                "expiry_date": rec.get("expiry_date"),
                "amount": rec.get("amount"),
            }))

        log_info(f"Total records after deduplication: {len(valid_records)}")
        return valid_records


    # ---------------- SUBMISSION ---------------- #
    def submit(
        self,
        batch_id,
        cleaned_items,
        candidate_name=CANDIDATE_NAME,
        retries=RETRIES,
        backoff=1,
    ):
        url = f"{self.base_url}/api/submit"
        headers = {
            "X-Candidate-Id": self.candidate_id,
            "Content-Type": "application/json",
        }

        safe_items = []
        for item in cleaned_items:
            safe_items.append(
                {
                    "doc_id": item["doc_id"],
                    "type": item.get("type"),
                    "counterparty": item.get("counterparty"),
                    "project": item.get("project"),
                    "expiry_date": item.get("expiry_date"),
                    "amount": item.get("amount"),
                }
            )

        payload = {
            "candidate_name": candidate_name,
            "batch_id": str(batch_id),
            "cleaned_items": safe_items,
        }

        log_info(
            f"Submitting {len(safe_items)} cleaned records for batch {batch_id}"
        )
        print("HEADER", headers)
        print("payload", payload)
        for attempt in range(retries):
            try:
                response = requests.post(
                    url, headers=headers, json=payload, timeout=5
                )
                response.raise_for_status()
                log_info(f"Submission successful on attempt {attempt + 1}")
                return response.json()
            except requests.RequestException as e:
                log_warning(
                    f"Submission attempt {attempt + 1} failed: {e}"
                )
                time.sleep(backoff * (2 ** attempt))

        log_error(
            f"Failed to submit cleaned records for batch {batch_id} after {retries} attempts"
        )
        return None
