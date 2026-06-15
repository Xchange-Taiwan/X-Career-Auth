from src.config.constant import AccountType
from src.domain.auth.model.auth_entity import AccountEntity
from src.infra.db.sql.orm.auth_orm import Account


def test_account_entity_to_orm_account_type_is_string():
    # 驗證 entity → ORM 轉換後 account_type 為字串，而非 enum 物件（寫入 SQL 前格式正確）
    entity = AccountEntity(
        aid=123,
        email="test@example.com",
        user_id=456,
        region="TW",
        account_type=AccountType.XC,
        pass_hash="hash",
        pass_salt="salt",
        oauth_id="",
        refresh_token="",
        is_active=True,
    )
    orm_obj = entity.to_orm()
    assert orm_obj.account_type == "XC"
    assert isinstance(orm_obj.account_type, str)


def test_account_entity_from_orm_xc_account_type():
    # 模擬從 DB 讀回的 ORM 物件（account_type 為字串，如 Postgres ENUM 欄位回傳值）
    account = Account()
    account.aid = 123
    account.email = "test@example.com"
    account.email2 = None
    account.user_id = 456
    account.region = "TW"
    account.account_type = "XC"
    account.is_active = True
    account.pass_hash = "hash"
    account.pass_salt = "salt"
    account.oauth_id = ""
    account.refresh_token = ""

    entity = AccountEntity.from_orm(account)
    # Pydantic v2 的 from_attributes 遷移時，若 coercion 行為改變，此斷言會失敗
    assert entity.account_type == AccountType.XC


def test_account_entity_from_orm_google_account_type():
    account = Account()
    account.aid = 789
    account.email = "google@example.com"
    account.email2 = None
    account.user_id = 101
    account.region = "TW"
    account.account_type = "GOOGLE"
    account.is_active = True
    account.pass_hash = ""
    account.pass_salt = ""
    account.oauth_id = "google-oauth-id-123"
    account.refresh_token = ""

    entity = AccountEntity.from_orm(account)
    assert entity.account_type == AccountType.GOOGLE
