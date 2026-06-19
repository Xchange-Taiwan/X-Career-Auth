"""PostgreSQL AuthRepository 整合測試（真打 postgres）。

目標是 DB 切換到 PostgreSQL 後使用的 AuthRepository。
直接對 repository 方法測（非經 HTTP），讓問題能定位在 repo 層而非整條 HTTP。

schema（accounts 表 + account_type enum）由 sql_session fixture 依 ORM 自建，
每個測試拿到一張乾淨的空表，測完整個拆掉（見 tests/integration/conftest.py）。
postgres 不可用時自動 skip。
"""
import pytest

from src.config.constant import AccountType
from src.domain.auth.model.auth_entity import AccountEntity
from src.domain.auth.model.auth_model import (
    NewAccountDTO,
    NewOauthAccountDTO,
    UpdatePasswordDTO,
)
from src.infra.db.sql.repo.auth_repository import AuthRepository
from src.infra.util.auth_util import match_password, gen_password_hash, gen_pass_salt

pytestmark = pytest.mark.requires_postgres


@pytest.fixture
def repo():
    return AuthRepository()


def build_entity(email, password="Password123!", region="TW"):
    return NewAccountDTO(
        region=region, email=email, password=password
    ).gen_account_entity(AccountType.XC)


def build_oauth_entity(email, oauth_id, region="TW"):
    return NewOauthAccountDTO(
        region=region, email=email, oauth_id=oauth_id
    ).gen_account_entity(AccountType.GOOGLE)


@pytest.fixture
async def created_account(sql_session, repo, unique_email):
    """建立一個 XC 帳號；表由 fixture 自建自拆，無需手動清除。"""
    entity = build_entity(unique_email)
    await repo.create_account(sql_session, entity)
    return entity


# --- create / find ---------------------------------------------------------

async def test_create_and_find_by_email(sql_session, repo, created_account):
    found = await repo.find_account_by_email(sql_session, created_account.email)

    assert found is not None
    assert found.email == created_account.email
    assert found.region == "TW"
    assert found.account_type == AccountType.XC   # enum 正確 round-trip
    assert isinstance(found.aid, int)
    assert isinstance(found.user_id, int)


async def test_find_by_email_returns_none_when_absent(sql_session, repo):
    found = await repo.find_account_by_email(sql_session, "nobody-xyz@example.com")
    assert found is None


async def test_find_by_email_with_fields_existence(sql_session, repo, created_account):
    """service 層（send_code_by_email 等）以 fields=["email","region"] 查詢後只判斷
    存在與否，這裡鎖住「存在回非 None、不存在回 None」的契約。"""
    present = await repo.find_account_by_email(
        sql_session, created_account.email, fields=["email", "region"]
    )
    assert present is not None
    assert isinstance(present, AccountEntity)
    assert present.email == created_account.email
    assert present.region == "TW"

    absent = await repo.find_account_by_email(
        sql_session, "ghost@example.com", fields=["email", "region"]
    )
    assert absent is None


async def test_find_by_email_with_aid_field_for_reset_password(sql_session, repo, created_account):
    """send_reset_password_confirm_email 以 fields=["aid"] 檢查帳號存在。
    這裡鎖住 partial field 查詢仍回 AccountEntity，而不是 scalar aid。"""
    account = await repo.find_account_by_email(
        sql_session, created_account.email, fields=["aid"]
    )

    assert isinstance(account, AccountEntity)
    assert account.aid == created_account.aid
    assert account.email is None


async def test_create_duplicate_returns_none(sql_session, repo, created_account):
    # email 唯一約束 → 重複建立應觸發 IntegrityError，被 repo 攔下回 None
    dup = build_entity(created_account.email)
    result = await repo.create_account(sql_session, dup)
    assert result is None


async def test_find_by_user_id(sql_session, repo, created_account):
    found = await repo.find_account_by_user_id(sql_session, created_account.user_id)
    assert found is not None
    assert found.email == created_account.email


async def test_find_by_oauth_id(sql_session, repo, unique_email):
    """SQL repo 有實作 find_account_by_oauth_id。"""
    oauth_id = "google-oauth-id-abc123"
    entity = build_oauth_entity(unique_email, oauth_id)
    await repo.create_account(sql_session, entity)

    found = await repo.find_account_by_oauth_id(sql_session, oauth_id)
    assert found is not None
    assert found.email == unique_email
    assert found.account_type == AccountType.GOOGLE
    assert found.oauth_id == oauth_id

    partial = await repo.find_account_by_oauth_id(
        sql_session, oauth_id, fields=["email", "oauth_id"]
    )
    assert isinstance(partial, AccountEntity)
    assert partial.email == unique_email
    assert partial.oauth_id == oauth_id


# --- update_password -------------------------------------------------------

async def test_update_password_changes_hash(sql_session, repo, created_account):
    new_salt = gen_pass_salt()
    new_hash = gen_password_hash("NewPassw0rd!", new_salt)
    params = UpdatePasswordDTO(
        pass_hash=new_hash, pass_salt=new_salt, email=created_account.email
    )

    rc = await repo.update_password(sql_session, params)
    assert rc == 1

    found = await repo.find_account_by_email(sql_session, created_account.email)
    assert found.pass_hash == new_hash
    assert found.pass_salt == new_salt


async def test_update_password_no_account(sql_session, repo):
    params = UpdatePasswordDTO(
        pass_hash="x", pass_salt="y", email="ghost-abc@example.com"
    )
    rc = await repo.update_password(sql_session, params)
    assert rc == 0


# --- check_and_update_password ---------------------------------------------

async def test_check_and_update_password_correct_origin(sql_session, repo, created_account):
    new_salt = gen_pass_salt()
    new_hash = gen_password_hash("Another1!", new_salt)
    params = UpdatePasswordDTO(
        pass_hash=new_hash,
        pass_salt=new_salt,
        email=created_account.email,
        origin_password="Password123!",   # created_account 的原始密碼
    )

    rc = await repo.check_and_update_password(sql_session, params, match_password)
    assert rc == 1

    found = await repo.find_account_by_email(sql_session, created_account.email)
    assert found.pass_hash == new_hash


async def test_check_and_update_password_wrong_origin(sql_session, repo, created_account):
    params = UpdatePasswordDTO(
        pass_hash="x",
        pass_salt="y",
        email=created_account.email,
        origin_password="WRONG-password",
    )
    rc = await repo.check_and_update_password(sql_session, params, match_password)
    assert rc == -1


async def test_check_and_update_password_no_account(sql_session, repo):
    params = UpdatePasswordDTO(
        pass_hash="x",
        pass_salt="y",
        email="ghost-abc@example.com",
        origin_password="whatever",
    )
    rc = await repo.check_and_update_password(sql_session, params, match_password)
    assert rc == 0


# --- delete ----------------------------------------------------------------

async def test_delete_account_removes_item(sql_session, repo, unique_email):
    entity = build_entity(unique_email)
    await repo.create_account(sql_session, entity)
    assert await repo.find_account_by_email(sql_session, unique_email) is not None

    rc = await repo.delete_account_by_email(sql_session, entity)
    assert rc == 1
    assert await repo.find_account_by_email(sql_session, unique_email) is None
