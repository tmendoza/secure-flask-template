# app/auth/oidc.py

import os
import flask
import httpx
import cachetools
from authlib.jose import jwt, JsonWebKey

# OIDC configuration
ISSUER = os.getenv("OIDC_ISSUER", "http://keycloak:8080/realms/dev")
AUD     = os.getenv("OIDC_AUDIENCE", "todo-svc")

@cachetools.cached(cachetools.TTLCache(maxsize=1, ttl=600))
def _jwks():
    """
    Fetch and cache the JSON Web Key Set from the OIDC issuer.
    """
    # Discover OIDC configuration
    config = httpx.get(f"{ISSUER}/.well-known/openid-configuration").json()
    jwks_uri = config.get("jwks_uri")
    return JsonWebKey.import_key_set(httpx.get(jwks_uri).json())

def decode(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    """
    return jwt.decode(
        token,
        key=_jwks(),
        claims_options={
            "iss": {"values": [ISSUER]},
            "aud": {"values": [AUD]},
            "exp": {"essential": True},
        },
    )

def configure_oidc(app: flask.Flask):
    """
    Install a Flask before_request hook that:
      - Reads the Authorization header
      - Validates and decodes the Bearer token
      - Stores the token claims in flask.g.token_claims
    """
    @app.before_request
    def attach_claims():
        auth_header = flask.request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(maxsplit=1)[1]
            flask.g.token_claims = decode(token)
        else:
            # No token provided → empty claims
            flask.g.token_claims = {}
