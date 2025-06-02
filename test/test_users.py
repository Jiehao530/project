import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../"))
from app.routers.users import router
from fastapi.testclient import TestClient

client = TestClient(router)
