import pytest


def _resolve_sql_url():
    """整合測試的 postgres 連線字串。

    優先用 TEST_POSTGRES_URL，否則退回 app 設定的 DB_URL（Docker 內即指向
    docker-compose 的 postgres）。在 Docker 內跑測試時不需額外設定。
    """
    import os
    url = os.environ.get("TEST_POSTGRES_URL")
    if url:
        return url
    from src.config.conf import DB_URL
    return DB_URL


# test_sql_* 的自建表放在專屬 schema，與 app 使用的 public.accounts 完全隔離，
# 兩者可在同一顆 postgres、同一個 pytest session 共存而不互相清表。
SQL_TEST_SCHEMA = "auth_test"


@pytest.fixture
async def sql_session():
    """提供連到真實 postgres 的 SQLAlchemy AsyncSession，並「依 ORM 在專屬 schema 自建 accounts 表」。

    背景：本地 postgres 的 public.accounts 由 app/init 使用；為了不干擾 HTTP 整合測試，
    repo 層測試把表建在獨立 schema（auth_test），測完整個 DROP SCHEMA 拆掉，
    達到自我隔離、不依賴外部 DDL，也不會碰到 app 的 public.accounts。

    注意：PostgreSQL AuthRepository 的寫入方法內部會自行 commit，無法用
    transaction rollback 隔離，故改採「每個測試建空表 → 測完 drop schema」的方式。

    postgres 不可連線時（例如在沒有 DB 的開發機）自動 skip。
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text

    from src.config.constant import AccountType
    from src.infra.db.sql.orm.auth_orm import Base

    url = _resolve_sql_url()
    # search_path 指向專屬 schema，使 repo 的非限定 `accounts` 解析到 auth_test.accounts。
    # connect timeout 設小，開發機沒有 postgres 時能快速 skip 而非長時間卡住。
    engine = create_async_engine(
        url,
        connect_args={"timeout": 3, "server_settings": {"search_path": SQL_TEST_SCHEMA}},
    )

    enum_values = ", ".join(f"'{e.value}'" for e in AccountType)

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            # 重建乾淨的專屬 schema：含 account_type enum 與 accounts 表
            await conn.execute(text(f"DROP SCHEMA IF EXISTS {SQL_TEST_SCHEMA} CASCADE"))
            await conn.execute(text(f"CREATE SCHEMA {SQL_TEST_SCHEMA}"))
            await conn.execute(
                text(f"CREATE TYPE {SQL_TEST_SCHEMA}.account_type AS ENUM ({enum_values})")
            )
            await conn.run_sync(Base.metadata.create_all)
    except pytest.skip.Exception:
        raise
    except Exception as e:
        await engine.dispose()
        pytest.skip(f"postgres 不可用，skip SQL 整合測試: {e}")

    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with factory() as session:
            yield session
    finally:
        async with engine.begin() as conn:
            await conn.execute(text(f"DROP SCHEMA IF EXISTS {SQL_TEST_SCHEMA} CASCADE"))
        await engine.dispose()


@pytest.fixture(autouse=True)
def _clean_accounts():
    """每個整合測試前，清空 app 的 public.accounts，達到資料隔離。

    postgres 是持久化的，固定值（如 oauth_id）+ 唯一約束會讓跨測試/跨次數的資料
    互相衝突；每測試清表可確保每個測試從乾淨狀態開始。
    用 asyncio.run 包成同步介面（專案僅有 asyncpg），對 sync/async 測試都適用；
    postgres 不可用或表不存在時靜默略過（需 DB 的測試自會 skip/fail）。
    """
    import asyncio

    async def _truncate():
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from src.config.conf import DB_URL

        engine = create_async_engine(DB_URL, connect_args={"timeout": 3})
        try:
            async with engine.begin() as conn:
                await conn.execute(text("TRUNCATE accounts RESTART IDENTITY"))
        finally:
            await engine.dispose()

    try:
        asyncio.run(_truncate())
    except Exception:
        pass
    yield


@pytest.fixture
def fetch_account():
    """回傳一個同步函式，依 email 查 app 的 public.accounts（用於驗證資料真的寫進 postgres）。"""
    import asyncio

    def _fetch(email):
        async def _query():
            from sqlalchemy.ext.asyncio import create_async_engine
            from sqlalchemy import text
            from src.config.conf import DB_URL

            engine = create_async_engine(DB_URL, connect_args={"timeout": 3})
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(
                        text(
                            "SELECT aid, email, email2, pass_hash, pass_salt, "
                            "oauth_id, refresh_token, user_id, "
                            "account_type::text AS account_type, is_active, "
                            "region, created_at, updated_at "
                            "FROM accounts WHERE email = :email"
                        ),
                        {"email": email},
                    )
                    return result.mappings().one_or_none()
            finally:
                await engine.dispose()

        return asyncio.run(_query())

    return _fetch


@pytest.fixture
def registered_account(client, unique_email): # fixture 注入其他 fixture
    client.post(
        "/auth-service/api/v1/signup",
        json={
            "region": "TW",
            "email": unique_email,
            "password": "Password123!",
        }
    )
    return unique_email, "Password123!"


@pytest.fixture
async def postgres_session():
    """提供真實 asyncpg/SQLAlchemy async session，用於 requires_postgres 測試。
    未設定 TEST_POSTGRES_URL 環境變數時自動 skip。
    Session 在 yield 前開啟 transaction，yield 後 rollback，確保測試資料不殘留。
    """
    import os
    postgres_url = os.environ.get("TEST_POSTGRES_URL")
    if not postgres_url:
        pytest.skip("TEST_POSTGRES_URL not set; skipping requires_postgres tests")

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(postgres_url, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()

    await engine.dispose()
