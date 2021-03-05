from fastapi.testclient import TestClient

from main import api

client = TestClient(api)

def test_getItemList():
    res = client.get("/items")
    assert res.status_code == 200
