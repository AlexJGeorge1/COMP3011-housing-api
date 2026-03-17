"""
Shared pytest fixtures for the test suite.

Uses an in-memory SQLite database for fast, isolated tests — no Docker required.
Each test function gets a fresh database via function-scoped fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

import os

# Use SQLite in-memory database for tests by default (no PostgreSQL needed)
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")

# Use slightly different connect_args for SQLite
if "sqlite" in TEST_DATABASE_URL:
    connect_args = {"check_same_thread": False}
    engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args, poolclass=StaticPool)
else:
    engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "secret"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
