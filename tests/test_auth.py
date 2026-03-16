"""
Tests for /token authentication endpoint.
"""


class TestAuth:
    def test_login_valid_credentials(self, client):
        response = client.post(
            "/token",
            data={"username": "admin", "password": "secret"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        response = client.post(
            "/token",
            data={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_wrong_username(self, client):
        response = client.post(
            "/token",
            data={"username": "notauser", "password": "secret"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_rejects_no_token(self, client):
        response = client.post("/listings", json={})
        assert response.status_code == 401

    def test_protected_endpoint_rejects_invalid_token(self, client):
        response = client.post(
            "/listings",
            json={},
            headers={"Authorization": "Bearer totally.invalid.token"},
        )
        assert response.status_code == 401

    def test_token_allows_protected_access(self, client, auth_headers):
        # With a valid token, the request reaches the endpoint (fails on validation, not auth)
        response = client.post("/listings", json={}, headers=auth_headers)
        assert response.status_code == 422  # validation error, not 401
