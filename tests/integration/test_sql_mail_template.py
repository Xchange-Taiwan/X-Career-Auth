import pytest


@pytest.mark.requires_postgres
async def test_get_mail_template_success(postgres_session):
    from src.infra.cache.mail_template_cache import MailTemplateCache
    from src.infra.db.sql.orm.mail_template_orm import MailTemplate

    # 插入測試資料
    template = MailTemplate(
        id="auth_template",
        content="<h1>Hello {{ name }}</h1>",
        name="auth",
    )
    postgres_session.add(template)
    await postgres_session.flush()  # 寫入但不 commit，測試結束後自動 rollback

    cache = MailTemplateCache(db_session=postgres_session)
    content = await cache.get_mail_template()

    assert content is not None
    assert "Hello" in content


@pytest.mark.requires_postgres
async def test_get_mail_template_not_found_raises_server_exception(postgres_session):
    # 驗證當 mail_template 表中無對應 row 時，MailTemplateCache 拋出 ServerException
    # 而非靜默回傳 None 或 Python 原生 exception（確保 Python 3.13 下 asyncpg/SQLAlchemy 可正常執行 async query）
    from src.infra.cache.mail_template_cache import MailTemplateCache
    from src.config.exception import ServerException

    cache = MailTemplateCache(db_session=postgres_session)

    with pytest.raises(ServerException) as exc_info:
        await cache.get_mail_template()

    assert exc_info.value.msg == "get_mail_template_error"
