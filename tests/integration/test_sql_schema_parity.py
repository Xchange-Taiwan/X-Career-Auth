"""Schema parity 整合測試（真打 postgres，introspection）。

對「實際的 postgres accounts 表」做 introspection（information_schema / pg_catalog），
驗證 live DB 的欄位、型別、約束、enum 標籤與 ORM 定義一致——也就是確認
PostgreSQL accounts 表真的和 account domain model 的持久化資料對得上。

注意：accounts 表由 sql_session fixture 依 ORM 自建（見 conftest.py）。因此本檔驗證的是
「ORM 定義能在真實 postgres 正確落地成預期 schema」。實際部署用的 auth_init.sql 另有
已知問題（見本次交付報告），不在此測試範圍。
postgres 不可用時自動 skip。
"""
import pytest
from sqlalchemy import text

from src.config.constant import AccountType
from src.infra.db.sql.orm.auth_orm import Account

pytestmark = pytest.mark.requires_postgres


# 預期欄位 → (information_schema.data_type, character_maximum_length)
# 來源：ORM Account 定義，對應 AccountEntity 持久化欄位。
EXPECTED_COLUMNS = {
    "aid": ("bigint", None),
    "email": ("character varying", 255),
    "email2": ("character varying", 255),
    "pass_hash": ("character varying", 60),
    "pass_salt": ("character varying", 60),
    "oauth_id": ("character varying", 255),
    "refresh_token": ("character varying", 255),
    "user_id": ("bigint", None),
    "account_type": ("USER-DEFINED", None),   # postgres ENUM
    "is_active": ("boolean", None),
    "region": ("character varying", 50),
    "created_at": ("bigint", None),
    "updated_at": ("bigint", None),
}


async def _fetch_columns(session):
    result = await session.execute(text(
        """
        SELECT column_name, data_type, character_maximum_length,
               is_nullable, udt_name
        FROM information_schema.columns
        WHERE table_name = 'accounts' AND table_schema = current_schema()
        """
    ))
    return {row["column_name"]: row for row in result.mappings().all()}


async def _fetch_constraints(session):
    result = await session.execute(text(
        """
        SELECT tc.constraint_type, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = 'accounts'
          AND tc.table_schema = current_schema()
        """
    ))
    return result.mappings().all()


# --- 表存在 / 欄位集合 -----------------------------------------------------

async def test_accounts_table_exists(sql_session):
    cols = await _fetch_columns(sql_session)
    assert cols, "postgres 找不到 accounts 表"


async def test_column_names_match_orm(sql_session):
    cols = await _fetch_columns(sql_session)
    orm_columns = set(Account.__table__.columns.keys())

    assert set(cols.keys()) == orm_columns, (
        f"live DB 與 ORM 欄位不一致：\n"
        f"  只在 DB: {set(cols.keys()) - orm_columns}\n"
        f"  只在 ORM: {orm_columns - set(cols.keys())}"
    )
    assert set(cols.keys()) == set(EXPECTED_COLUMNS.keys())


# --- 欄位型別 --------------------------------------------------------------

async def test_column_data_types(sql_session):
    cols = await _fetch_columns(sql_session)
    for name, (expected_type, expected_len) in EXPECTED_COLUMNS.items():
        col = cols[name]
        assert col["data_type"] == expected_type, (
            f"{name} 型別應為 {expected_type}，實際 {col['data_type']}"
        )
        if expected_len is not None:
            assert col["character_maximum_length"] == expected_len, (
                f"{name} 長度應為 {expected_len}，實際 {col['character_maximum_length']}"
            )


async def test_account_type_is_enum_udt(sql_session):
    cols = await _fetch_columns(sql_session)
    account_type = cols["account_type"]
    assert account_type["data_type"] == "USER-DEFINED"
    assert account_type["udt_name"] == "account_type"


async def test_enum_labels_match_account_type(sql_session):
    """postgres account_type enum 的標籤，必須與程式的 AccountType 一致。"""
    result = await sql_session.execute(text(
        """
        SELECT e.enumlabel AS label
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE t.typname = 'account_type'
        """
    ))
    labels = {row["label"] for row in result.mappings().all()}
    assert labels == {e.value for e in AccountType}


# --- 約束 ------------------------------------------------------------------

async def test_not_null_constraints(sql_session):
    cols = await _fetch_columns(sql_session)
    # email 是帳號查詢鍵、account_type 為必填
    assert cols["email"]["is_nullable"] == "NO"
    assert cols["account_type"]["is_nullable"] == "NO"


async def test_primary_and_unique_keys(sql_session):
    constraints = await _fetch_constraints(sql_session)
    pk_cols = {c["column_name"] for c in constraints if c["constraint_type"] == "PRIMARY KEY"}
    unique_cols = {c["column_name"] for c in constraints if c["constraint_type"] == "UNIQUE"}

    assert "aid" in pk_cols, "aid 應為主鍵"
    assert "email" in unique_cols, "email 應唯一"
    assert "user_id" in unique_cols, "user_id 應唯一"
