# tests/test_todos.py

import os
import pytest
from flask import g
from app import create_app
from app.auth import opa
from scripts.run_migrations import run_migrations

@pytest.fixture(scope="module")
def base_app():
    # point at the test DB (or your dev DB)
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@db:5432/todo"
    app = create_app()

    # run migrations once
    run_migrations()

    return app

@pytest.fixture
def unauth_client(base_app):
    # default opa._check returns False → 403
    return base_app.test_client()

@pytest.fixture
def auth_client(base_app):
    # monkey-patch OPA to always allow
    opa._check = lambda req, claims: True

    # attach dummy claims so g.token_claims exists
    @base_app.before_request
    def attach_dummy():
        g.token_claims = {"realm_access": {"roles": ["user"]}}

    return base_app.test_client()

def test_requires_auth(unauth_client):
    resp = unauth_client.get("/v1/todos/")
    assert resp.status_code == 403

def test_full_crud_cycle(auth_client):
    headers = {"Authorization": "Bearer dummy"}

    # CREATE
    create_resp = auth_client.post(
        "/v1/todos/",
        json={"title": "pytest todo"},
        headers=headers
    )
    assert create_resp.status_code == 201
    todo = create_resp.get_json()
    tid = todo["id"]
    assert todo["title"] == "pytest todo"

    # READ list
    list_resp = auth_client.get("/v1/todos/", headers=headers)
    assert list_resp.status_code == 200
    assert any(item["id"] == tid for item in list_resp.get_json())

    # READ single
    get_resp = auth_client.get(f"/v1/todos/{tid}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.get_json()["id"] == tid

    # UPDATE
    update_resp = auth_client.patch(
        f"/v1/todos/{tid}", json={"completed": True}, headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.get_json()["completed"] is True

    # DELETE
    delete_resp = auth_client.delete(f"/v1/todos/{tid}", headers=headers)
    assert delete_resp.status_code == 204

    # FINAL LIST
    final = auth_client.get("/v1/todos/", headers=headers)
    assert all(item["id"] != tid for item in final.get_json())
