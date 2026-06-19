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

def test_signup_creates_postgres_row(client, unique_email, fetch_account):
    # 遷移後資料寫入 PostgreSQL：驗證 signup 後 accounts 表確實有對應 row
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

    row = fetch_account(unique_email)

    assert row is not None
    assert row["email"] == unique_email
    assert row["account_type"] == "XC"
    assert row["region"] == "TW"


def test_signup_postgres_row_data_format(client, unique_email, fetch_account):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 201

    row = fetch_account(unique_email)
    assert row is not None
    assert isinstance(row["aid"], int)
    assert isinstance(row["user_id"], int)
    assert isinstance(row["pass_hash"], str)
    assert isinstance(row["pass_salt"], str)
    assert row["account_type"] == "XC"
    assert row["is_active"] is True
    assert row["oauth_id"] in ("", None)
    assert isinstance(row["created_at"], int)
    assert isinstance(row["updated_at"], int)

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

def test_signup_response_serializes_account_vo(client, unique_email):
    # 升級守門:AccountVO 的 use_enum_values + Field(default) 序列化(account_type enum→字串 "XC")
    # 是 pydantic v1→v2 已知會漂移的點,且為對外 API 契約。鎖住回應的完整欄位形狀。
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
            "password": "Password123!"
        }
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["email"] == unique_email
    assert data["account_type"] == "XC"   # 必須是字串值,非 enum 物件 / "AccountType.XC"
    assert data["region"] == "TW"
    assert isinstance(data["aid"], int)
    assert isinstance(data["user_id"], int)

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


# --- 必填欄位缺失 → 422(NewAccountDTO: region / email / password 皆必填)-----
# 升級守門:缺必填欄位應擋在 pydantic 請求驗證層(不進 service/DB)。
# 只斷言 status_code 與 loc 指向的欄位(v1/v2 穩定);不斷言 msg/type 文字(會漂移)。

def test_signup_missing_password_returns_422(client, unique_email):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
        }
    )

    assert response.status_code == 422
    body = response.json()
    assert any("password" in str(err.get("loc", [])) for err in body["detail"])


def test_signup_missing_region_returns_422(client, unique_email):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "email": unique_email,
            "password": "Password123!",
        }
    )

    assert response.status_code == 422
    body = response.json()
    assert any("region" in str(err.get("loc", [])) for err in body["detail"])


def test_signup_missing_email_returns_422(client):
    response = client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "password": "Password123!",
        }
    )

    assert response.status_code == 422
    body = response.json()
    assert any("email" in str(err.get("loc", [])) for err in body["detail"])
