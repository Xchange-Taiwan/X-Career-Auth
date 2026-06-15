import pytest
from unittest.mock import AsyncMock, MagicMock

def make_account(email=None):
    from src.domain.auth.model.auth_entity import AccountEntity
    return AccountEntity(email=email)

@pytest.fixture
def mock_calendar_client():
    client = MagicMock()
    client.create_event = AsyncMock()
    client.delete_event = AsyncMock()
    return client

@pytest.fixture
def mock_auth_repo():
    repo = MagicMock()
    repo.find_account_by_user_id = AsyncMock()
    return repo

@pytest.fixture
def calendar_service(mock_calendar_client, mock_auth_repo):
    from src.domain.calendar.service.calendar_service import CalendarService
    return CalendarService(
        calendar_client=mock_calendar_client,
        auth_repo=mock_auth_repo
    )

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db