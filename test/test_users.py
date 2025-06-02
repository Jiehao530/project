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
