from src.infra.resource.handler import sql_resource


def test_db_schema_configures_search_path_and_schema_translation():
    assert sql_resource.schema_translate_map == {
        "schema": sql_resource.DB_SCHEMA,
    }
    if sql_resource.DB_SCHEMA:
        assert sql_resource.server_settings["search_path"] == (
            f'"{sql_resource.DB_SCHEMA}", public'
        )
    else:
        assert "search_path" not in sql_resource.server_settings


def test_engine_uses_db_schema_translation(monkeypatch):
    captured = {}
    expected_engine = object()

    def fake_create_async_engine(database_url, **kwargs):
        captured["database_url"] = database_url
        captured["kwargs"] = kwargs
        return expected_engine

    monkeypatch.setattr(
        sql_resource,
        "create_async_engine",
        fake_create_async_engine,
    )

    engine = sql_resource._create_database_engine()

    assert engine is expected_engine
    assert captured["database_url"] == sql_resource.DATABASE_URL
    assert captured["kwargs"]["execution_options"] == {
        "schema_translate_map": {
            "schema": sql_resource.DB_SCHEMA,
        },
    }


def test_ssl_is_only_passed_when_configured():
    if sql_resource.DB_SSL:
        assert sql_resource.connect_args["ssl"] == sql_resource.DB_SSL
    else:
        assert "ssl" not in sql_resource.connect_args
