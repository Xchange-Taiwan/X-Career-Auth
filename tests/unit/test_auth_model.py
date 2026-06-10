from src.config.constant import AccountType
from src.domain.auth.model.auth_entity import AccountEntity
from src.domain.auth.model.auth_model import (
    AccountVO,
    AccountOauthVO,
    NewAccountDTO,
    NewOauthAccountDTO,
    UpdatePasswordDTO,
)


def test_account_vo_account_type_serializes_to_string():
    vo = AccountVO(
        aid=123,
        email="test@example.com",
        account_type=AccountType.XC,
        region="TW",
        user_id=456,
    )
    data = vo.dict()
    assert data["account_type"] == "XC"
    assert isinstance(data["account_type"], str)


def test_account_oauth_vo_account_type_serializes_to_string():
    vo = AccountOauthVO(
        aid=123,
        email="test@example.com",
        account_type=AccountType.GOOGLE,
        oauth_id="google-oauth-id-123",
        region="TW",
        user_id=456,
    )
    data = vo.dict()
    assert data["account_type"] == "GOOGLE"
    assert isinstance(data["account_type"], str)
    assert data["oauth_id"] == "google-oauth-id-123"


def test_new_account_dto_gen_account_entity_xc_has_required_fields():
    dto = NewAccountDTO(
        region="TW",
        email="test@example.com",
        password="Password123!",
    )
    entity = dto.gen_account_entity(AccountType.XC)

    assert entity is not None
    assert entity.aid is not None
    assert entity.user_id is not None
    assert entity.pass_hash not in (None, "")
    assert entity.pass_salt not in (None, "")
    assert entity.region == "TW"
    # gen_account_entity 傳入 account_type.value（字串），AccountEntity 欄位應 coerce 回 enum。
    # Pydantic v2 若 coercion 行為改變（例如改為 strict mode），此斷言會立即失敗。
    assert entity.account_type == AccountType.XC


def test_new_oauth_account_dto_gen_account_entity_google_preserves_oauth_id():
    dto = NewOauthAccountDTO(
        region="TW",
        email="test@example.com",
        oauth_id="google-oauth-id-123",
    )
    entity = dto.gen_account_entity(AccountType.GOOGLE)

    assert entity is not None
    assert entity.oauth_id == "google-oauth-id-123"
    assert entity.pass_hash == ""
    assert entity.pass_salt == ""


def test_update_password_dto_origin_password_defaults_to_none():
    # Pydantic v2 對 Optional 欄位規則較嚴格；此測試確保 origin_password 在未傳入時仍為 None
    dto = UpdatePasswordDTO(
        email="test@example.com",
        pass_hash="somehash",
        pass_salt="somesalt",
    )
    assert dto.origin_password is None


def test_account_entity_register_format_account_type_is_string():
    entity = AccountEntity(
        aid=123,
        email="test@example.com",
        user_id=456,
        region="TW",
        account_type=AccountType.XC,
    )
    result = entity.register_format()
    assert result["account_type"] == "XC"
    assert isinstance(result["account_type"], str)
