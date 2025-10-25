from fastapi.testclient import TestClient
from persian_linux_rag.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "mode" in data
