def test_login_success(client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    assert body["data"]["email"] == email

def test_login_wrong_password(client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": email,
            "password": "nobodyPassword555@"
        }
    )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "40100"
    assert "password" in body["msg"].lower()

def test_login_email_not_found(client):
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": "nobody@example.com",
            "password": "nobodyPassword555@"
        }
    )

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "40400"
    assert "not found" in body["msg"].lower()

def test_login_oauth_account_with_xc(client, registered_oauth_account):
    email, oauth_id = registered_oauth_account
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": email,
            "password": "nobodyPassword555@"
        }
    )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "40100"
    assert "GOOGLE" in body["msg"]