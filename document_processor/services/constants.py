# document_processor/utils/constants.py


CANDIDATE_NAME = "Nandu P S"

DEFAULT_BATCH = 1
RETRIES = 3
FIELD_MAP = {
    "doc_id": ["id", "documentId", "ref", "document_ref", "doc_number", "doc_id"],
    "type": ["docType", "category", "document_type", "doc_category", "type"],
    "counterparty": ["vendorName", "supplier", "partyA", "vendor", "party_name"],
    "project": ["projectName", "project_name", "proj", "meta.project", "project"],
    "expiry_date": ["expiry", "expiryDate", "end_date", "valid_till", "expires_on", "expiration"],
    "amount": ["value", "contractValue", "amount_aed", "total", "contract_amount", "amount"]
}

DATE_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%b %d %Y", "%d %b %Y",
    "%Y%m%d", "%d-%m-%Y"
]

