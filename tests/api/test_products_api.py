import uuid

import pytest

TOKEN_REJECTED = {
    "message": "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"
}


@pytest.fixture
def new_product() -> dict:
    # Product names are unique in ServeRest, so each test brings its own.
    return {
        "nome": f"QA Lab product {uuid.uuid4().hex[:12]}",
        "preco": 100,
        "descricao": "Created by the API tests",
        "quantidade": 1,
    }


def test_creating_a_product_without_a_token_is_unauthorized(api, new_product):
    response = api.post("/produtos", json=new_product)

    assert response.status_code == 401
    assert response.json() == TOKEN_REJECTED


def test_creating_a_product_as_a_regular_user_is_forbidden(api, create_user, login, new_product):
    # 401 is "who are you?"; 403 is "I know who you are, and you cannot do this".
    token = login(create_user(admin=False))

    response = api.post("/produtos", json=new_product, token=token)

    assert response.status_code == 403
    assert response.json() == {"message": "Rota exclusiva para administradores"}


def test_admin_creates_a_product(api, create_user, login, new_product):
    token = login(create_user(admin=True))

    response = api.post("/produtos", json=new_product, token=token)

    assert response.status_code == 201
    assert response.json()["message"] == "Cadastro realizado com sucesso"
    api.delete(f"/produtos/{response.json()['_id']}", token=token)
