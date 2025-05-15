import httpx, os, flask, functools

OPA_URL = os.getenv("OPA_URL","http://localhost:8181/v1/data/http/authz")

async def _check(req, claims):
    inp = { "input": {{
        "method": req.method,
        "path":   req.path.strip("/").split("/"),
        "token":  claims
    }}}
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
