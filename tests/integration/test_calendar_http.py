import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException


def test_post_calendar_event_success(client, mocker):
    from src.app.adapter import _calendar_service

    mock_send = mocker.patch.object(
        _calendar_service,
        'send_calendar_invite',
        new=AsyncMock(return_value={
            "event_id": "evt_test_001",
            "html_link": "https://calendar.google.com/evt_test_001",
            "status": "success",
            "sent_to": ["test@example.com"],
        })
    )

    response = client.post(
        "/auth-service/api/v1/calendar/events",
        json={
            "summary": "Test Meeting",
            "description": "Test Description",
            "start_time": 1700000000,
            "end_time": 1700003600,
            "user_ids": [1],
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "0"
    assert body["data"]["event_id"] == "evt_test_001"
    assert body["data"]["status"] == "success"

    # 驗證 router 把 HTTP body 經 Pydantic DTO 正確轉交 service（db 由 Depends 注入，不在此斷言）
    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args.kwargs
    assert call_kwargs["summary"] == "Test Meeting"
    assert call_kwargs["description"] == "Test Description"
    assert call_kwargs["start_time_ts"] == 1700000000
    assert call_kwargs["end_time_ts"] == 1700003600
    assert call_kwargs["user_ids"] == [1]


def test_post_calendar_event_missing_start_time_returns_422(client):
    # CalendarEventDTO 的 start_time/end_time 是必填；Pydantic v2 升級後此欄位行為若改變，此測試會失敗
    response = client.post(
        "/auth-service/api/v1/calendar/events",
        json={
            "summary": "Test Meeting",
            "description": "No times",
            "user_ids": [1],
        }
    )
    assert response.status_code == 422


def test_post_calendar_event_service_raises_404(client, mocker):
    from src.app.adapter import _calendar_service

    mocker.patch.object(
        _calendar_service,
        'send_calendar_invite',
        new=AsyncMock(side_effect=HTTPException(status_code=404, detail="Users not found"))
    )

    response = client.post(
        "/auth-service/api/v1/calendar/events",
        json={
            "summary": "Test Meeting",
            "description": "Test Description",
            "start_time": 1700000000,
            "end_time": 1700003600,
            "user_ids": [999],
        }
    )

    assert response.status_code == 404


def test_delete_calendar_event_success(client, mocker):
    from src.app.adapter import _calendar_service

    mock_delete = mocker.patch.object(
        _calendar_service,
        'delete_calendar_event',
        new=AsyncMock(return_value={
            "event_id": "evt_to_delete",
            "status": "deleted",
        })
    )

    response = client.delete(
        "/auth-service/api/v1/calendar/events/evt_to_delete"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == "0"
    assert body["data"]["event_id"] == "evt_to_delete"
    assert body["data"]["status"] == "deleted"

    # 驗證 router 把 path param event_id 正確轉交 service
    mock_delete.assert_called_once_with(event_id="evt_to_delete")
