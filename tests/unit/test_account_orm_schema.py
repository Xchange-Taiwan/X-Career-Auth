"""Schema parity 單元測試（不需 DB）。

legacy account store 的「有效 schema」= repository 實際寫入的欄位集合，
也就是 AccountEntity 的持久化欄位。
搬到 PostgreSQL 後，accounts 表（由 ORM `Account` 定義）必須能完整對應這組欄位，
否則資料遷移時會塞不進去或塞錯位。

本檔在「程式碼層」鎖住三者一致：
    AccountEntity 持久化欄位  ==  ORM Account 欄位  ⊇  legacy 寫入欄位

需要真實 postgres 表的 introspection 對照，另見
tests/integration/test_sql_schema_parity.py。
"""
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.dialects.postgresql import ENUM

from src.config.constant import AccountType
from src.domain.auth.model.auth_entity import AccountEntity
from src.infra.db.sql.orm.auth_orm import Account


# AccountEntity 與 legacy account store 實際持久化的欄位（兩者一致）。
# 來源：auth_entity.AccountEntity 欄位。
EXPECTED_FIELDS = {
    "email",
    "aid",
    "email2",
    "pass_hash",
    "pass_salt",
    "oauth_id",
    "refresh_token",
    "user_id",
    "account_type",
    "is_active",
    "region",
    "created_at",
    "updated_at",
}


def _cols():
    return Account.__table__.columns


# --- 欄位集合一致 ----------------------------------------------------------

def test_orm_columns_match_account_entity_fields():
    """ORM accounts 表的欄位集合，必須與 AccountEntity 持久化欄位完全相同。

    多一欄或少一欄都代表 postgres 表與 domain model 漂移，遷移會出問題。
    """
    orm_columns = set(_cols().keys())
    entity_fields = set(AccountEntity.__fields__.keys())

    assert orm_columns == entity_fields, (
        f"ORM 與 AccountEntity 欄位不一致：\n"
        f"  只在 ORM: {orm_columns - entity_fields}\n"
        f"  只在 Entity: {entity_fields - orm_columns}"
    )


def test_orm_covers_legacy_persisted_fields():
    """ORM 欄位必須涵蓋 legacy account store 實際寫入的欄位（schema parity 的核心）。"""
    orm_columns = set(_cols().keys())
    missing = EXPECTED_FIELDS - orm_columns
    assert not missing, f"postgres accounts 表缺少 legacy account store 會寫入的欄位: {missing}"


# --- 主鍵 / 唯一鍵 ---------------------------------------------------------

def test_aid_is_primary_key():
    assert _cols()["aid"].primary_key is True


def test_email_is_unique_and_not_null():
    """email 是帳號查詢鍵；postgres 必須對應唯一且非空。"""
    email = _cols()["email"]
    assert email.unique is True
    assert email.nullable is False


def test_user_id_is_unique():
    assert _cols()["user_id"].unique is True


def test_account_type_not_null():
    assert _cols()["account_type"].nullable is False


# --- 欄位型別 --------------------------------------------------------------

def test_integer_columns_are_bigint():
    """aid / user_id / created_at / updated_at 以數字儲存，
    postgres 對應須為 BIGINT，避免遷移大數值時溢位。"""
    for name in ("aid", "user_id", "created_at", "updated_at"):
        assert isinstance(_cols()[name].type, BigInteger), f"{name} 應為 BigInteger"


def test_string_columns_types_and_lengths():
    expected = {
        "email": 255,
        "email2": 255,
        "pass_hash": 60,
        "pass_salt": 60,
        "oauth_id": 255,
        "refresh_token": 255,
        "region": 50,
    }
    for name, length in expected.items():
        col = _cols()[name]
        assert isinstance(col.type, String), f"{name} 應為 String"
        assert col.type.length == length, f"{name} 長度應為 {length}，實際 {col.type.length}"


def test_is_active_is_boolean():
    assert isinstance(_cols()["is_active"].type, Boolean)


def test_account_type_is_enum_with_expected_values():
    """account_type 對應 postgres ENUM，且列舉值與 AccountType 一致。"""
    col_type = _cols()["account_type"].type
    assert isinstance(col_type, ENUM)
    assert col_type.name == "account_type"
    assert set(col_type.enums) == {e.value for e in AccountType}
