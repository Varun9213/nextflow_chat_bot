from fastapi.testclient import TestClient
from server import APP

client = TestClient(APP)

def test_empty_message():
    resp = client.post("/chat", json={"message": ""})
    assert resp.status_code == 400

def test_basic_mock_flow(monkeypatch):
    # enable mock mode
    import server
    server.MOCK_MODE = True
    r = client.post("/chat", json={"message": "What is Nextflow version?"})
    assert r.status_code == 200
    data = r.json()
    assert "MOCK" in data["reply"]