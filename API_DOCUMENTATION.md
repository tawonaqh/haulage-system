# API Documentation

Base URL: `http://localhost:8000/api/v1`

Interactive documentation is also available at:

- `http://localhost:8000/docs`

## Authentication

### Register

- Method: `POST`
- Path: `/auth/register`
- Body:

```json
{
  "username": "admin",
  "password": "password123"
}
```

### Login

- Method: `POST`
- Path: `/auth/login`
- Content type: `application/x-www-form-urlencoded`
- Body:

```text
username=admin&password=password123
```

### Authenticated Requests

Include the bearer token in the header:

```text
Authorization: Bearer <token>
```

## Trucks

### Create Truck

- Method: `POST`
- Path: `/trucks`

```json
{
  "registration_number": "ABX1234",
  "capacity": 30,
  "status": "available"
}
```

### List Trucks

- Method: `GET`
- Path: `/trucks?limit=10&offset=0`

### Get Truck

- Method: `GET`
- Path: `/trucks/{truck_id}`

### Update Truck

- Method: `PUT`
- Path: `/trucks/{truck_id}`

### Delete Truck

- Method: `DELETE`
- Path: `/trucks/{truck_id}`

## Drivers

### Create Driver

- Method: `POST`
- Path: `/drivers`

```json
{
  "name": "Blessing Ncube",
  "license_number": "LIC-1001",
  "phone_number": "0771234567"
}
```

### List Drivers

- Method: `GET`
- Path: `/drivers?limit=10&offset=0`

### Get Driver

- Method: `GET`
- Path: `/drivers/{driver_id}`

### Update Driver

- Method: `PUT`
- Path: `/drivers/{driver_id}`

### Delete Driver

- Method: `DELETE`
- Path: `/drivers/{driver_id}`

## Jobs

### Create Job

- Method: `POST`
- Path: `/jobs`

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

### List Jobs

- Method: `GET`
- Path: `/jobs?limit=10&offset=0`

### Get Job

- Method: `GET`
- Path: `/jobs/{job_id}`

### Update Job

- Method: `PUT`
- Path: `/jobs/{job_id}`

### Delete Job

- Method: `DELETE`
- Path: `/jobs/{job_id}`

## Business Rule Responses

- `400 Bad Request` when assigning a truck that is `in_transit` or `maintenance`
- `400 Bad Request` when assigning a driver who already has an active job
- `400 Bad Request` when deleting an active job, truck, or driver still tied to active work
- `404 Not Found` when referenced trucks, drivers, or jobs do not exist
