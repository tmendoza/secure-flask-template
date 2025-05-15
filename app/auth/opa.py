# app/auth/opa.py

import os
import functools
import httpx
import flask

# URL for your OPA sidecar’s policy endpoint
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181/v1/data/http/authz")

def _check(req: flask.Request, claims: dict) -> bool:
    """
    Calls OPA with the HTTP method, path, and token claims.
    Returns True if OPA allows the action, False otherwise.
    """
    payload = {
        "input": {
            "method": req.method,
            "path": req.path.strip("/").split("/"),
            "token": claims,
        }
    }
    try:
        response = httpx.post(OPA_URL, json=payload, timeout=1.0)
        response.raise_for_status()
        # OPA returns {"result": true} or {"result": false}
        return bool(response.json().get("result", False))
    except httpx.RequestError:
        # If OPA is unreachable or times out, deny by default
        return False

def opa_guard(fn):
    """
    Decorator to enforce ABAC via OPA.
    If _check() returns False, aborts with HTTP 403.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        claims = getattr(flask.g, "token_claims", {})
        if not _check(flask.request, claims):
            flask.abort(403)
        return fn(*args, **kwargs)
    return wrapper
