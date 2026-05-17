import pytest

@pytest.fixture
def registered_account(client, unique_email): # fixture 注入其他 fixture
    client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
            "password": "Password123!",
        }   
    )
    return unique_email, "Password123!"
