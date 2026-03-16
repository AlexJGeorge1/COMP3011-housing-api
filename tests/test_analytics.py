"""
Tests for analytics endpoints: /affordability, /trends, /rent-to-buy.
Note: tests for the 'no data' case are marked postgres_only because
SQLite (used in unit tests) does not support the percentile_cont aggregate.
Those tests can be run against the full Docker stack.
"""

import pytest

SAMPLE_REGION = {
    "name": "North West",
    "ons_code": "TLD",
    "median_salary": 31694.0,
    "median_rent": 699.0,
    "year": 2023,
}

# Mark tests that require PostgreSQL-specific SQL (percentile_cont)
postgres_only = pytest.mark.skip(reason="Requires PostgreSQL (percentile_cont not supported by SQLite)")


class TestAffordabilityEndpoint:
    def test_affordability_region_not_found(self, client):
        response = client.get("/affordability/NonexistentRegion")
        assert response.status_code == 404

    def test_affordability_region_not_found_message(self, client):
        response = client.get("/affordability/Atlantis")
        assert "not found" in response.json()["detail"].lower()

    @postgres_only
    def test_affordability_no_data_returns_404(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/affordability/North West")
        assert response.status_code == 404


class TestTrendsEndpoint:
    def test_trends_region_not_found(self, client):
        response = client.get("/trends/NonexistentRegion")
        assert response.status_code == 404

    @postgres_only
    def test_trends_no_data_returns_404(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/trends/North West")
        assert response.status_code == 404


class TestRentToBuyEndpoint:
    def test_rent_to_buy_region_not_found(self, client):
        response = client.get("/rent-to-buy/NonexistentRegion")
        assert response.status_code == 404

    @postgres_only
    def test_rent_to_buy_no_data_returns_404(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/rent-to-buy/North West")
        assert response.status_code == 404


class TestHealthCheck:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_contains_status_ok(self, client):
        response = client.get("/health")
        assert response.json()["status"] == "ok"

