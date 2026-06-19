def test_delete_account_success(client, registered_account, fetch_account):
    email, password = registered_account
    assert fetch_account(email) is not None

    response = client.delete(
        "/auth-service/api/v1/accounts",
        json={
            "email": email
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "deleted"

    # 驗證 account 真的從 PostgreSQL 被刪除
    assert fetch_account(email) is None

def test_delete_account_not_found(client):
    # NOTE: 刪除不存在帳號回 200(冪等刪除設計)— auth_service.delete_account 在帳號不存在時 silently 回 0,
    # router 仍回 res_success(msg='deleted')。此為刻意設計,測試鎖住此契約。
    response = client.delete(
        "/auth-service/api/v1/accounts",
        json={
            "email": "nobody@example.com"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "0"
    assert body["msg"] == "deleted"
