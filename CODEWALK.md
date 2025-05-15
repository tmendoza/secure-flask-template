# CODEWALK.md

This document explains each Python component in the **todo-svc** repository. Read it section by section to understand how the pieces fit together.

---

## 1. `app/__init__.py`

```python
from flask import Flask
from flask_smorest import Api
from app.api.v1.todos import blp as todos_blp
from app.auth.oidc import configure_oidc

def create_app():
    app = Flask(__name__)
    app.config.update(
        API_TITLE="todo-svc",
        API_VERSION="1.0.0",
        OPENAPI_VERSION="3.1.0",
        DATABASE_URL="postgresql://postgres:postgres@db:5432/todo"
    )
    api = Api(app)
    api.register_blueprint(todos_blp, url_prefix="/v1/todos")
    configure_oidc(app)
    return app
````

**What it does:**

* Imports Flask, Flask-Smorest, the todos blueprint, and OIDC setup.
* Defines `create_app()` as the application factory:

  1. Creates the Flask app.
  2. Configures API metadata and the database URL.
  3. Wraps the app in a Smorest `Api` to enable OpenAPI.
  4. Registers the todos blueprint at `/v1/todos`.
  5. Attaches JWT claim parsing via `configure_oidc`.

---

## 2. `app/api/v1/todos.py`

```python
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from app.schemas import TodoSchema
from app.services import list_todos, create_todo, get_todo, update_todo, delete_todo
from app.auth.opa import opa_guard

blp = Blueprint("todos", "todos", description="Todo CRUD operations")

@blp.route("/")
class TodoList(MethodView):
    @opa_guard
    @blp.response(200, TodoSchema(many=True))
    def get(self):
        return list_todos()

    @opa_guard
    @blp.arguments(TodoSchema)
    @blp.response(201, TodoSchema)
    def post(self, new_data):
        return create_todo(new_data)

@blp.route("/<int:todo_id>")
class TodoItem(MethodView):
    @opa_guard
    @blp.response(200, TodoSchema)
    def get(self, todo_id):
        todo = get_todo(todo_id) or abort(404)
        return todo

    @opa_guard
    @blp.arguments(TodoSchema(partial=True))
    @blp.response(200, TodoSchema)
    def patch(self, update_data, todo_id):
        return update_todo(todo_id, update_data)

    @opa_guard
    @blp.response(204)
    def delete(self, todo_id):
        delete_todo(todo_id)
        return ""
```

**What it does:**

* Defines a Smorest Blueprint `blp` for `/todos`.
* Uses class-based views (`MethodView`) for CRUD operations.
* Applies `@opa_guard` for authorization.
* Uses `@blp.arguments` to parse/validate input via Marshmallow.
* Uses `@blp.response` to serialize output via Marshmallow.

---

## 3. `app/auth/oidc.py`

```python
from authlib.jose import jwt, JsonWebKey
import httpx, cachetools, os, flask

ISSUER = os.getenv("OIDC_ISSUER", "http://keycloak:8080/realms/dev")
AUD    = "todo-svc"

@cachetools.cached(cachetools.TTLCache(maxsize=1, ttl=600))
def _jwks():
    cfg = httpx.get(f"{ISSUER}/.well-known/openid-configuration").json()
    return JsonWebKey.import_key_set(httpx.get(cfg["jwks_uri"]).json())

def decode(token: str):
    return jwt.decode(token, key=_jwks(), claims_options={
        "iss": {"values":[ISSUER]},
        "aud": {"values":[AUD]},
        "exp": {"essential":True}
    })

def configure_oidc(app: flask.Flask):
    @app.before_request
    def attach_claims():
        auth = flask.request.headers.get("Authorization","")
        if auth.startswith("Bearer "):
            flask.g.token_claims = decode(auth.split()[1])
        else:
            flask.g.token_claims = {}
```

**What it does:**

* Fetches & caches JWKs from Keycloak.
* Defines `decode()` to verify JWT claims.
* Adds a `before_request` hook to attach `token_claims` to `flask.g`.

---

## 4. `app/auth/opa.py`

```python
import httpx, os, flask, functools

OPA_URL = os.getenv("OPA_URL","http://localhost:8181/v1/data/http/authz")

async def _check(req, claims):
    inp = {"input": {
        "method": req.method,
        "path":   req.path.strip("/").split("/"),
        "token":  claims
    }}
    async with httpx.AsyncClient() as client:
        res = await client.post(OPA_URL, json=inp, timeout=1)
    return res.json().get("result", False)

def opa_guard(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        if not await _check(flask.request, flask.g.token_claims):
            flask.abort(403)
        return await fn(*args, **kwargs)
    return wrapper
```

**What it does:**

* Sends request info & JWT claims to OPA.
* Returns allow/deny based on your Rego policies.
* Decorator `opa_guard` enforces authorization before view logic.

---

## 5. `app/db.py`

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
```

**What it does:**

* Reads the `DATABASE_URL` env var.
* Returns a psycopg2 connection that uses `RealDictCursor` for dict rows.

---

## 6. `app/schemas.py`

```python
from marshmallow import Schema, fields, validate

class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=120))
    completed = fields.Bool(missing=False)
```

**What it does:**

* Marshmallow schema for serializing/deserializing Todo items.
* Enforces `title` presence and max length, defaults `completed` to `False`.

---

## 7. `app/services.py`

```python
from app.db import get_connection

def list_todos():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, completed FROM todos")
        return cur.fetchall()

def create_todo(data):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id, title, completed",
            (data['title'], data.get('completed', False))
        )
        return cur.fetchone()

def get_todo(todo_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, completed FROM todos WHERE id=%s", (todo_id,))
        return cur.fetchone()

def update_todo(todo_id, data):
    conn = get_connection()
    set_clause = ", ".join(f"{k}=%s" for k in data.keys())
    values = list(data.values()) + [todo_id]
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE todos SET {set_clause} WHERE id=%s RETURNING id, title, completed",
            values
        )
        return cur.fetchone()

def delete_todo(todo_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM todos WHERE id=%s", (todo_id,))
```

**What it does:**

* Implements raw-SQL CRUD against the `todos` table.
* Returns Python dicts via `RealDictCursor`.

---

## 8. `scripts/run_migrations.py`

```python
from app.db import get_connection

def run_migrations():
    conn = get_connection()
    with conn.cursor() as cur:
        with open('migrations/init.sql') as f:
            cur.execute(f.read())
    conn.commit()

if __name__ == '__main__':
    run_migrations()
```

**What it does:**

* Executes `migrations/init.sql` to create the `todos` table before the API starts.

---

## 9. `tests/test_smoke.py`

```python
from app import create_app

def test_health():
    client = create_app().test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
```

**What it does:**

* A basic smoke test ensuring the Flask app loads and responds on `/health`.

---

### Summary

Each component in **todo-svc** serves a clear role:

1. **`app/__init__.py`** – Sets up Flask, API, and auth.
2. **`app/api/v1/todos.py`** – Defines CRUD endpoints with validation, auth, and serialization.
3. **`app/auth/oidc.py`** – Handles JWT decoding & request claim attachment.
4. **`app/auth/opa.py`** – Communicates with OPA for authorization.
5. **`app/db.py`** – Provides psycopg2 connections.
6. **`app/schemas.py`** – Marshmallow schemas for request/response.
7. **`app/services.py`** – Business logic: raw SQL CRUD.
8. **`scripts/run_migrations.py`** – Applies SQL migrations.
9. **`tests/test_smoke.py`** – Verifies basic app health.

With this walkthrough, you should understand how each file interacts to deliver a secure, validated, and authorized Todo microservice.
