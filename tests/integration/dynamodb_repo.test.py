"""P1-G：DynamoDBAuthRepository 整合測試（LocalStack 真打）

直接對 repository 方法測（非經 HTTP），讓升級後 boto3/aioboto3 連帶變動時能把
問題定位到 repo 層而非整條 HTTP。依測試策略：AWS 走 LocalStack 真實整合。

需求：LocalStack 在 :4566 並已建好 dev_x_career_auth_accounts 表
（由 X-Talent-infra 的 init script 建立）。localstack_ready fixture 會先把關。
"""
import aioboto3
import pytest

from src.config.constant import AccountType
from src.domain.auth.model.auth_model import NewAccountDTO, UpdatePasswordDTO
from src.infra.db.nosql.repo.dynamodb_auth_repository import DynamoDBAuthRepository
from src.infra.util.auth_util import match_password, gen_password_hash, gen_pass_salt


@pytest.fixture
async def db(localstack_ready):
    """aioboto3 async DynamoDB resource，指向 LocalStack。"""
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url="http://localhost:4566",
        region_name="ap-northeast-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    ) as resource:
        yield resource


@pytest.fixture
def repo():
    return DynamoDBAuthRepository()


def build_entity(email, password="Password123!", region="TW"):
    return NewAccountDTO(
        region=region, email=email, password=password
    ).gen_account_entity(AccountType.XC)


@pytest.fixture
async def created_account(db, repo, unique_email):
    """建立一個帳號並在測試後清除（delete 本身另有測試覆蓋）。"""
    entity = build_entity(unique_email)
    await repo.create_account(db, entity)
    yield entity
    await repo.delete_account_by_email(db, entity)


# --- create / find ---------------------------------------------------------

async def test_create_and_find_by_email(db, repo, created_account):
    found = await repo.find_account_by_email(db, created_account.email)

    assert found is not None
    assert found.email == created_account.email
    assert found.region == "TW"
    assert found.account_type == AccountType.XC
    assert isinstance(found.aid, int)        # Decimal → int 正規化
    assert isinstance(found.user_id, int)


async def test_find_by_email_returns_none_when_absent(db, repo):
    found = await repo.find_account_by_email(db, "nobody-xyz@example.com")
    assert found is None


async def test_create_duplicate_returns_none(db, repo, created_account):
    # ConditionExpression='attribute_not_exists(email)' → 重複建立應失敗回 None
    dup = build_entity(created_account.email)
    result = await repo.create_account(db, dup)
    assert result is None


async def test_find_by_user_id(db, repo, created_account):
    found = await repo.find_account_by_user_id(db, created_account.user_id)
    assert found is not None
    assert found.email == created_account.email


# --- update_password -------------------------------------------------------

async def test_update_password_changes_hash(db, repo, created_account):
    new_salt = gen_pass_salt()
    new_hash = gen_password_hash("NewPassw0rd!", new_salt)
    params = UpdatePasswordDTO(
        pass_hash=new_hash, pass_salt=new_salt, email=created_account.email
    )

    rc = await repo.update_password(db, params)
    assert rc == 1

    found = await repo.find_account_by_email(db, created_account.email)
    assert found.pass_hash == new_hash
    assert found.pass_salt == new_salt


# --- check_and_update_password ---------------------------------------------

async def test_check_and_update_password_correct_origin(db, repo, created_account):
    new_salt = gen_pass_salt()
    new_hash = gen_password_hash("Another1!", new_salt)
    params = UpdatePasswordDTO(
        pass_hash=new_hash,
        pass_salt=new_salt,
        email=created_account.email,
        origin_password="Password123!",  # created_account 的原始密碼
    )

    rc = await repo.check_and_update_password(db, params, match_password)
    assert rc == 1

    found = await repo.find_account_by_email(db, created_account.email)
    assert found.pass_hash == new_hash


async def test_check_and_update_password_wrong_origin(db, repo, created_account):
    params = UpdatePasswordDTO(
        pass_hash="x",
        pass_salt="y",
        email=created_account.email,
        origin_password="WRONG-password",
    )
    rc = await repo.check_and_update_password(db, params, match_password)
    assert rc == -1


async def test_check_and_update_password_no_account(db, repo):
    params = UpdatePasswordDTO(
        pass_hash="x",
        pass_salt="y",
        email="ghost-abc@example.com",
        origin_password="whatever",
    )
    rc = await repo.check_and_update_password(db, params, match_password)
    assert rc == 0


# --- delete ----------------------------------------------------------------

async def test_delete_account_removes_item(db, repo, unique_email):
    entity = build_entity(unique_email)
    await repo.create_account(db, entity)
    assert await repo.find_account_by_email(db, unique_email) is not None

    rc = await repo.delete_account_by_email(db, entity)
    assert rc == 1
    assert await repo.find_account_by_email(db, unique_email) is None
