"""
Extended tests for analytics endpoints: /rent-to-buy, /affordability, /trends.

Focuses on query-parameter validation and error messages not covered by the
original test_analytics.py.  Does NOT modify existing tests.
"""

import pytest
from tests.conftest import TEST_DATABASE_URL

postgres_only = pytest.mark.skipif(
    "sqlite" in TEST_DATABASE_URL,
    reason="Requires PostgreSQL (percentile_cont not supported by SQLite)",
)

SAMPLE_REGION = {
    "name": "North West",
    "ons_code": "TLD",
    "median_salary": 31694.0,
    "median_rent": 699.0,
    "year": 2023,
}


# ── Rent-to-buy parameter validation ─────────────────────────────────────────
# FastAPI validates Query constraints before the function body runs, so these
# return 422 without hitting the database at all.

class TestRentToBuyParamValidation:
    def test_deposit_pct_below_minimum(self, client):
        response = client.get("/rent-to-buy/AnyRegion?deposit_pct=0.01")
        assert response.status_code == 422

    def test_deposit_pct_above_maximum(self, client):
        response = client.get("/rent-to-buy/AnyRegion?deposit_pct=0.50")
        assert response.status_code == 422

    def test_interest_rate_below_minimum(self, client):
        response = client.get("/rent-to-buy/AnyRegion?interest_rate=0.01")
        assert response.status_code == 422

    def test_interest_rate_above_maximum(self, client):
        response = client.get("/rent-to-buy/AnyRegion?interest_rate=20.0")
        assert response.status_code == 422

    def test_term_years_below_minimum(self, client):
        response = client.get("/rent-to-buy/AnyRegion?term_years=2")
        assert response.status_code == 422

    def test_term_years_above_maximum(self, client):
        response = client.get("/rent-to-buy/AnyRegion?term_years=40")
        assert response.status_code == 422

    def test_defaults_accepted(self, client):
        """Default param values don't cause validation errors (returns 404 for missing region)."""
        response = client.get("/rent-to-buy/NonexistentRegion")
        assert response.status_code == 404

    def test_valid_custom_params_accepted(self, client):
        """Valid non-default params pass validation (returns 404 for missing region)."""
        response = client.get(
            "/rent-to-buy/NonexistentRegion?deposit_pct=0.20&interest_rate=5.5&term_years=30"
        )
        assert response.status_code == 404

    def test_boundary_deposit_pct_min(self, client):
        """Exact minimum (0.05) is accepted."""
        response = client.get("/rent-to-buy/NonexistentRegion?deposit_pct=0.05")
        assert response.status_code == 404  # past validation, into region lookup

    def test_boundary_deposit_pct_max(self, client):
        """Exact maximum (0.40) is accepted."""
        response = client.get("/rent-to-buy/NonexistentRegion?deposit_pct=0.40")
        assert response.status_code == 404

    def test_boundary_term_years_min(self, client):
        response = client.get("/rent-to-buy/NonexistentRegion?term_years=5")
        assert response.status_code == 404

    def test_boundary_term_years_max(self, client):
        response = client.get("/rent-to-buy/NonexistentRegion?term_years=35")
        assert response.status_code == 404


# ── Rent-to-buy error messages ────────────────────────────────────────────────

class TestRentToBuyErrors:
    def test_region_not_found_suggests_regions(self, client):
        response = client.get("/rent-to-buy/Nowhere")
        assert "/regions" in response.json()["detail"]

    @postgres_only
    def test_no_data_message(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/rent-to-buy/North West")
        assert response.status_code == 404
        assert "no listing data" in response.json()["detail"].lower()


# ── Affordability error messages ──────────────────────────────────────────────

class TestAffordabilityErrors:
    def test_region_not_found_suggests_regions(self, client):
        response = client.get("/affordability/Nowhere")
        assert "/regions" in response.json()["detail"]

    @postgres_only
    def test_no_data_message(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/affordability/North West")
        assert response.status_code == 404
        assert "no listing data" in response.json()["detail"].lower()


# ── Trends error messages ─────────────────────────────────────────────────────

class TestTrendsErrors:
    def test_region_not_found_suggests_regions(self, client):
        response = client.get("/trends/Nowhere")
        assert "/regions" in response.json()["detail"]

    @postgres_only
    def test_no_data_message(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/trends/North West")
        assert response.status_code == 404
        assert "no listing data" in response.json()["detail"].lower()


# ── Health check extended ─────────────────────────────────────────────────────

class TestHealthCheckExtended:
    def test_health_includes_version(self, client):
        response = client.get("/health")
        assert "version" in response.json()

    def test_health_version_format(self, client):
        version = client.get("/health").json()["version"]
        parts = version.split(".")
        assert len(parts) == 3
