import pytest
from src.config.exception import ClientException
from src.domain.auth.model.gateway_auth_model import (
    ResetPasswordDTO,
    UpdatePasswordDTO,
    SSOLoginDTO,
)


def test_reset_password_dto_matching_passwords_succeeds():
    dto = ResetPasswordDTO(
        register_email="test@example.com",
        password="Password123!",
        confirm_password="Password123!",
    )
    assert dto.password == "Password123!"
    assert dto.confirm_password == "Password123!"


def test_reset_password_dto_mismatched_passwords_raises():
    # 鎖定例外型別為 ClientException：v1 的 @validator 遷移成 v2 的 @field_validator 時，
    # 若例外被包成 ValidationError 或型別漂移，此測試會明確抓到（而非僅靠訊息字串僥倖通過）。
    with pytest.raises(ClientException) as exc_info:
        ResetPasswordDTO(
            register_email="test@example.com",
            password="Password123!",
            confirm_password="Different456!",
        )
    assert "passwords do not match" in str(exc_info.value).lower()


def test_update_password_dto_with_origin_password():
    dto = UpdatePasswordDTO(
        register_email="test@example.com",
        password="NewPassword456!",
        confirm_password="NewPassword456!",
        origin_password="OldPassword123!",
    )
    assert dto.origin_password == "OldPassword123!"


def test_update_password_dto_without_origin_password_defaults_to_none():
    # Pydantic v2 對 Optional 無預設值的欄位行為更嚴格；此測試鎖住 reset flow 可省略 origin_password
    dto = UpdatePasswordDTO(
        register_email="test@example.com",
        password="NewPassword456!",
        confirm_password="NewPassword456!",
    )
    assert dto.origin_password is None


def test_sso_login_dto_to_dict_excludes_sso_type():
    # Pydantic v2 將 .dict() 改為 .model_dump()；此測試確保自訂 to_dict() 仍正確移除內部欄位
    dto = SSOLoginDTO(
        code="auth_code_123",
        state="state_xyz",
        sso_type="GOOGLE",
    )
    result = dto.to_dict()
    assert "sso_type" not in result
    assert result["code"] == "auth_code_123"
    assert result["state"] == "state_xyz"
