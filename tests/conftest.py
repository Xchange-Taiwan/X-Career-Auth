import pytest
import os
from fastapi.testclient import TestClient
import uuid
from unittest.mock import AsyncMock


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_postgres: mark test as requiring a running Postgres database (skipped when TEST_POSTGRES_URL is not set)",
    )

@pytest.fixture(scope="session")
def app():
    os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"
    os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"

    from main import app
    return app # 將 FastAPI object 傳給用到這個 fixture 的測試

@pytest.fixture(scope="session")
def client(app):
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

@pytest.fixture # default 就是 function scope
def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture
def registered_oauth_account(client, unique_email):
    # oauth_id 由 unique_email 衍生，確保每個帳號唯一，符合 PostgreSQL 的 oauth_id 唯一約束
    oauth_id = f"google-oauth-{unique_email}"
    client.post(
        "/auth-service/api/v1/signup/oauth/GOOGLE",
        json={
            "region": "TW",
            "email": unique_email,
            "oauth_id": oauth_id
        }
    )

    return unique_email, oauth_id

@pytest.fixture
def mock_email_client(mocker):
    from src.app.adapter import _auth_service

    mock = mocker.patch.object(_auth_service, 'email_client')

    mock.send_conform_code = AsyncMock(return_value=None)
    mock.send_signup_confirm_email = AsyncMock(return_value=None)
    mock.send_reset_password_comfirm_email = AsyncMock(return_value=None)

    return mock
