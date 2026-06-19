import pytest


@pytest.mark.requires_postgres
async def test_get_mail_template_success(postgres_session):
    from src.infra.cache.mail_template_cache import MailTemplateCache

    cache = MailTemplateCache(db_session=postgres_session)
    content = await cache.get_mail_template()

    assert content is not None
    assert "verification_code" in content
    assert "signup" in content
    assert "reset_password" in content


@pytest.mark.requires_postgres
async def test_get_mail_template_not_found_raises_server_exception(postgres_session):
    # 驗證當 mail_template 表中無對應 row 時，MailTemplateCache 拋出 ServerException
    # 而非靜默回傳 None 或 Python 原生 exception（確保 Python 3.13 下 asyncpg/SQLAlchemy 可正常執行 async query）
    from sqlalchemy import text
    from src.infra.cache.mail_template_cache import MailTemplateCache
    from src.config.exception import ServerException

    await postgres_session.execute(
        text("DELETE FROM mail_template WHERE id = 'auth_template'")
    )

    cache = MailTemplateCache(db_session=postgres_session)

    with pytest.raises(ServerException) as exc_info:
        await cache.get_mail_template()

    assert exc_info.value.msg == "get_mail_template_error"
