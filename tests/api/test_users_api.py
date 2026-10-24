import pytest
from jsonschema import validate

from tests.api.contracts import schema


def test_created_user_can_be_read_back(api, create_user):
    user = create_user()

    response = api.get(f"/usuarios/{user['_id']}")

    # Beyond the status: the record was stored with the data that was sent.
    assert response.status_code == 200
    stored = response.json()
    assert {key: stored[key] for key in ("nome", "email", "administrador", "_id")} == {
        key: user[key] for key in ("nome", "email", "administrador", "_id")
    }


def test_duplicate_email_is_rejected(api, create_user):
    user = create_user()
    duplicate = {key: value for key, value in user.items() if key != "_id"} | {"nome": "Other"}

    response = api.post("/usuarios", json=duplicate)

    assert response.status_code == 400
    assert response.json() == {"message": "Este email já está sendo usado"}


def test_user_list_matches_the_contract(api, create_user):
    create_user()

    response = api.get("/usuarios")

    assert response.status_code == 200
    validate(response.json(), schema("user_list"))


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-005: GET /usuarios lists every user's password, with no authentication",
)
def test_user_list_does_not_expose_passwords(api, create_user):
    create_user()

    users = api.get("/usuarios").json()["usuarios"]

    assert not any("password" in user for user in users)
