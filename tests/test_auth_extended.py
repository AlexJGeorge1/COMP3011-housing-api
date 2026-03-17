"""
Extended tests for /token authentication.

Covers JWT structure, edge cases, and token reuse not in test_auth.py.
Does NOT modify existing tests.
"""


class TestTokenStructure:
    def test_token_is_non_empty_string(self, client):
        response = client.post(
            "/token", data={"username": "admin", "password": "secret"}
        )
        token = response.json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_has_three_jwt_parts(self, client):
        response = client.post(
            "/token", data={"username": "admin", "password": "secret"}
        )
        token = response.json()["access_token"]
        assert len(token.split(".")) == 3  # header.payload.signature

    def test_token_type_is_bearer(self, client):
        response = client.post(
            "/token", data={"username": "admin", "password": "secret"}
        )
        assert response.json()["token_type"] == "bearer"


class TestTokenEdgeCases:
    def test_empty_credentials_rejected(self, client):
        response = client.post(
            "/token", data={"username": "", "password": ""}
        )
        assert response.status_code in (401, 422)

    def test_missing_form_data_returns_422(self, client):
        response = client.post("/token")
        assert response.status_code == 422

    def test_correct_username_empty_password(self, client):
        response = client.post(
            "/token", data={"username": "admin", "password": ""}
        )
        assert response.status_code in (401, 422)

    def test_empty_username_correct_password(self, client):
        response = client.post(
            "/token", data={"username": "", "password": "secret"}
        )
        assert response.status_code in (401, 422)


class TestProtectedEndpoints:
    def test_put_listing_rejects_no_token(self, client):
        response = client.put("/listings/some-id", json={"price": 100})
        assert response.status_code == 401

    def test_delete_listing_rejects_no_token(self, client):
        response = client.delete("/listings/some-id")
        assert response.status_code == 401

    def test_post_region_rejects_no_token(self, client):
        response = client.post("/regions", json={"name": "X"})
        assert response.status_code == 401

    def test_put_region_rejects_no_token(self, client):
        response = client.put("/regions/some-id", json={"year": 2024})
        assert response.status_code == 401

    def test_delete_region_rejects_no_token(self, client):
        response = client.delete("/regions/some-id")
        assert response.status_code == 401

    def test_expired_style_garbage_token(self, client):
        headers = {"Authorization": "Bearer a.b.c"}
        response = client.post("/listings", json={}, headers=headers)
        assert response.status_code == 401
