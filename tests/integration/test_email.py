from unittest.mock import ANY

def test_sendcode_new_email(client, unique_email, mock_email_client):
    response = client.post(
        "/auth-service/api/v1/sendcode/email",
        json={
            "email": unique_email,
            "code": "123456",
            "exist": False
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    mock_email_client.send_conform_code.assert_called_once_with(
        email=unique_email,
        confirm_code="123456"
    )

def test_sendcode_existing_email(client, mock_email_client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/sendcode/email",
        json={
            "email": email,
            "code": "123456",
            "exist": True
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    mock_email_client.send_conform_code.assert_called_once_with(
        email=email,
        confirm_code="123456"
    )

def test_sendcode_exist_false_but_email_taken(client, mock_email_client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/sendcode/email",
        json={
            "email": email,
            "code": "123456",
            "exist": False
        }
    )

    assert response.status_code == 406
    body = response.json()
    assert body["code"] == "40600"
    assert "registered" in body["msg"].lower()
    mock_email_client.send_conform_code.assert_not_called()

def test_sendcode_exist_true_but_email_not_found(client, mock_email_client, unique_email):
    response = client.post(
        "/auth-service/api/v1/sendcode/email",
        json={
            "email": unique_email,
            "code": "123456",
            "exist": True
        }
    )

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "40400"
    assert "not found" in body["msg"].lower()
    mock_email_client.send_conform_code.assert_not_called()

def test_signup_email_new(client, mock_email_client, unique_email):
    response = client.post(
        "/auth-service/api/v1/signup/email",
        json={
            "email": unique_email,
            "exist": False
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    assert body["data"]["token"] is not None
    mock_email_client.send_signup_confirm_email.assert_called_once_with(
        email = unique_email,
        token=ANY
    )

def test_signup_email_existing(client, mock_email_client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/signup/email",
        json={
            "email": email,
            "exist": True
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "ok"
    assert body["data"]["token"] is not None
    mock_email_client.send_signup_confirm_email.assert_called_once_with(
        email=email,
        token=ANY
    )

def test_signup_email_exist_false_but_taken(client, mock_email_client, registered_account):
    email, password = registered_account
    response = client.post(
        "/auth-service/api/v1/signup/email",
        json={
            "email": email,
            "exist": False
        }
    )

    assert response.status_code == 406
    body = response.json()
    assert body["code"] == "40600"
    assert "registered" in body["msg"].lower()
    mock_email_client.send_signup_confirm_email.assert_not_called()

def test_signup_email_exist_true_but_not_found(client, mock_email_client, unique_email):
    response = client.post(
        "/auth-service/api/v1/signup/email",
        json={
            "email": unique_email,
            "exist": True
        }
    )

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "40400"
    assert "not found" in body["msg"].lower()
    mock_email_client.send_signup_confirm_email.assert_not_called()

def test_reset_password_email_success(client, mock_email_client, registered_account):
    email, password = registered_account
    response = client.get(
        "/auth-service/api/v1/password/reset/email",
        params={"email": email}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "email sent"
    assert body["data"]["token"] is not None
    mock_email_client.send_reset_password_comfirm_email.assert_called_once_with(
        email=email,
        token=ANY
    )

def test_reset_password_email_not_found(client, mock_email_client):
    response = client.get(
        "/auth-service/api/v1/password/reset/email",
        params={"email": "nobody@example.com"}
    )

    # NOTE: email 不存在回 500 是 source 端設計疑慮(應為 404 NotFoundException),
    # 此處鎖住現況以利遷移比對,源頭修正另案處理。
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "50000"
    assert "invalid account" in body["msg"].lower()
    mock_email_client.send_reset_password_comfirm_email.assert_not_called()