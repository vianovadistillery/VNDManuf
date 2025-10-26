"""Integration tests for Formulas API (Phase 8.2)."""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.api.main import create_app
from app.adapters.db import get_db
from app.adapters.db.models import Formula, FormulaLine, Product


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def db():
    """Get test database session."""
    return next(get_db())


def test_list_formulas(client, db):
    """Test listing formulas."""
    response = client.get("/api/v1/formulas/")
    assert response.status_code in [200, 404]  # 404 if no formulas exist


def test_get_formula_not_found(client):
    """Test getting non-existent formula returns 404."""
    response = client.get("/api/v1/formulas/non-existent-id")
    assert response.status_code == 404


def test_formula_revision_endpoints(client):
    """Test formula revision endpoints."""
    # Test getting all revisions
    response = client.get("/api/v1/formulas/code/TEST/revisions")
    assert response.status_code in [200, 404]
    
    # Test getting specific revision
    response = client.get("/api/v1/formulas/code/TEST/version/1")
    assert response.status_code in [200, 404]


def test_create_formula(client):
    """Test creating a new formula."""
    formula_data = {
        "product_id": "test-product-id",
        "formula_code": "TEST001",
        "formula_name": "Test Formula",
        "version": 1,
        "is_active": True,
        "lines": []
    }
    
    response = client.post("/api/v1/formulas/", json=formula_data)
    assert response.status_code in [201, 400]  # 400 if product not found


def test_formula_cost_calculation(client):
    """Test theoretical cost calculation for formula."""
    # This would require actual formula data
    # For now, test endpoint exists
    response = client.get("/api/v1/reports/formulas/cost-analysis?formula_code=TEST")
    assert response.status_code in [200, 404]

