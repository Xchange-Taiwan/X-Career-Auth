# 測試 PUT /password/update
def test_update_password_success(client, registered_account):
    email, password = registered_account
    response = client.put(
        "/auth-service/api/v1/password/update",
        json={
            "register_email": email,
            "password": "NewPassword456!",
            "confirm_password": "NewPassword456!",
            "origin_password": password
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "update success"

    # 驗證密碼真的有改成功, 用新密碼登入
    response = client.post(
        "/auth-service/api/v1/login",
        json={
            "email": email,
            "password": "NewPassword456!"
        }
    )

    assert response.status_code == 201
    assert response.json()["code"] == "0"

def test_update_password_wrong_origin(client, registered_account):
    email, password = registered_account

    response = client.put(
        "/auth-service/api/v1/password/update",
        json={
            "register_email": email,
            "password": "NewPassword456!",
            "confirm_password": "NewPassword456!",
            "origin_password": "WrongOriginPassword123!"
        }
    )

    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "40300"
    assert "invalid password" in body["msg"].lower()

def test_update_password_mismatch(client, registered_account):
    email, password = registered_account

    response = client.put(
        "/auth-service/api/v1/password/update",
        json={
            "register_email": email,
            "password": "NewPassword456!",
            "confirm_password": "NotTheSamePassword123!",
            "origin_password": password
        }
    )

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "40000"
    assert "passwords do not match" in body["msg"].lower()

def test_update_password_account_not_found(client):
    response = client.put(
        "/auth-service/api/v1/password/update",
        json={
            "register_email": "nobody@example.com",
            "password": "NewPassword456!",
            "confirm_password": "NewPassword456!",
            "origin_password": "Password123!"
        }
    )

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "40400"
    assert "not found" in body["msg"].lower()
