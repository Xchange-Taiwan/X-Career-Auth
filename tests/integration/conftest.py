import pytest


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
