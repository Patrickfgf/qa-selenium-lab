import base64
import json

import pytest
from jsonschema import validate

from tests.api.contracts import schema

INVALID_CREDENTIALS = {"message": "Email e/ou senha inválidos"}


def _jwt_payload(authorization: str) -> dict:
    # A JWT is header.payload.signature, each part base64url without padding.
    payload = authorization.removeprefix("Bearer ").split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def test_login_returns_a_bearer_token_for_that_user(api, create_user):
    user = create_user()

    response = api.post("/login", json={"email": user["email"], "password": user["password"]})

    assert response.status_code == 200
    body = response.json()
    validate(body, schema("login_success"))
    assert body["message"] == "Login realizado com sucesso"
    assert _jwt_payload(body["authorization"])["email"] == user["email"]


# 401 means "credentials rejected"; 400 means "request malformed", with the error per field.
@pytest.mark.parametrize(
    ("email", "password", "expected_status", "expected_body"),
    [
        pytest.param(
            None, "wrong-password", 401, INVALID_CREDENTIALS, id="TC-API-LOGIN-02-wrong-password"
        ),
        # Same answer as a wrong password: the API does not reveal which e-mails exist.
        pytest.param(
            "nobody-qa-lab@example.com",
            "secret-123",
            401,
            INVALID_CREDENTIALS,
            id="TC-API-LOGIN-03-unknown-email",
        ),
        pytest.param(
            None,
            "",
            400,
            {"password": "password não pode ficar em branco"},
            id="TC-API-LOGIN-04-empty-password",
        ),
        pytest.param(
            "not-an-email",
            "secret-123",
            400,
            {"email": "email deve ser um email válido"},
            id="TC-API-LOGIN-05-malformed-email",
        ),
    ],
)
def test_login_is_rejected(api, create_user, email, password, expected_status, expected_body):
    user = create_user()

    response = api.post("/login", json={"email": email or user["email"], "password": password})

    assert response.status_code == expected_status
    assert response.json() == expected_body
