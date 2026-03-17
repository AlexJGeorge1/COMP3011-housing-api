"""
Tests for the /insights AI-generated intelligence endpoint.

The insights endpoint uses percentile_cont (PostgreSQL-only) for median
house prices, so happy-path tests are skipped on SQLite.  Region-not-found
tests work on any backend since they return before querying listings.
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


class TestInsightsRegionNotFound:
    def test_insights_region_not_found(self, client):
        response = client.get("/insights/NonexistentRegion")
        assert response.status_code == 404

    def test_insights_region_not_found_message(self, client):
        response = client.get("/insights/Atlantis")
        assert "not found" in response.json()["detail"].lower()

    def test_insights_region_not_found_suggests_regions_endpoint(self, client):
        response = client.get("/insights/Nowhere")
        assert "/regions" in response.json()["detail"]


class TestInsightsNoListingData:
    @postgres_only
    def test_insights_no_data_returns_fallback(self, client, auth_headers):
        """Region exists but has no listing data — returns a fallback insight."""
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/insights/North West")
        assert response.status_code == 200
        data = response.json()
        assert data["powered_by"] == "fallback"
        assert "no transaction data" in data["insight"].lower()

    @postgres_only
    def test_insights_no_data_still_includes_region(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/insights/North West")
        assert response.json()["region"] == "North West"

    @postgres_only
    def test_insights_no_data_includes_data_used(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/insights/North West")
        data_used = response.json()["data_used"]
        assert "median_salary" in data_used
        assert "median_rent_monthly" in data_used
        assert "transaction_count" in data_used
        assert data_used["median_house_price"] is None


class TestInsightsResponseStructure:
    @postgres_only
    def test_insights_response_has_all_fields(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/insights/North West")
        assert response.status_code == 200
        data = response.json()
        assert "region" in data
        assert "insight" in data
        assert "data_used" in data
        assert "powered_by" in data

    @postgres_only
    def test_insights_data_used_has_salary_from_region(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/insights/North West")
        data_used = response.json()["data_used"]
        assert data_used["median_salary"] == SAMPLE_REGION["median_salary"]
        assert data_used["median_rent_monthly"] == SAMPLE_REGION["median_rent"]

    @postgres_only
    def test_insights_case_insensitive_region(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/insights/north west")
        assert response.status_code == 200
        assert response.json()["region"] == "North West"
