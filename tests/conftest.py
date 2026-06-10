import pytest
import httpx
import os
from fastapi.testclient import TestClient
import uuid
from unittest.mock import AsyncMock

@pytest.fixture(scope="session")
def localstack_ready():
    url = "http://localhost:4566/_localstack/health"
    try:
        response = httpx.get(url, timeout=3)
        if response.status_code != 200:
            pytest.fail(f"Service not healthy: {response.status_code}")
    except httpx.ConnectError:
        pytest.fail("Cannot connect to service")

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
    return TestClient(app, raise_server_exceptions=False)

@pytest.fixture(scope="session")
def dynamodb_table():
    import boto3
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="ap-northeast-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    return dynamodb.Table("dev_x_career_auth_accounts")

@pytest.fixture # default 就是 function scope
def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture
def registered_oauth_account(client, unique_email):
    oauth_id = "fake-google-oauth-id-12345"
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