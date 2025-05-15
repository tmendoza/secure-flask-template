from app import create_app

def test_health():
    client = create_app().test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
