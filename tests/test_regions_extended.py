"""
Extended tests for /regions CRUD endpoints.

Covers edge cases not in test_regions.py.
Does NOT modify existing tests.
"""


SAMPLE_REGION = {
    "name": "Test Region",
    "ons_code": "TLX",
    "median_salary": 32000.0,
    "median_rent": 750.0,
    "year": 2023,
}


class TestDeleteRegionExtended:
    def test_delete_region_not_found(self, client, auth_headers):
        response = client.delete("/regions/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_region_not_found_message(self, client, auth_headers):
        response = client.delete("/regions/nonexistent-id", headers=auth_headers)
        assert "not found" in response.json()["detail"].lower()


class TestUpdateRegionExtended:
    def test_update_region_requires_auth(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.put(f"/regions/{region_id}", json={"median_salary": 35000.0})
        assert response.status_code == 401

    def test_update_preserves_unchanged_fields(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.put(
            f"/regions/{region_id}",
            json={"median_salary": 40000.0},
            headers=auth_headers,
        )
        data = response.json()
        assert data["median_salary"] == 40000.0
        assert data["name"] == SAMPLE_REGION["name"]
        assert data["ons_code"] == SAMPLE_REGION["ons_code"]
        assert data["median_rent"] == SAMPLE_REGION["median_rent"]

    def test_update_multiple_fields(self, client, auth_headers):
        create_resp = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        region_id = create_resp.json()["id"]
        response = client.put(
            f"/regions/{region_id}",
            json={"median_salary": 38000.0, "median_rent": 800.0},
            headers=auth_headers,
        )
        data = response.json()
        assert data["median_salary"] == 38000.0
        assert data["median_rent"] == 800.0


class TestCreateRegionExtended:
    def test_create_region_invalid_data(self, client, auth_headers):
        response = client.post("/regions", json={"name": "Only Name"}, headers=auth_headers)
        assert response.status_code == 422

    def test_create_region_id_is_uuid_length(self, client, auth_headers):
        response = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        assert len(response.json()["id"]) == 36

    def test_create_region_echoes_all_fields(self, client, auth_headers):
        response = client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        data = response.json()
        assert data["name"] == SAMPLE_REGION["name"]
        assert data["ons_code"] == SAMPLE_REGION["ons_code"]
        assert data["median_salary"] == SAMPLE_REGION["median_salary"]
        assert data["median_rent"] == SAMPLE_REGION["median_rent"]
        assert data["year"] == SAMPLE_REGION["year"]


class TestGetRegionsExtended:
    def test_get_region_not_found_message(self, client):
        response = client.get("/regions/does-not-exist")
        assert "not found" in response.json()["detail"].lower()

    def test_get_regions_returns_multiple(self, client, auth_headers):
        region2 = {**SAMPLE_REGION, "name": "Another Region", "ons_code": "TLY"}
        client.post("/regions", json=SAMPLE_REGION, headers=auth_headers)
        client.post("/regions", json=region2, headers=auth_headers)
        response = client.get("/regions")
        assert len(response.json()) == 2
