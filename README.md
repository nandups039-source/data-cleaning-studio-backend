# Lumicore Data Cleaning Challenge - Backend

A Django REST API application for fetching, normalizing, and cleaning data from the Lumicore API.

## Features
# Lumicore Data Cleaning Studio — Backend

A lightweight Django REST backend that fetches raw document records from the Lumicore API, normalizes and deduplicates them for human review, then validates and submits cleaned records back to Lumicore.

**Status:** Minimal production-like implementation for the Lumicore data cleaning challenge.

**Contents:**
- Project overview
- Setup and environment
- API reference (endpoints, parameters, examples)
- Internal behavior summary
- Development & testing

---

**Overview**

This service provides three primary endpoints under the `/documents/` prefix:
- `GET /documents/fetch-raw/` — fetch a batch of raw records from Lumicore
- `POST /documents/fetch-clean/` — normalize and deduplicate edited raw records for UI display
- `POST /documents/submit-clean/` — validate cleaned records and submit them to Lumicore

All responses use a consistent JSON wrapper:
- `hasError` (bool)
- `errorCode` (int)
- `message` (string)
- `data` (object)

---

**Tech stack**

- Python (3.8+ recommended)
- Django 6.x
- Django REST Framework
- SQLite (default dev DB)

---

**Quick setup**

1. Clone the repository and enter it:

```bash
git clone <repo-url>
cd data-cleaning-studio-BE
```

2. Create and activate a virtual environment (Windows example):

```powershell
python -m venv venv
venv\\Scripts\\Activate.ps1    # or use venv\\Scripts\\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` (or set env vars) in the project root. Required variables:

```
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
LUMICORE_BASE_URL=https://lumicore.example.com
X_CANDIDATE_ID=expected-candidate-id
```

Notes:
- The settings expect `DJANGO_SECRET_KEY`, not `SECRET_KEY`.
- `LUMICORE_BASE_URL` should be the base URL of the external Lumicore API used by this service.

5. Run migrations and (optionally) create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Start the development server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` for Django admin (if you created a superuser).

---

**Authentication / Candidate validation**

- Requests to endpoints under `/documents/` must include the `X-Candidate-Id` header matching the `X_CANDIDATE_ID` configured in settings. The custom middleware `CandidateValidationMiddleware` enforces this and will return a JSON error response on failure.
- DRF `BasicAuthentication` is enabled by default in settings; adjust `REST_FRAMEWORK` as needed.

---

**API Reference**

Base path: `http://<host>:<port>/documents/`

1) Fetch raw

- URL: `GET /documents/fetch-raw/`
- Query params:
   - `batch` (int, optional) — batch number to fetch (default: `1`).
- Headers:
   - `X-Candidate-Id`: required
- Success response (200):

```json
{
   "hasError": false,
   "errorCode": -1,
   "message": "Success",
   "data": {
      "batchId": "<batch_id>",
      "records": [ ... raw records as received from Lumicore ... ]
   }
}
```

- Failure: returns `hasError: true` with `errorCode` and `message`.

2) Clean (normalize & deduplicate)

- URL: `POST /documents/fetch-clean/`
- Body (JSON):

```json
{
   "batchId": "string",
   "records": [ { /* raw record objects */ }, ... ]
}
```

- Headers:
   - `X-Candidate-Id`: required
- Behavior:
   - Normalizes incoming raw records to a stable schema
   - Parses dates (several formats supported), amounts (stripped of currency), and maps multiple source keys to canonical fields
   - Deduplicates by `doc_id` and returns camelCase keys ready for UI

- Success response (200):

```json
{
   "hasError": false,
   "errorCode": -1,
   "message": "Success",
   "data": {
      "batchId": "<batchId>",
      "cleanedItems": [
         {
            "docId": "...",
            "type": "...",
            "counterparty": "...",
            "project": "...",
            "expiryDate": "YYYY-MM-DD",
            "amount": 123.45
         }
      ]
   }
}
```

3) Submit cleaned records

- URL: `POST /documents/submit-clean/`
- Body (JSON):

```json
{
   "batchId": "string",
   "cleanedItems": [
      {
         "docId": "...",
         "type": "...",
         "counterparty": "...",
         "project": "...",
         "expiryDate": "YYYY-MM-DD",
         "amount": 123.45
      }
   ]
}
```

- Headers:
   - `X-Candidate-Id`: required
- Behavior:
   - Converts incoming camelCase keys to snake_case for validation
   - Validates each record against `DocumentSerializer` which requires: `doc_id`, `type`, `counterparty`, `project`, `expiry_date` (date), and `amount` (float)
   - If any records fail validation, responds with `hasError: true` and a `data.invalid_records` array describing failures
   - On successful validation, forwards cleaned records to Lumicore `POST /api/submit` (configured by `LUMICORE_BASE_URL`) and returns the external API response

- Validation failure example (400):

```json
{
   "hasError": true,
   "errorCode": 1004,
   "message": "Some records are invalid",
   "data": {
      "invalid_records": [
         { "index": 1, "doc_id": "ABC123", "errors": { "expiry_date": ["Expiry Date is invalid."] } }
      ]
   }
}
```

---

**Internal behavior summary**

- `document_processor.services.DocumentUtils` implements core business logic:
   - `fetch(batch)`: GETs `LUMICORE_BASE_URL/api/data?batch=<n>` with `X-Candidate-Id` header, retry/backoff logic
   - `normalize(raw_records)`: maps multiple possible input keys to canonical fields using `FIELD_MAP`; parses dates and amounts
   - `validate_and_deduplicate(normalized_records)`: removes duplicates by `doc_id`, drops records missing `doc_id`, and returns camelCase payloads
   - `submit(batch_id, cleaned_items)`: POSTs cleaned data to `LUMICORE_BASE_URL/api/submit` with retries/backoff

- `document_processor.serializers.DocumentSerializer` enforces required fields for final submission and triggers errors returned to the client.

- The app uses `utils.responses.APIResponse` to standardize success/failure payload shapes.

---

**Error codes** (used in code)

- `1001` — fetch failed / server error while fetching
- `1002` — missing batch or records / candidate header issues (middleware may use other codes)
- `1003` — missing batch or cleaned_items on submit
- `1004` — validation failed for some records
- `1005` — submission to Lumicore failed after retries

(Refer to view code for exact places these are raised.)

---

**Development & testing**

- Run tests:

```bash
python manage.py test
```

- Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

- To enable debug logging and view logs created under `/logs/`, set `DEBUG=True` and check `logs/info.log` and `logs/error.log`.

---

**Extending / Notes**

- The field mapping (`FIELD_MAP`) and date formats (`DATE_FORMATS`) live in `document_processor/services/constants.py` and are easy to extend to support additional source formats.
- The candidate header is enforced only for `/documents/` routes by `core.middleware.CandidateValidationMiddleware`.
- For production usage, ensure `DEBUG=False`, set proper `ALLOWED_HOSTS`, and secure environment variables.

---

**Deployment**
- Render config for deployment

---

Project root: see `manage.py` and app code in `document_processor/`.
