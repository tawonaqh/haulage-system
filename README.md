# Haulage Truck Management System

Technical assessment solution for Marytechenock Solutions. The project provides a REST API for managing trucks, drivers, and delivery jobs with business-rule validation, JWT authentication, pagination, logging, Docker support, and unit tests.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker and Docker Compose
- Pytest

## Features

- Truck CRUD
- Driver CRUD
- Delivery job CRUD
- JWT authentication
- Pagination on list endpoints
- Application logging
- Business rules for truck and driver assignment
- OpenAPI documentation via Swagger UI

## Business Rules Implemented

- Trucks cannot be assigned when their status is `in_transit` or `maintenance`
- Drivers cannot be assigned to more than one active job
- Active job states (`assigned`, `in_transit`) automatically set the linked truck to `in_transit`
- Completed, cancelled, or removed jobs release the linked truck back to `available` unless the truck is under maintenance

## Run With Docker

1. Copy `.env.example` to `.env` if you want to change defaults.
2. Start the stack:

```bash
docker-compose up --build
```

3. Open:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## Authentication Flow

1. Register a user:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

2. Or log in using form data:

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=password123
```

3. Use the returned bearer token for protected endpoints.

## API Summary

### Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Trucks

- `GET /api/v1/trucks?limit=10&offset=0`
- `POST /api/v1/trucks`
- `GET /api/v1/trucks/{truck_id}`
- `PUT /api/v1/trucks/{truck_id}`
- `DELETE /api/v1/trucks/{truck_id}`

### Drivers

- `GET /api/v1/drivers?limit=10&offset=0`
- `POST /api/v1/drivers`
- `GET /api/v1/drivers/{driver_id}`
- `PUT /api/v1/drivers/{driver_id}`
- `DELETE /api/v1/drivers/{driver_id}`

### Jobs

- `GET /api/v1/jobs?limit=10&offset=0`
- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`
- `PUT /api/v1/jobs/{job_id}`
- `DELETE /api/v1/jobs/{job_id}`

## Example Job Payload

```json
{
  "pickup_location": "Harare",
  "delivery_location": "Bulawayo",
  "cargo_description": "Construction materials",
  "status": "assigned",
  "assigned_truck_id": 1,
  "assigned_driver_id": 1
}
```

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run Tests

```bash
pytest
```

## Notes

- Database tables are created automatically on startup for simplicity in an assessment setting.
- The default database connection in Docker points to the `db` service from `docker-compose.yml`.
