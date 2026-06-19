def test_oauth_signup_success(client, unique_email, fetch_account):
    oauth_id = "google-oauth-abc123"
    response = client.post(
        "/auth-service/api/v1/signup/oauth/GOOGLE",
        json={
            "region": "TW",
            "email": unique_email,
            "oauth_id": oauth_id
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    assert body["data"]["account_type"] == "GOOGLE"
    assert body["data"]["oauth_id"] == oauth_id

    row = fetch_account(unique_email)
    assert row is not None
    assert row["account_type"] == "GOOGLE"
    assert row["oauth_id"] == oauth_id
    assert row["pass_hash"] == ""
    assert row["pass_salt"] == ""
    assert isinstance(row["aid"], int)
    assert isinstance(row["user_id"], int)

def test_oauth_signup_duplicate_email(client, registered_oauth_account):
    email, oauth_id = registered_oauth_account
    response = client.post(
        "/auth-service/api/v1/signup/oauth/GOOGLE",
        json={
            "region": "TW",
            "email": email,
            "oauth_id": "google-oauth-abc123"
        }
    )

    # NOTE: 重複註冊回 500 是 source 端設計疑慮(應為 409/406),此處鎖住現況以利遷移比對。
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "50000"
    assert "already registered" in body["msg"]

def test_oauth_login_success(client, registered_oauth_account):
    email, oauth_id = registered_oauth_account
    response = client.post(
        "/auth-service/api/v1/login/oauth/GOOGLE",
        json={
            "email": email,
            "oauth_id": oauth_id
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    assert body["data"]["email"] == email

def test_oauth_login_wrong_oauth_id(client, registered_oauth_account):
    email, oauth_id = registered_oauth_account
    response = client.post(
        "/auth-service/api/v1/login/oauth/GOOGLE",
        json={
            "email": email,
            "oauth_id": "google-oauth-abc123"
        }
    )

    # NOTE: 錯誤的 oauth_id 回 500 是 source 端設計疑慮(資安觀點應為 401 UnauthorizedException),
    # 此處鎖住現況以利遷移比對,源頭修正另案處理。
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "50000"
    assert "not valid" in body["msg"]

def test_oauth_login_account_not_found(client):
    response = client.post(
        "/auth-service/api/v1/login/oauth/GOOGLE",
        json={
            "email": "noreply@example.com",
            "oauth_id": "google-oauth-abc123"
        }
    )

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "40400"
    assert "not found" in body["msg"].lower()

def test_oauth_login_xc_account_with_oauth(client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/login/oauth/GOOGLE",
        json={
            "email": email,
            "oauth_id": "google-oauth-abc123"
        }
    )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "40100"
    assert "google account is not valid" in body["msg"]
