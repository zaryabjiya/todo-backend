import pytest
from fastapi.testclient import TestClient
from ..main import app


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as client:
        yield client