def test_signup_success(client, unique_email):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    assert body["data"]["email"] == unique_email

def test_signup_creates_dynamodb_item(client, unique_email, dynamodb_table):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 201
    assert response.json()["code"] == "0"

    result = dynamodb_table.get_item(Key={"email": unique_email})
    item = result.get("Item")

    assert item is not None
    assert item["email"] == unique_email
    assert item["account_type"] == "XC"

def test_signup_duplicate_email(client, registered_account):
    # 打2次 /signup
    email, password = registered_account

    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": email,
            "password": password
        }
    )

    # NOTE: 重複註冊回 500 是 source 端的設計疑慮(應為 409/406),此處鎖住現況以利遷移比對,源頭修正另案處理。
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "50000"
    assert "already registered" in body["msg"]

def test_signup_invalid_email(client):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": "not-an-email",
            "password": "TestPassword"
        }
    )

    # NOTE: 422 由 FastAPI/pydantic 自動處理,body 為 pydantic 原生格式(非 {code,msg,data} 契約)。
    # 此斷言為 pydantic v1↔v2 升級的最敏感點:錯誤格式會改變。
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert any("email" in str(err.get("loc", [])) for err in body["detail"])
