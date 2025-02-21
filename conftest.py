from fastapi.testclient import TestClient
import pytest
from main import app

test_client = TestClient(app)
response = test_client.post("/token", data={"username": "string", "password": "string"})
token = response.json()["access_token"]


def test_token():
    response = test_client.post(
        "/token", data={"username": "string", "password": "string"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    if response.status_code != 200:
        pytest.exit("Exiting pytest, missing token")


@pytest.fixture()
def get_test_token():
    if not token:
        test_token()
    return token
