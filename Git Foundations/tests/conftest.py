import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


@pytest.fixture()
def member(client):
    res = client.post("/api/members", json={
        "name": "Asha Rao", "email": "asha@example.com", "age": 34, "plan_id": 1})
    return res.get_json()
