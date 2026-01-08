# Lumicore Data Cleaning Challenge - Backend

A Django REST API application for fetching, normalizing, and cleaning data from the Lumicore API.

## Features

- **Fetch Raw Data**: Retrieve records from the Lumicore API
- **Data Cleaning**: Normalize and deduplicate records
- **Document Processing**: Comprehensive document processing pipeline
- **Logging**: Structured logging with separate info and error logs
- **RESTful API**: Built with Django REST Framework

## Tech Stack

- **Django** 6.0.1
- **Django REST Framework** 3.16.1
- **Python** 3.14
- **SQLite** (default database)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file** in the root directory:
   ```env
   DEBUG=True
   LUMICORE_BASE_URL=your_lumicore_api_url
   X_CANDIDATE_ID=your_candidate_id
   SECRET_KEY=your-secret-key-here
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Fetch Raw Data
- **Endpoint**: `GET /api/fetch-raw/`
- **Description**: Fetches raw records from the Lumicore API
- **Response**: Returns batch ID and raw records

### Clean Data
- **Endpoint**: `POST /api/clean-data/`
- **Description**: Normalizes and deduplicates records
- **Request Body**:
  ```json
  {
    "batchId": "string",
    "records": [...]
  }
  ```
- **Response**: Returns cleaned and deduplicated records

## Project Structure

```
backend/
├── core/                    # Main Django project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── middleware.py       # Custom middleware
├── document_processor/      # Main application
│   ├── views.py            # API views
│   ├── models.py           # Database models
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # App URL configuration
│   └── services/           # Business logic services
├── utils/                   # Utility modules
│   ├── exceptions.py       # Custom exceptions
│   ├── helper.py           # Helper functions
│   ├── logger.py           # Logging utilities
│   └── responses.py        # API response utilities
├── logs/                    # Application logs
├── manage.py               # Django management script
└── requirements.txt        # Python dependencies
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEBUG` | Enable/disable debug mode | Yes |
| `LUMICORE_BASE_URL` | Base URL for Lumicore API | Yes |
| `X_CANDIDATE_ID` | Candidate ID for API authentication | Yes |
| `SECRET_KEY` | Django secret key | Yes |

## Logging

The application logs to two files in the `logs/` directory:
- `info.log`: Information and warning messages
- `error.log`: Error and critical messages

Logs are also output to the console during development.

## Development

### Running Tests
```bash
python manage.py test
```

### Making Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Django Admin
1. Create a superuser (if not already created)
   ```bash
   python manage.py createsuperuser
   ```
2. Start the server and navigate to `http://127.0.0.1:8000/admin/`

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass
4. Submit a pull request

## License

This project is part of the Lumicore Data Cleaning Challenge.
