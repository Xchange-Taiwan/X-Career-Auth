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

def test_login_response_serializes_account_vo(client, registered_account):
    # 升級守門:login 走「DB 讀回 entity → parse_obj → AccountVO」路徑(與 signup 不同來源),
    # 驗 from_attributes / model_validate 升級後序列化仍符合對外契約(account_type 字串化)。
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["email"] == email
    assert data["account_type"] == "XC"
    assert isinstance(data["aid"], int)
    assert isinstance(data["user_id"], int)

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


# --- 必填欄位缺失 → 422(LoginDTO: email / password 皆必填)------------------
# 升級守門:缺必填欄位應擋在 pydantic 請求驗證層(不進 service)。
# 只斷言 status_code 與 loc 指向的欄位(v1/v2 穩定);不斷言 msg/type 文字(會漂移)。

def test_login_missing_password_returns_422(client):
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": "user@example.com",
        }
    )

    assert response.status_code == 422
    body = response.json()
    assert any("password" in str(err.get("loc", [])) for err in body["detail"])


def test_login_missing_email_returns_422(client):
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "password": "Password123!",
        }
    )

    assert response.status_code == 422
    body = response.json()
    assert any("email" in str(err.get("loc", [])) for err in body["detail"])