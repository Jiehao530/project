import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../"))
from app.routers.users import router
from fastapi.testclient import TestClient

client = TestClient(router)

def test_signup_user():
    data = {
        "username": "UserTester",
        "password": "Testing123",
        "email": "usertester@gmail.com",
        "department": "Testing",
        "rol": "admin"
        }
    response = client.post("/signup", json=data)
    assert response.status_code == 201
    assert response.json()["username"] == "UserTester"

def test_login_user():
    data = {
        "username": "UserTester",
        "password": "Testing123"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 200
    assert "Token" in response.json()

@pytest.fixture
def get_token():
    token = client.post("/login", data={"username": "UserTester","password": "Testing123"})
    assert token.status_code == 200
    assert "Token" in token.json()
    return token.json()["Token"]

@pytest.fixture
def get_headers(get_token):
    return {"Authorization": f"Bearer {get_token}"}

def test_get_user(get_headers):
    response = client.get("/user/UserTester", headers=get_headers)
    assert response.status_code == 202
    assert response.json()["username"] == "UserTester"

def test_get_user_admin(get_headers):
    response = client.get("/user/UserTester/admin", headers=get_headers)
    assert response.status_code == 202
    assert type(response.json()) == list