"""
Extended tests for /listings CRUD endpoints.

Covers edge cases and response-shape checks not in test_listings.py.
Does NOT modify existing tests.
"""


SAMPLE_LISTING = {
    "address": "10 Test Street, Manchester",
    "region": "North West",
    "price": 180000,
    "bedrooms": 3,
    "property_type": "terraced",
    "transaction_date": "2023-06-15",
}


class TestDeleteListingExtended:
    def test_delete_listing_not_found(self, client, auth_headers):
        response = client.delete("/listings/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_listing_not_found_message(self, client, auth_headers):
        response = client.delete("/listings/nonexistent-id", headers=auth_headers)
        assert "not found" in response.json()["detail"].lower()


class TestCreateListingResponseShape:
    def test_create_listing_returns_created_at(self, client, auth_headers):
        response = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        assert response.status_code == 201
        assert "created_at" in response.json()

    def test_create_listing_id_is_uuid_length(self, client, auth_headers):
        response = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        assert len(response.json()["id"]) == 36

    def test_create_listing_echoes_all_fields(self, client, auth_headers):
        response = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        data = response.json()
        assert data["address"] == SAMPLE_LISTING["address"]
        assert data["region"] == SAMPLE_LISTING["region"]
        assert data["price"] == SAMPLE_LISTING["price"]
        assert data["bedrooms"] == SAMPLE_LISTING["bedrooms"]
        assert data["property_type"] == SAMPLE_LISTING["property_type"]
        assert data["transaction_date"] == SAMPLE_LISTING["transaction_date"]

    def test_create_two_listings_get_different_ids(self, client, auth_headers):
        r1 = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing2 = {**SAMPLE_LISTING, "address": "20 Other Street"}
        r2 = client.post("/listings", json=listing2, headers=auth_headers)
        assert r1.json()["id"] != r2.json()["id"]


class TestUpdateListingExtended:
    def test_update_preserves_unchanged_fields(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.put(
            f"/listings/{listing_id}",
            json={"price": 200000},
            headers=auth_headers,
        )
        data = response.json()
        assert data["price"] == 200000
        assert data["address"] == SAMPLE_LISTING["address"]
        assert data["region"] == SAMPLE_LISTING["region"]
        assert data["bedrooms"] == SAMPLE_LISTING["bedrooms"]

    def test_update_multiple_fields(self, client, auth_headers):
        create_resp = client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        listing_id = create_resp.json()["id"]
        response = client.put(
            f"/listings/{listing_id}",
            json={"price": 250000, "bedrooms": 4},
            headers=auth_headers,
        )
        data = response.json()
        assert data["price"] == 250000
        assert data["bedrooms"] == 4


class TestGetListingsExtended:
    def test_get_listings_offset_past_end(self, client, auth_headers):
        client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        response = client.get("/listings?offset=100")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_listings_region_filter_case_insensitive(self, client, auth_headers):
        client.post("/listings", json=SAMPLE_LISTING, headers=auth_headers)
        response = client.get("/listings?region=north west")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_listing_not_found_message(self, client):
        response = client.get("/listings/does-not-exist")
        assert "not found" in response.json()["detail"].lower()
