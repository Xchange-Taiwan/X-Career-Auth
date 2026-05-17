import pytest
from fastapi import HTTPException
from datetime import datetime, timezone
from tests.unit.conftest import make_account

async def test_send_invite_single_user_success(
    calendar_service,
    mock_auth_repo,
    mock_calendar_client,
    mock_db
):
    ### Arrange
    # repo 被呼叫, 回傳一個 email 為 xchange 的 account
    mock_auth_repo.find_account_by_user_id.return_value = make_account(email="xchange@example.com")

    # calendar client 被呼叫時, return google 假裝給的 event data
    mock_calendar_client.create_event.return_value = {
        "id": "evt_1",
        "htmlLink": "https://cal/evt_1"
    }

    ### Act
    result = await calendar_service.send_calendar_invite(
        db=mock_db,
        summary="Meeting",
        description="Desc",
        start_time_ts=1700000000,
        end_time_ts=1700003600,
        user_ids=[1], # mock_auth_repo.find_account_by_user_id 會被呼叫 1 次
    )

    ### Assert
    assert result["event_id"] == "evt_1"
    assert result["html_link"] == "https://cal/evt_1"
    assert result["status"] == "success"
    assert result["sent_to"] == ["xchange@example.com"]

    # 驗證 calendar_client.create_event 被正確呼叫
    mock_calendar_client.create_event.assert_called_once()
    # 驗證 service 有把 id 轉換成 email
    call_kwargs = mock_calendar_client.create_event.call_args.kwargs
    assert call_kwargs["attendee_emails"] == ["xchange@example.com"]
    assert call_kwargs["start_time"] == datetime.fromtimestamp(1700000000, tz=timezone.utc)
    assert call_kwargs["end_time"] == datetime.fromtimestamp(1700003600, tz=timezone.utc)

async def test_send_invite_multiple_users_all_valid(
    calendar_service,
    mock_auth_repo,
    mock_calendar_client,
    mock_db
):
    ### Arrange
    mock_auth_repo.find_account_by_user_id.side_effect = [
        make_account(email="xchange_1@example.com"), # 第一次呼叫回傳
        make_account(email="xchange_2@example.com") # 第二次呼叫回傳
    ]

    # create_event return 固定值, 只被呼叫1次
    mock_calendar_client.create_event.return_value = {
        "id": "evt_2",
        "htmlLink": "https://cal/evt_2"
    }

    ### Act
    # user_ids 給2個, 對應 side_effect 的兩個回傳值
    result = await calendar_service.send_calendar_invite(
        db=mock_db,
        summary="Meeting",
        description="Desc",
        start_time_ts=1700000000,
        end_time_ts=1700003600,
        user_ids=[1,2]
    )

    ### Assert
    assert set(result["sent_to"]) == {"xchange_1@example.com","xchange_2@example.com"}

    # 驗證 create_event 收到的 attendee_emails 也有2個
    call_kwargs = mock_calendar_client.create_event.call_args.kwargs
    assert set(call_kwargs["attendee_emails"]) == {"xchange_1@example.com","xchange_2@example.com"}

async def test_send_invite_skips_user_not_found(
    calendar_service,
    mock_auth_repo,
    mock_calendar_client,
    mock_db
):
    ## Arrange
    mock_auth_repo.find_account_by_user_id.side_effect = [
        None,
        make_account(email="xchange@example.com")
    ]

    # create_event return 固定值, 只被呼叫1次
    mock_calendar_client.create_event.return_value = {
        "id": "evt_3",
        "htmlLink": "https://cal/evt_3"
    }

    ### Act
    # user_ids 給2個, 對應 side_effect 的2個回傳值, 其中一個是 None
    result = await calendar_service.send_calendar_invite(
        db=mock_db,
        summary="Meeting",
        description="Desc",
        start_time_ts=1700000000,
        end_time_ts=1700003600,
        user_ids=[1,2]
    )
    
    ### Assert
    assert result["sent_to"] == ["xchange@example.com"]
    # 驗證 create_event 收到的 attendee_emails 有1個
    call_kwargs = mock_calendar_client.create_event.call_args.kwargs
    assert set(call_kwargs["attendee_emails"]) == {"xchange@example.com"}

async def test_send_invite_skips_user_without_email(
    calendar_service,
    mock_auth_repo,
    mock_calendar_client,
    mock_db
):
    ## Arrange
    mock_auth_repo.find_account_by_user_id.side_effect = [
        make_account(email=None), # 帳號存在, 但沒 Email
        make_account(email="xchange@example.com")
    ]

    # create_event return 固定值, 只被呼叫1次
    mock_calendar_client.create_event.return_value = {
        "id": "evt_4",
        "htmlLink": "https://cal/evt_4"
    }

    ### Act
    # user_ids 給2個, 對應 side_effect 的2個回傳值
    result = await calendar_service.send_calendar_invite(
        db=mock_db,
        summary="Meeting",
        description="Desc",
        start_time_ts=1700000000,
        end_time_ts=1700003600,
        user_ids=[1,2]
    )
    
    ### Assert
    assert result["sent_to"] == ["xchange@example.com"]
    # 驗證 create_event 收到的 attendee_emails 有1個
    call_kwargs = mock_calendar_client.create_event.call_args.kwargs
    assert set(call_kwargs["attendee_emails"]) == {"xchange@example.com"}

async def test_send_invite_all_invalid_raises_404(
    calendar_service,
    mock_auth_repo,
    mock_db
):
    ## Arrange
    mock_auth_repo.find_account_by_user_id.side_effect = [
        None, # 查無帳號
        make_account(email=None)
    ]

    ### Act + Assert
    # user_ids 給2個, 對應 side_effect 的2個回傳值
    with pytest.raises(HTTPException) as exc_info:
        await calendar_service.send_calendar_invite(
            db=mock_db,
            summary="Meeting",
            description="Desc",
            start_time_ts=1700000000,
            end_time_ts=1700003600,
            user_ids=[1,2]
        )
    
    ### Assert
    assert exc_info.value.status_code == 404
    
async def test_send_invite_calendar_client_raises_reraises(
    calendar_service,
    mock_auth_repo,
    mock_calendar_client,
    mock_db
):
    ### Arrange
    mock_auth_repo.find_account_by_user_id.return_value = make_account(email="xchange@example.com")

    mock_calendar_client.create_event.side_effect = RuntimeError("Google API Error")

    ### Act
    with pytest.raises(RuntimeError, match="Google API Error"):
        await calendar_service.send_calendar_invite(
            db=mock_db,
            summary="Meeting",
            description="Desc",
            start_time_ts=1700000000,
            end_time_ts=1700003600,
            user_ids=[1]
        )

async def test_delete_event_success(calendar_service, mock_calendar_client):
    ### Arrange
    mock_calendar_client.delete_event.return_value = None

    ### Act
    result = await calendar_service.delete_calendar_event(event_id="evt_99")

    ### Assert
    assert result == {"event_id": "evt_99", "status": "deleted"}
    # 驗證 calendar service 有沒有把 event_id 正確傳遞下去
    mock_calendar_client.delete_event.assert_called_once_with(event_id="evt_99")

async def test_delete_event_client_raises_reraises(calendar_service, mock_calendar_client):
    ### Arrange
    mock_calendar_client.delete_event.side_effect = RuntimeError("delete failed")

    ### Act
    with pytest.raises(RuntimeError, match="delete failed"):
        await calendar_service.delete_calendar_event(event_id="evt_99")
