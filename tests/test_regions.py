"""
Tests for /regions CRUD endpoints.
"""

import pytest

SAMPLE_REGION = {
    "name": "Test Region",
    "ons_code": "TLX",
    "median_salary": 32000.0,
    "median_rent": 750.0,
    "year": 2023,
}


class TestGetRegions:
    def test_get_regions_empty(self, client):
        response = client.get("/regions")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_regions_returns_created_region(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.get("/regions")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Test Region"


class TestGetSingleRegion:
    def test_get_region_by_id(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.get(f"/regions/{region_id}")
        assert response.status_code == 200
        assert response.json()["ons_code"] == "TLX"

    def test_get_region_not_found(self, client):
        response = client.get("/regions/nonexistent")
        assert response.status_code == 404


class TestCreateRegion:
    def test_create_region_requires_auth(self, client):
        response = client.post("/regions", json=SAMPLE_REGION)
        assert response.status_code == 401

    def test_create_region_success(self, client, auth_headers):
        response = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Region"
        assert data["median_salary"] == 32000.0
        assert "id" in data

    def test_create_duplicate_region_returns_conflict(self, client, auth_headers):
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        response = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        assert response.status_code == 409


class TestUpdateRegion:
    def test_update_region_success(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.put(
            f"/regions/{region_id}",
            json={"median_salary": 35000.0},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["median_salary"] == 35000.0

    def test_update_region_not_found(self, client, auth_headers):
        response = client.put("/regions/bad-id", json={"median_salary": 35000.0}, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteRegion:
    def test_delete_region_success(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.delete(f"/regions/{region_id}", headers=auth_headers)
        assert response.status_code == 204
        assert client.get(f"/regions/{region_id}").status_code == 404

    def test_delete_region_requires_auth(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.delete(f"/regions/{region_id}")
        assert response.status_code == 401
