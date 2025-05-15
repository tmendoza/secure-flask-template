from authlib.jose import jwt, JsonWebKey
import httpx, cachetools, os, flask

ISSUER = os.getenv("OIDC_ISSUER", "http://keycloak:8080/realms/dev")
AUD    = "todo-svc"

@cachetools.cached(cachetools.TTLCache(maxsize=1, ttl=600))
def _jwks():
    cfg = httpx.get(f"{ISSUER}/.well-known/openid-configuration").json()
    return JsonWebKey.import_key_set(httpx.get(cfg["jwks_uri"]).json())

def decode(token: str):
    return jwt.decode(token, key=_jwks(), claims_options={{
        "iss": {{"values":[ISSUER]}},
        "aud": {{"values":[AUD]}},
        "exp": {{"essential":True}}
    }})

def configure_oidc(app: flask.Flask):
    @app.before_request
    def attach_claims():
        auth = flask.request.headers.get("Authorization","")
        if auth.startswith("Bearer "):
            flask.g.token_claims = decode(auth.split()[1])
        else:
            flask.g.token_claims = {{}}
