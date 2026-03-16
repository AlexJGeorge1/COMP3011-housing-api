"""
Tests for /listings CRUD endpoints.
"""

import pytest
from tests.conftest import client, auth_headers


SAMPLE_LISTING = {
    "address": "10 Test Street, Manchester",
    "region": "North West",
    "price": 180000,
    "bedrooms": 3,
    "property_type": "terraced",
    "transaction_date": "2023-06-15",
}


class TestGetListings:
    def test_get_listings_returns_empty_list(self, client):
        response = client.get("/listings")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_listings_with_region_filter(self, client, auth_headers):
        client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        response = client.get("/listings?region=North West")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_listings_with_no_matching_region(self, client, auth_headers):
        client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        response = client.get("/listings?region=London")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_listings_pagination(self, client, auth_headers):
        for i in range(5):
            listing = {**SAMPLE_LISTING, "address": f"{i} Test Road"}
            client.post("/listings", json=listing, headers=auth_headers)
        response = client.get("/listings?limit=3&offset=0")
        assert response.status_code == 200
        assert len(response.json()) == 3


class TestGetSingleListing:
    def test_get_listing_by_id(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.get(f"/listings/{listing_id}")
        assert response.status_code == 200
        assert response.json()["id"] == listing_id

    def test_get_listing_not_found(self, client):
        response = client.get("/listings/nonexistent-id")
        assert response.status_code == 404


class TestCreateListing:
    def test_create_listing_requires_auth(self, client):
        response = client.post("/listings", json=SAMPLE_LISTING)
        assert response.status_code == 401

    def test_create_listing_success(self, client, auth_headers):
        response = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["address"] == SAMPLE_LISTING["address"]
        assert data["price"] == SAMPLE_LISTING["price"]
        assert "id" in data

    def test_create_listing_invalid_data(self, client, auth_headers):
        response = client.post("/listings", json={"address": "Only address"}, headers=auth_headers)
        assert response.status_code == 422


class TestUpdateListing:
    def test_update_listing_success(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.put(
            f"/listings/{listing_id}",
            json={"price": 200000},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["price"] == 200000

    def test_update_listing_requires_auth(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.put(f"/listings/{listing_id}", json={"price": 200000})
        assert response.status_code == 401

    def test_update_listing_not_found(self, client, auth_headers):
        response = client.put("/listings/bad-id", json={"price": 200000}, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteListing:
    def test_delete_listing_success(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.delete(f"/listings/{listing_id}", headers=auth_headers)
        assert response.status_code == 204
        # Verify it's gone
        assert client.get(f"/listings/{listing_id}").status_code == 404

    def test_delete_listing_requires_auth(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.delete(f"/listings/{listing_id}")
        assert response.status_code == 401
