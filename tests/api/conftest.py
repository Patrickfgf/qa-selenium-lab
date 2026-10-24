import os
import uuid
from collections.abc import Callable, Iterator

import pytest
import requests

from tests.api.client import ServeRestClient

API_URL = os.getenv("API_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def api() -> ServeRestClient:
    client = ServeRestClient(API_URL)
    try:
        client.get("/usuarios")
    except requests.ConnectionError:
        message = f"ServeRest is not running at {API_URL}; start it with: npx serverest@3.2.2"
        # A skip on CI would be lost coverage that nobody notices, so there it is a failure.
        if os.getenv("CI"):
            pytest.fail(message)
        pytest.skip(message)
    return client


@pytest.fixture
def create_user(api: ServeRestClient) -> Iterator[Callable[..., dict[str, str]]]:
    """Create users with a unique e-mail and delete them after the test."""
    created_ids = []

    def _create(admin: bool = False) -> dict[str, str]:
        user = {
            "nome": "QA Lab",
            "email": f"qa-lab-{uuid.uuid4().hex[:12]}@example.com",
            "password": "secret-123",
            "administrador": "true" if admin else "false",
        }
        response = api.post("/usuarios", json=user)
        assert response.status_code == 201, response.text
        created_ids.append(response.json()["_id"])
        return {**user, "_id": response.json()["_id"]}

    yield _create
    for user_id in created_ids:
        api.delete(f"/usuarios/{user_id}")


@pytest.fixture
def login(api: ServeRestClient) -> Callable[[dict[str, str]], str]:
    """Log a user in and return the Authorization value ("Bearer <jwt>")."""

    def _login(user: dict[str, str]) -> str:
        response = api.post("/login", json={"email": user["email"], "password": user["password"]})
        assert response.status_code == 200, response.text
        return response.json()["authorization"]

    return _login
