def test_driver_cannot_have_multiple_active_jobs(client, auth_headers):
    truck_one = client.post(
        "/api/v1/trucks",
        json={"registration_number": "ABC123", "capacity": 20, "status": "available"},
        headers=auth_headers,
    ).json()
    truck_two = client.post(
        "/api/v1/trucks",
        json={"registration_number": "XYZ789", "capacity": 25, "status": "available"},
        headers=auth_headers,
    ).json()
    driver = client.post(
        "/api/v1/drivers",
        json={"name": "John Doe", "license_number": "LIC-1", "phone_number": "0770000000"},
        headers=auth_headers,
    ).json()

    first_job = client.post(
        "/api/v1/jobs",
        json={
            "pickup_location": "Harare",
            "delivery_location": "Bulawayo",
            "cargo_description": "Cement",
            "status": "assigned",
            "assigned_truck_id": truck_one["id"],
            "assigned_driver_id": driver["id"],
        },
        headers=auth_headers,
    )
    assert first_job.status_code == 201

    second_job = client.post(
        "/api/v1/jobs",
        json={
            "pickup_location": "Gweru",
            "delivery_location": "Mutare",
            "cargo_description": "Steel",
            "status": "assigned",
            "assigned_truck_id": truck_two["id"],
            "assigned_driver_id": driver["id"],
        },
        headers=auth_headers,
    )
    assert second_job.status_code == 400
    assert second_job.json()["detail"] == "Driver already has an active job"


def test_truck_unavailable_when_in_transit(client, auth_headers):
    truck = client.post(
        "/api/v1/trucks",
        json={"registration_number": "BHZ001", "capacity": 18, "status": "in_transit"},
        headers=auth_headers,
    ).json()
    driver = client.post(
        "/api/v1/drivers",
        json={"name": "Jane Doe", "license_number": "LIC-2", "phone_number": "0771111111"},
        headers=auth_headers,
    ).json()

    response = client.post(
        "/api/v1/jobs",
        json={
            "pickup_location": "Harare",
            "delivery_location": "Masvingo",
            "cargo_description": "Fuel",
            "status": "assigned",
            "assigned_truck_id": truck["id"],
            "assigned_driver_id": driver["id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Truck is not available for assignment"


def test_completing_job_releases_truck(client, auth_headers):
    truck = client.post(
        "/api/v1/trucks",
        json={"registration_number": "REL001", "capacity": 30, "status": "available"},
        headers=auth_headers,
    ).json()
    driver = client.post(
        "/api/v1/drivers",
        json={"name": "Tariro Moyo", "license_number": "LIC-3", "phone_number": "0772222222"},
        headers=auth_headers,
    ).json()
    job = client.post(
        "/api/v1/jobs",
        json={
            "pickup_location": "Kwekwe",
            "delivery_location": "Chitungwiza",
            "cargo_description": "Tiles",
            "status": "in_transit",
            "assigned_truck_id": truck["id"],
            "assigned_driver_id": driver["id"],
        },
        headers=auth_headers,
    ).json()

    update_response = client.put(
        f"/api/v1/jobs/{job['id']}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200

    truck_response = client.get(f"/api/v1/trucks/{truck['id']}", headers=auth_headers)
    assert truck_response.status_code == 200
    assert truck_response.json()["status"] == "available"
