# nutikas-elektrivork-back

## Requirements

- Python 3.11+
- MongoDB 6+

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment

Create a `.env` file in the project root with the required values:

```
mongo_username=admin
mongo_password=change-me
mongo_host=localhost
mongo_port=27017
mongo_db=app_db

jwt_secret_key=change-me
jwt_algorithm=HS256
access_token_expire_minutes=60
```

## Run

From the project root:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternatively:

```bash
python -m app.main
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json