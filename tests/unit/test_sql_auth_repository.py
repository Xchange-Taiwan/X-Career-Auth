from unittest.mock import AsyncMock, Mock

from src.domain.auth.model.auth_entity import AccountEntity
from src.infra.db.sql.repo.auth_repository import AuthRepository


def _mock_mapping_result(row):
    result = Mock()
    result.mappings.return_value.one_or_none.return_value = row
    return result


async def test_find_account_by_email_with_fields_returns_account_entity():
    db = AsyncMock()
    db.execute.return_value = _mock_mapping_result(
        {"email": "user@example.com", "region": "TW"}
    )
    repo = AuthRepository()

    account = await repo.find_account_by_email(
        db, "user@example.com", fields=["email", "region"]
    )

    assert isinstance(account, AccountEntity)
    assert account.email == "user@example.com"
    assert account.region == "TW"


async def test_find_account_by_oauth_id_with_fields_returns_account_entity():
    db = AsyncMock()
    db.execute.return_value = _mock_mapping_result(
        {"email": "oauth@example.com", "oauth_id": "google-oauth-id"}
    )
    repo = AuthRepository()

    account = await repo.find_account_by_oauth_id(
        db, "google-oauth-id", fields=["email", "oauth_id"]
    )

    assert isinstance(account, AccountEntity)
    assert account.email == "oauth@example.com"
    assert account.oauth_id == "google-oauth-id"
