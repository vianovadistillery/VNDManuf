"""Integration tests for Excise Rates API CRUD operations."""

import pytest
from fastapi.testclient import TestClient

from app.adapters.db import get_db
from app.api.main import create_app


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_excise_rate(client):
    """Test creating a new excise rate."""
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "120.50",
        "description": "Standard excise rate",
        "is_active": True,
    }

    response = client.post("/api/v1/excise-rates/", json=data)
    assert response.status_code == 201

    result = response.json()
    assert result["rate_per_l_abv"] == "120.50"
    assert result["date_active_from"] == "2024-01-01T00:00:00"
    assert result["description"] == "Standard excise rate"
    assert result["is_active"] is True
    assert "id" in result
    assert "created_at" in result
    assert "updated_at" in result


def test_create_excise_rate_duplicate_date(client):
    """Test creating excise rate with duplicate date_active_from fails."""
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "120.50",
        "description": "First rate",
    }

    response = client.post("/api/v1/excise-rates/", json=data)
    assert response.status_code == 201

    # Try to create another with same date
    response = client.post("/api/v1/excise-rates/", json=data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_excise_rate_invalid_rate(client):
    """Test creating excise rate with invalid rate fails."""
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "0",  # Must be greater than 0
        "description": "Invalid rate",
    }

    response = client.post("/api/v1/excise-rates/", json=data)
    assert response.status_code == 422


def test_list_excise_rates(client):
    """Test listing excise rates."""
    # Create some test rates
    rates = [
        {
            "date_active_from": f"2024-{i:02d}-01T00:00:00",
            "rate_per_l_abv": str(100 + i),
            "description": f"Rate {i}",
        }
        for i in range(1, 4)
    ]

    for rate_data in rates:
        response = client.post("/api/v1/excise-rates/", json=rate_data)
        assert response.status_code == 201

    # List all rates
    response = client.get("/api/v1/excise-rates/")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 3
    # Should be ordered by date descending (newest first)
    assert results[0]["date_active_from"] == "2024-03-01T00:00:00"
    assert results[2]["date_active_from"] == "2024-01-01T00:00:00"


def test_list_excise_rates_with_filtering(client):
    """Test listing excise rates with date filtering."""
    # Create rates at different dates
    rates = [
        {"date_active_from": "2024-01-01T00:00:00", "rate_per_l_abv": "100.00"},
        {"date_active_from": "2024-06-01T00:00:00", "rate_per_l_abv": "110.00"},
        {"date_active_from": "2024-12-01T00:00:00", "rate_per_l_abv": "120.00"},
    ]

    for rate_data in rates:
        response = client.post("/api/v1/excise-rates/", json=rate_data)
        assert response.status_code == 201

    # Filter by date
    response = client.get("/api/v1/excise-rates/?as_of_date=2024-07-01T00:00:00")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 2  # Should get Jan and June rates only
    assert all(r["date_active_from"] <= "2024-07-01T00:00:00" for r in results)


def test_list_excise_rates_with_pagination(client):
    """Test listing excise rates with pagination."""
    # Create more rates than limit
    rates = [
        {
            "date_active_from": f"2024-{i:02d}-01T00:00:00",
            "rate_per_l_abv": str(100 + i),
        }
        for i in range(1, 11)
    ]

    for rate_data in rates:
        response = client.post("/api/v1/excise-rates/", json=rate_data)
        assert response.status_code == 201

    # Get first page
    response = client.get("/api/v1/excise-rates/?limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get second page
    response = client.get("/api/v1/excise-rates/?skip=5&limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_excise_rate_by_id(client):
    """Test getting excise rate by ID."""
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "120.50",
        "description": "Test rate",
    }

    create_response = client.post("/api/v1/excise-rates/", json=data)
    assert create_response.status_code == 201
    rate_id = create_response.json()["id"]

    # Get by ID
    response = client.get(f"/api/v1/excise-rates/{rate_id}")
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == rate_id
    assert result["rate_per_l_abv"] == "120.50"


def test_get_excise_rate_not_found(client):
    """Test getting non-existent excise rate returns 404."""
    response = client.get("/api/v1/excise-rates/non-existent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_current_excise_rate(client):
    """Test getting current excise rate."""
    # Create rates at different dates
    rates = [
        {"date_active_from": "2024-01-01T00:00:00", "rate_per_l_abv": "100.00"},
        {"date_active_from": "2024-06-01T00:00:00", "rate_per_l_abv": "110.00"},
        {"date_active_from": "2024-12-01T00:00:00", "rate_per_l_abv": "120.00"},
    ]

    for rate_data in rates:
        response = client.post("/api/v1/excise-rates/", json=rate_data)
        assert response.status_code == 201

    # Get current as of date
    response = client.get("/api/v1/excise-rates/current?as_of_date=2024-07-01T00:00:00")
    assert response.status_code == 200

    result = response.json()
    assert result["rate_per_l_abv"] == "110.00"  # Should be the June rate


def test_get_current_excise_rate_not_found(client):
    """Test getting current excise rate when none exists returns 404."""
    response = client.get("/api/v1/excise-rates/current?as_of_date=2023-01-01T00:00:00")
    assert response.status_code == 404
    assert "No excise rate found" in response.json()["detail"]


def test_update_excise_rate(client):
    """Test updating an excise rate."""
    # Create a rate
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "120.50",
        "description": "Original description",
        "is_active": True,
    }

    create_response = client.post("/api/v1/excise-rates/", json=data)
    assert create_response.status_code == 201
    rate_id = create_response.json()["id"]

    # Update the rate
    update_data = {
        "rate_per_l_abv": "125.00",
        "description": "Updated description",
        "is_active": False,
    }

    response = client.put(f"/api/v1/excise-rates/{rate_id}", json=update_data)
    assert response.status_code == 200

    result = response.json()
    assert result["rate_per_l_abv"] == "125.00"
    assert result["description"] == "Updated description"
    assert result["is_active"] is False
    # date_active_from should remain unchanged
    assert result["date_active_from"] == "2024-01-01T00:00:00"


def test_update_excise_rate_partial(client):
    """Test partial update of excise rate."""
    # Create a rate
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "120.50",
        "description": "Original description",
    }

    create_response = client.post("/api/v1/excise-rates/", json=data)
    assert create_response.status_code == 201
    rate_id = create_response.json()["id"]

    # Update only rate
    update_data = {"rate_per_l_abv": "125.00"}

    response = client.put(f"/api/v1/excise-rates/{rate_id}", json=update_data)
    assert response.status_code == 200

    result = response.json()
    assert result["rate_per_l_abv"] == "125.00"
    assert result["description"] == "Original description"  # Unchanged


def test_update_excise_rate_date_duplicate(client):
    """Test updating to duplicate date_active_from fails."""
    # Create two rates
    rate1_data = {"date_active_from": "2024-01-01T00:00:00", "rate_per_l_abv": "100.00"}
    rate2_data = {"date_active_from": "2024-06-01T00:00:00", "rate_per_l_abv": "110.00"}

    response1 = client.post("/api/v1/excise-rates/", json=rate1_data)
    response2 = client.post("/api/v1/excise-rates/", json=rate2_data)
    assert response1.status_code == 201
    assert response2.status_code == 201

    rate2_id = response2.json()["id"]

    # Try to update rate2 to have same date as rate1
    update_data = {"date_active_from": "2024-01-01T00:00:00"}
    response = client.put(f"/api/v1/excise-rates/{rate2_id}", json=update_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_update_excise_rate_not_found(client):
    """Test updating non-existent excise rate returns 404."""
    update_data = {"rate_per_l_abv": "125.00"}

    response = client.put("/api/v1/excise-rates/non-existent-id", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_excise_rate(client):
    """Test deleting an excise rate."""
    # Create a rate
    data = {
        "date_active_from": "2024-01-01T00:00:00",
        "rate_per_l_abv": "120.50",
        "description": "Test rate",
    }

    create_response = client.post("/api/v1/excise-rates/", json=data)
    assert create_response.status_code == 201
    rate_id = create_response.json()["id"]

    # Delete the rate
    response = client.delete(f"/api/v1/excise-rates/{rate_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/excise-rates/{rate_id}")
    assert get_response.status_code == 404


def test_delete_excise_rate_not_found(client):
    """Test deleting non-existent excise rate returns 404."""
    response = client.delete("/api/v1/excise-rates/non-existent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_excise_rate_crud_workflow(client):
    """Test complete CRUD workflow."""
    # Create multiple rates
    rates_data = [
        {
            "date_active_from": "2024-01-01T00:00:00",
            "rate_per_l_abv": "100.00",
            "description": "Q1 rate",
        },
        {
            "date_active_from": "2024-04-01T00:00:00",
            "rate_per_l_abv": "110.00",
            "description": "Q2 rate",
        },
        {
            "date_active_from": "2024-07-01T00:00:00",
            "rate_per_l_abv": "120.00",
            "description": "Q3 rate",
        },
    ]

    rate_ids = []
    for rate_data in rates_data:
        response = client.post("/api/v1/excise-rates/", json=rate_data)
        assert response.status_code == 201
        rate_ids.append(response.json()["id"])

    # List all rates
    response = client.get("/api/v1/excise-rates/")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # Update middle rate
    update_data = {"description": "Updated Q2 rate", "is_active": False}
    response = client.put(f"/api/v1/excise-rates/{rate_ids[1]}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated Q2 rate"
    assert response.json()["is_active"] is False

    # Get current as of different dates
    response = client.get("/api/v1/excise-rates/current?as_of_date=2024-05-01T00:00:00")
    assert response.status_code == 200
    assert response.json()["rate_per_l_abv"] == "110.00"

    # Delete first rate
    response = client.delete(f"/api/v1/excise-rates/{rate_ids[0]}")
    assert response.status_code == 204

    # Verify deletion
    response = client.get("/api/v1/excise-rates/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Verify can still get current
    response = client.get("/api/v1/excise-rates/current?as_of_date=2024-09-01T00:00:00")
    assert response.status_code == 200
    assert response.json()["rate_per_l_abv"] == "120.00"
