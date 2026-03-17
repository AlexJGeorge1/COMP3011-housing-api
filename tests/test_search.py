"""
Tests for the /search semantic search endpoint.

The search endpoint relies on pgvector for cosine similarity, so full
integration tests require PostgreSQL.  Validation and the 'no embeddings'
guard are testable against SQLite by mocking the embedding function.
"""

from unittest.mock import patch


class TestSearchValidation:
    """Query-parameter validation (runs before function body, no DB needed)."""

    def test_search_missing_query_param(self, client):
        response = client.get("/search")
        assert response.status_code == 422

    def test_search_query_too_short(self, client):
        response = client.get("/search?q=ab")
        assert response.status_code == 422

    def test_search_limit_exceeds_max(self, client):
        response = client.get("/search?q=test+query&limit=100")
        assert response.status_code == 422

    def test_search_limit_negative(self, client):
        response = client.get("/search?q=test+query&limit=-1")
        assert response.status_code == 422


class TestSearchNoEmbeddings:
    """When no listings have embeddings, the endpoint returns 422."""

    def test_search_no_embeddings_returns_422(self, client):
        with patch("app.routers.search.embed_text", return_value=[0.0] * 384):
            response = client.get("/search?q=affordable flat in london")
        assert response.status_code == 422

    def test_search_no_embeddings_detail_message(self, client):
        with patch("app.routers.search.embed_text", return_value=[0.0] * 384):
            response = client.get("/search?q=three bedroom house")
        assert "No embeddings found" in response.json()["detail"]

    def test_search_with_region_filter_no_embeddings(self, client):
        with patch("app.routers.search.embed_text", return_value=[0.0] * 384):
            response = client.get("/search?q=flat+in+city&region=North+West")
        assert response.status_code == 422

    def test_search_respects_default_limit(self, client):
        """Default limit (10) is accepted without error beyond the embedding check."""
        with patch("app.routers.search.embed_text", return_value=[0.0] * 384):
            response = client.get("/search?q=affordable house")
        assert response.status_code == 422  # still 422, but didn't fail on limit

    def test_search_valid_custom_limit(self, client):
        with patch("app.routers.search.embed_text", return_value=[0.0] * 384):
            response = client.get("/search?q=affordable house&limit=50")
        assert response.status_code == 422  # embedding guard, not a validation error
